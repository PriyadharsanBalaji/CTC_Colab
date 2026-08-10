"""Main orchestration pipeline for PDF to Manim Videos (End-to-End V5 Ollama)."""

import argparse
import json
import os
import subprocess
import gc
from pathlib import Path

from core.parser import parse_pdf_to_concepts
from core.llm_client import OllamaClient, HFVisionClient
from storyboard.planner import generate_storyboard
from storyboard.schemas import Storyboard
from manim_gen.generator import generate_manim_script, fix_manim_script

def sanitize_filename(name: str) -> str:
    """Removes invalid characters for filenames."""
    return "".join(c if c.isalnum() else "_" for c in name)[:30].strip("_")


def stitch_videos(video_paths: list[str], output_path: str):
    """Uses ffmpeg to concatenate multiple video files into one."""
    if not video_paths:
        return
        
    if len(video_paths) == 1:
        os.rename(video_paths[0], output_path)
        return

    concat_file = "concat_list.txt"
    with open(concat_file, "w") as f:
        for vp in video_paths:
            safe_vp = str(Path(vp).absolute()).replace("\\", "/")
            f.write(f"file '{safe_vp}'\n")

    print(f"Stitching {len(video_paths)} videos into {output_path}...")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", 
        "-i", concat_file, "-c", "copy", output_path
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(concat_file):
        os.remove(concat_file)


def run_pipeline(pdf_path: str, limit: int = 10):
    base_dir = Path("data")
    storyboard_dir = base_dir / "outputs" / "storyboards"
    script_dir = base_dir / "outputs" / "scripts"
    video_dir = base_dir / "outputs" / "videos"
    
    for d in [storyboard_dir, script_dir, video_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"--- Starting V6 Kaggle Pipeline for {pdf_path} (Limit: {limit} concepts) ---")
    
    print("Parsing PDF into Concept Chunks...")
    all_concepts = parse_pdf_to_concepts(pdf_path)
    if not all_concepts:
        print("No concepts found in PDF.")
        return
        
    # Filter concepts and apply limit
    concepts = []
    for concept in all_concepts:
        if len(concept.content.strip()) >= 100:
            concepts.append(concept)
            
    concepts = concepts[:limit]
    print(f"Processing {len(concepts)} concepts after filtering and limiting.")

    # Model Definitions
    STORYBOARD_MODEL = "Qwen/Qwen2-VL-7B-Instruct"
    CODE_MODEL = "Maternion/manim-coder:14b"

    # ---------------------------------------------------------
    # PHASE 1: STORYBOARD GENERATION
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print(f"PHASE 1: STORYBOARD GENERATION ({STORYBOARD_MODEL})")
    print("="*50)
    
    missing_storyboards = []
    for i, concept in enumerate(concepts):
        safe_name = f"concept_{i:02d}_{sanitize_filename(concept.title)}"
        sb_file = storyboard_dir / f"{safe_name}.json"
        if not sb_file.exists():
            missing_storyboards.append((concept, sb_file))
        else:
            print(f"  [Skip] Storyboard already exists: {sb_file}")

    if missing_storyboards:
        print(f"\nProcessing {len(missing_storyboards)} missing storyboards...")
        
        for concept, sb_file in missing_storyboards:
            print(f"  [Task] Generating Storyboard for: {sb_file.stem}...")
            # We MUST instantiate and unload the model for every single concept to bypass a severe memory leak in HuggingFace Qwen2-VL
            client = HFVisionClient(model_name=STORYBOARD_MODEL)
            storyboard = generate_storyboard(client, concept, pdf_path)
            with open(sb_file, "w") as f:
                f.write(storyboard.model_dump_json(indent=2))
            
            client.unload()
    else:
        print("All storyboards already generated. Skipping Phase 1 model load.")

    # ---------------------------------------------------------
    # PHASE 2 & 3: SCRIPT GENERATION & MANIM RENDERING
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("PHASE 2 & 3: SCRIPT GENERATION & MANIM RENDERING (WITH SELF-HEALING)")
    print("="*50)

    code_client = None
    def get_code_client():
        nonlocal code_client
        if code_client is None:
            print(f"\nLoading Code Model: {CODE_MODEL}")
            code_client = OllamaClient(model_name=CODE_MODEL)
        return code_client

    for i, concept in enumerate(concepts):
        safe_name = f"concept_{i:02d}_{sanitize_filename(concept.title)}"
        sb_file = storyboard_dir / f"{safe_name}.json"
        script_file = script_dir / f"{safe_name}.py"
        final_video = video_dir / f"{safe_name}.mp4"
        
        if final_video.exists():
            print(f"  [Skip] Final video already exists: {final_video}")
            continue

        # Generate Script if missing
        if not script_file.exists():
            print(f"  [Task] Generating Manim Script for: {safe_name}...")
            if not sb_file.exists():
                print(f"  [Error] No storyboard found for {safe_name}. Skipping.")
                continue
            with open(sb_file, "r") as f:
                storyboard = Storyboard(**json.load(f))
            client = get_code_client()
            script_code = generate_manim_script(client, storyboard)
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script_code)
                
        # Self-Healing Render Loop
        max_retries = 3
        media_out = base_dir / "outputs" / "manim_temp" / safe_name
        # Prevent Manim from deadlocking/waiting for user input by explicitly providing the Scene class name
        scene_name = "ConceptScene"
        try:
            with open(script_file, "r", encoding="utf-8") as f:
                script_content = f.read()
            import re
            match = re.search(r"class\s+([A-Za-z0-9_]+)\((?:Scene|MovingCameraScene|ZoomedScene)\):", script_content)
            if match:
                scene_name = match.group(1)
        except Exception:
            pass
            
        cmd = [
            "manim", "-ql", 
            "--media_dir", str(media_out.absolute()),
            str(script_file.absolute()),
            scene_name
        ]
        
        for attempt in range(max_retries):
            print(f"  [Task] Rendering Manim Video for: {safe_name} (Attempt {attempt + 1}/{max_retries})...")
            
            # Run Manim, capturing stdout and stderr
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                video_search_dir = media_out / "videos" / script_file.stem / "480p15"
                if video_search_dir.exists():
                    parts = list(video_search_dir.glob("*.mp4"))
                    parts.sort(key=lambda x: x.name)
                    
                    if parts:
                        stitch_videos([str(p) for p in parts], str(final_video))
                        print(f"  [Success] Saved final video to {final_video}")
                    else:
                        print(f"  [Warning] Manim ran but no mp4 files were found for {safe_name}.")
                else:
                    print(f"  [Warning] Manim output directory not found for {safe_name}.")
                break # Success! Break out of retry loop
            else:
                print(f"  [Error] Manim rendering failed!")
                if attempt < max_retries - 1:
                    print(f"  [Self-Healing] Sending traceback to LLM for auto-correction...")
                    with open(script_file, "r", encoding="utf-8") as f:
                        bad_code = f.read()
                    
                    # Extract the bottom part of stderr as traceback
                    traceback_error = process.stderr.strip()
                    if not traceback_error:
                        traceback_error = process.stdout.strip()
                    if len(traceback_error) > 2000:
                        traceback_error = "..." + traceback_error[-2000:]
                        
                    client = get_code_client()
                    fixed_code = fix_manim_script(client, bad_code, traceback_error)
                    
                    with open(script_file, "w", encoding="utf-8") as f:
                        f.write(fixed_code)
                else:
                    print(f"  [Fatal] Manim rendering failed after {max_retries} attempts.")
                    print("--- LAST ERROR TRACEBACK ---")
                    err = process.stderr.strip() or process.stdout.strip()
                    print(err[-1000:])
                    print("----------------------------")

    if code_client is not None:
        print("Unloading Code Model to free VRAM...")
        del code_client
        gc.collect()

    print("\nPipeline Complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CTC End-to-End V5 Pipeline")
    parser.add_argument("--pdf", type=str, required=True, help="Path to input PDF")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of concepts to process (default: 10)")
    
    args = parser.parse_args()
    run_pipeline(args.pdf, args.limit)
