"""Manim script generation using the LLM from a JSON storyboard."""

import re
from core.llm_client import LocalLLMClient
from storyboard.schemas import Storyboard


def build_manim_prompt(storyboard: Storyboard) -> str:
    """Creates the prompt to generate a Manim Python script from the storyboard."""
    
    storyboard_json = storyboard.model_dump_json(indent=2)
    
    return f"""You are an expert Manim (Python) animator.
I have a highly detailed continuous storyboard for a mathematical animation.

STORYBOARD JSON:
{storyboard_json}

REQUIREMENTS:
1. Write a complete, runnable Python script using the Manim library.
2. The script must contain a single class `ConceptScene(Scene)`.
3. Read the `scenes` array from the JSON and animate the events in sequence. The storyboard is CONTINUOUS, meaning you should NOT use `self.clear()` between scenes unless explicitly instructed.
4. Pay very close attention to the `visual_description` and `animation_instructions`.
5. Do NOT use `ImageMobject`, `SVGMobject`, or any external files. Use built-in Manim shapes (Circle, Rectangle, Polygon) or `Text`/`MathTex`.
6. STRICT MANIM RULES to prevent crashes:
   - Do NOT use `MoveToTarget`. Use `self.play(Transform(obj1, obj2))` or `self.play(obj.animate.shift(RIGHT))`.
   - Use `VGroup` instead of `Group`.
   - Never instantiate a raw `Mobject()`. Use `VMobject()`, `VGroup()`, or specific geometric shapes.
   - Do NOT pass Python lists directly into animations like `Create(my_list)`. You MUST unpack them: e.g., `self.play(*[Create(obj) for obj in my_list])`.
7. BOUNDARY ENFORCEMENT & ANTI-OVERLAP (CRITICAL):
   - You MUST ensure text and formulas NEVER overlap on screen.
   - You MUST group elements into a `VGroup` and use `.arrange(DOWN, buff=0.5)` to mathematically guarantee they do not overlap.
   - After arranging a group, you MUST scale it to fit within the screen boundaries. ALWAYS do: `if my_group.width > config.frame_width - 1: my_group.scale_to_fit_width(config.frame_width - 1)`
   - Do NOT use absolute coordinates like `.move_to([4, 2, 0])` which push things off-screen. Center items using `.move_to(ORIGIN)` or position them relative to others.
   - Manim coordinates are 3D! Never add a 2D tuple to `ORIGIN`. Use 3D vectors: e.g., `ORIGIN + RIGHT * x + UP * y`.
   - Mobjects do NOT take `x` or `y` parameters in their constructors. Do NOT do `Rectangle(x=2)`.
   - When using `.arrange_in_grid()`, specify ONLY `rows=` or ONLY `cols=` to let Manim auto-calculate the other dimension.
8. PREMIUM ANIMATIONS:
   - Make the visuals engaging.
   - Do NOT just use `Create()` for everything. Use engaging animations like `Write()` for Text, `GrowFromCenter()` for shapes, and `TransformMatchingTex()` for math formulas.
9. Return ONLY the raw Python code inside a markdown code block ```python ... ``` without any surrounding explanations.
"""

def extract_python_code(llm_response: str) -> str:
    """Extracts Python code from a markdown block, ignoring <think> blocks."""
    match = re.search(r"```python\s+(.*?)\s+```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match2 = re.search(r"```\s+(.*?)\s+```", llm_response, re.DOTALL)
    if match2:
        return match2.group(1).strip()
        
    # Fallback if no markdown block is used, but strip <think> first
    text_no_think = re.sub(r"<think>.*?</think>", "", llm_response, flags=re.DOTALL)
    return text_no_think.strip()

def generate_manim_script(client, storyboard: Storyboard) -> str:
    """Generates the Manim python script string."""
    prompt = build_manim_prompt(storyboard)
    
    system_prompt = "You are an expert Python Manim animator. Output only valid Python code inside ```python blocks."
    
    print("[LLM] Generating Manim Script (this might take a minute)...")
    # For Ollama Client
    raw_text = client.generate(prompt, system=system_prompt, temperature=0.2)
    
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
    
    # Fix common LLM hallucination for VGroup arrange
    code = code.replace("spacing=", "buff=")
        
    return code

def fix_manim_script(client, bad_code: str, traceback_error: str) -> str:
    """Sends the traceback to the LLM and asks it to fix the script."""
    system_prompt = "You are an expert Python Manim animator. Output only valid Python code inside ```python blocks."
    
    prompt = f"""I tried to run your Manim script, but it crashed with the following error:

<ERROR_TRACEBACK>
{traceback_error}
</ERROR_TRACEBACK>

Here is the code you wrote that caused the error:
```python
{bad_code}
```

Please fix the error and rewrite the complete, runnable Python script.
Remember the CRITICAL rules:
- Only output the raw python code inside a ```python block.
- Use `VGroup` instead of `Group`.
- If a method like `Create()` or `Write()` was passed a list, unpack it! (e.g., `*my_list`).
- Make sure all variables are defined before using them.
"""
    
    print("[LLM] Fixing Manim Script based on Traceback...")
    raw_text = client.generate(prompt, system=system_prompt, temperature=0.1)
    code = extract_python_code(raw_text)
    
    # Re-apply the monkey patch just in case
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
    code = code.replace("from manim import *", "").strip()
    code = header + code
    code = code.replace("spacing=", "buff=")
    
    return code

