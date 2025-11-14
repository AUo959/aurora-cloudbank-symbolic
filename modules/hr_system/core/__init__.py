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
from .staffing_analyzer import (
    StaffingAnalyzer,
    StaffingMetrics,
    StaffingRecommendation
)

__all__ = [
    "CharacterGenerator",
    "StaffingAnalyzer",
    "StaffingMetrics",
    "StaffingRecommendation",
    "CharacterProfile",
    "QuantumProfile",
    "Rank",
    "ExperienceLevel",
    "Department"
]
