"""
Aurora HR Module v3.0 "Helios"
Production-ready personnel management system

Symbolic Anchor: HR-HELIOS-V3-20251111
Protocol: Picard_Delta_3
"""

from .aurora_hr_module_advanced_v3 import (
    AuroraHRModule,
    TeamLayer,
    PsychologicalSafetyLevel,
    ConflictSeverity,
    OnboardingPhase,
    TeamMember,
    Department,
    ConflictEvent,
    OnboardingJourney,
    CulturalHealthReport
)

__version__ = "3.0.0"
__codename__ = "Helios"
__all__ = [
    "AuroraHRModule",
    "TeamLayer",
    "PsychologicalSafetyLevel",
    "ConflictSeverity",
    "OnboardingPhase",
    "TeamMember",
    "Department",
    "ConflictEvent",
    "OnboardingJourney",
    "CulturalHealthReport"
]
