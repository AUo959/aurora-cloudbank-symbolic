"""
Quantum-Inspired VSA Prototype using Qiskit

This module demonstrates how to generate symbolic vectors using quantum circuits.
"""

import os

import numpy as np

from modules.symbolic_core.vsa import SymbolicVector


def _fallback_symbolic_vector(symbol: str, dim: int) -> np.ndarray:
    """Deterministic fallback vector generator that avoids simulator dependencies."""
    h = hash(symbol) % (2**32)
    rng = np.random.default_rng(h)
    bits = rng.integers(0, 2, size=dim, dtype=np.int8)
    return np.where(bits == 1, 1, -1)


def quantum_symbolic_vector(symbol: str, dim: int = 8) -> np.ndarray:
    """
    Generate a symbolic vector using a quantum circuit seeded by the symbol hash.
    The output is a vector of -1/+1 based on quantum measurement results.
    """
    # Qiskit path is opt-in because Aer can be unstable on some local runtimes
    # (notably legacy Python toolchains). Keep deterministic behavior via fallback.
    if os.getenv("AURORA_ENABLE_QISKIT_VSA", "0") != "1":
        return _fallback_symbolic_vector(symbol, dim)

    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator

        h = hash(symbol) % (2**32)
        np.random.seed(h)
        qc = QuantumCircuit(dim, dim)
        for i in range(dim):
            qc.h(i)
            if np.random.rand() > 0.5:
                qc.x(i)
        qc.measure(range(dim), range(dim))
        backend = AerSimulator()
        result = backend.run(qc, shots=1).result()
        counts = list(result.get_counts().keys())[0]
        return np.array([1 if b == "1" else -1 for b in counts[::-1]])
    except Exception:
        return _fallback_symbolic_vector(symbol, dim)


class QuantumSymbolicVector(SymbolicVector):

    def __init__(self, symbol: str, dim: int = 8):
        vec = quantum_symbolic_vector(symbol, dim)
        super().__init__(symbol=symbol, dim=dim, vector=vec.tolist(), vector_type="bipolar")
        # store numpy array for convenience
        self.vector = vec
