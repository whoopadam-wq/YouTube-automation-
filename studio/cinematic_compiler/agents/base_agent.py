"""
Base Compiler Agent
Abstract base class for all internal compiler agents
"""
from abc import ABC, abstractmethod
from typing import Any
from ..schemas import CinematicScene, CinematicProject


class BaseCompilerAgent(ABC):
    """
    Abstract base class for compiler agents

    Each agent:
    - Receives a scene and project context
    - Performs ONE specific transformation
    - Returns the scene with new data added
    - NEVER overwrites prior agent data
    - Operates deterministically
    """

    def __init__(self, name: str):
        """
        Initialize agent

        Args:
            name: Human-readable agent name
        """
        self.name = name

    @abstractmethod
    def process(self, scene: CinematicScene, project: CinematicProject) -> CinematicScene:
        """
        Process a scene through this agent's transformation

        Args:
            scene: CinematicScene to transform
            project: Full project context (for global state access)

        Returns:
            Transformed scene with agent's data added
        """
        pass

    def validate_input(self, scene: CinematicScene, required_fields: list) -> bool:
        """
        Validate that scene has required fields populated from prior agents

        Args:
            scene: Scene to validate
            required_fields: List of field names that must be non-None

        Returns:
            True if valid, False otherwise
        """
        for field in required_fields:
            if not hasattr(scene, field) or getattr(scene, field) is None:
                print(f"⚠️  {self.name}: Missing required field '{field}'")
                return False

        return True

    def log(self, message: str):
        """Log agent activity"""
        print(f"[{self.name}] {message}")
