"""Manim script generation using the LLM from a JSON storyboard."""

import re
from core.llm_client import LocalLLMClient
from storyboard.schemas import Storyboard


def build_manim_prompt(storyboard: Storyboard) -> str:
    """Creates the prompt to generate a Manim Python script from the storyboard."""
    
    # We serialize the storyboard object to pass into the prompt
    storyboard_json = storyboard.model_dump_json(indent=2)
    
    return f"""You are an expert Manim (Python) animator.
I have a storyboard for an educational video.

STORYBOARD JSON:
{storyboard_json}

REQUIREMENTS:
1. Write a complete, runnable Python script using the Manim library.
2. The script must contain a single class `ConceptScene(Scene)`.
3. Animate the scenes described in the storyboard sequentially within this single class.
4. Implement the `math_overlay` (using `MathTex`) exactly as specified when `reveals_formula` is true.
5. Do NOT use `ImageMobject`, `SVGMobject`, or any external files (no .png, .jpg, .svg). You must draw everything using built-in Manim shapes (Circle, Rectangle, Polygon) or represent them with `Text` or `MathTex`.
6. STRICT MANIM RULES to prevent crashes:
   - Do NOT use `MoveToTarget`. If you need to move/change an object, use `self.play(Transform(obj1, obj2))` or `self.play(obj.animate.shift(RIGHT))`.
   - Use `VGroup` instead of `Group`.
   - Never instantiate a raw `Mobject()`. Use `VMobject()`, `VGroup()`, or specific geometric shapes.
   - Do NOT use hallucinated classes like `Grid`, `Box`, `Point`. ONLY use standard classes: `Circle`, `Rectangle`, `Line`, `Arrow`, `NumberPlane`, `Text`, `MathTex`, and `VGroup`.
   - Do NOT pass Python lists directly into animations like `Create(my_list)`. You MUST unpack them or use a VGroup: e.g., `Create(VGroup(*my_list))` or `self.play(*[Create(obj) for obj in my_list])`.
7. SPATIAL AWARENESS & SCREEN CLEARING (CRITICAL):
   - You MUST call `self.play(FadeOut(*self.mobjects))` at the very end of EVERY scene. The screen must be completely blank before the next scene begins.
   - Do NOT use `.to_edge(RIGHT)`, `.to_edge(LEFT)`, or absolute coordinates like `.move_to([4, 2, 0])` which push things off-screen.
   - Instead, you MUST group related text/math using `VGroup(text1, text2).arrange(DOWN).move_to(ORIGIN)` so that everything is perfectly centered in the middle of the screen.
   - Scale down large equations using `.scale(0.7)`.
8. Do NOT include `self.play(Wait(...))` endlessly, just animate the actions and pause briefly between scenes.
9. Return ONLY the raw Python code inside a markdown code block ```python ... ``` without any surrounding explanations.
"""

def extract_python_code(llm_response: str) -> str:
    """Extracts Python code from a markdown block."""
    match = re.search(r"```python\n(.*?)\n```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Fallback if no markdown block is used
    return llm_response.strip()

def generate_manim_script(client: LocalLLMClient, storyboard: Storyboard) -> str:
    """Generates the Manim python script string."""
    prompt = build_manim_prompt(storyboard)
    
    # We bypass the strict JSON mode here since we want Python code
    # We'll construct a direct prompt
    system_prompt = "You are an expert Python Manim animator. Output only valid Python code inside ```python blocks."
    
    formatted_prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n```python\n"
    )
    
    print("[LLM] Generating Manim Script (this might take a minute)...")
    response = client.llm(
        formatted_prompt,
        max_tokens=4096,
        temperature=0.2, # Low temp for code
        stop=["```\n<|im_end|>", "<|im_end|>"],
        echo=False
    )
    
    raw_text = "```python\n" + response['choices'][0]['text']
    code = extract_python_code(raw_text)
    
    # Safety net: If the LLM still tries to use ImageMobject, replace it with a Text placeholder
    # so Manim doesn't crash looking for external files.
    code = re.sub(r'ImageMobject\((.*?)\)', r'Text(\1)', code)
    code = re.sub(r'SVGMobject\((.*?)\)', r'Text(\1)', code)
    
    # Basic import check and Safety Monkey Patch header
    header = """from manim import *

# --- Safety Monkey Patches for LLM Generated Code ---
_original_create = Create
_original_write = Write
_original_fadein = FadeIn
_original_fadeout = FadeOut

def _safe_wrap(mobj):
    if isinstance(mobj, list):
        return VGroup(*[_safe_wrap(m) for m in mobj])
    return mobj

class SafeCreate(_original_create):
    def __init__(self, mobject, **kwargs):
        super().__init__(_safe_wrap(mobject), **kwargs)

class SafeWrite(_original_write):
    def __init__(self, mobject, **kwargs):
        super().__init__(_safe_wrap(mobject), **kwargs)

class SafeFadeIn(_original_fadein):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(*[_safe_wrap(m) for m in mobjects], **kwargs)

class SafeFadeOut(_original_fadeout):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(*[_safe_wrap(m) for m in mobjects], **kwargs)

Create = SafeCreate
Write = SafeWrite
FadeIn = SafeFadeIn
FadeOut = SafeFadeOut
# ---------------------------------------------------

"""
    
    # Remove any existing standard imports to prevent duplication
    code = code.replace("from manim import *", "").strip()
    code = header + code
        
    return code
