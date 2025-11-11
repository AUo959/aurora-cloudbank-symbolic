"""
HR System Core Module

Core functionality for HR operations including:
- Character generation with quantum-symbolic properties
- Staffing need analysis
- Organizational intelligence
"""

from .character_generator import (
    CharacterGenerator,
    CharacterProfile,
    QuantumProfile,
    Rank,
    ExperienceLevel,
    Department
)

__all__ = [
    "CharacterGenerator",
    "CharacterProfile",
    "QuantumProfile",
    "Rank",
    "ExperienceLevel",
    "Department"
]
