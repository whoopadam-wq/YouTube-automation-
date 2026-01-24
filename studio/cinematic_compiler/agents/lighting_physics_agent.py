"""
Agent 6: Lighting Physics Agent
Ensures believable light behavior
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, LightingPhysics


class LightingPhysicsAgent(BaseCompilerAgent):
    """
    AGENT 6: LIGHTING PHYSICS

    Purpose: Ensure believable light behavior

    Responsibilities:
    - Identify natural or practical light sources
    - Define directionality
    - Define shadow behavior
    - Define color temperature based on environment

    Rules:
    - No studio lighting unless justified
    - No dramatic lighting clichés
    - Light must come from something that exists
    """

    def __init__(self):
        super().__init__("Lighting Physics Agent")

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Define lighting physics"""

        if not self.validate_input(scene, ['spatial_state']):
            raise ValueError(f"Scene {scene.scene_id} missing spatial state")

        self.log(f"Defining lighting physics for scene {scene.sequence_number}")

        # Analyze environment to determine natural light sources
        # (In production, Claude analyzes location and time_of_day)

        time_of_day = scene.spatial_state.time_of_day
        location = scene.spatial_state.location_description

        # Determine primary light source based on context
        if "outdoor" in location.lower() or "outside" in location.lower():
            primary_source = f"natural {time_of_day} light"
            color_temp = self._get_natural_color_temp(time_of_day)
        else:
            primary_source = "window light"
            color_temp = "5000K mixed"

        lighting = LightingPhysics(
            primary_source=primary_source,
            primary_direction="from left",
            primary_color_temp=color_temp,
            secondary_sources=[],
            shadow_direction="to right",
            shadow_hardness="soft",
            shadow_density="medium",
            ambient_level="medium",
            ambient_color="neutral",
            natural_light_only=True
        )

        scene.lighting = lighting

        self.log(f"✓ Lighting: {lighting.primary_source} ({lighting.primary_color_temp})")

        return scene

    def _get_natural_color_temp(self, time_of_day: str) -> str:
        """Get color temperature for natural light"""
        temps = {
            "dawn": "4000K warm golden",
            "morning": "5000K neutral",
            "day": "5600K daylight",
            "afternoon": "5200K slightly warm",
            "dusk": "3500K warm orange",
            "night": "3200K tungsten"
        }
        return temps.get(time_of_day.lower(), "5600K daylight")
