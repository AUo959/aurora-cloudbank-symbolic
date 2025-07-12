"""
geometric_algebra.py
Native Python geometric algebra utilities without external dependencies.
"""

import math
from typing import List, Union, Tuple


def create_vector(x: float, y: float, z: float) -> List[float]:
    """Create a 3D vector as a list."""
    return [x, y, z]


def geometric_product(a: List[float], b: List[float]) -> float:
    """Compute the dot product (simplified geometric product for vectors)."""
    if len(a) != len(b):
        raise ValueError("Vectors must have same length")
    return sum(ai * bi for ai, bi in zip(a, b))


def add_multivectors(a: List[float], b: List[float]) -> List[float]:
    """Add two vectors."""
    if len(a) != len(b):
        raise ValueError("Vectors must have same length")
    return [ai + bi for ai, bi in zip(a, b)]


def multivector_to_array(mv: List[float]) -> List[float]:
    """Convert a multivector to array of coefficients (identity operation)."""
    return mv.copy()


def cross_product(a: List[float], b: List[float]) -> List[float]:
    """3D cross product."""
    if len(a) < 3 or len(b) < 3:
        return [0, 0, 0]
    
    return [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]
    ]


def vector_magnitude(v: List[float]) -> float:
    """Calculate magnitude of vector."""
    return math.sqrt(sum(x * x for x in v))


def normalize_vector(v: List[float]) -> List[float]:
    """Normalize vector to unit length."""
    mag = vector_magnitude(v)
    if mag == 0:
        return [0.0] * len(v)
    return [x / mag for x in v]


def rotate_vector(v: List[float], axis: List[float], angle: float) -> List[float]:
    """Rotate vector around axis by angle (Rodrigues' rotation formula)."""
    if len(v) < 3 or len(axis) < 3:
        return v.copy()
    
    # Normalize axis
    k = normalize_vector(axis)
    
    # Rodrigues' rotation formula
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    
    # v_rot = v*cos(θ) + (k × v)*sin(θ) + k*(k·v)*(1-cos(θ))
    k_dot_v = geometric_product(k, v)
    k_cross_v = cross_product(k, v)
    
    result = []
    for i in range(3):
        component = (v[i] * cos_theta + 
                   k_cross_v[i] * sin_theta + 
                   k[i] * k_dot_v * (1 - cos_theta))
        result.append(component)
    
    return result


# Example usage (for testing/demo purposes)
if __name__ == "__main__":
    v1 = create_vector(1, 0, 0)
    v2 = create_vector(0, 1, 0)
    print("v1:", v1)
    print("v2:", v2)
    print("v1 + v2:", add_multivectors(v1, v2))
    print("v1 · v2 (dot product):", geometric_product(v1, v2))
    print("v1 × v2 (cross product):", cross_product(v1, v2))
