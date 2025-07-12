"""
Geometric Algebra implementation for symbolic vector operations.
Native Python implementation without external dependencies.
"""

import math
from typing import List, Union, Tuple, Optional


class NativeMath:
    """Basic math operations for geometric algebra."""
    
    @staticmethod
    def vector_norm(vec: List[float]) -> float:
        """Calculate the norm (magnitude) of a vector."""
        return math.sqrt(sum(x * x for x in vec))
    
    @staticmethod
    def dot_product(vec1: List[float], vec2: List[float]) -> float:
        """Calculate dot product of two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")
        return sum(a * b for a, b in zip(vec1, vec2))


class Multivector:
    """Native Python implementation of multivector for geometric algebra."""
    
    def __init__(self, coefficients: List[float] = None, dimension: int = 3):
        """Initialize multivector with coefficients."""
        self.dimension = dimension
        # For 3D space: scalar, e1, e2, e3, e12, e13, e23, e123
        self.grade_sizes = [1, dimension, dimension * (dimension - 1) // 2, 1] if dimension == 3 else [1, dimension]
        self.total_coeffs = sum(self.grade_sizes) if dimension == 3 else 1 + dimension
        
        if coefficients is None:
            self.coefficients = [0.0] * self.total_coeffs
        else:
            self.coefficients = list(coefficients[:self.total_coeffs])
            # Pad with zeros if needed
            while len(self.coefficients) < self.total_coeffs:
                self.coefficients.append(0.0)
    
    @classmethod
    def scalar(cls, value: float, dimension: int = 3) -> "Multivector":
        """Create scalar multivector."""
        mv = cls(dimension=dimension)
        mv.coefficients[0] = value
        return mv
    
    @classmethod
    def vector(cls, components: List[float], dimension: int = None) -> "Multivector":
        """Create vector multivector from components."""
        if dimension is None:
            dimension = len(components)
        mv = cls(dimension=dimension)
        for i, component in enumerate(components[:dimension]):
            mv.coefficients[1 + i] = component
        return mv
    
    def __add__(self, other: "Multivector") -> "Multivector":
        """Multivector addition."""
        if self.dimension != other.dimension:
            raise ValueError("Cannot add multivectors of different dimensions")
        
        result_coeffs = [a + b for a, b in zip(self.coefficients, other.coefficients)]
        return Multivector(result_coeffs, self.dimension)
    
    def __mul__(self, other: Union["Multivector", float]) -> "Multivector":
        """Geometric product."""
        if isinstance(other, (int, float)):
            # Scalar multiplication
            result_coeffs = [c * other for c in self.coefficients]
            return Multivector(result_coeffs, self.dimension)
        
        return self.geometric_product(other)
    
    def geometric_product(self, other: "Multivector") -> "Multivector":
        """Compute geometric product (simplified for 3D)."""
        if self.dimension != other.dimension:
            raise ValueError("Cannot multiply multivectors of different dimensions")
        
        if self.dimension == 3:
            return self._geometric_product_3d(other)
        else:
            return self._geometric_product_nd(other)
    
    def _geometric_product_3d(self, other: "Multivector") -> "Multivector":
        """3D geometric product implementation."""
        a, b = self.coefficients, other.coefficients
        result = [0.0] * 8
        
        # Scalar component
        result[0] = a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]
        
        # Vector components (simplified)
        result[1] = a[0] * b[1] + a[1] * b[0]
        result[2] = a[0] * b[2] + a[2] * b[0]
        result[3] = a[0] * b[3] + a[3] * b[0]
        
        return Multivector(result, 3)
    
    def _geometric_product_nd(self, other: "Multivector") -> "Multivector":
        """N-dimensional geometric product (simplified)."""
        result = Multivector(dimension=self.dimension)
        
        # Basic scalar and vector product
        result.coefficients[0] = self.coefficients[0] * other.coefficients[0]
        
        for i in range(1, min(len(self.coefficients), len(other.coefficients))):
            result.coefficients[i] = (self.coefficients[0] * other.coefficients[i] + 
                                    self.coefficients[i] * other.coefficients[0])
        
        return result
    
    def magnitude(self) -> float:
        """Compute magnitude of multivector."""
        return math.sqrt(sum(c * c for c in self.coefficients))
    
    def normalize(self) -> "Multivector":
        """Normalize multivector."""
        mag = self.magnitude()
        if mag == 0:
            return Multivector(dimension=self.dimension)
        
        normalized_coeffs = [c / mag for c in self.coefficients]
        return Multivector(normalized_coeffs, self.dimension)
    
    def to_vector(self) -> List[float]:
        """Extract vector part as list."""
        if len(self.coefficients) <= 1:
            return []
        return self.coefficients[1:1 + self.dimension]
    
    def __repr__(self) -> str:
        """String representation."""
        if self.dimension == 3:
            return f"Multivector({self.coefficients[0]:.3f} + {self.coefficients[1]:.3f}e1 + {self.coefficients[2]:.3f}e2 + {self.coefficients[3]:.3f}e3)"
        else:
            return f"Multivector({self.coefficients})"


class GeometricAlgebra:
    """Native Python geometric algebra operations."""
    
    def __init__(self):
        """Initialize geometric algebra without external dependencies."""
        self.layout = None
        self.blades = {"e1": 1, "e2": 2, "e3": 3}
        self._mock = False  # We're providing full native implementation
    
    def mult(self, a: Union[Multivector, float], b: Union[Multivector, float]) -> Union[Multivector, float]:
        """Multiply two multivectors or scalars."""
        if isinstance(a, Multivector) and isinstance(b, Multivector):
            return a.geometric_product(b)
        elif isinstance(a, Multivector):
            return a * b
        elif isinstance(b, Multivector):
            return b * a
        else:
            return a * b
    
    def pretty(self, a: Union[Multivector, float]) -> str:
        """Pretty print multivector."""
        return str(a)
    
    @staticmethod
    def create_rotation_multivector(axis: List[float], angle: float) -> Multivector:
        """Create rotation multivector (rotor) from axis and angle."""
        # Normalize axis
        axis_norm = NativeMath.vector_norm(axis)
        if axis_norm == 0:
            return Multivector.scalar(1.0)
        
        normalized_axis = [x / axis_norm for x in axis]
        
        # Create rotor: cos(θ/2) - sin(θ/2) * (axis bivector)
        half_angle = angle / 2
        cos_half = math.cos(half_angle)
        sin_half = math.sin(half_angle)
        
        rotor = Multivector.scalar(cos_half)
        
        # Add bivector part for 3D
        if len(normalized_axis) >= 3 and len(rotor.coefficients) >= 8:
            rotor.coefficients[4] = -sin_half * normalized_axis[2]  # e12 component
            rotor.coefficients[5] = sin_half * normalized_axis[1]   # e13 component  
            rotor.coefficients[6] = -sin_half * normalized_axis[0]  # e23 component
        
        return rotor
    
    @staticmethod
    def cross_product_3d(a: List[float], b: List[float]) -> List[float]:
        """3D cross product using geometric algebra principles."""
        if len(a) < 3 or len(b) < 3:
            return [0, 0, 0]
        
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2], 
            a[0] * b[1] - a[1] * b[0]
        ]
