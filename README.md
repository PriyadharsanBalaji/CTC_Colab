# CTC_Colab: V3 Single-Scene Visual Bounds

Welcome to the V3 branch! Building on the Multi-Pass architecture from V2, V3 introduces massive improvements to visual layout, bounds enforcement, and storyboard simplicity to ensure high-quality Manim outputs.

## What Changed in V3?

1. **Single Continuous Scene (`storyboard/schemas.py`)**
   In previous versions, the Storyboard planner would generate 4-5 distinct scenes. This caused Manim to constantly wipe the screen and recalculate coordinates, leading to bugs. V3 forces the LLM to design exactly ONE continuous, highly creative scene that builds fluidly, acting as a focused visual metaphor.

2. **Strict Boundary Enforcement (`manim_gen/generator.py`)**
   The Codestral prompt has been injected with strict mathematical rules to prevent the "text overlapping" and "off-screen" bugs:
   - Elements are forced into `VGroup`s and mathematically arranged using `.arrange(DOWN, buff=0.5)` to guarantee they never physically overlap.
   - Dynamic scaling logic is injected: `if my_group.width > config.frame_width - 1: my_group.scale_to_fit_width(config.frame_width - 1)` so that nothing ever renders off-screen.

3. **Premium Animations**
   Boring `.Create()` animations have been heavily discouraged. The LLM is now instructed to use engaging, child-friendly animations like `Write()`, `GrowFromCenter()`, and `TransformMatchingTex()`.

## Argparse Controls

Use the `--limit` flag to test batches:

```bash
# Processes the first 2 concepts
python pipeline.py --pdf "data/inputs/pdfs/Permutations_text.pdf" --limit 2
```
