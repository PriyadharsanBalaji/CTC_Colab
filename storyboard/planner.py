"""Storyboard planning prompt and generation logic (V6 Vision Mode)."""

import base64
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from core.llm_client import OllamaClient
from core.parser import ConceptChunk
from storyboard.schemas import Storyboard


def get_pdf_page_image_base64(pdf_path: str, page_num: int) -> str:
    """Renders a PDF page to a PNG image and encodes it as base64."""
    if fitz_absent := (fitz is None):
        raise ImportError("PyMuPDF is not installed. Please run: pip install pymupdf")
        
    doc = fitz.open(pdf_path)
    # PyMuPDF uses 0-based indexing for pages, but parser page_num might be 1-based.
    # We'll assume page_num from parser is 1-based (i+1), so subtract 1.
    page_index = max(0, page_num - 1)
    
    if page_index >= len(doc):
        page_index = len(doc) - 1
        
    page = doc.load_page(page_index)
    
    # Render at 150 DPI for good VLM readability without massive token usage
    pix = page.get_pixmap(matrix=fitz.Matrix(150/72, 150/72))
    img_bytes = pix.tobytes("png")
    doc.close()
    
    return base64.b64encode(img_bytes).decode('utf-8')


def build_planner_prompt(concept: ConceptChunk) -> str:
    """Creates the prompt to generate a continuous visual storyboard."""
    
    return f"""You are a master educational director and mathematical animation expert.
We need to teach a specific mathematical concept extracted from a textbook using Manim (Python).

Concept Title: {concept.title}
Source Material Context (Text):
{concept.content}

You also have an IMAGE of the actual textbook page containing this concept. Look at the layout, diagrams, and equations in the image to inform your storyboard!

CRITICAL RULES:
1. CONTINUOUS STORYTELLING: Your storyboard MUST be one continuous visual flow. Do not abruptly wipe the screen between scenes. The visual elements established in Scene 1 must logically evolve and transition into Scene 2, and so on.
2. TEXTBOOK ALIGNMENT: Ensure the animation directly relates to and explains the core mathematical concept provided in the Source Material Context and Image.
3. SCENE LIMIT: Do NOT generate more than 6 scenes total. For large chunks or exercises, summarize them into a maximum of 6 key scenes.
4. UNIFORM PACING: Each scene MUST represent approximately 8 seconds of screen time. Your narration and visual descriptions should be concise and uniform in length to maintain coherency.
5. MANIM COMPATIBILITY: Your `visual_description` and `animation_instructions` must be EASILY achievable using basic Manim elements (Text, MathTex, Rectangle, Circle, Arrow). Do not describe highly complex 3D scenes, external 3D models, or intricate custom SVGs. Focus on clean, basic mathematical visualizations.
6. NARRATION: Write clear, engaging voiceover narration for each scene.

Output the result strictly matching the provided simple JSON schema.
"""

def generate_storyboard(client: OllamaClient, concept: ConceptChunk, pdf_path: str) -> Storyboard:
    """Generates the structured Pydantic storyboard for a concept chunk using a Vision model."""
    prompt = build_planner_prompt(concept)
    
    # Extract the textbook page as an image for the VLM
    b64_image = get_pdf_page_image_base64(pdf_path, concept.page_num)
    
    json_data = client.generate_json(prompt, Storyboard, images=[b64_image])
    
    # Validate and parse into Pydantic model
    storyboard = Storyboard(**json_data)
    return storyboard
