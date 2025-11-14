"""
Aurora HR Module v3.0 "Helios"
Production-ready personnel management system with quantum enhancements

Symbolic Anchor: HR-HELIOS-V3-20251111
Quantum Anchor: T9-HR-QUANTUM
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

# Quantum enhancements (optional - graceful degradation if dependencies unavailable)
try:
    from .quantum_hr_enhancement import (
        QuantumCharacterProfile,
        QuantumCharacterDatabase,
        QuantumTeamDynamics,
        QuantumHRIntegration
    )
    QUANTUM_HR_AVAILABLE = True
except ImportError:
    QUANTUM_HR_AVAILABLE = False

__version__ = "3.0.0"
__quantum_version__ = "1.0.0"
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
    "CulturalHealthReport",
    "QUANTUM_HR_AVAILABLE"
]

# Add quantum exports if available
if QUANTUM_HR_AVAILABLE:
    __all__.extend([
        "QuantumCharacterProfile",
        "QuantumCharacterDatabase",
        "QuantumTeamDynamics",
        "QuantumHRIntegration"
    ])
