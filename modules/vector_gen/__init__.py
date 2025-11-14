"""
Vector Gen v2.0 - Symbolic Vector Chain Generation and Management

This module provides production-ready vector chain management with VECTORCHAIN
capsule packaging, DriftConcord integration, and constellation support.

T1: VECTOR_GEN_v2.0
SRB: CHAIN_MANAGEMENT_ENGINE
DLP: context_tag=vector_gen_init, symbolic_hash=VG_v2_INIT

Author: Aurora CloudBank Team
Version: 2.0.0
Date: 2025-11-13
"""

from .vector_gen_v2 import (
    VectorGen,
    VectorCapsulePackager,
    ChainTopology,
    InjectionMode,
    LinkStrength,
    SymbolicVector,
    VectorChain,
    VectorLink,
)

__version__ = "2.0.0"
__all__ = [
    "VectorGen",
    "VectorCapsulePackager",
    "ChainTopology",
    "InjectionMode",
    "LinkStrength",
    "SymbolicVector",
    "VectorChain",
    "VectorLink",
]
