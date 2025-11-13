"""
Vector Gen v2.0 - Advanced Symbolic Vector Chain Generator

This module provides enterprise-grade vector generation and symbolic chain management
with DriftConcord integration and Picard_Delta_3 ethics enforcement.
"""

from .vector_gen_v2 import (
    SymbolicVectorGenerator,
    VectorChainBuilder,
    VectorChainType,
    ChainLinkStrength,
    VectorInjectionMode,
    ConstellationTarget,
)

__version__ = "2.0.0"
__all__ = [
    "SymbolicVectorGenerator",
    "VectorChainBuilder",
    "VectorChainType",
    "ChainLinkStrength",
    "VectorInjectionMode",
    "ConstellationTarget",
]
