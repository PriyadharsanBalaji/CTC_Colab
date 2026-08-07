"""Main orchestration pipeline for PDF to Manim Videos (End-to-End)."""

import argparse
import json
import os
import subprocess
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

def get_or_download_model(model_path: str = None) -> str:
    if model_path and os.path.exists(model_path):
        return model_path
    
    if hf_hub_download is None:
        raise ImportError("huggingface_hub is required to auto-download models. pip install huggingface_hub")
        
    print("Model not found or not provided. Downloading default Qwen2.5-7B GGUF model...")
    repo_id = "Qwen/Qwen2.5-7B-Instruct-GGUF"
    filename = "qwen2.5-7b-instruct-q4_k_m.gguf"
    
    download_dir = "/content/models" if os.path.exists("/content") else "./models"
    os.makedirs(download_dir, exist_ok=True)
    
    downloaded_path = hf_hub_download(
        repo_id=repo_id, 
        filename=filename, 
        local_dir=download_dir,
        local_dir_use_symlinks=False
    )
    print(f"Model downloaded to: {downloaded_path}")
    return downloaded_path


def sanitize_filename(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name)[:30].strip("_")


def stitch_videos(video_paths: list[str], output_path: str):
    """Uses ffmpeg to concatenate multiple video files into one."""
    if not video_paths:
        return
        
    if len(video_paths) == 1:
        # Just rename/copy
        os.rename(video_paths[0], output_path)
        return

    # Create a concat file for ffmpeg
    concat_file = "concat_list.txt"
    with open(concat_file, "w") as f:
        for vp in video_paths:
            # Format requires forward slashes and escaping
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


def run_pipeline(pdf_path: str, model_path: str = None):
    base_dir = Path("data")
    storyboard_dir = base_dir / "outputs" / "storyboards"
    script_dir = base_dir / "outputs" / "scripts"
    video_dir = base_dir / "outputs" / "videos"
    
    # Ensure dirs exist
    for d in [storyboard_dir, script_dir, video_dir]:
        d.mkdir(parents=True, exist_ok=True)

    print(f"--- Starting Pipeline for {pdf_path} ---")
    
    # 1. Parse PDF
    print("Parsing PDF into Concept Chunks...")
    concepts = parse_pdf_to_concepts(pdf_path)
    
    if not concepts:
        print("No concepts found in PDF.")
        return
        
    # We load the LLM client lazily to save resources if everything is cached
    client = None
    def get_client():
        nonlocal client
        if client is None:
            actual_model_path = get_or_download_model(model_path)
            print(f"\nLoading Model from: {actual_model_path} (Offloading all layers to GPU for Colab T4)")
            client = LocalLLMClient(model_path=actual_model_path, n_gpu_layers=-1) # -1 is best for Colab T4 (16GB VRAM)
        return client

    # 2. Iterate through concepts
    for i, concept in enumerate(concepts):
        # Ignore very short chunks
        if len(concept.content.strip()) < 100:
            continue
            
        safe_name = f"concept_{i:02d}_{sanitize_filename(concept.title)}"
        print(f"\n--- Processing: {safe_name} ---")
        
        sb_file = storyboard_dir / f"{safe_name}.json"
        script_file = script_dir / f"{safe_name}.py"
        final_video = video_dir / f"{safe_name}.mp4"
        
        # A. STORYBOARD GENERATION (RESUME CHECK)
        if sb_file.exists():
            print(f"  [Skip] Storyboard already exists: {sb_file}")
            with open(sb_file, "r") as f:
                sb_data = json.load(f)
                storyboard = Storyboard(**sb_data)
        else:
            print(f"  [Task] Generating Storyboard...")
            storyboard = generate_storyboard(get_client(), concept)
            with open(sb_file, "w") as f:
                json.dump(storyboard.model_dump(), f, indent=2)
                
        # B. MANIM SCRIPT GENERATION (RESUME CHECK)
        if script_file.exists():
            print(f"  [Skip] Manim script already exists: {script_file}")
            with open(script_file, "r") as f:
                script_code = f.read()
        else:
            print(f"  [Task] Generating Manim Script...")
            script_code = generate_manim_script(get_client(), storyboard)
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(script_code)
                
        # C. MANIM RENDERING & STITCHING (RESUME CHECK)
        if final_video.exists():
            print(f"  [Skip] Final video already exists: {final_video}")
        else:
            print(f"  [Task] Rendering Manim Video...")
            # We run manim on the generated script
            # -p = preview (we omit to avoid opening player)
            # -q l = low quality (480p15) for speed
            # --media_dir = override where media is saved
            media_out = base_dir / "outputs" / "manim_temp" / safe_name
            cmd = [
                "manim", "-ql", 
                "--media_dir", str(media_out.absolute()),
                str(script_file.absolute())
            ]
            
            try:
                subprocess.run(cmd, check=True)
                
                # Manim outputs videos to media_dir/videos/script_name/480p15/
                # We need to find all mp4 files generated and stitch them
                video_search_dir = media_out / "videos" / script_file.stem / "480p15"
                if video_search_dir.exists():
                    parts = list(video_search_dir.glob("*.mp4"))
                    parts.sort(key=lambda x: x.name) # Ensure sequential order
                    
                    if parts:
                        stitch_videos([str(p) for p in parts], str(final_video))
                        print(f"  [Success] Saved final video to {final_video}")
                    else:
                        print("  [Warning] Manim ran but no mp4 files were found.")
                else:
                    print("  [Warning] Manim output directory not found.")
            except subprocess.CalledProcessError as e:
                print(f"  [Error] Manim rendering failed for {safe_name}. See logs for details.")

    print("\nPipeline Complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run CTC End-to-End Pipeline on Colab")
    parser.add_argument("--pdf", type=str, required=True, help="Path to input PDF")
    parser.add_argument("--model", type=str, required=False, default=None, help="Path to local .gguf model (optional, will download if not provided)")
    
    args = parser.parse_args()
    run_pipeline(args.pdf, args.model)
