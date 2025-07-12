"""
Vector Symbolic Architecture (VSA) utility for symbolic data encoding/decoding.
Optimized zero-dependency implementation.
"""

import hashlib
from typing import Literal, Dict, Any, List
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.native_vsa import NativeSymbolicVector, NativeVSAMemory


class SymbolicVector:
    """Legacy compatibility wrapper for native symbolic vector"""
    
    def __init__(self, symbol: str, dim: int = 512, vector: List[float] = None, vector_type: Literal["bipolar", "binary", "real"] = "bipolar"):
        # Use native implementation internally
        self._native_vector = NativeSymbolicVector(symbol, dim, vector, vector_type)
        
        # Legacy attribute compatibility
        self.symbol = self._native_vector.symbol
        self.dim = self._native_vector.dim
        self.vector = self._native_vector.vector
        self.vector_type = self._native_vector.vector_type

    @classmethod
    def from_symbol(cls, symbol: str, dim: int = 512, vector_type: str = "bipolar"):
        """Create symbolic vector from symbol"""
        return cls(symbol, dim, None, vector_type)

    def to_json(self) -> dict:
        """Convert to JSON representation"""
        return self._native_vector.to_dict()

    @classmethod
    def from_json(cls, data: dict) -> "SymbolicVector":
        """Create from JSON representation"""
        instance = cls.__new__(cls)
        instance._native_vector = NativeSymbolicVector.from_dict(data)
        instance.symbol = instance._native_vector.symbol
        instance.dim = instance._native_vector.dim
        instance.vector = instance._native_vector.vector
        instance.vector_type = instance._native_vector.vector_type
        return instance

    def similarity(self, other: "SymbolicVector") -> float:
        """Calculate similarity with another vector"""
        return self._native_vector.similarity(other._native_vector)

    def __repr__(self):
        return f"SymbolicVector(symbol={self.symbol!r}, dim={self.dim})"

    def bind(self, other: "SymbolicVector") -> "SymbolicVector":
        """Bind two symbolic vectors (elementwise multiplication)."""
        result_native = self._native_vector.bind(other._native_vector)
        
        # Create wrapper instance
        result = SymbolicVector.__new__(SymbolicVector)
        result._native_vector = result_native
        result.symbol = result_native.symbol
        result.dim = result_native.dim
        result.vector = result_native.vector
        result.vector_type = result_native.vector_type
        return result

    def superpose(self, other: "SymbolicVector") -> "SymbolicVector":
        """Superpose two symbolic vectors (elementwise addition, then normalization)."""
        result_native = self._native_vector.superpose(other._native_vector)
        
        # Create wrapper instance
        result = SymbolicVector.__new__(SymbolicVector)
        result._native_vector = result_native
        result.symbol = result_native.symbol
        result.dim = result_native.dim
        result.vector = result_native.vector
        result.vector_type = result_native.vector_type
        return result

    def from_vector(self, vec: List[float]) -> "SymbolicVector":
        """Create from raw vector"""
        self._native_vector.vector = vec
        self.vector = vec
        return self

    @staticmethod
    def cleanup(query: List[float], memory: List[List[float]]) -> List[float]:
        """Return the vector in memory most similar to the query."""
        if not memory:
            raise ValueError("Memory is empty")
        
        best_similarity = float('-inf')
        best_vector = None
        
        for vec in memory:
            similarity = sum(a * b for a, b in zip(query, vec)) / len(query)
            if similarity > best_similarity:
                best_similarity = similarity
                best_vector = vec
        
        return best_vector


# Legacy utility functions for backward compatibility

def encode_symbol(symbol: str, dim: int = 512, vector_type: str = "bipolar") -> List[float]:
    """Utility function to encode symbol as vector"""
    vector = NativeSymbolicVector.from_symbol(symbol, dim, vector_type)
    return vector.vector


def similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate similarity between two raw vectors"""
    if len(vec1) != len(vec2):
        raise ValueError("Vector dimensions must match")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    return dot_product / len(vec1)
