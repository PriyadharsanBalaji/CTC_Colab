"""Pydantic models for the PDF-to-Manim storyboard pipeline."""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    FOUNDATIONAL = "foundational"
    CORE = "core"
    EXTENSION = "extension"


class ShotType(str, Enum):
    ESTABLISHING = "establishing"
    JOURNEY = "journey"
    REVEAL = "reveal"
    RECAP = "recap"


class Scene(BaseModel):
    scene_number: int
    title: str
    duration_seconds: int = 8
    narration: str = Field(description="The voiceover text explaining the concept")
    animation_description: str = Field(description="Visual action happening in this scene")
    manim_hint: str = Field(default="", description="Optional: specific Manim classes or logic to use")
    reveals_formula: bool = False
    math_overlay: Optional[str] = Field(default=None, description="LaTeX string for math formula to overlay")
    shot_type: ShotType = ShotType.JOURNEY


class Storyboard(BaseModel):
    topic: str
    grade: int = Field(default=8)
    total_duration_seconds: int = Field(description="Total duration across all scenes")
    scenario_title: str = Field(description="Title of the overall video")
    scenario_summary: str = Field(description="Short summary of the story/metaphor used")
    visual_setting: str = Field(description="One visual world for all scenes to maintain continuity (e.g. 'cricket pitch', 'balance scale')")
    scenes: List[Scene] = Field(description="Sequential list of scenes, each ~8 seconds")
