"""Storyboard planning prompt and generation logic (Simplified V4)."""

from core.llm_client import LocalLLMClient
from core.parser import ConceptChunk
from storyboard.schemas import Storyboard


def build_planner_prompt(concept: ConceptChunk) -> str:
    """Creates the prompt to generate a simple but continuous storyboard."""
    
    return f"""You are a master educational director and mathematical animation expert.
We need to teach a specific mathematical concept extracted from a textbook using Manim (Python).

Concept Title: {concept.title}
Source Material Context:
{concept.content}

CRITICAL RULES:
1. CONTINUOUS STORYTELLING: Your storyboard MUST be one continuous visual flow. Do not abruptly wipe the screen between scenes. The visual elements established in Scene 1 must logically evolve and transition into Scene 2, and so on.
2. TEXTBOOK ALIGNMENT: Ensure the animation directly relates to and explains the core mathematical concept provided in the Source Material Context.
3. SCENE LIMIT: Do NOT generate more than 6 scenes total. For large chunks or exercises, summarize them into a maximum of 6 key scenes.
4. VISUAL SIMPLICITY: Your `visual_description` and `animation_instructions` must be achievable using basic Manim elements (Text, MathTex, Rectangle, Circle, Arrow). Do not describe overly complex 3D scenes or external images.
5. NARRATION: Write clear, engaging voiceover narration for each scene.

Output the result strictly matching the provided simple JSON schema.
"""

def generate_storyboard(client: LocalLLMClient, concept: ConceptChunk) -> Storyboard:
    """Generates the structured Pydantic storyboard for a concept chunk."""
    prompt = build_planner_prompt(concept)
    json_data = client.generate_json(prompt, Storyboard)
    
    # Validate and parse into Pydantic model
    storyboard = Storyboard(**json_data)
    return storyboard
