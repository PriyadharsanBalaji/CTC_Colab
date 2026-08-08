# Project Trajectory: Concept-To-Canvas (CTC) Manim Video Generation

## **Project Overview & Objective**
**Concept-To-Canvas (CTC)** is a fully autonomous, offline AI pipeline designed to democratize high-quality mathematical education. The core inspiration for this project is to automatically generate **"3Blue1Brown-style"** video animations—known for their stunning, intuitive visual math explanations—directly from raw, static textbook material (e.g., NCERT educational PDFs). 

By leveraging the powerful **Manim** graphics engine (the exact same engine created and used by 3Blue1Brown), CTC aims to scale this elite tier of visual education to every concept in a textbook, all without requiring expensive human intervention or costly API calls.

To achieve this, the pipeline runs entirely locally (or on free-tier cloud environments like Google Colab) using heavily quantized, open-weights Large Language Models (LLMs) to perform complex zero-shot reasoning. The AI acts as both a master curriculum designer (planning the pedagogical narrative) and an expert Python animator (writing the Manim code).

This document tracks the evolution of the CTC Colab pipeline, detailing the architectural shifts, the problems encountered with zero-shot AI generation, and the solutions implemented to resolve them.

---

## **Phase 1: The Initial Baseline (V1)**

**Goal:** Build an end-to-end Python pipeline that takes an educational PDF, chunks it into concepts, uses a local LLM to generate a storyboard, uses that same LLM to write a Manim Python script, and finally renders the video using `ffmpeg` to stitch the scenes.

**Architecture:**
- **Pipeline Structure:** Single-pass, interleaved loop. For every concept, the pipeline loaded the LLM, generated the storyboard, generated the script, and rendered the video before moving to the next concept.
- **Model Used:** `Qwen2.5-Coder-7B` (GGUF). 
- **Environment:** Google Colab T4 GPU (16GB VRAM) and a local Windows replica.

**The Problems Encountered:**
1. **Spatial Reasoning Failures:** `Qwen2.5-Coder-7B` is a fantastic coding model but struggles with the complex 3D coordinate geometry required for Manim animations. It frequently hallucinated custom helper functions (like `highlight_column()`) that didn't exist in the Manim library, causing Python `NameError` crashes.
2. **Pedantic Manim Quirks:** The LLM would try to pass `spacing=` instead of `buff=` in `.arrange()`, causing `TypeError`s. It would also try to re-use the exact same `Mobject` instance multiple times in a loop, crashing the Manim renderer.
3. **The "Wait" Trap:** The LLM often generated infinite `self.play(Wait())` loops.

**The Fixes Implemented in V1:**
- Built a sophisticated regex extractor to safely parse ````python` blocks from the LLM output.
- Monkey-patched standard Manim classes (`Create`, `Write`, `FadeIn`) via a generated header script to automatically wrap Python lists in `VGroup`s, preventing crashes when the LLM incorrectly passed lists to animations.
- Added strict system prompts banning hallucinated functions and enforcing `buff=` over `spacing=`.

---

## **Phase 2: The Multi-Model & Multi-Pass Shift (V2)**

**Goal:** Stop the Manim hallucinations by upgrading to "Best-in-Class" models for each specific task: a spatial reasoning model for storyboards, and a flagship coding model for Python scripts.

**Architecture:**
- **Storyboard Model:** `DeepSeek-R1-Distill-Qwen-14B` (Q4_K_M, 9GB). Chosen for its `<think>` Chain-of-Thought capabilities, allowing it to mathematically plan out visual layouts before generating JSON.
- **Code Model:** `Codestral-22B-v0.1` (Q4_K_M, 13.34GB). Mistral's flagship coding model, vastly superior at zero-shot Manim Python syntax.

**The Problems Encountered:**
1. **VRAM Constraints (OOM):** The Google Colab T4 only has 16GB of VRAM. Attempting to load both a 9GB and a 13GB model simultaneously caused an instant Out-Of-Memory crash. 
2. **DeepSeek `<think>` Leakage:** DeepSeek-R1 outputs its reasoning inside `<think>` blocks. Because the original V1 prompt prefilled ````python` at the start of the assistant response, DeepSeek panicked and stuffed its `<think>` block *inside* the Python code, causing an instant `SyntaxError` on line 1 for every single script generated.
3. **KV Cache Explosion:** Even loading just the 13.34GB `Codestral` model independently caused a `Failed to create llama_context` OOM crash. This was because the pipeline initialized an `8192` token context window (KV Cache), which for a massive 22B model, pushed the VRAM usage over the 15GB usable limit.

**The Fixes Implemented in V2:**
- **Multi-Pass Pipeline:** Completely rebuilt `pipeline.py` into a three-phase system. Phase 1 loads DeepSeek, generates all storyboards, and explicitly deletes the model from RAM (`gc.collect()`). Phase 2 loads Codestral, generates all scripts, and unloads. Phase 3 renders the videos.
- **Regex Rescue:** Rewrote the Python extractor to safely strip `<think>...</think>` tags from DeepSeek's output.
- **Context Window Tuning:** Explicitly constrained `Codestral-22B`'s context window (`n_ctx`) down to `4096` to chop the KV cache footprint in half, allowing it to squeeze perfectly into the T4 GPU. (DeepSeek was restored to `8192` since it is a smaller 9GB model and needs room for its massive `<think>` blocks).

---

## **Phase 3: The Pedagogical & Boundary Overhaul (V3 - Current)**

**Goal:** Solve the visual "ugliness" (text overlapping, items rendering off-screen) and elevate the educational quality of the storyboards from a basic list of scenes to a masterclass curriculum design.

**Architecture:**
- Retained the V2 Multi-Pass Pipeline and Model selections.
- Completely replaced the basic Pydantic JSON schema with a highly advanced, deeply nested pedagogical schema.

**The Problems Encountered:**
1. **The Screen Wipe Bug:** V1/V2 asked the LLM to design 4-5 separate "scenes". This caused the coding LLM to constantly wipe the screen and recalculate absolute coordinates, leading to text printing on top of other text, or pushing massive grids entirely off-screen.
2. **Lack of Educational Flow:** The simple storyboard schema failed to map semantic mathematical concepts to visual representations effectively.

**The Fixes Implemented in V3:**
- **Massive Schema Overhaul:** Built 10+ interlocking Pydantic models (`EducationalStrategy`, `ConceptualObject`, `TimelineEvent`, `NarrationVisualAlignment`). The DeepSeek storyboard prompt now acts as a master curriculum designer, mapping every visual element to a mathematical constraint.
- **Continuous Scene Paradigm:** Banned the LLM from generating multiple disconnected scenes. It must now design ONE continuous, evolving visual metaphor that builds fluidly without wiping the screen, making spatial tracking infinitely easier for the coding model.
- **Strict Boundary Scaling:** Injected mathematical boundary constraints into the Codestral prompt:
  - Elements MUST be grouped in a `VGroup` and arranged using `.arrange(DOWN, buff=0.5)` to mathematically guarantee text cannot overlap.
  - Elements MUST dynamically scale using `if my_group.width > config.frame_width - 1: my_group.scale_to_fit_width(config.frame_width - 1)` to mathematically guarantee nothing renders off-screen.
- **Premium Animations:** Banned boring `.Create()` pop-ins, forcing Codestral to use `Write()`, `GrowFromCenter()`, and `TransformMatchingTex()` for engaging, child-friendly visuals. 

---

### **Future Considerations (V4+)**
- **Error Recovery Loop:** If Manim crashes due to a syntax error, pass the Python traceback back to Codestral to auto-fix its own code.
- **Voiceover TTS:** Integrate an open-source TTS model (like XTTS or Edge-TTS) to automatically read the `narration` track from the storyboard and sync it with the Manim timings.
