"""Pydantic models for the PDF-to-Manim storyboard pipeline (Simplified V4)."""

from typing import List, Any
from pydantic import BaseModel, Field

class Scene(BaseModel):
    scene_number: int
    narration: str = Field(description="The voiceover text spoken during this scene. MUST be a plain text string.")
    visual_description: str = Field(description="Describe exactly what appears on screen. MUST be a plain text string. Do NOT output a dictionary or an image URL. MUST connect continuously with the previous scene without wiping the screen.")
    mathematical_concept: str = Field(description="The exact concept from the textbook being explained in this scene. MUST be a plain text string.")
    animation_instructions: str = Field(description="Instructions for Manim (e.g., 'Fade in the formula, highlight the 6'). MUST be a plain text string.")

class Storyboard(BaseModel):
    title: str = Field(description="Title of the concept video.")
    target_audience: str = Field(description="e.g., 8th-grade math students.")
    story_continuity_plan: str = Field(description="A brief explanation of how the visual narrative flows continuously from Scene 1 to the end without breaking or resetting.")
    scenes: List[Scene]
