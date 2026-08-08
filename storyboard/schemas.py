"""Pydantic models for the PDF-to-Manim storyboard pipeline (V3)."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    FOUNDATIONAL = "foundational"
    CORE = "core"
    EXTENSION = "extension"


class SingleContinuousScene(BaseModel):
    title: str = Field(description="Title of this creative visual scene")
    duration_seconds: int = Field(default=30)
    narration: str = Field(description="The complete voiceover text explaining the concept fluidly.")
    visual_layout: str = Field(description="How elements are arranged on screen. (e.g. 'A central title at the top, a 2x3 grid below it, and an equation at the bottom'). Everything must fit within the frame.")
    animation_sequence: List[str] = Field(description="Step-by-step logical sequence of Manim animations to build this scene. (e.g., ['Write the title', 'Fade in the grid', 'Highlight the first column', 'Transform into the formula']).")
    manim_hint: str = Field(default="", description="Specific Manim classes (e.g. VGroup, Text, MathTex) or layout hints.")
    math_overlay: Optional[str] = Field(default=None, description="LaTeX string for math formula")


class Storyboard(BaseModel):
    topic: str
    grade: int = Field(default=8)
    scenario_title: str = Field(description="Title of the overall video")
    visual_setting: str = Field(description="One visual metaphor built entirely out of basic Manim objects (Text, MathTex, Circle, Rectangle, VGroup).")
    scene: SingleContinuousScene = Field(description="The single, continuous, highly creative scene that builds step-by-step without wiping the screen.")
