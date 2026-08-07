# CTC_Colab: V2 Multi-Pass Architecture

Welcome to the V2 branch! This branch introduces a major architectural shift to solve Google Colab's VRAM constraints and improve the quality of the generated Manim code.

## Why Multi-Pass?

In V1, the pipeline operated on a per-concept loop: it would load the LLM, generate a storyboard, generate a script, and render the video, all before moving to the next concept.

**The Problem:**
Generating a high-quality storyboard requires excellent spatial reasoning (which `DeepSeek-R1-Distill-Qwen-14B` excels at due to its Chain-of-Thought `<think>` process). However, generating pristine, zero-shot Manim Python code requires a model specifically trained on massive coding datasets (which `Codestral-22B` excels at). 

Using two powerful 14B+ models requires ~24GB of VRAM, but the free Google Colab T4 GPU only provides **16GB**. Loading both simultaneously causes an instant Out-Of-Memory (OOM) crash.

**The Solution:**
V2 implements a strict Multi-Pass execution pipeline to isolate GPU memory:

1. **Phase 1 (Storyboard)**: Loads `DeepSeek-R1-14B` (9GB). Generates all storyboards for the PDF. Then deletes the model from memory and triggers Python garbage collection (`gc.collect()`).
2. **Phase 2 (Manim Code)**: Loads `Codestral-22B` (13.34GB). Reads the storyboards and generates all Manim scripts. Deletes the model from memory.
3. **Phase 3 (Render)**: Executes the Manim compiler for all generated scripts.

## Argparse Controls

To prevent the pipeline from running for hours on large PDFs, V2 introduces a `--limit` flag.

```bash
# Processes the first 10 concepts (default)
python pipeline.py --pdf "data/inputs/pdfs/Permutations_text.pdf"

# Processes only the first 2 concepts
python pipeline.py --pdf "data/inputs/pdfs/Permutations_text.pdf" --limit 2
```
