"""
Cinematic Production Compiler
A deterministic multi-agent system for generating high-fidelity cinematic prompts

This system operates as a COMPILER, not a writer.
Each transformation adds information without overwriting prior decisions.
All state is persistent and immutable once locked.
"""

from .engine import CinematicCompiler
from .schemas import (
    CinematicProject,
    CinematicScene,
    CharacterIdentity,
    SpatialState,
    CameraSpec,
    LightingPhysics,
    CompositionRules,
    MotionDelta,
    CompiledPrompt
)
from .state_manager import CompilerStateManager

__all__ = [
    'CinematicCompiler',
    'CinematicProject',
    'CinematicScene',
    'CharacterIdentity',
    'SpatialState',
    'CameraSpec',
    'LightingPhysics',
    'CompositionRules',
    'MotionDelta',
    'CompiledPrompt',
    'CompilerStateManager'
]

__version__ = '1.0.0'
