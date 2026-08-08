"""Pydantic models for the PDF-to-Manim storyboard pipeline (Advanced V3)."""

from typing import Optional, List, Dict, Union, Any
from pydantic import BaseModel, Field

class Metadata(BaseModel):
    subject: str = Field(default="Mathematics")
    grade: int = Field(default=8)
    topic: str
    title: str
    target_duration_seconds: int = Field(default=30)
    learning_objective: str
    difficulty: str
    prerequisite_knowledge: Any

class EducationalStrategy(BaseModel):
    core_idea: str
    teaching_progression: Any
    misconception_to_address: str
    visual_teaching_principle: str

class Camera(BaseModel):
    movement: str
    framing: str
    zoom: str

class GlobalVisualLanguage(BaseModel):
    style: str
    background: str
    primary_representation: str
    secondary_representation: str
    layout: str
    visual_density: str
    text_density: str
    camera: Camera

class ConceptualObject(BaseModel):
    id: str
    type: str
    semantic_role: str
    content: Any
    meaning: str

class Story(BaseModel):
    narrative_arc: Any

class TimeRange(BaseModel):
    start: int
    end: int

class VisualState(BaseModel):
    visible: Any = []
    hidden: Any = []
    emphasis: Any = []
    previous_visual: Any = None

class VisualAction(BaseModel):
    type: str
    description: str

class Transition(BaseModel):
    conceptual_change: str

class TimelineEvent(BaseModel):
    scene_id: str
    time: TimeRange
    purpose: str
    narration: str
    visual_state: VisualState
    visual_action: VisualAction
    mathematical_meaning: Optional[str] = None
    transition: Optional[Transition] = None
    mathematical_mapping: Optional[Dict[str, Any]] = None
    mathematical_content: Optional[Dict[str, str]] = None
    student_should_notice: str

class Transitions(BaseModel):
    preferred: Any
    avoid: Any

class NarrationVisualAlignment(BaseModel):
    concept: str
    visual: str

class MathematicalConstraints(BaseModel):
    must_be_correct: bool = True
    expressions: Any
    important_distinction: Optional[str] = None

class GenerationConstraints(BaseModel):
    total_duration_seconds: int = 30
    visuals_must_support_narration: bool = True
    no_scene_should_introduce_unexplained_concepts: bool = True
    important_equations_must_be_readable: bool = True
    all_visual_elements_must_have_clear_semantic_purpose: bool = True
    prefer_continuity_between_scenes: bool = True
    avoid_excessive_animation: bool = True

class FinalState(BaseModel):
    main_message: str
    example_result: Optional[str] = None
    repetition_result: Optional[str] = None
    general_formula: Optional[str] = None

class Storyboard(BaseModel):
    metadata: Metadata
    educational_strategy: EducationalStrategy
    global_visual_language: GlobalVisualLanguage
    conceptual_objects: Any
    story: Story
    timeline: List[TimelineEvent]
    transitions: Transitions
    narration_visual_alignment: Any
    mathematical_constraints: MathematicalConstraints
    generation_constraints: GenerationConstraints
    final_state: FinalState
