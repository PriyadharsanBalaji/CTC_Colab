"""Pydantic models for the PDF-to-Manim storyboard pipeline (Simplified V4)."""

from typing import List, Any
from pydantic import BaseModel, Field

class Scene(BaseModel):
    scene_number: int
    narration: str = Field(description="The voiceover text spoken during this scene. MUST be a plain text string.")
    visual_description: str = Field(description="Describe EXACTLY what shapes, text, and numbers appear on screen. Ban phrases like 'display an image' or 'show a diagram'. Specify explicit layouts (e.g., 'Write 5! = 120 in the center and draw a blue box around it'). MUST connect continuously with the previous scene without wiping the screen.")
    mathematical_concept: str = Field(description="The exact concept from the textbook being explained in this scene. MUST be a plain text string.")
    latex_equations: List[str] = Field(description="Extract the EXACT mathematical equations, symbols, and formulas from the image using strict LaTeX formatting (e.g. ['x = \\frac{1}{2}', '5! = 120']).")
    animation_instructions: str = Field(description="Instructions for Manim (e.g., 'Fade in the formula, highlight the 6'). MUST be a plain text string.")

class Storyboard(BaseModel):
    title: str = Field(description="Title of the concept video.")
    target_audience: str = Field(description="e.g., 8th-grade math students.")
    story_continuity_plan: str = Field(description="A brief explanation of how the visual narrative flows continuously from Scene 1 to the end without breaking or resetting.")
    scenes: List[Scene]
