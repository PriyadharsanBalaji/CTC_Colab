"""Storyboard planning prompt and generation logic (Advanced V3)."""

from core.llm_client import LocalLLMClient
from core.parser import ConceptChunk
from storyboard.schemas import Storyboard


def build_planner_prompt(concept: ConceptChunk) -> str:
    """Creates the prompt to generate a highly structured advanced storyboard."""
    
    return f"""You are a master curriculum designer and mathematical animation director.
We need to teach a specific mathematical concept extracted from an NCERT textbook using Manim (Python).

Concept Title: {concept.title}
Source Material Context:
{concept.content}

Requirements:
1. You must act as a master educational director. Do NOT just dump a scene. You must map out the exact `educational_strategy`, `conceptual_objects`, and the precise `timeline` of events that will occur on screen.
2. The `timeline` MUST be continuous. Visual state in one scene must carry over logically to the next.
3. Every `conceptual_object` you define must be visually achievable using basic Manim abstractions (Text, MathTex, Rectangle, Circle, Arrows).
4. The timeline must explicitly define `visual_state` (what is visible/hidden) and `visual_action` (what happens).
5. Align your narration mathematically with the visual actions using `narration_visual_alignment`.
6. SIMPLICITY IN MANIM: While your educational logic must be advanced and precise, the `visual_action`s must be mathematically clean and easy to code (e.g. "Highlight the second column", "Fade in the equation", "Transform the 6 into a 5").

Output the result strictly matching the provided massive JSON schema.
"""

def generate_storyboard(client: LocalLLMClient, concept: ConceptChunk) -> Storyboard:
    """Generates the structured Pydantic storyboard for a concept chunk."""
    prompt = build_planner_prompt(concept)
    json_data = client.generate_json(prompt, Storyboard)
    
    # Validate and parse into Pydantic model
    storyboard = Storyboard(**json_data)
    return storyboard
