"""
Vector Symbolic Architecture (VSA) utility for symbolic data encoding/decoding.
"""

import hashlib
from typing import Literal

import numpy as np
from pydantic import BaseModel, ValidationInfo, field_validator


class SymbolicVector(BaseModel):
    symbol: str
    dim: int = 512
    vector: list  # Accept any type for vector elements
    vector_type: Literal["bipolar", "binary", "real"] = "bipolar"

    @field_validator("vector")
    @classmethod
    def validate_vector(cls, v, info: ValidationInfo):
        dim = info.data.get("dim", 512)
        if len(v) != dim:
            raise ValueError(f"Vector length {len(v)} does not match dim {dim}")
        return v

    @classmethod
    def from_symbol(cls, symbol: str, dim: int = 512, vector_type: str = "bipolar"):
        h = hashlib.sha256(symbol.encode()).digest()
        rng = np.random.default_rng(int.from_bytes(h, "big"))
        if vector_type == "bipolar":
            vec = [int(x) for x in rng.choice([-1, 1], size=dim)]
        elif vector_type == "binary":
            vec = [int(x) for x in rng.choice([0, 1], size=dim)]
        elif vector_type == "real":
            arr = rng.normal(0, 1, size=dim)
            vec = [float(x) for x in arr.tolist()]
            return cls(symbol=symbol, dim=dim, vector=vec, vector_type=vector_type)
        else:
            raise ValueError(f"Unknown vector_type: {vector_type}")
        return cls(symbol=symbol, dim=dim, vector=vec, vector_type=vector_type)

    def to_json(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_json(cls, data: dict) -> "SymbolicVector":
        return cls(**data)

    def similarity(self, other: "SymbolicVector") -> float:
        return float(np.dot(self.vector, other.vector) / self.dim)

    def __repr__(self):
        return f"SymbolicVector(symbol={self.symbol!r}, dim={self.dim})"

    def bind(self, other: "SymbolicVector") -> "SymbolicVector":
        """Bind two symbolic vectors (elementwise multiplication)."""
        assert self.dim == other.dim, "Dimension mismatch in binding."
        bound_vec = self.vector * other.vector
        return SymbolicVector(f"({self.symbol})*({other.symbol})", self.dim).from_vector(bound_vec)

    def superpose(self, other: "SymbolicVector") -> "SymbolicVector":
        """Superpose two symbolic vectors (elementwise addition, then sign normalization)."""
        assert self.dim == other.dim, "Dimension mismatch in superposition."
        superposed = self.vector + other.vector
        normed = np.sign(superposed)
        return SymbolicVector(f"({self.symbol})+({other.symbol})", self.dim).from_vector(normed)

    def from_vector(self, vec: np.ndarray) -> "SymbolicVector":
        self.vector = vec
        return self

    @staticmethod
    def cleanup(query: np.ndarray, memory: list) -> np.ndarray:
        """Return the vector in memory most similar to the query."""
        sims = [float(np.dot(query, v) / len(query)) for v in memory]
        return memory[int(np.argmax(sims))]


# Example utility function


def encode_symbol(symbol: str, dim: int = 512, vector_type: str = "bipolar") -> list:
    return SymbolicVector.from_symbol(symbol, dim, vector_type).vector


def similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return float(np.dot(vec1, vec2) / len(vec1))
