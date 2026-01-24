"""
Agent 5: Camera & Optics Agent
Enforces photographic realism
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, CameraSpec


class CameraOpticsAgent(BaseCompilerAgent):
    """
    AGENT 5: CAMERA & OPTICS

    Purpose: Enforce photographic realism

    Responsibilities:
    - Select real camera bodies
    - Select real lenses
    - Define focal length behavior
    - Define depth of field
    - Define camera position relative to subjects

    Rules:
    - Documentary realism over cinematic framing
    - No impossible lenses
    - No virtual camera tricks
    - No drone shots unless explicitly grounded
    """

    def __init__(self):
        super().__init__("Camera & Optics Agent")

        # Real camera/lens database
        self.cameras = [
            "Sony FX6", "Sony FX3", "Canon C70", "Canon C300 Mark III",
            "RED Komodo 6K", "ARRI Alexa Mini LF", "Blackmagic Pocket 6K"
        ]

        self.lenses = {
            "wide": ["Sony 16-35mm f/2.8 GM", "Canon RF 15-35mm f/2.8", "Sigma 18-35mm f/1.8"],
            "standard": ["Sony 24-70mm f/2.8 GM II", "Canon RF 24-70mm f/2.8", "Sigma 24-70mm f/2.8"],
            "portrait": ["Sony 85mm f/1.4 GM", "Canon RF 85mm f/1.2", "Sigma 85mm f/1.4"],
            "telephoto": ["Sony 70-200mm f/2.8 GM", "Canon RF 70-200mm f/2.8", "Sigma 100-400mm"]
        }

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Define camera and optics specifications"""

        if not self.validate_input(scene, ['spatial_state']):
            raise ValueError(f"Scene {scene.scene_id} missing spatial state")

        self.log(f"Defining camera specs for scene {scene.sequence_number}")

        # Select appropriate camera and lens based on scene requirements
        # (In production, Claude analyzes scene to choose optimal setup)

        camera = CameraSpec(
            camera_body="Sony FX6",
            lens_model="Sony 24-70mm f/2.8 GM II",
            focal_length_mm=35,
            aperture="f/2.8",
            camera_position="slightly offset",
            camera_height="eye-level",
            camera_distance="medium",
            depth_of_field="medium",
            focus_point="subject's eyes",
            documentary_realism=True
        )

        scene.camera = camera

        self.log(f"✓ Camera: {camera.camera_body} + {camera.lens_model} @ {camera.focal_length_mm}mm")

        return scene
