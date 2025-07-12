"""
Vector Symbolic Architecture (VSA) utility for symbolic data encoding/decoding.
"""

import hashlib
from typing import Literal, Union, List
from .native_math import NativeMath, NativeRandom


class SymbolicVector:
    """Symbolic vector implementation with native Python validation."""
    
    def __init__(self, symbol: str, dim: int = 512, vector: List[Union[int, float]] = None, 
                 vector_type: str = "bipolar"):
        self.symbol = symbol
        self.dim = dim
        self.vector_type = vector_type
        
        if vector is None:
            vector = []
        
        # Validate vector
        if len(vector) != dim:
            raise ValueError(f"Vector length {len(vector)} does not match dim {dim}")
        
        # Validate vector_type
        if vector_type not in ["bipolar", "binary", "real"]:
            raise ValueError(f"Invalid vector_type: {vector_type}")
        
        self.vector = vector

    @classmethod
    def from_symbol(cls, symbol: str, dim: int = 512, vector_type: str = "bipolar"):
        h = hashlib.sha256(symbol.encode()).digest()
        seed = int.from_bytes(h, "big") % (2**32)  # Limit seed size for compatibility
        
        if vector_type == "bipolar":
            vec = NativeMath.generate_random_vector(dim, "bipolar", seed)
        elif vector_type == "binary":
            vec = NativeMath.generate_random_vector(dim, "binary", seed)
        elif vector_type == "real":
            vec = NativeMath.generate_random_vector(dim, "real", seed)
        else:
            raise ValueError(f"Unknown vector_type: {vector_type}")
        return cls(symbol=symbol, dim=dim, vector=vec, vector_type=vector_type)

    def to_json(self) -> dict:
        return {
            "symbol": self.symbol,
            "dim": self.dim,
            "vector": self.vector,
            "vector_type": self.vector_type
        }

    @classmethod
    def from_json(cls, data: dict) -> "SymbolicVector":
        return cls(
            symbol=data["symbol"],
            dim=data["dim"],
            vector=data["vector"],
            vector_type=data["vector_type"]
        )

    def similarity(self, other: "SymbolicVector") -> float:
        return NativeMath.dot_product(self.vector, other.vector) / self.dim

    def __repr__(self):
        return f"SymbolicVector(symbol={self.symbol!r}, dim={self.dim})"

    def bind(self, other: "SymbolicVector") -> "SymbolicVector":
        """Bind two symbolic vectors (elementwise multiplication)."""
        assert self.dim == other.dim, "Dimension mismatch in binding."
        bound_vec = NativeMath.element_wise_multiply(self.vector, other.vector)
        new_vector = SymbolicVector(
            symbol=f"({self.symbol})*({other.symbol})", 
            dim=self.dim,
            vector=bound_vec,
            vector_type=self.vector_type
        )
        return new_vector

    def superpose(self, other: "SymbolicVector") -> "SymbolicVector":
        """Superpose two symbolic vectors (elementwise addition, then sign normalization)."""
        assert self.dim == other.dim, "Dimension mismatch in superposition."
        superposed = NativeMath.element_wise_add(self.vector, other.vector)
        # Sign normalization: convert to -1, 0, 1
        normed = [1 if x > 0 else (-1 if x < 0 else 0) for x in superposed]
        new_vector = SymbolicVector(
            symbol=f"({self.symbol})+({other.symbol})", 
            dim=self.dim,
            vector=normed,
            vector_type=self.vector_type
        )
        return new_vector

    def from_vector(self, vec: List[Union[int, float]]) -> "SymbolicVector":
        self.vector = vec
        return self

    @staticmethod
    def cleanup(query: List[Union[int, float]], memory: List[List[Union[int, float]]]) -> List[Union[int, float]]:
        """Return the vector in memory most similar to the query."""
        sims = [NativeMath.dot_product(query, v) / len(query) for v in memory]
        max_sim_idx = max(range(len(sims)), key=lambda i: sims[i])
        return memory[max_sim_idx]


# Example utility function


def encode_symbol(symbol: str, dim: int = 512, vector_type: str = "bipolar") -> list:
    return SymbolicVector.from_symbol(symbol, dim, vector_type).vector


def similarity(vec1: List[Union[int, float]], vec2: List[Union[int, float]]) -> float:
    return NativeMath.dot_product(vec1, vec2) / len(vec1)
