"""
Vector Symbolic Architecture (VSA) utility for symbolic data encoding/decoding.
"""
import numpy as np
import hashlib


class SymbolicVector:
    def __init__(self, symbol: str, dim: int = 512):
        self.symbol = symbol
        self.dim = dim
        self.vector = self._encode(symbol)

    def _encode(self, symbol: str) -> np.ndarray:
        # Hash the symbol and use it to seed a random vector
        h = hashlib.sha256(symbol.encode()).digest()
        rng = np.random.default_rng(int.from_bytes(h, 'big'))
        return rng.choice([-1, 1], size=self.dim)

    def similarity(self, other: 'SymbolicVector') -> float:
        return float(np.dot(self.vector, other.vector) / self.dim)

    def __repr__(self):
        return f"SymbolicVector(symbol={self.symbol!r}, dim={self.dim})"

    def bind(self, other: 'SymbolicVector') -> 'SymbolicVector':
        """Bind two symbolic vectors (elementwise multiplication)."""
        assert self.dim == other.dim, "Dimension mismatch in binding."
        bound_vec = self.vector * other.vector
        return SymbolicVector(f"({self.symbol})*({other.symbol})", self.dim).from_vector(bound_vec)

    def superpose(self, other: 'SymbolicVector') -> 'SymbolicVector':
        """Superpose two symbolic vectors (elementwise addition, then sign normalization)."""
        assert self.dim == other.dim, "Dimension mismatch in superposition."
        superposed = self.vector + other.vector
        normed = np.sign(superposed)
        return SymbolicVector(f"({self.symbol})+({other.symbol})", self.dim).from_vector(normed)

    def from_vector(self, vec: np.ndarray) -> 'SymbolicVector':
        self.vector = vec
        return self

    @staticmethod
    def cleanup(query: np.ndarray, memory: list) -> np.ndarray:
        """Return the vector in memory most similar to the query."""
        sims = [float(np.dot(query, v) / len(query)) for v in memory]
        return memory[int(np.argmax(sims))]


# Example utility function


def encode_symbol(symbol: str, dim: int = 512) -> np.ndarray:
    return SymbolicVector(symbol, dim).vector


def similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    return float(np.dot(vec1, vec2) / len(vec1))
