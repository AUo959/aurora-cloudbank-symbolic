"""CASK Integration Module.

Expose analysis utilities for tests and downstream consumers.
"""

from .analysis import (
    generate_technical_specifications,
    generate_vs_sota_comparison,
    generate_risk_assessment,
)

__all__ = [
    "generate_technical_specifications",
    "generate_vs_sota_comparison",
    "generate_risk_assessment",
]
