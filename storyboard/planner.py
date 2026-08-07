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
2. SIMPLICITY IS CRITICAL: This storyboard will be coded by an AI using Manim. If you ask for complex diagrams, physical objects, or 3D rotations, the code will fail! Keep every scene EXTREMELY simple.
3. Limit each scene to ONE major action (e.g., reveal a single equation, OR show a single definition, OR draw a simple circle). Do NOT pack multiple steps into one scene.
4. The `visual_setting` must be strictly basic Manim objects: `Text`, `MathTex`, `Circle`, `Rectangle`, and `Arrow`. DO NOT design real-world visual metaphors.
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
