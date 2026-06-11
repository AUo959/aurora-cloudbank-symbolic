"""CASK Integration Module.

Expose analysis utilities and runtime components for tests and downstream consumers.
"""

from .analysis import (
    generate_technical_specifications,
    generate_vs_sota_comparison,
    generate_risk_assessment,
)
from .cultural_cognition import score_cultural_sensitivity, CulturalSensitivityScore
from .recursive_ethics_validator import RecursiveEthicsValidator, ValidationVerdict

__all__ = [
    "generate_technical_specifications",
    "generate_vs_sota_comparison",
    "generate_risk_assessment",
    "score_cultural_sensitivity",
    "CulturalSensitivityScore",
    "RecursiveEthicsValidator",
    "ValidationVerdict",
]
