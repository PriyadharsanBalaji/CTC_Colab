"""Main orchestration pipeline for PDF to Manim Videos (End-to-End V2 Multi-Pass)."""

import argparse
import json
import os
import subprocess
import gc
from pathlib import Path

from core.parser import parse_pdf_to_concepts
from core.llm_client import LocalLLMClient
from storyboard.planner import generate_storyboard
from storyboard.schemas import Storyboard
from manim_gen.generator import generate_manim_script

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    hf_hub_download = None

def get_or_download_model(repo_id: str, filename: str) -> str:
    if hf_hub_download is None:
        raise ImportError("huggingface_hub is required to auto-download models. pip install huggingface_hub")
        
    print(f"Ensuring model {filename} is downloaded from {repo_id}...")
    
    download_dir = "/content/models" if os.path.exists("/content") else "./models"
    os.makedirs(download_dir, exist_ok=True)
    
    downloaded_path = hf_hub_download(
        repo_id=repo_id, 
        filename=filename, 
        local_dir=download_dir,
        local_dir_use_symlinks=False
    )
    return downloaded_path


def sanitize_filename(name: str) -> str:
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

    print(f"--- Starting V2 Pipeline for {pdf_path} (Limit: {limit} concepts) ---")
    
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
    STORYBOARD_REPO = "unsloth/DeepSeek-R1-Distill-Qwen-14B-GGUF"
    STORYBOARD_FILE = "DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf"
    
    CODE_REPO = "bartowski/Codestral-22B-v0.1-GGUF"
    CODE_FILE = "Codestral-22B-v0.1-Q4_K_M.gguf"

    # ---------------------------------------------------------
    # PHASE 1: STORYBOARD GENERATION
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("PHASE 1: STORYBOARD GENERATION (DeepSeek-R1-14B)")
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
        sb_model_path = get_or_download_model(STORYBOARD_REPO, STORYBOARD_FILE)
        print(f"\nLoading Storyboard Model: {sb_model_path}")
        client = LocalLLMClient(model_path=sb_model_path, n_gpu_layers=-1, n_ctx=8192)
        
        for concept, sb_file in missing_storyboards:
            print(f"  [Task] Generating Storyboard for: {sb_file.stem}...")
            storyboard = generate_storyboard(client, concept)
            with open(sb_file, "w") as f:
                json.dump(storyboard.model_dump(), f, indent=2)
                
        # UNLOAD MODEL TO FREE VRAM
        print("Unloading Storyboard Model to free VRAM...")
        del client
        gc.collect()
    else:
        print("All storyboards already generated. Skipping Phase 1 model load.")

    # ---------------------------------------------------------
    # PHASE 2: MANIM SCRIPT GENERATION
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("PHASE 2: MANIM SCRIPT GENERATION (Codestral-22B)")
    print("="*50)
    
    missing_scripts = []
    for i, concept in enumerate(concepts):
        safe_name = f"concept_{i:02d}_{sanitize_filename(concept.title)}"
        sb_file = storyboard_dir / f"{safe_name}.json"
        script_file = script_dir / f"{safe_name}.py"
        
        if not script_file.exists():
            # Load the storyboard
            with open(sb_file, "r") as f:
                storyboard = Storyboard(**json.load(f))
            missing_scripts.append((storyboard, script_file))
        else:
            print(f"  [Skip] Manim script already exists: {script_file}")

    if missing_scripts:
        code_model_path = get_or_download_model(CODE_REPO, CODE_FILE)
        print(f"\nLoading Code Model: {code_model_path}")
        client = LocalLLMClient(model_path=code_model_path, n_gpu_layers=-1, n_ctx=4096)
        
        for storyboard, script_file in missing_scripts:
            print(f"  [Task] Generating Manim Script for: {script_file.stem}...")
            script_code = generate_manim_script(client, storyboard)
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script_code)
                
        # UNLOAD MODEL TO FREE VRAM
        print("Unloading Code Model to free VRAM...")
        del client
        gc.collect()
    else:
        print("All scripts already generated. Skipping Phase 2 model load.")

    # ---------------------------------------------------------
    # PHASE 3: MANIM RENDERING
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("PHASE 3: MANIM RENDERING")
    print("="*50)

    for i, concept in enumerate(concepts):
        safe_name = f"concept_{i:02d}_{sanitize_filename(concept.title)}"
        script_file = script_dir / f"{safe_name}.py"
        final_video = video_dir / f"{safe_name}.mp4"
        
        if final_video.exists():
            print(f"  [Skip] Final video already exists: {final_video}")
            continue
            
        print(f"  [Task] Rendering Manim Video for: {safe_name}...")
        media_out = base_dir / "outputs" / "manim_temp" / safe_name
        cmd = [
            "manim", "-ql", 
            "--media_dir", str(media_out.absolute()),
            str(script_file.absolute())
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
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
        except subprocess.CalledProcessError:
            print(f"  [Error] Manim rendering failed for {safe_name}. Run manually to see logs.")

    print("\nPipeline Complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CTC End-to-End Multi-Pass Pipeline")
    parser.add_argument("--pdf", type=str, required=True, help="Path to input PDF")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of concepts to process (default: 10)")
    
    args = parser.parse_args()
    run_pipeline(args.pdf, args.limit)
