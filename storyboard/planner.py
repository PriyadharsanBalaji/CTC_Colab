"""Storyboard planning prompt and generation logic (V3)."""

from core.llm_client import LocalLLMClient
from core.parser import ConceptChunk
from storyboard.schemas import Storyboard


def build_planner_prompt(concept: ConceptChunk) -> str:
    """Creates the prompt to generate a single continuous storyboard scene."""
    
    return f"""Design ONE highly educational Manim mathematical animation storyboard.
We need to teach a specific mathematical concept extracted from an NCERT textbook.

Concept Title: {concept.title}
Source Material Context:
{concept.content}

Requirements:
1. Design exactly ONE continuous, highly creative scene that visually explains the concept step-by-step. Do NOT create multiple separate scenes that require clearing the screen. Build the concept fluidly.
2. SIMPLICITY IS CRITICAL: This storyboard will be coded by an AI using Manim. Do NOT ask for complex real-world objects (like drawing a lock, a car, or complex machinery). Instead, use simple abstractions like a rectangle divided into columns, simple text lists, or basic geometric shapes.
3. Your `visual_layout` must be precise. (e.g. "Title at the top, a 2x3 grid of Rectangles in the center, and a formula at the bottom").
4. The `animation_sequence` should be a logical list of actions (e.g. 1. Write title, 2. Draw grid, 3. Highlight column, 4. Fade in formula).
5. The `visual_setting` must be strictly basic Manim objects: `Text`, `MathTex`, `Circle`, `Rectangle`, `Square`, `Line`, and `Arrow`.
6. Provide a fluid `narration` (voiceover) that matches the animation sequence perfectly.
7. Use `math_overlay` to show the LaTeX math when applicable. Keep LaTeX very simple and standard.

Output the result strictly matching the provided JSON schema.
"""

def generate_storyboard(client: LocalLLMClient, concept: ConceptChunk) -> Storyboard:
    """Generates the structured Pydantic storyboard for a concept chunk."""
    prompt = build_planner_prompt(concept)
    json_data = client.generate_json(prompt, Storyboard)
    
    # Validate and parse into Pydantic model
    storyboard = Storyboard(**json_data)
    return storyboard
