"""
Native Python mathematical operations to replace numpy dependencies.
Lightweight implementations for symbolic vector operations.
"""

import random
import math
from typing import List, Union


class NativeMath:
    """Native Python mathematical operations for symbolic processing."""
    
    @staticmethod
    def dot_product(vec1: List[Union[int, float]], vec2: List[Union[int, float]]) -> float:
        """Calculate dot product of two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")
        return sum(a * b for a, b in zip(vec1, vec2))
    
    @staticmethod
    def vector_norm(vec: List[Union[int, float]]) -> float:
        """Calculate the norm (magnitude) of a vector."""
        return math.sqrt(sum(x * x for x in vec))
    
    @staticmethod
    def normalize_vector(vec: List[Union[int, float]]) -> List[float]:
        """Normalize a vector to unit length."""
        norm = NativeMath.vector_norm(vec)
        if norm == 0:
            return [0.0] * len(vec)
        return [x / norm for x in vec]
    
    @staticmethod
    def cosine_similarity(vec1: List[Union[int, float]], vec2: List[Union[int, float]]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot = NativeMath.dot_product(vec1, vec2)
        norm1 = NativeMath.vector_norm(vec1)
        norm2 = NativeMath.vector_norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
    
    @staticmethod
    def generate_random_vector(dim: int, vector_type: str = "bipolar", seed: int = None) -> List[Union[int, float]]:
        """Generate random vector with specified type."""
        if seed is not None:
            random.seed(seed)
        
        if vector_type == "bipolar":
            return [random.choice([-1, 1]) for _ in range(dim)]
        elif vector_type == "binary":
            return [random.choice([0, 1]) for _ in range(dim)]
        elif vector_type == "real":
            return [random.gauss(0, 1) for _ in range(dim)]
        else:
            raise ValueError(f"Unknown vector_type: {vector_type}")
    
    @staticmethod
    def element_wise_multiply(vec1: List[Union[int, float]], vec2: List[Union[int, float]]) -> List[Union[int, float]]:
        """Element-wise multiplication of two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")
        return [a * b for a, b in zip(vec1, vec2)]
    
    @staticmethod
    def element_wise_add(vec1: List[Union[int, float]], vec2: List[Union[int, float]]) -> List[Union[int, float]]:
        """Element-wise addition of two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")
        return [a + b for a, b in zip(vec1, vec2)]
    
    @staticmethod
    def permute_vector(vec: List[Union[int, float]], seed: int = None) -> List[Union[int, float]]:
        """Permute vector elements using deterministic shuffling."""
        if seed is not None:
            random.seed(seed)
        
        result = vec.copy()
        random.shuffle(result)
        return result
    
    @staticmethod
    def circular_shift(vec: List[Union[int, float]], shift: int) -> List[Union[int, float]]:
        """Circular shift of vector elements."""
        if not vec:
            return vec
        shift = shift % len(vec)
        return vec[shift:] + vec[:shift]


class NativeRandom:
    """Native Python random number generation to replace numpy random."""
    
    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)
    
    def seed(self, seed: int):
        """Set random seed."""
        self.rng.seed(seed)
    
    def choice(self, choices: List, size: int = 1) -> Union[List, any]:
        """Choose random elements from list."""
        if size == 1:
            return self.rng.choice(choices)
        return [self.rng.choice(choices) for _ in range(size)]
    
    def normal(self, mean: float = 0.0, std: float = 1.0, size: int = 1) -> Union[List[float], float]:
        """Generate normally distributed random numbers."""
        if size == 1:
            return self.rng.gauss(mean, std)
        return [self.rng.gauss(mean, std) for _ in range(size)]
    
    def uniform(self, low: float = 0.0, high: float = 1.0, size: int = 1) -> Union[List[float], float]:
        """Generate uniformly distributed random numbers."""
        if size == 1:
            return self.rng.uniform(low, high)
        return [self.rng.uniform(low, high) for _ in range(size)]