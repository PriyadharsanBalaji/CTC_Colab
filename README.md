# CTC_Colab: V3 Advanced Pedagogical Pipeline

Welcome to the V3 branch! This branch introduces massive improvements to visual layout, bounds enforcement, and a highly advanced pedagogical storyboard schema to ensure high-quality, educationally sound Manim outputs.

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
V4 abandons the bloated schema and pivots back to an ultra-simple JSON structure (`Scene` and `Storyboard`). 
- **The Fix:** To solve the "screen wipe" and "bad layout" bugs from V1/V2, V4 relies entirely on **Prompt Engineering** instead of schema bloat. The system prompt explicitly bans wiping the screen (`self.clear()`) and mathematically forces a continuous, evolving narrative that maps directly to the textbook.

## 3. Environment Setup (Google Colab)

To run this on a free Google Colab T4 GPU, run the following cells.

**Cell 1: Install Dependencies**
```bash
!pip install pypdf pydantic manim requests
```

**Cell 2: Install and Start Ollama**
```bash
!curl -fsSL https://ollama.com/install.sh | sh

# Start the Ollama server in the background
import subprocess
import time
print("Starting Ollama server...")
subprocess.Popen(["ollama", "serve"])
time.sleep(3)

# Pull the models (this will automatically quantize them to fit in the 16GB GPU)
!ollama pull deepseek-r1:14b
!ollama pull materion/manim-coder:14b
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
