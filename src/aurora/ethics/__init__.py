"""
Aurora Ethics Gate Module

Central ethics evaluation system wrapping GUMAS and preparing for Picard_Delta_3.

DLP: ethics_gate_core_v1
Anchors: T1, SRB, EOS_SEED_ORION, Picard_Delta_3
Symbolic tags: ETHICS_GATE_CORE, GUMAS_INTEGRATION, PICARD_DELTA_3_READY
"""

from .ethics_gate import (
    EthicsVerdict,
    GUMASEthicsClient,
    EthicsGate,
    EthicsViolation as EthicsGateViolation
)

__all__ = [
    "EthicsVerdict",
    "GUMASEthicsClient",
    "EthicsGate",
    "EthicsGateViolation"
]
