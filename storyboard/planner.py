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
2. EACH SCENE must be exactly 8 seconds long. However, 8 seconds is a long time in animation! You must pack at least 2-3 distinct, meaningful mathematical steps, transitions, or text reveals into EVERY 8-second scene. Combine simple logical steps (e.g., "Choose Pant, then Choose Shirt") into a SINGLE scene. Do not drag out simple equations.
3. The `visual_setting` must be Manim-Native: Use a clean, dark background focusing exclusively on mathematical notation (LaTeX), geometric primitives (Circles, Rectangles, Arrows), and clean text labels. DO NOT design complex real-world visual metaphors.
4. ABSTRACTION RULE (CRITICAL): If the text uses real-world examples (e.g., pants, shirts, cars, locks), you MUST abstract them. Manim cannot draw physical objects. Represent them as mathematical sets (e.g., $S = \\{{s_1, s_2\\}}$), nodes, color-coded geometric shapes, or simple text labels. Keep the visuals strictly abstract and mathematical.
5. Provide a `narration` (voiceover) and `animation_description` (what is visually happening, e.g., "A formula fades in, then an arrow points to the variable x") for each scene.
6. In later scenes, reveal the formula (if applicable) and use `math_overlay` to show the LaTeX math.
7. The final scene should recap the concept.

Output the result strictly matching the provided JSON schema.
"""

def generate_storyboard(client: LocalLLMClient, concept: ConceptChunk) -> Storyboard:
    """Generates the structured Pydantic storyboard for a concept chunk."""
    prompt = build_planner_prompt(concept)
    json_data = client.generate_json(prompt, Storyboard)
    
    # Validate and parse into Pydantic model
    storyboard = Storyboard(**json_data)
    return storyboard
