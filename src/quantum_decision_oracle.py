"""Compatibility import for the scenario-outcome decision oracle.

The feature implementation is owned by :mod:`modules.quantum_decision_oracle`.
This module preserves the established ``src.quantum_decision_oracle`` import
without marking it for deletion.
"""

from modules.quantum_decision_oracle import (
    AuditTrailEntry,
    ConfidenceLevel,
    QuantumDecisionOracle,
    QuantumDecisionResult,
    QuantumReasoningMode,
)

__all__ = [
    "AuditTrailEntry",
    "ConfidenceLevel",
    "QuantumDecisionOracle",
    "QuantumDecisionResult",
    "QuantumReasoningMode",
]
