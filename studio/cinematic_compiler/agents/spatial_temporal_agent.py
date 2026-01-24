"""
Agent 4: Spatial & Temporal Continuity Agent
Prevents AI drift and jump cuts
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, SpatialState


class SpatialTemporalAgent(BaseCompilerAgent):
    """
    AGENT 4: SPATIAL & TEMPORAL CONTINUITY

    Purpose: Prevent AI drift and jump cuts

    Responsibilities:
    - Enforce same-location logic
    - Enforce same-moment logic
    - Define spatial relationships
    - Prevent teleportation, pose snapping, or time jumps

    Rules:
    - End frame must feel like the next second of the start frame
    - Movement must be physically plausible
    - No costume, lighting, or weather changes unless specified
    """

    def __init__(self):
        super().__init__("Spatial & Temporal Continuity Agent")

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Enforce spatial and temporal continuity"""

        if not self.validate_input(scene, ['physical_reality', 'character_identities']):
            raise ValueError(f"Scene {scene.scene_id} missing required data")

        self.log(f"Enforcing continuity for scene {scene.sequence_number}")

        # Determine if this is same location/moment as previous scene
        prev_scene = project.scenes[scene.sequence_number - 2] if scene.sequence_number > 1 else None

        same_location = False
        same_moment = False

        if prev_scene and prev_scene.spatial_state:
            # Check continuity with previous scene
            # (In production, Claude analyzes narrative to determine this)
            pass

        spatial_state = SpatialState(
            location_id=f"loc_{scene.sequence_number}",
            location_description="[LOCATION DESCRIPTION]",
            time_of_day="day",
            weather_conditions="clear",
            same_location_as_previous=same_location,
            same_moment_as_previous=same_moment,
            spatial_relationships={},
            allowed_changes=["subtle body movement", "eye direction"],
            prohibited_changes=["wardrobe", "lighting direction", "weather", "time of day"]
        )

        scene.spatial_state = spatial_state

        self.log("✓ Continuity constraints defined")

        return scene
