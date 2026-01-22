"""
Production Studio Data Schemas
Data structures that flow between agents in the sequential pipeline
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AgentStage(Enum):
    """Sequential agent stages - no skipping allowed"""
    SCRIPT = "script"
    CHARACTER_LOCK = "character_lock"
    LIGHTING = "lighting"
    COMPOSITION = "composition"
    FRAME = "frame"
    VIDEO = "video"
    ASSEMBLY = "assembly"
    COMPLETE = "complete"


class ProductionMode(Enum):
    """Production execution modes"""
    REVIEW = "review"  # Stop at each agent for human review
    AUTO = "auto"      # Run all agents automatically


@dataclass
class CharacterSpec:
    """Locked character specification"""
    character_id: str
    name: str
    visual_description: str
    reference_image_url: Optional[str] = None
    lora_model_id: Optional[str] = None  # For consistency across generations
    appearance_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "name": self.name,
            "visual_description": self.visual_description,
            "reference_image_url": self.reference_image_url,
            "lora_model_id": self.lora_model_id,
            "appearance_notes": self.appearance_notes
        }


@dataclass
class LightingSpec:
    """Lighting specification for a scene"""
    lighting_type: str  # "natural", "studio", "dramatic", "soft", "hard"
    direction: str  # "front", "back", "side", "top", "bottom"
    intensity: str  # "low", "medium", "high"
    color_temperature: str  # "warm", "neutral", "cool"
    mood: str
    technical_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lighting_type": self.lighting_type,
            "direction": self.direction,
            "intensity": self.intensity,
            "color_temperature": self.color_temperature,
            "mood": self.mood,
            "technical_notes": self.technical_notes
        }


@dataclass
class CompositionSpec:
    """Camera composition for a scene"""
    shot_type: str  # "wide", "medium", "close-up", "extreme-close-up"
    camera_angle: str  # "eye-level", "high", "low", "birds-eye", "worms-eye"
    camera_movement: str  # "static", "pan", "tilt", "zoom", "dolly", "tracking"
    framing_notes: str
    rule_of_thirds: bool
    depth_of_field: str  # "shallow", "medium", "deep"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "shot_type": self.shot_type,
            "camera_angle": self.camera_angle,
            "camera_movement": self.camera_movement,
            "framing_notes": self.framing_notes,
            "rule_of_thirds": self.rule_of_thirds,
            "depth_of_field": self.depth_of_field
        }


@dataclass
class FrameSpec:
    """Start and end frame specifications for controlled video generation"""
    start_frame_prompt: str
    end_frame_prompt: str
    motion_description: str
    transition_type: str  # "cut", "fade", "dissolve", "wipe"
    duration_seconds: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_frame_prompt": self.start_frame_prompt,
            "end_frame_prompt": self.end_frame_prompt,
            "motion_description": self.motion_description,
            "transition_type": self.transition_type,
            "duration_seconds": self.duration_seconds
        }


@dataclass
class SceneClip:
    """A single scene/clip in the timeline"""
    clip_id: str
    sequence_number: int

    # Script Agent output
    script_content: str
    narration_text: str
    scene_description: str
    emotional_beat: str
    duration: float

    # Character Lock Agent output
    characters: List[CharacterSpec] = field(default_factory=list)

    # Lighting Agent output
    lighting: Optional[LightingSpec] = None

    # Composition Agent output
    composition: Optional[CompositionSpec] = None

    # Frame Agent output
    frame_spec: Optional[FrameSpec] = None

    # Video Agent output
    video_url: Optional[str] = None
    video_status: str = "pending"  # "pending", "generating", "complete", "failed"

    # Assembly metadata
    audio_url: Optional[str] = None
    captions_data: Optional[Dict[str, Any]] = None

    # Timeline editing
    is_locked: bool = False
    override_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "sequence_number": self.sequence_number,
            "script_content": self.script_content,
            "narration_text": self.narration_text,
            "scene_description": self.scene_description,
            "emotional_beat": self.emotional_beat,
            "duration": self.duration,
            "characters": [c.to_dict() for c in self.characters],
            "lighting": self.lighting.to_dict() if self.lighting else None,
            "composition": self.composition.to_dict() if self.composition else None,
            "frame_spec": self.frame_spec.to_dict() if self.frame_spec else None,
            "video_url": self.video_url,
            "video_status": self.video_status,
            "audio_url": self.audio_url,
            "captions_data": self.captions_data,
            "is_locked": self.is_locked,
            "override_notes": self.override_notes
        }


@dataclass
class ProductionJob:
    """A complete video production job"""
    job_id: str
    channel_id: str
    created_at: datetime

    # Production settings
    mode: ProductionMode
    current_stage: AgentStage

    # Video specification
    title: str
    topic: str
    duration_target: float
    platform: str  # "youtube", "tiktok", "instagram", "all"

    # Timeline
    clips: List[SceneClip] = field(default_factory=list)

    # Global settings
    global_characters: List[CharacterSpec] = field(default_factory=list)
    visual_style: str = ""
    tone: str = ""

    # Assembly output
    final_video_url: Optional[str] = None
    final_video_path: Optional[str] = None

    # Status tracking
    is_complete: bool = False
    error_message: Optional[str] = None

    # Platform posting
    posted_to_youtube: bool = False
    posted_to_tiktok: bool = False
    posted_to_instagram: bool = False
    youtube_url: Optional[str] = None
    tiktok_url: Optional[str] = None
    instagram_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "channel_id": self.channel_id,
            "created_at": self.created_at.isoformat(),
            "mode": self.mode.value,
            "current_stage": self.current_stage.value,
            "title": self.title,
            "topic": self.topic,
            "duration_target": self.duration_target,
            "platform": self.platform,
            "clips": [c.to_dict() for c in self.clips],
            "global_characters": [c.to_dict() for c in self.global_characters],
            "visual_style": self.visual_style,
            "tone": self.tone,
            "final_video_url": self.final_video_url,
            "final_video_path": self.final_video_path,
            "is_complete": self.is_complete,
            "error_message": self.error_message,
            "posted_to_youtube": self.posted_to_youtube,
            "posted_to_tiktok": self.posted_to_tiktok,
            "posted_to_instagram": self.posted_to_instagram,
            "youtube_url": self.youtube_url,
            "tiktok_url": self.tiktok_url,
            "instagram_url": self.instagram_url
        }

    def get_progress_percentage(self) -> float:
        """Calculate overall progress"""
        total_stages = len(AgentStage) - 1  # Exclude COMPLETE
        current_index = list(AgentStage).index(self.current_stage)
        return (current_index / total_stages) * 100

    def get_next_stage(self) -> Optional[AgentStage]:
        """Get the next stage in the pipeline"""
        stages = list(AgentStage)
        current_index = stages.index(self.current_stage)
        if current_index < len(stages) - 1:
            return stages[current_index + 1]
        return None
