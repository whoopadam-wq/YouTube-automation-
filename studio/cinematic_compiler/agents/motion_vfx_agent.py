"""
Agent 8: Motion & VFX Agent
Handles controlled motion and overlays
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, MotionDelta


class MotionVFXAgent(BaseCompilerAgent):
    """
    AGENT 8: MOTION & VFX

    Purpose: Handle controlled motion and overlays

    Responsibilities:
    - Define subtle physical movement
    - Define slow motion if used
    - Define motion graphics or VFX as NON-DESTRUCTIVE layers

    Rules:
    - VFX never alters base reality
    - Motion is restrained and believable
    - No spectacle without narrative reason
    """

    def __init__(self):
        super().__init__("Motion & VFX Agent")

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Define motion delta between start and end frames"""

        if not self.validate_input(scene, ['physical_reality', 'spatial_state']):
            raise ValueError(f"Scene {scene.scene_id} missing required data")

        self.log(f"Defining motion delta for scene {scene.sequence_number}")

        # Extract temporal changes from physical reality
        temporal_changes = scene.physical_reality.temporal_changes

        motion = MotionDelta(
            motion_type="subtle",
            motion_description=temporal_changes,
            start_state="initial position and expression",
            end_state="final position and expression after subtle movement",
            motion_physics="realistic",
            vfx_layers=[],
            motion_must_be_plausible=True,
            no_teleportation=True
        )

        scene.motion = motion

        self.log(f"✓ Motion: {motion.motion_type} - {motion.motion_description[:50]}...")

        return scene
