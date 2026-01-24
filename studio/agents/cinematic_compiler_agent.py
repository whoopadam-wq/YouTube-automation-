"""
Cinematic Compiler Agent
Bridge between studio pipeline and cinematic compiler system

This agent can be inserted into the existing pipeline to use the
deterministic multi-agent cinematic compiler for enhanced prompt generation.
"""
import os
from typing import List

from studio.schemas import SceneClip, ProductionJob
from studio.cinematic_compiler import (
    CinematicCompiler,
    CinematicProject,
    CinematicScene,
    CharacterIdentity,
    PhysicalReality,
    NarrativeBeat
)


class CinematicCompilerAgent:
    """
    Optional agent that uses the Cinematic Compiler system to enhance
    the existing FrameAgent's output with deterministic compilation.

    Position in pipeline: Between FrameAgent and VideoAgent (optional)

    What it does:
    - Takes existing SceneClip data from prior agents
    - Translates to CinematicScene format
    - Runs through 9-agent compiler
    - Returns enhanced prompts back to SceneClip.frame_spec

    Benefits:
    - Enforces strict continuity
    - Character identity persistence
    - Anti-AI artifact enforcement
    - Documentary realism
    - Photographic camera specs
    """

    def __init__(self):
        self.compiler = CinematicCompiler()
        self.project_cache = {}  # Cache projects per job_id

    async def enhance_clips(
        self,
        job: ProductionJob,
        clips: List[SceneClip]
    ) -> List[SceneClip]:
        """
        Enhance clips using cinematic compiler

        Args:
            job: ProductionJob
            clips: List of SceneClip objects with prior agent data

        Returns:
            Enhanced clips with compiler-generated prompts
        """
        print(f"🎬 Cinematic Compiler Agent: Enhancing {len(clips)} clips...")

        # Create or load cinematic project
        project = self._get_or_create_project(job)

        # Translate clips to cinematic scenes and compile
        for i, clip in enumerate(clips):
            scene = self._clip_to_scene(clip, i + 1)

            # Run through compiler
            scene = self.compiler.compile_scene(project, scene, auto_save=False)

            # Translate back to clip format
            clip = self._scene_to_clip(scene, clip)

        # Save project
        self.compiler.state_manager.save_project(project)

        print(f"✅ Cinematic Compiler Agent: Enhanced all clips")

        return clips

    def _get_or_create_project(self, job: ProductionJob) -> CinematicProject:
        """Get or create cinematic project for this job"""

        # Check cache
        if job.job_id in self.project_cache:
            return self.project_cache[job.job_id]

        # Try to load existing
        project_id = f"job_{job.job_id}"
        project = self.compiler.load_project(project_id)

        if not project:
            # Create new
            project = CinematicProject(
                project_id=project_id,
                title=job.title,
                created_at=job.created_at,
                visual_style_rules=job.visual_style,
                target_platform=job.platform
            )

        self.project_cache[job.job_id] = project
        return project

    def _clip_to_scene(self, clip: SceneClip, sequence: int) -> CinematicScene:
        """
        Translate SceneClip to CinematicScene

        This bridges the existing agent output format to the compiler format
        """
        scene = CinematicScene(
            scene_id=clip.clip_id,
            sequence_number=sequence,
            duration_seconds=clip.duration
        )

        # Translate narrative
        if clip.script_content:
            scene.narrative = NarrativeBeat(
                beat_id=f"{clip.clip_id}_narrative",
                narrative_intent=clip.scene_description,
                emotional_temperature=self._map_emotion(clip.emotional_beat),
                cause_effect_chain=clip.script_content[:200],
                continuity_requirements=[]
            )

        # Translate physical reality
        if clip.scene_description:
            scene.physical_reality = PhysicalReality(
                environment_description=clip.scene_description,
                characters_present=[c.character_id for c in clip.characters],
                character_positions={},
                physical_actions=[],
                temporal_changes="[Derived from narration]"
            )

        # Translate characters
        if clip.characters:
            scene.character_identities = [
                self._translate_character(c) for c in clip.characters
            ]

        return scene

    def _scene_to_clip(self, scene: CinematicScene, clip: SceneClip) -> SceneClip:
        """
        Translate compiled CinematicScene back to SceneClip

        Updates the clip's frame_spec with compiler-generated prompts
        """
        if scene.start_frame_prompt and scene.end_frame_prompt:
            from studio.schemas import FrameSpec

            # Replace existing frame_spec with compiler-generated prompts
            clip.frame_spec = FrameSpec(
                start_frame_prompt=scene.start_frame_prompt.full_prompt,
                end_frame_prompt=scene.end_frame_prompt.full_prompt,
                motion_description=scene.motion.motion_description if scene.motion else "",
                transition_type="cut",
                duration_seconds=scene.duration_seconds
            )

        return clip

    def _translate_character(self, char_spec) -> CharacterIdentity:
        """Translate CharacterSpec to CharacterIdentity"""
        # Parse visual description into structured format
        # (In production, use Claude to extract structured data)

        return CharacterIdentity(
            character_id=char_spec.character_id,
            canonical_name=char_spec.name,
            age="30-35",  # Would be extracted from visual_description
            ethnicity="neutral",
            bone_structure="average",
            face_shape="oval",
            distinctive_features="none",
            hair_description="short dark hair",
            facial_hair="clean shaven",
            body_type="average",
            height_relative="average",
            posture_tendencies="upright",
            wardrobe=char_spec.visual_description[:100],
            accessories="none"
        )

    def _map_emotion(self, emotional_beat: str) -> str:
        """Map emotional beat to temperature"""
        emotion_map = {
            "tense": "hot",
            "dramatic": "hot",
            "calm": "neutral",
            "peaceful": "cool",
            "sad": "cold",
            "angry": "hot",
            "happy": "warm",
            "excited": "hot"
        }

        for key, temp in emotion_map.items():
            if key in emotional_beat.lower():
                return temp

        return "neutral"
