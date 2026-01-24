"""
Agent 7: Composition & Observation Agent
Removes "AI cinematic look"
"""
from .base_agent import BaseCompilerAgent
from ..schemas import CinematicScene, CinematicProject, CompositionRules


class CompositionObservationAgent(BaseCompilerAgent):
    """
    AGENT 7: COMPOSITION & OBSERVATION

    Purpose: Remove "AI cinematic look"

    Responsibilities:
    - Enforce unstructured framing
    - Enforce asymmetry
    - Enforce observer-as-witness perspective

    Rules:
    - No rule-of-thirds enforcement
    - No stylized framing
    - No "perfect" balance
    """

    def __init__(self):
        super().__init__("Composition & Observation Agent")

    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """Define anti-AI composition rules"""

        if not self.validate_input(scene, ['camera']):
            raise ValueError(f"Scene {scene.scene_id} missing camera spec")

        self.log(f"Defining composition rules for scene {scene.sequence_number}")

        composition = CompositionRules(
            framing_style="unstructured",
            balance_type="asymmetric",
            observer_perspective="witness",
            avoid_rule_of_thirds=True,
            avoid_symmetry=True,
            allow_imperfection=True,
            composition_notes="Natural, documentary-style framing. No perfect composition."
        )

        scene.composition = composition

        self.log("✓ Composition: Unstructured, asymmetric, witness perspective")

        return scene
