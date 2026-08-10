# CTC_Colab: V7 Advanced Pedagogical Pipeline (HuggingFace Vision)

Welcome to the V7 branch! This branch replaces Ollama with a robust HuggingFace `transformers` pipeline for Phase 1 (Storyboard Generation) using Qwen2-VL to guarantee flawless JSON schema adherence.

## Architecture Trajectory (Why did we switch?)

### V1: The Baseline Single-Pass
In V1, the pipeline operated on a per-concept loop: it would load the LLM, generate a storyboard, generate a script, and render the video, all before moving to the next concept. 
- **The Problem:** We were using a single small model (Qwen 7B Coder) for everything. It was decent at code but terrible at spatial/creative reasoning. Manim requires complex spatial coordinate tracking, causing the models to hallucinate custom helper functions (`highlight_column()`) and crash.
- **The Fix:** We needed a model that could "think" spatially for the storyboard, and a flagship coding model to write the Python. But we couldn't load both into a free Google Colab 16GB GPU.

### V2: The Multi-Pass Architecture
To solve the VRAM limits, V2 implemented a strict Multi-Pass execution pipeline to isolate GPU memory:
1. **Phase 1 (Storyboard)**: Loads `DeepSeek-R1-14B` (9GB). Uses its `<think>` capability to handle spatial logic, coordinate math, and narrative flow. Generates all storyboards, then completely unloads from memory.
2. **Phase 2 (Manim Code)**: Loads `Codestral-22B` (13.34GB). Reads the storyboards and generates all Manim scripts using Mistral's flagship coding knowledge. Unloads from memory.
3. **Phase 3 (Render)**: Executes the Manim compiler.
- **The Problem:** The storyboard schema was too simple (just returning a list of basic scenes). Manim had to constantly wipe the screen and recalculate coordinates, leading to text overlapping and items rendering off-screen. It also lacked deep educational structure.

### V3: The Advanced Pedagogical Structure (Deprecated)
V3 kept the Multi-Pass architecture but introduced a massive, highly detailed Pydantic JSON schema (10+ classes) forcing the AI to act as a master curriculum designer.
- **The Problem:** 14B models are not smart enough to consistently output 150+ lines of strictly formatted nested JSON. It hallucinated invalid JSON arrays and dictionaries, causing Pydantic and `json.loads()` to crash miserably despite aggressive type loosening and auto-retry loops.

### V4: The Simple Continuous Storyboard (Current)
## 3. Environment Setup (Kaggle)

Kaggle gives you access to 2x T4 GPUs (32GB VRAM total), which provides the massive compute power needed to run a Vision model alongside the Code model!

**Cell 1: Install Dependencies**
```bash
!apt-get update && apt-get install -y zstd pciutils build-essential libcairo2-dev libpango1.0-dev ffmpeg
!pip install pdfplumber pypdf pymupdf pydantic manim requests transformers accelerate qwen-vl-utils torch torchvision
```

**Cell 2: Install and Start Ollama**
```bash
!curl -fsSL https://ollama.com/install.sh | sh

# Set Ollama to save models in the persistent working directory!
import os
os.environ["OLLAMA_MODELS"] = "/kaggle/working/ollama_models"

# Start the Ollama server in the background
import subprocess
import time
print("Starting Ollama server...")
subprocess.Popen(["ollama", "serve"], env=os.environ.copy())
time.sleep(3)

# Pull the Code model (Maternion for Manim code)
!ollama pull Maternion/manim-coder:14b
```

## 4. Running the Pipeline

Once Ollama is running and the models are pulled, you can execute the pipeline:

```bash
!python pipeline.py --pdf "data/inputs/pdfs/Permutations_text.pdf" --limit 5
```

## Argparse Controls

Use the `--limit` flag to test batches and avoid running a 50-page PDF at once:

```bash
# Processes the first 2 concepts
python pipeline.py --pdf "data/inputs/pdfs/Permutations_text.pdf" --limit 2
```

### V6: Kaggle Dual-GPU Pipeline (Ollama Vision Bottleneck)
While V6 successfully migrated the pipeline to Kaggle, we hit severe limitations using Ollama for Phase 1 (Storyboard Generation) with Vision models:
1. **Architecture Lags:** New models like Llama 3.2 Vision (mllama architecture) were not immediately supported on Kaggle's cached Ollama binaries, leading to unknown model architecture errors.
2. **Persistence Issues:** Kaggle destroys the /root/.ollama directory on kernel restarts, forcing 8GB+ models to be re-downloaded every session.
3. **JSON Schema Adherence:** Small quantization models like llava:13b and llava-llama3 heavily struggled to consistently generate massive, deeply nested JSON schemas (e.g., Storyboard containing lists of Scenes). They would frequently drop root keys, output single scenes instead of lists, or literally echo the schema definition back due to weak instruction tuning.

Due to these unreliability issues with Ollama's vision ecosystem, V7 shifts Phase 1 to native HuggingFace 	ransformers (using models like Qwen2-VL) for perfect JSON adherence, while retaining Ollama strictly for Phase 2 code generation.
