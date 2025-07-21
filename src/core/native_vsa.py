"""
Native Vector Symbolic Architecture (VSA) - Zero Dependencies
Lightweight symbolic data encoding/decoding without numpy.
"""

import hashlib
import math
import random
from typing import Any, Dict, List, Literal


class NativeSymbolicVector:
    """Native Python implementation of Vector Symbolic Architecture"""

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
            if len(vector) != dim:
                raise ValueError(f"Vector length {len(vector)} does not match dim {dim}")
            self.vector = vector

    def _generate_vector(self) -> List[float]:
        """Generate deterministic vector from symbol using native Python"""
        # Use symbol hash as seed for deterministic generation
        h = hashlib.sha256(self.symbol.encode()).digest()
        seed = int.from_bytes(h[:4], "big")  # Use first 4 bytes for seed
        random.seed(seed)

        if self.vector_type == "bipolar":
            return [random.choice([-1.0, 1.0]) for _ in range(self.dim)]
        elif self.vector_type == "binary":
            return [random.choice([0.0, 1.0]) for _ in range(self.dim)]
        elif self.vector_type == "real":
            # Generate normal distribution using Box-Muller transform
            vec = []
            for _ in range(self.dim // 2):
                u1, u2 = random.random(), random.random()
                z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
                z1 = math.sqrt(-2.0 * math.log(u1)) * math.sin(2.0 * math.pi * u2)
                vec.extend([z0, z1])
            if self.dim % 2:  # If odd dimension, add one more
                u1, u2 = random.random(), random.random()
                z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
                vec.append(z0)
            return vec[: self.dim]
        else:
            raise ValueError(f"Unknown vector_type: {self.vector_type}")

    @classmethod
    def from_symbol(cls, symbol: str, dim: int = 512, vector_type: str = "bipolar") -> "NativeSymbolicVector":
        """Create symbolic vector from symbol"""
        return cls(symbol, dim, None, vector_type)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {"symbol": self.symbol, "dim": self.dim, "vector": self.vector, "vector_type": self.vector_type}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NativeSymbolicVector":
        """Create from dictionary representation"""
        return cls(symbol=data["symbol"], dim=data["dim"], vector=data["vector"], vector_type=data["vector_type"])

    def similarity(self, other: "NativeSymbolicVector") -> float:
        """Calculate cosine similarity with another vector"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch in similarity calculation")

        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        return dot_product / self.dim

    def bind(self, other: "NativeSymbolicVector") -> "NativeSymbolicVector":
        """Bind two symbolic vectors (elementwise multiplication)"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch in binding")

        bound_vec = [a * b for a, b in zip(self.vector, other.vector)]
        bound_symbol = f"({self.symbol})*({other.symbol})"

        return NativeSymbolicVector(symbol=bound_symbol, dim=self.dim, vector=bound_vec, vector_type=self.vector_type)

    def superpose(self, other: "NativeSymbolicVector") -> "NativeSymbolicVector":
        """Superpose two symbolic vectors (elementwise addition with normalization)"""
        if self.dim != other.dim:
            raise ValueError("Dimension mismatch in superposition")

        superposed = [a + b for a, b in zip(self.vector, other.vector)]

        # Sign normalization for bipolar/binary, regular normalization for real
        if self.vector_type in ["bipolar", "binary"]:
            normed = [1.0 if x > 0 else -1.0 if x < 0 else 0.0 for x in superposed]
        else:
            # Normalize to unit length for real vectors
            magnitude = math.sqrt(sum(x * x for x in superposed))
            normed = [x / magnitude if magnitude > 0 else 0.0 for x in superposed]

        superposed_symbol = f"({self.symbol})+({other.symbol})"

        return NativeSymbolicVector(symbol=superposed_symbol, dim=self.dim, vector=normed, vector_type=self.vector_type)

    def permute(self, shift: int = 1) -> "NativeSymbolicVector":
        """Permute vector elements (circular shift)"""
        shift = shift % self.dim  # Handle shifts larger than dimension
        permuted_vec = self.vector[shift:] + self.vector[:shift]
        permuted_symbol = f"perm({self.symbol},{shift})"

        return NativeSymbolicVector(
            symbol=permuted_symbol, dim=self.dim, vector=permuted_vec, vector_type=self.vector_type
        )

    def __repr__(self):
        return f"NativeSymbolicVector(symbol={self.symbol!r}, dim={self.dim}, type={self.vector_type})"


class NativeVSAMemory:
    """Native VSA associative memory system"""

    def __init__(self, dim: int = 512):
        self.dim = dim
        self.memory: List[NativeSymbolicVector] = []
        self.symbol_index: Dict[str, int] = {}

    def store(self, vector: NativeSymbolicVector):
        """Store vector in associative memory"""
        if vector.dim != self.dim:
            raise ValueError(f"Vector dimension {vector.dim} does not match memory dimension {self.dim}")

        if vector.symbol in self.symbol_index:
            # Update existing vector
            idx = self.symbol_index[vector.symbol]
            self.memory[idx] = vector
        else:
            # Add new vector
            self.symbol_index[vector.symbol] = len(self.memory)
            self.memory.append(vector)

    def retrieve(self, symbol: str) -> NativeSymbolicVector:
        """Retrieve vector by symbol"""
        if symbol not in self.symbol_index:
            raise KeyError(f"Symbol '{symbol}' not found in memory")

        idx = self.symbol_index[symbol]
        return self.memory[idx]

    def cleanup(self, query_vector: NativeSymbolicVector, threshold: float = 0.0) -> NativeSymbolicVector:
        """Find most similar vector in memory (cleanup/auto-associative recall)"""
        if not self.memory:
            raise ValueError("Memory is empty")

        if query_vector.dim != self.dim:
            raise ValueError(f"Query vector dimension {query_vector.dim} does not match memory dimension {self.dim}")

        best_vector = None
        best_similarity = float("-inf")

        for stored_vector in self.memory:
            similarity = query_vector.similarity(stored_vector)
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_vector = stored_vector

        if best_vector is None:
            raise ValueError(f"No vector found with similarity >= {threshold}")

        return best_vector

    def list_symbols(self) -> List[str]:
        """List all stored symbols"""
        return list(self.symbol_index.keys())

    def size(self) -> int:
        """Get number of stored vectors"""
        return len(self.memory)


def encode_symbol(symbol: str, dim: int = 512, vector_type: str = "bipolar") -> List[float]:
    """Utility function to encode symbol as vector"""
    vector = NativeSymbolicVector.from_symbol(symbol, dim, vector_type)
    return vector.vector


def calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate similarity between two raw vectors"""
    if len(vec1) != len(vec2):
        raise ValueError("Vector dimensions must match")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    return dot_product / len(vec1)


def bind_vectors(vec1: List[float], vec2: List[float]) -> List[float]:
    """Bind two raw vectors (elementwise multiplication)"""
    if len(vec1) != len(vec2):
        raise ValueError("Vector dimensions must match")

    return [a * b for a, b in zip(vec1, vec2)]


def superpose_vectors(vec1: List[float], vec2: List[float]) -> List[float]:
    """Superpose two raw vectors (elementwise addition with sign normalization)"""
    if len(vec1) != len(vec2):
        raise ValueError("Vector dimensions must match")

    superposed = [a + b for a, b in zip(vec1, vec2)]
    return [1.0 if x > 0 else -1.0 if x < 0 else 0.0 for x in superposed]
