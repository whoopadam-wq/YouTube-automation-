"""
Agent 2: Scene Decomposition Agent
Translates story beats into physical reality
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, PhysicalReality


class SceneDecompositionAgent(BaseCompilerAgent):
    """
    AGENT 2: SCENE DECOMPOSITION

    Purpose: Translate story beats into physical reality

    Responsibilities:
    - Define what physically exists in the scene
    - Who is present
    - Where they are standing
    - What they are doing
    - What changes between start and end of the scene

    Rules:
    - No camera language
    - No lighting yet
    - No stylistic language
    - Only objective physical facts
    """

    def __init__(self):
        super().__init__("Scene Decomposition Agent")

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Decompose narrative into physical reality"""

        # Validate narrative exists
        if not self.validate_input(scene, ['narrative']):
            raise ValueError(f"Scene {scene.scene_id} missing narrative data")

        self.log(f"Decomposing scene {scene.sequence_number} into physical reality")

        # Build physical reality from narrative
        # In production, this uses Claude to extract objective facts

        physical_reality = PhysicalReality(
            environment_description="[PHYSICAL ENVIRONMENT]",
            characters_present=[],  # Populated from project.global_characters
            character_positions={},
            physical_actions=["[OBJECTIVE ACTIONS]"],
            temporal_changes="[START STATE → END STATE]"
        )

        scene.physical_reality = physical_reality

        self.log("✓ Physical reality defined")

        return scene
