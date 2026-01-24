"""
Cinematic Compiler Data Schemas
Immutable, structured data representations for deterministic compilation
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class CompilerStage(Enum):
    """Internal compiler stages - sequential transformation chain"""
    IDEA_NARRATIVE = "idea_narrative"
    SCENE_DECOMPOSITION = "scene_decomposition"
    CHARACTER_IDENTITY = "character_identity"
    SPATIAL_TEMPORAL = "spatial_temporal"
    CAMERA_OPTICS = "camera_optics"
    LIGHTING_PHYSICS = "lighting_physics"
    COMPOSITION = "composition"
    MOTION_VFX = "motion_vfx"
    PROMPT_COMPILATION = "prompt_compilation"
    COMPLETE = "complete"


class FrameType(Enum):
    """Frame types for video generation"""
    START = "start"
    END = "end"


@dataclass
class NarrativeBeat:
    """
    Agent 1 Output: Story meaning without visuals
    """
    beat_id: str
    narrative_intent: str
    emotional_temperature: str  # "cold", "neutral", "warm", "hot"
    cause_effect_chain: str
    continuity_requirements: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "beat_id": self.beat_id,
            "narrative_intent": self.narrative_intent,
            "emotional_temperature": self.emotional_temperature,
            "cause_effect_chain": self.cause_effect_chain,
            "continuity_requirements": self.continuity_requirements
        }


@dataclass
class PhysicalReality:
    """
    Agent 2 Output: Objective physical facts
    """
    environment_description: str
    characters_present: List[str]  # Character IDs
    character_positions: Dict[str, str]  # character_id -> position description
    physical_actions: List[str]
    temporal_changes: str  # What changes from start to end

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment_description": self.environment_description,
            "characters_present": self.characters_present,
            "character_positions": self.character_positions,
            "physical_actions": self.physical_actions,
            "temporal_changes": self.temporal_changes
        }


@dataclass
class CharacterIdentity:
    """
    Agent 3 Output: Absolute identity anchor (IMMUTABLE once locked)
    """
    character_id: str
    canonical_name: str

    # Physical immutables
    age: str
    ethnicity: str
    bone_structure: str
    face_shape: str
    distinctive_features: str

    # Appearance immutables
    hair_description: str
    facial_hair: str
    body_type: str
    height_relative: str
    posture_tendencies: str

    # Wardrobe (locked per scene, can change between scenes if specified)
    wardrobe: str
    accessories: str

    # Reference
    reference_image_url: Optional[str] = None
    identity_locked: bool = True

    def to_prompt_block(self) -> str:
        """Generate reusable identity text for prompts"""
        return f"""{self.canonical_name}, {self.age} year old {self.ethnicity}, {self.bone_structure} bone structure, {self.face_shape} face, {self.distinctive_features}. {self.hair_description}. {self.facial_hair}. {self.body_type} build, {self.height_relative} height, {self.posture_tendencies} posture. Wearing: {self.wardrobe}. {self.accessories}."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "canonical_name": self.canonical_name,
            "age": self.age,
            "ethnicity": self.ethnicity,
            "bone_structure": self.bone_structure,
            "face_shape": self.face_shape,
            "distinctive_features": self.distinctive_features,
            "hair_description": self.hair_description,
            "facial_hair": self.facial_hair,
            "body_type": self.body_type,
            "height_relative": self.height_relative,
            "posture_tendencies": self.posture_tendencies,
            "wardrobe": self.wardrobe,
            "accessories": self.accessories,
            "reference_image_url": self.reference_image_url,
            "identity_locked": self.identity_locked
        }


@dataclass
class SpatialState:
    """
    Agent 4 Output: Continuity enforcement
    """
    location_id: str
    location_description: str
    time_of_day: str
    weather_conditions: str

    # Continuity constraints
    same_location_as_previous: bool
    same_moment_as_previous: bool
    spatial_relationships: Dict[str, str]  # object/character -> position

    # Delta rules (what can change)
    allowed_changes: List[str]
    prohibited_changes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location_id": self.location_id,
            "location_description": self.location_description,
            "time_of_day": self.time_of_day,
            "weather_conditions": self.weather_conditions,
            "same_location_as_previous": self.same_location_as_previous,
            "same_moment_as_previous": self.same_moment_as_previous,
            "spatial_relationships": self.spatial_relationships,
            "allowed_changes": self.allowed_changes,
            "prohibited_changes": self.prohibited_changes
        }


@dataclass
class CameraSpec:
    """
    Agent 5 Output: Photographic realism
    """
    camera_body: str  # Real camera model (e.g., "Sony FX6", "Canon C70")
    lens_model: str  # Real lens (e.g., "Sony 24-70mm f/2.8 GM II")
    focal_length_mm: int
    aperture: str  # e.g., "f/2.8"

    # Camera position
    camera_position: str  # Relative to subjects
    camera_height: str  # "eye-level", "low", "high"
    camera_distance: str  # "close", "medium", "far"

    # Optical properties
    depth_of_field: str  # "shallow", "medium", "deep"
    focus_point: str

    # Anti-cinematic enforcement
    documentary_realism: bool = True

    def to_prompt_block(self) -> str:
        """Generate camera specification text"""
        return f"""Shot on {self.camera_body} with {self.lens_model} at {self.focal_length_mm}mm, {self.aperture}. Camera positioned {self.camera_position}, {self.camera_height}, {self.camera_distance} from subject. {self.depth_of_field} depth of field, focus on {self.focus_point}. Documentary style, handheld realism."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "camera_body": self.camera_body,
            "lens_model": self.lens_model,
            "focal_length_mm": self.focal_length_mm,
            "aperture": self.aperture,
            "camera_position": self.camera_position,
            "camera_height": self.camera_height,
            "camera_distance": self.camera_distance,
            "depth_of_field": self.depth_of_field,
            "focus_point": self.focus_point,
            "documentary_realism": self.documentary_realism
        }


@dataclass
class LightingPhysics:
    """
    Agent 6 Output: Believable light behavior
    """
    # Light sources (must exist in scene)
    primary_source: str
    primary_direction: str
    primary_color_temp: str  # e.g., "5600K daylight", "3200K tungsten"

    secondary_sources: List[str] = field(default_factory=list)

    # Shadow behavior
    shadow_direction: str
    shadow_hardness: str  # "hard", "soft", "diffused"
    shadow_density: str  # "deep", "medium", "light"

    # Ambient light
    ambient_level: str  # "low", "medium", "high"
    ambient_color: str

    # Enforcement
    natural_light_only: bool = True

    def to_prompt_block(self) -> str:
        """Generate lighting description text"""
        sources = f"{self.primary_source} from {self.primary_direction} ({self.primary_color_temp})"
        if self.secondary_sources:
            sources += f", with {', '.join(self.secondary_sources)}"
        return f"""Lighting: {sources}. Shadows cast {self.shadow_direction}, {self.shadow_hardness}, {self.shadow_density} density. Ambient light {self.ambient_level}, {self.ambient_color} tone. Natural lighting only, no studio setup."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_source": self.primary_source,
            "primary_direction": self.primary_direction,
            "primary_color_temp": self.primary_color_temp,
            "secondary_sources": self.secondary_sources,
            "shadow_direction": self.shadow_direction,
            "shadow_hardness": self.shadow_hardness,
            "shadow_density": self.shadow_density,
            "ambient_level": self.ambient_level,
            "ambient_color": self.ambient_color,
            "natural_light_only": self.natural_light_only
        }


@dataclass
class CompositionRules:
    """
    Agent 7 Output: Anti-AI composition
    """
    framing_style: str  # "unstructured", "asymmetric", "off-center"
    balance_type: str  # "unbalanced", "dynamic", "chaotic"
    observer_perspective: str  # "witness", "participant", "distant"

    # Anti-perfection rules
    avoid_rule_of_thirds: bool = True
    avoid_symmetry: bool = True
    allow_imperfection: bool = True

    # Specific composition notes
    composition_notes: str = ""

    def to_prompt_block(self) -> str:
        """Generate composition instruction text"""
        return f"""{self.framing_style} framing, {self.balance_type} balance, {self.observer_perspective} perspective. Avoid centered composition, avoid symmetry, embrace natural imperfection. {self.composition_notes}"""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "framing_style": self.framing_style,
            "balance_type": self.balance_type,
            "observer_perspective": self.observer_perspective,
            "avoid_rule_of_thirds": self.avoid_rule_of_thirds,
            "avoid_symmetry": self.avoid_symmetry,
            "allow_imperfection": self.allow_imperfection,
            "composition_notes": self.composition_notes
        }


@dataclass
class MotionDelta:
    """
    Agent 8 Output: Controlled motion specification
    """
    motion_type: str  # "subtle", "moderate", "dramatic"
    motion_description: str

    # Physical movement constraints
    start_state: str
    end_state: str
    motion_physics: str  # "realistic", "slow_motion"

    # VFX overlays (non-destructive)
    vfx_layers: List[Dict[str, str]] = field(default_factory=list)

    # Motion constraints
    motion_must_be_plausible: bool = True
    no_teleportation: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "motion_type": self.motion_type,
            "motion_description": self.motion_description,
            "start_state": self.start_state,
            "end_state": self.end_state,
            "motion_physics": self.motion_physics,
            "vfx_layers": self.vfx_layers,
            "motion_must_be_plausible": self.motion_must_be_plausible,
            "no_teleportation": self.no_teleportation
        }


@dataclass
class CompiledPrompt:
    """
    Agent 9 Output: Final deterministic prompt
    """
    frame_type: FrameType

    # Assembled components
    characters: str  # From CharacterIdentity blocks
    environment: str  # From SpatialState
    camera: str  # From CameraSpec
    lighting: str  # From LightingPhysics
    composition: str  # From CompositionRules
    motion: str  # From MotionDelta (for end frame)

    # Anti-AI enforcement block (mandatory)
    anti_ai_rules: str = """No AI gloss. No plastic skin. No symmetry correction. No face drift. No wardrobe drift. No film grain. No lens flares. No bokeh. No post-processing. No stylized filters. RAW documentary photography. Unmediated reality. Imperfect but real."""

    # Final compiled prompt
    full_prompt: str = ""

    def compile(self) -> str:
        """Assemble all components into final prompt"""
        parts = [
            self.characters,
            self.environment,
            self.camera,
            self.lighting,
            self.composition,
        ]

        if self.frame_type == FrameType.END and self.motion:
            parts.append(f"Motion: {self.motion}")

        parts.append(self.anti_ai_rules)

        self.full_prompt = " ".join(filter(None, parts))
        return self.full_prompt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_type": self.frame_type.value,
            "characters": self.characters,
            "environment": self.environment,
            "camera": self.camera,
            "lighting": self.lighting,
            "composition": self.composition,
            "motion": self.motion,
            "anti_ai_rules": self.anti_ai_rules,
            "full_prompt": self.full_prompt
        }


@dataclass
class CinematicScene:
    """
    A complete scene after all 9 agents have processed it
    """
    scene_id: str
    sequence_number: int

    # Agent outputs (populated sequentially)
    narrative: Optional[NarrativeBeat] = None
    physical_reality: Optional[PhysicalReality] = None
    character_identities: List[CharacterIdentity] = field(default_factory=list)
    spatial_state: Optional[SpatialState] = None
    camera: Optional[CameraSpec] = None
    lighting: Optional[LightingPhysics] = None
    composition: Optional[CompositionRules] = None
    motion: Optional[MotionDelta] = None

    # Final compiled prompts
    start_frame_prompt: Optional[CompiledPrompt] = None
    end_frame_prompt: Optional[CompiledPrompt] = None

    # Metadata
    duration_seconds: float = 5.0
    locked: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "sequence_number": self.sequence_number,
            "narrative": self.narrative.to_dict() if self.narrative else None,
            "physical_reality": self.physical_reality.to_dict() if self.physical_reality else None,
            "character_identities": [c.to_dict() for c in self.character_identities],
            "spatial_state": self.spatial_state.to_dict() if self.spatial_state else None,
            "camera": self.camera.to_dict() if self.camera else None,
            "lighting": self.lighting.to_dict() if self.lighting else None,
            "composition": self.composition.to_dict() if self.composition else None,
            "motion": self.motion.to_dict() if self.motion else None,
            "start_frame_prompt": self.start_frame_prompt.to_dict() if self.start_frame_prompt else None,
            "end_frame_prompt": self.end_frame_prompt.to_dict() if self.end_frame_prompt else None,
            "duration_seconds": self.duration_seconds,
            "locked": self.locked
        }


@dataclass
class CinematicProject:
    """
    A complete cinematic project with persistent state
    """
    project_id: str
    title: str
    created_at: datetime

    # Global locked state
    global_characters: Dict[str, CharacterIdentity] = field(default_factory=dict)
    global_locations: Dict[str, str] = field(default_factory=dict)
    visual_style_rules: str = ""

    # Scenes
    scenes: List[CinematicScene] = field(default_factory=list)

    # Compiler state
    current_stage: CompilerStage = CompilerStage.IDEA_NARRATIVE
    compilation_complete: bool = False

    # Output configuration
    target_platform: str = "veo3"  # "veo3", "nanoBanana", "both"
    target_resolution: str = "1920x1080"
    target_fps: int = 24

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_id": self.project_id,
            "title": self.title,
            "created_at": self.created_at.isoformat(),
            "global_characters": {k: v.to_dict() for k, v in self.global_characters.items()},
            "global_locations": self.global_locations,
            "visual_style_rules": self.visual_style_rules,
            "scenes": [s.to_dict() for s in self.scenes],
            "current_stage": self.current_stage.value,
            "compilation_complete": self.compilation_complete,
            "target_platform": self.target_platform,
            "target_resolution": self.target_resolution,
            "target_fps": self.target_fps
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CinematicProject':
        """Deserialize project from dict"""
        # This will be implemented with full deserialization logic
        return cls(
            project_id=data["project_id"],
            title=data["title"],
            created_at=datetime.fromisoformat(data["created_at"]),
            current_stage=CompilerStage(data.get("current_stage", "idea_narrative")),
            compilation_complete=data.get("compilation_complete", False),
            target_platform=data.get("target_platform", "veo3"),
            target_resolution=data.get("target_resolution", "1920x1080"),
            target_fps=data.get("target_fps", 24)
        )
