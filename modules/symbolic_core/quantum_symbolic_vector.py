#!/usr/bin/env python3
"""Quantum Symbolic Vector - Quantum-enhanced vector operations.

This module provides the QuantumSymbolicVector class for quantum-enhanced
symbolic vector operations in the Aurora CloudBank Symbolic system.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


class QuantumSymbolicVector:
    """Quantum-enhanced symbolic vector with VSA (Vector Symbolic Architecture) operations.

    Combines quantum-inspired processing with traditional vector symbolic architectures
    for high-dimensional symbolic computing.
    """

    def __init__(
        self,
        dimension: int = 10000,
        data: Optional[Union[List[float], np.ndarray]] = None,
        quantum_state: str = "superposition",
        coherence: float = 1.0,
    ):
        """Initialize a quantum symbolic vector.

        Args:
            dimension: Vector dimensionality (default: 10000 for VSA)
            data: Optional initial data (random if not provided)
            quantum_state: Quantum processing state ('superposition', 'entangled', 'coherent')
            coherence: Quantum coherence factor (0.0 to 1.0)
        """
        self.dimension = dimension
        self.quantum_state = quantum_state
        self.coherence = max(0.0, min(1.0, coherence))

        # Initialize vector data
        if data is not None:
            if isinstance(data, list):
                self.data = np.array(data, dtype=np.float32)
            else:
                self.data = np.array(data, dtype=np.float32)

            # Ensure dimension matches
            if len(self.data) != dimension:
                logger.warning(f"Data length {len(self.data)} doesn't match dimension {dimension}, resizing")
                if len(self.data) < dimension:
                    # Pad with zeros
                    self.data = np.pad(self.data, (0, dimension - len(self.data)), mode='constant')
                else:
                    # Truncate
                    self.data = self.data[:dimension]
        else:
            # Random initialization with quantum noise
            self.data = self._generate_quantum_vector()

        # Normalize
        self._normalize()

        logger.debug(
            f"QuantumSymbolicVector initialized: dim={dimension}, "
            f"state={quantum_state}, coherence={coherence}"
        )

    def _generate_quantum_vector(self) -> np.ndarray:
        """Generate a quantum-enhanced random vector.

        Returns:
            Random vector with quantum-inspired noise characteristics
        """
        # Use normal distribution scaled by coherence
        base_vector = np.random.randn(self.dimension).astype(np.float32)

        # Add quantum noise (uniform distribution)
        quantum_noise = np.random.uniform(-1, 1, self.dimension).astype(np.float32)

        # Combine with coherence weighting
        vector = (self.coherence * base_vector + (1 - self.coherence) * quantum_noise)

        return vector

    def _normalize(self):
        """Normalize the vector to unit length."""
        norm = np.linalg.norm(self.data)
        if norm > 1e-10:  # Avoid division by zero
            self.data = self.data / norm

    def bind(self, other: QuantumSymbolicVector) -> QuantumSymbolicVector:
        """VSA binding operation (element-wise multiplication).

        Args:
            other: Another quantum symbolic vector

        Returns:
            New vector representing the binding
        """
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} vs {other.dimension}")

        bound_data = self.data * other.data

        return QuantumSymbolicVector(
            dimension=self.dimension,
            data=bound_data,
            quantum_state=self._merge_quantum_state(other),
            coherence=(self.coherence + other.coherence) / 2,
        )

    def bundle(self, other: QuantumSymbolicVector) -> QuantumSymbolicVector:
        """VSA bundling operation (element-wise addition + normalization).

        Args:
            other: Another quantum symbolic vector

        Returns:
            New vector representing the bundle
        """
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} vs {other.dimension}")

        bundled_data = self.data + other.data

        return QuantumSymbolicVector(
            dimension=self.dimension,
            data=bundled_data,
            quantum_state=self._merge_quantum_state(other),
            coherence=(self.coherence + other.coherence) / 2,
        )

    def permute(self, shift: int = 1) -> QuantumSymbolicVector:
        """VSA permutation operation (circular shift).

        Args:
            shift: Number of positions to shift (default: 1)

        Returns:
            New permuted vector
        """
        permuted_data = np.roll(self.data, shift)

        return QuantumSymbolicVector(
            dimension=self.dimension,
            data=permuted_data,
            quantum_state=self.quantum_state,
            coherence=self.coherence,
        )

    def similarity(self, other: QuantumSymbolicVector) -> float:
        """Calculate similarity (cosine distance) with another vector.

        Args:
            other: Another quantum symbolic vector

        Returns:
            Similarity score between -1 and 1
        """
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} vs {other.dimension}")

        return float(np.dot(self.data, other.data))

    def _merge_quantum_state(self, other: QuantumSymbolicVector) -> str:
        """Merge quantum states from two vectors.

        Args:
            other: Another quantum symbolic vector

        Returns:
            Merged quantum state string
        """
        if self.quantum_state == other.quantum_state:
            return self.quantum_state

        # State hierarchy: superposition > entangled > coherent
        states = {self.quantum_state, other.quantum_state}

        if "superposition" in states:
            return "superposition"
        elif "entangled" in states:
            return "entangled"
        else:
            return "coherent"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with vector metadata and (optionally) data
        """
        return {
            "dimension": self.dimension,
            "quantum_state": self.quantum_state,
            "coherence": self.coherence,
            "norm": float(np.linalg.norm(self.data)),
            "mean": float(np.mean(self.data)),
            "std": float(np.std(self.data)),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"QuantumSymbolicVector(dim={self.dimension}, "
            f"state={self.quantum_state}, coherence={self.coherence:.3f})"
        )
