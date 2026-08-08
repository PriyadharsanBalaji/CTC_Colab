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

### V3: The Advanced Pedagogical Structure (Current)
V3 keeps the V2 Multi-Pass memory architecture, but completely overhauls the internal logic:
1. **Massive Pydantic Schema Overhaul (`storyboard/schemas.py`)**
   The storyboard planner no longer just asks for "scenes". DeepSeek-R1 is now forced to act as a master curriculum designer, filling out a massive, highly detailed JSON structure containing:
   - `educational_strategy` (core idea, misconceptions)
   - `conceptual_objects` (semantic meaning of on-screen items)
   - `timeline` (continuous, step-by-step logic detailing exact `visual_state` changes without wiping the screen)
   - `mathematical_constraints` and `narration_visual_alignment`
2. **Strict Boundary Enforcement (`manim_gen/generator.py`)**
   Codestral is given strict mathematical rules to prevent the "text overlapping" and "off-screen" bugs:
   - Elements are forced into `VGroup`s and arranged using `.arrange(DOWN, buff=0.5)`.
   - Dynamic scaling logic is injected: `if my_group.width > config.frame_width - 1: my_group.scale_to_fit_width(config.frame_width - 1)` so nothing renders off-screen.
3. **Premium Animations**
   Boring `.Create()` animations have been replaced. Codestral uses `Write()`, `GrowFromCenter()`, and `TransformMatchingTex()`.

## Argparse Controls

Use the `--limit` flag to test batches and avoid running a 50-page PDF at once:

```bash
# Processes the first 2 concepts
python pipeline.py --pdf "data/inputs/pdfs/Permutations_text.pdf" --limit 2
```
