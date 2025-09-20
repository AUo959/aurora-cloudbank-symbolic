"""
Vector Symbolic Architecture (VSA) utility for symbolic data encoding/decoding.
Zero-dependency native implementation for Aurora CloudBank.
"""

import hashlib
import math
import secrets
from typing import Any, Dict, List, Literal


class SymbolicVector:
    """Native Python implementation of Vector Symbolic Architecture - Zero Dependencies"""

    def __init__(
        self,
        symbol: str,
        dim: int = 512,
        vector: List[float] = None,
        vector_type: Literal["bipolar", "binary", "real"] = "bipolar",
    ):
        self.symbol = symbol
        self.dim = dim
        self.vector_type = vector_type

        if vector is None:
            self.vector = self._generate_vector()
        else:
            # Validate vector length
            if len(vector) != dim:
                raise ValueError(f"Vector length {len(vector)} does not match dim {dim}")
            self.vector = list(vector)  # Ensure it's a list

    def _generate_vector(self) -> List[float]:
        """Generate deterministic vector from symbol using native Python"""
        # Use symbol hash for deterministic generation
        h = hashlib.sha256(self.symbol.encode()).digest()
        
        # Generate deterministic vector from hash bytes
        vector = []
        byte_index = 0
        
        for i in range(self.dim):
            # Use hash bytes cyclically for deterministic generation
            byte_val = h[byte_index % len(h)]
            byte_index += 1
            
            if self.vector_type == "bipolar":
                vector.append(-1.0 if byte_val < 128 else 1.0)
            elif self.vector_type == "binary":
                vector.append(0.0 if byte_val < 128 else 1.0)
            elif self.vector_type == "real":
                # Generate pairs of uniform random numbers for Box-Muller transform
                if i % 2 == 0 and i + 1 < self.dim:
                    # Box-Muller transform for normal distribution using hash bytes
                    u1 = max(0.001, (h[byte_index % len(h)] + 1) / 257.0)  # Avoid 0
                    byte_index += 1
                    u2 = (h[byte_index % len(h)] + 1) / 257.0
                    byte_index += 1
                    
                    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
                    z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
                    
                    vector.append(z0)
                    if i + 1 < self.dim:
                        vector.append(z1)
                elif len(vector) < self.dim:
                    # Handle odd dimension case
                    u = (h[byte_index % len(h)] + 1) / 257.0
                    byte_index += 1
                    vector.append(math.sqrt(-2.0 * math.log(max(0.001, u))))
            else:
                raise ValueError(f"Unknown vector_type: {self.vector_type}")
        
        return vector[:self.dim]  # Ensure exact dimension

    @classmethod
    def from_symbol(cls, symbol: str, dim: int = 512, vector_type: str = "bipolar"):
        """Create symbolic vector from symbol - zero dependency version"""
        return cls(symbol, dim, None, vector_type)

    def to_json(self) -> dict:
        """Convert to dictionary representation"""
        return {
            "symbol": self.symbol,
            "dim": self.dim,
            "vector": self.vector,
            "vector_type": self.vector_type
        }

    @classmethod
    def from_json(cls, data: dict) -> "SymbolicVector":
        """Create from dictionary representation"""
        return cls(
            symbol=data["symbol"],
            dim=data["dim"],
            vector=data["vector"],
            vector_type=data["vector_type"]
        )

    def similarity(self, other: "SymbolicVector") -> float:
        """Calculate cosine similarity with another vector - zero dependency"""
        if len(self.vector) != len(other.vector):
            raise ValueError("Vector dimensions must match")
        
        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        return dot_product / self.dim

    def __repr__(self):
        return f"SymbolicVector(symbol={self.symbol!r}, dim={self.dim})"

    def __eq__(self, other):
        """Equality comparison for testing compatibility"""
        if not isinstance(other, SymbolicVector):
            return False
        return (
            self.symbol == other.symbol and
            self.dim == other.dim and
            self.vector == other.vector and
            self.vector_type == other.vector_type
        )

    def bind(self, other: "SymbolicVector") -> "SymbolicVector":
        """Bind two symbolic vectors (elementwise multiplication) - zero dependency"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch in binding.")
        
        bound_vec = [a * b for a, b in zip(self.vector, other.vector)]
        return SymbolicVector(
            symbol=f"({self.symbol})*({other.symbol})",
            dim=self.dim,
            vector=bound_vec,
            vector_type=self.vector_type
        )

    def superpose(self, other: "SymbolicVector") -> "SymbolicVector":
        """Superpose two symbolic vectors (elementwise addition, then sign normalization) - zero dependency"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch in superposition.")
        
        superposed = [a + b for a, b in zip(self.vector, other.vector)]
        # Sign normalization without numpy
        normed = [1.0 if x > 0 else (-1.0 if x < 0 else 0.0) for x in superposed]
        
        return SymbolicVector(
            symbol=f"({self.symbol})+({other.symbol})",
            dim=self.dim,
            vector=normed,
            vector_type=self.vector_type
        )

    @staticmethod
    def cleanup(query: List[float], memory: List[List[float]]) -> List[float]:
        """Return the vector in memory most similar to the query - zero dependency"""
        if not memory:
            return query
        
        best_sim = float('-inf')
        best_vec = memory[0]
        
        for vec in memory:
            if len(vec) != len(query):
                continue
            sim = sum(a * b for a, b in zip(query, vec)) / len(query)
            if sim > best_sim:
                best_sim = sim
                best_vec = vec
        
        return best_vec


# Zero-dependency utility functions

def encode_symbol(symbol: str, dim: int = 512, vector_type: str = "bipolar") -> list:
    """Utility function to encode symbol as vector - zero dependency"""
    vector = SymbolicVector.from_symbol(symbol, dim, vector_type)
    return vector.vector


def similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate similarity between two raw vectors - zero dependency"""
    if len(vec1) != len(vec2):
        raise ValueError("Vector dimensions must match")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    return dot_product / len(vec1)
