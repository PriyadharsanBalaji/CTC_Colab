"""Storyboard planning prompt and generation logic."""

from core.llm_client import LocalLLMClient
from core.parser import ConceptChunk
from storyboard.schemas import Storyboard


def build_planner_prompt(concept: ConceptChunk) -> str:
    """Creates the prompt to generate an 8-second chunked storyboard."""
    
    return f"""Design ONE highly educational Manim mathematical animation storyboard.
We need to teach a specific mathematical concept extracted from an NCERT textbook.

Concept Title: {concept.title}
Source Material Context:
{concept.content}

Requirements:
1. Break down the concept into multiple sequential scenes.
2. SIMPLICITY IS CRITICAL: This storyboard will be coded by an AI using Manim. Do NOT ask for complex real-world objects (like drawing a lock, a car, or complex machinery). Instead, use simple abstractions like a rectangle divided into columns, simple text lists, or basic geometric shapes.
3. You may include 2 to 3 logical actions in a scene, but they must be simple and doable in Manim (e.g., revealing a grid of squares, then filling a column, then writing an equation).
4. The `visual_setting` must be strictly basic Manim objects: `Text`, `MathTex`, `Circle`, `Rectangle`, `Square`, `Line`, and `Arrow`.
5. Provide a `narration` (voiceover) and a very simple `animation_description` (e.g., "A formula fades in on screen").
6. Use `math_overlay` to show the LaTeX math when applicable. Keep LaTeX very simple and standard.
7. The final scene should recap the concept using basic bullet points (`Text`).

Output the result strictly matching the provided JSON schema.
"""

def generate_storyboard(client: LocalLLMClient, concept: ConceptChunk) -> Storyboard:
    """Generates the structured Pydantic storyboard for a concept chunk."""
    prompt = build_planner_prompt(concept)
    json_data = client.generate_json(prompt, Storyboard)
    
    # Validate and parse into Pydantic model
    storyboard = Storyboard(**json_data)
    return storyboard
