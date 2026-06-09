"""
Quantum State Representation

Classes for representing and manipulating quantum states.

Supports pure states (state vectors) and mixed states (density matrices).
Mixed-state operations (measure, entropy, fidelity_with) use standard
density-matrix formulations:
  - Measurement: diagonal elements of ρ in the computational basis
  - Von Neumann entropy: -Tr(ρ log₂ ρ) via spectral decomposition
  - Fidelity: F(ρ₁,ρ₂) = Tr(√(√ρ₁ ρ₂ √ρ₁))²

Anchor: T1-QSS-001
"""

import math
from typing import Dict, List, Optional, Tuple

import numpy as np


def _matrix_sqrt(matrix: np.ndarray) -> np.ndarray:
    """Compute the matrix square root of a Hermitian positive-semidefinite matrix."""
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    sqrt_eigs = np.sqrt(np.maximum(eigenvalues.real, 0.0))
    return (eigenvectors * sqrt_eigs) @ eigenvectors.conj().T


class StateVector:
    """
    Quantum state vector representation.

    Represents a pure quantum state as a complex vector in Hilbert space.
    """

    def __init__(self, amplitudes: List[complex], basis_labels: Optional[List[str]] = None):
        """
        Initialize state vector.

        Args:
            amplitudes: Complex amplitudes for each basis state
            basis_labels: Optional labels for basis states (e.g., "|00⟩", "|01⟩")

        Raises:
            ValueError: If state vector is not properly normalized
        """
        self.amplitudes = np.array(amplitudes, dtype=complex)
        self.num_qubits = int(math.log2(len(amplitudes)))

        if 2**self.num_qubits != len(amplitudes):
            raise ValueError(
                f"Number of amplitudes ({len(amplitudes)}) must be power of 2"
            )

        # Check normalization
        norm_sq = np.sum(np.abs(self.amplitudes) ** 2)
        if not (0.99 <= norm_sq <= 1.01):
            raise ValueError(f"State vector not normalized: norm² = {norm_sq}")

        # Generate or validate basis labels
        if basis_labels is None:
            self.basis_labels = self._generate_basis_labels()
        else:
            if len(basis_labels) != len(amplitudes):
                raise ValueError("Number of basis labels must match amplitudes")
            self.basis_labels = basis_labels

    def _generate_basis_labels(self) -> List[str]:
        """Generate computational basis labels."""
        return [f"|{bin(i)[2:].zfill(self.num_qubits)}⟩" for i in range(len(self.amplitudes))]

    def probabilities(self) -> Dict[str, float]:
        """Get measurement probabilities for each basis state."""
        probs = np.abs(self.amplitudes) ** 2
        return {label: float(prob) for label, prob in zip(self.basis_labels, probs)}

    def measure(self, num_shots: int = 1000, seed: Optional[int] = None) -> Dict[str, int]:
        """
        Simulate measurement of the state.

        Args:
            num_shots: Number of measurements to perform
            seed: Random seed for reproducibility

        Returns:
            Dictionary mapping basis states to counts
        """
        if seed is not None:
            np.random.seed(seed)

        probs = np.abs(self.amplitudes) ** 2
        indices = np.random.choice(len(probs), size=num_shots, p=probs)

        counts = {}
        for idx in indices:
            label = self.basis_labels[idx]
            counts[label] = counts.get(label, 0) + 1

        return counts

    def entropy(self) -> float:
        """Calculate Von Neumann entropy of the state."""
        probs = np.abs(self.amplitudes) ** 2
        # Filter out zero probabilities to avoid log(0)
        probs_nonzero = probs[probs > 1e-10]
        return float(-np.sum(probs_nonzero * np.log2(probs_nonzero)))

    def fidelity(self, other: "StateVector") -> float:
        """
        Calculate fidelity with another state.

        Args:
            other: Another state vector

        Returns:
            Fidelity (0.0 to 1.0)
        """
        if len(self.amplitudes) != len(other.amplitudes):
            raise ValueError("States must have same dimension")

        # Fidelity = |⟨ψ|φ⟩|²
        overlap = np.abs(np.vdot(self.amplitudes, other.amplitudes))
        return float(overlap**2)

    def __repr__(self) -> str:
        """String representation."""
        terms = []
        for amp, label in zip(self.amplitudes, self.basis_labels):
            if abs(amp) > 1e-6:  # Only show significant terms
                terms.append(f"{amp:.3f}{label}")
        return " + ".join(terms)


class QuantumState:
    """
    General quantum state representation.

    Can represent pure states (state vectors) or mixed states (density matrices).
    """

    def __init__(self, state_vector: Optional[StateVector] = None, num_qubits: Optional[int] = None):
        """
        Initialize quantum state.

        Args:
            state_vector: Optional state vector (for pure states)
            num_qubits: Number of qubits (if creating from scratch)
        """
        self._density_matrix: Optional[np.ndarray] = None

        if state_vector is not None:
            self.state_vector = state_vector
            self.num_qubits = state_vector.num_qubits
            self.is_pure = True
        elif num_qubits is not None:
            # Initialize to |0⟩^⊗n (all qubits in |0⟩)
            dim = 2**num_qubits
            amplitudes = np.zeros(dim, dtype=complex)
            amplitudes[0] = 1.0 + 0j
            self.state_vector = StateVector(amplitudes.tolist())
            self.num_qubits = num_qubits
            self.is_pure = True
        else:
            raise ValueError("Must provide either state_vector or num_qubits")

    @classmethod
    def from_computational_basis(cls, bitstring: str) -> "QuantumState":
        """
        Create state from computational basis string.

        Args:
            bitstring: Binary string (e.g., "101" for |101⟩)

        Returns:
            QuantumState in specified computational basis state
        """
        num_qubits = len(bitstring)
        dim = 2**num_qubits
        amplitudes = np.zeros(dim, dtype=complex)

        # Convert bitstring to index
        index = int(bitstring, 2)
        amplitudes[index] = 1.0 + 0j

        state_vector = StateVector(amplitudes.tolist())
        return cls(state_vector=state_vector)

    @classmethod
    def hadamard_state(cls, num_qubits: int) -> "QuantumState":
        """
        Create uniform superposition state (Hadamard on all qubits).

        Args:
            num_qubits: Number of qubits

        Returns:
            QuantumState in uniform superposition
        """
        dim = 2**num_qubits
        amplitude = (1.0 / math.sqrt(dim)) + 0j
        amplitudes = [amplitude] * dim

        state_vector = StateVector(amplitudes)
        return cls(state_vector=state_vector)

    @classmethod
    def bell_state(cls, bell_type: str = "phi_plus") -> "QuantumState":
        """
        Create Bell state (maximally entangled 2-qubit state).

        Args:
            bell_type: Type of Bell state (phi_plus, phi_minus, psi_plus, psi_minus)

        Returns:
            QuantumState representing Bell state
        """
        sqrt_half = 1.0 / math.sqrt(2)

        bell_states = {
            "phi_plus": [sqrt_half, 0, 0, sqrt_half],  # (|00⟩ + |11⟩)/√2
            "phi_minus": [sqrt_half, 0, 0, -sqrt_half],  # (|00⟩ - |11⟩)/√2
            "psi_plus": [0, sqrt_half, sqrt_half, 0],  # (|01⟩ + |10⟩)/√2
            "psi_minus": [0, sqrt_half, -sqrt_half, 0],  # (|01⟩ - |10⟩)/√2
        }

        if bell_type not in bell_states:
            raise ValueError(f"Unknown Bell state type: {bell_type}")

        amplitudes = [amp + 0j for amp in bell_states[bell_type]]
        state_vector = StateVector(amplitudes)
        return cls(state_vector=state_vector)

    @classmethod
    def from_density_matrix(cls, matrix: np.ndarray) -> "QuantumState":
        """
        Create a mixed (or pure) state from a density matrix.

        Args:
            matrix: Square complex ndarray of shape (2^n, 2^n) representing ρ.
                    Must be Hermitian, positive-semidefinite, and trace-1.

        Returns:
            QuantumState backed by the density matrix.

        Raises:
            ValueError: If the matrix dimensions are invalid or not power-of-2.
        """
        matrix = np.array(matrix, dtype=complex)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Density matrix must be a square 2-D array")
        dim = matrix.shape[0]
        num_qubits = int(math.log2(dim))
        if 2**num_qubits != dim:
            raise ValueError(f"Density matrix dimension ({dim}) must be a power of 2")

        obj = cls.__new__(cls)
        obj.num_qubits = num_qubits
        obj.state_vector = None  # type: ignore[assignment]
        obj._density_matrix = matrix.copy()

        # Determine whether the state is actually pure: Tr(ρ²) ≈ 1
        purity = float(np.real(np.trace(matrix @ matrix)))
        obj.is_pure = abs(purity - 1.0) < 1e-6

        return obj

    @classmethod
    def from_pure_ensemble(
        cls,
        ensemble: List[Tuple["QuantumState", float]],
    ) -> "QuantumState":
        """
        Create a mixed state from a probabilistic ensemble of pure states.

        ρ = Σᵢ pᵢ |ψᵢ⟩⟨ψᵢ|

        Args:
            ensemble: List of (pure_state, probability) pairs. Probabilities
                      must sum to 1 (within 1e-6 tolerance).

        Returns:
            QuantumState representing the mixed state.

        Raises:
            ValueError: If probabilities don't sum to 1 or states have different dimensions.
        """
        if not ensemble:
            raise ValueError("Ensemble must be non-empty")

        total_prob = sum(p for _, p in ensemble)
        if abs(total_prob - 1.0) > 1e-6:
            raise ValueError(f"Ensemble probabilities must sum to 1 (got {total_prob})")

        num_qubits = ensemble[0][0].num_qubits
        dim = 2**num_qubits
        rho = np.zeros((dim, dim), dtype=complex)

        for state, prob in ensemble:
            if state.num_qubits != num_qubits:
                raise ValueError("All states in ensemble must have the same number of qubits")
            psi = state.density_matrix
            rho += prob * psi

        return cls.from_density_matrix(rho)

    @property
    def density_matrix(self) -> np.ndarray:
        """
        Return the density matrix ρ for this state.

        For pure states: ρ = |ψ⟩⟨ψ|
        For mixed states: the stored density matrix.
        """
        if self._density_matrix is not None:
            return self._density_matrix
        # Pure state: compute ρ = |ψ⟩⟨ψ| on the fly
        psi = self.state_vector.amplitudes
        return np.outer(psi, psi.conj())

    def apply_gate(self, gate_name: str, target_qubits: List[int]) -> "QuantumState":
        """
        Apply quantum gate to specified qubits.

        Args:
            gate_name: Name of gate (X, Y, Z, H, CNOT, etc.)
            target_qubits: Qubit indices to apply gate to

        Returns:
            New QuantumState after gate application

        Note: This is a simplified implementation. Full quantum gates
        would require proper tensor product algebra.
        """
        # For now, return self (gates not fully implemented in mock)
        # In production, this would apply the actual gate matrix
        return self

    def measure(
        self, num_shots: int = 1000, seed: Optional[int] = None
    ) -> Tuple[Dict[str, int], Dict[str, float]]:
        """
        Measure the quantum state in the computational basis.

        For pure states: uses the state-vector amplitude approach.
        For mixed states: probabilities are the diagonal elements ρ[k,k],
        i.e. ⟨k|ρ|k⟩ for each computational basis state |k⟩.

        Args:
            num_shots: Number of measurements
            seed: Random seed for reproducibility

        Returns:
            Tuple of (counts, probabilities)
        """
        if self.is_pure:
            counts = self.state_vector.measure(num_shots=num_shots, seed=seed)
            probabilities = self.state_vector.probabilities()
            return counts, probabilities

        # Mixed state: diagonal elements of ρ are the measurement probabilities
        dim = 2**self.num_qubits
        basis_labels = [f"|{bin(i)[2:].zfill(self.num_qubits)}⟩" for i in range(dim)]
        probs = np.real(np.diagonal(self._density_matrix))
        probs = np.maximum(probs, 0.0)
        probs /= probs.sum()  # renormalize against floating-point drift

        if seed is not None:
            np.random.seed(seed)

        indices = np.random.choice(dim, size=num_shots, p=probs)
        counts: Dict[str, int] = {}
        for idx in indices:
            label = basis_labels[idx]
            counts[label] = counts.get(label, 0) + 1

        probabilities = {label: float(p) for label, p in zip(basis_labels, probs)}
        return counts, probabilities

    def entropy(self) -> float:
        """
        Calculate Von Neumann entropy of the state.

        For pure states backed by a state vector: delegates to StateVector.entropy().
        For all other cases (mixed or pure-but-density-matrix-backed):
        S(ρ) = -Tr(ρ log₂ ρ) = -Σᵢ λᵢ log₂(λᵢ) where λᵢ are eigenvalues of ρ.
        """
        if self.is_pure and self.state_vector is not None:
            return self.state_vector.entropy()

        eigenvalues = np.linalg.eigvalsh(self.density_matrix)
        eigenvalues = np.maximum(eigenvalues.real, 0.0)
        nonzero = eigenvalues[eigenvalues > 1e-12]
        return float(-np.sum(nonzero * np.log2(nonzero)))

    def fidelity_with(self, other: "QuantumState") -> float:
        """
        Calculate fidelity with another state.

        Pure–pure:   F = |⟨ψ₁|ψ₂⟩|²
        Pure–mixed or mixed–mixed:
                     F = Tr(√(√ρ₁ ρ₂ √ρ₁))²

        Args:
            other: Another quantum state

        Returns:
            Fidelity in [0.0, 1.0]
        """
        if self.is_pure and other.is_pure:
            return self.state_vector.fidelity(other.state_vector)

        rho1 = self.density_matrix
        rho2 = other.density_matrix
        sqrt_rho1 = _matrix_sqrt(rho1)
        inner = sqrt_rho1 @ rho2 @ sqrt_rho1
        sqrt_inner = _matrix_sqrt(inner)
        return float(max(0.0, np.real(np.trace(sqrt_inner))) ** 2)

    def __repr__(self) -> str:
        """String representation."""
        if self.is_pure and self.state_vector is not None:
            return f"QuantumState({self.num_qubits} qubits, pure): {self.state_vector}"
        kind = "pure (density matrix)" if self.is_pure else "mixed"
        return f"QuantumState({self.num_qubits} qubits, {kind})"


def create_ghz_state(num_qubits: int) -> QuantumState:
    """
    Create GHZ (Greenberger-Horne-Zeilinger) state.

    GHZ state: (|000...0⟩ + |111...1⟩) / √2

    Args:
        num_qubits: Number of qubits

    Returns:
        QuantumState representing GHZ state
    """
    dim = 2**num_qubits
    amplitudes = np.zeros(dim, dtype=complex)

    sqrt_half = 1.0 / math.sqrt(2)
    amplitudes[0] = sqrt_half + 0j  # |000...0⟩
    amplitudes[-1] = sqrt_half + 0j  # |111...1⟩

    state_vector = StateVector(amplitudes.tolist())
    return QuantumState(state_vector=state_vector)


def create_w_state(num_qubits: int) -> QuantumState:
    """
    Create W state (symmetric superposition with one |1⟩).

    W state: (|100...0⟩ + |010...0⟩ + ... + |000...1⟩) / √n

    Args:
        num_qubits: Number of qubits

    Returns:
        QuantumState representing W state
    """
    dim = 2**num_qubits
    amplitudes = np.zeros(dim, dtype=complex)

    # Amplitude for each basis state with exactly one |1⟩
    amplitude = (1.0 / math.sqrt(num_qubits)) + 0j

    # Set amplitudes for |100...0⟩, |010...0⟩, etc.
    for i in range(num_qubits):
        index = 2 ** (num_qubits - 1 - i)
        amplitudes[index] = amplitude

    state_vector = StateVector(amplitudes.tolist())
    return QuantumState(state_vector=state_vector)
