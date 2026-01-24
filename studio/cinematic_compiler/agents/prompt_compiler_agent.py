"""
Agent 9: Prompt Compiler Agent
Merges all prior agents into a single deterministic prompt
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, CompiledPrompt, FrameType


class PromptCompilerAgent(BaseCompilerAgent):
    """
    AGENT 9: PROMPT COMPILER

    Purpose: Merge all prior agents into a single deterministic prompt

    Responsibilities:
    - Assemble start frame prompt
    - Assemble end frame prompt
    - Preserve all constraints
    - Enforce anti-AI artifact rules

    Rules:
    - No missing information
    - No contradictions
    - No poetic language
    - Pure instruction
    """

    def __init__(self):
        super().__init__("Prompt Compiler Agent")

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Compile all agent outputs into final prompts"""

        # Validate all prior agents have run
        required_fields = [
            'narrative', 'physical_reality', 'character_identities',
            'spatial_state', 'camera', 'lighting', 'composition', 'motion'
        ]

        if not self.validate_input(scene, required_fields):
            raise ValueError(f"Scene {scene.scene_id} missing required agent data")

        self.log(f"Compiling final prompts for scene {scene.sequence_number}")

        # Build component blocks
        characters_block = self._build_characters_block(scene)
        environment_block = self._build_environment_block(scene)
        camera_block = scene.camera.to_prompt_block()
        lighting_block = scene.lighting.to_prompt_block()
        composition_block = scene.composition.to_prompt_block()
        motion_block = scene.motion.motion_description

        # Compile START frame prompt
        start_prompt = CompiledPrompt(
            frame_type=FrameType.START,
            characters=characters_block,
            environment=environment_block,
            camera=camera_block,
            lighting=lighting_block,
            composition=composition_block,
            motion=""  # No motion in start frame
        )
        start_prompt.compile()

        # Compile END frame prompt
        end_prompt = CompiledPrompt(
            frame_type=FrameType.END,
            characters=characters_block + " (exact same appearance as start frame)",
            environment=environment_block + " (exact same location and conditions as start frame)",
            camera=camera_block,
            lighting=lighting_block,
            composition=composition_block,
            motion=motion_block
        )
        end_prompt.compile()

        scene.start_frame_prompt = start_prompt
        scene.end_frame_prompt = end_prompt

        self.log("✓ Prompts compiled")
        self.log(f"   Start frame: {len(start_prompt.full_prompt)} chars")
        self.log(f"   End frame: {len(end_prompt.full_prompt)} chars")

        return scene

    def _build_characters_block(self, scene: CinematicScene) -> str:
        """Build characters prompt block"""
        if not scene.character_identities:
            return ""

        blocks = []
        for char in scene.character_identities:
            blocks.append(char.to_prompt_block())

        return " ".join(blocks)

    def _build_environment_block(self, scene: CinematicScene) -> str:
        """Build environment prompt block"""
        spatial = scene.spatial_state

        return f"""{spatial.location_description}. Time: {spatial.time_of_day}. Weather: {spatial.weather_conditions}."""
