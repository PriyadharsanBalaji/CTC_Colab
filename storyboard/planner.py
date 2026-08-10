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
1. STRICT OCR AND LATEX EXTRACTION: You MUST read the image. If there are equations, formulas, or numbers in the textbook image, you MUST extract them perfectly in LaTeX format. Do NOT skip them. Do NOT use generic placeholders like "solve for x" if the book says "x = 5!".
2. PEDAGOGICAL FLOW: Start the storyboard with a simple, intuitive, real-world example of the concept *before* throwing equations at the student. Make the concept extremely easy to understand.
3. CONCRETE VISUALS (NO HALLUCINATION): You are BANNED from using phrases like "display an image", "show a diagram", or "display a series of images". You must tell the animation engine exactly WHAT to draw. 
   - BAD: "Show an image of permutations."
   - GOOD: "Draw 3 empty boxes. Place the letters A, B, and C inside them. Write the equation $3! = 6$ below the boxes."
4. CONTINUOUS STORYTELLING: Your storyboard MUST be one continuous visual flow. Do not abruptly wipe the screen between scenes.
5. MANIM COMPATIBILITY: Your `visual_description` must be EASILY achievable using basic Manim elements (Text, MathTex, Rectangle, Circle, Arrow). Do not describe highly complex 3D scenes.
6. SCENE LIMIT: Do NOT generate more than 6 scenes total.

Output the result strictly matching the provided simple JSON schema. Include the extracted equations in the `latex_equations` list!
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
