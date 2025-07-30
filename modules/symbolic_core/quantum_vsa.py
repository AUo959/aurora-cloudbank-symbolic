"""
Quantum-Inspired VSA Prototype using Qiskit

This module demonstrates how to generate symbolic vectors using quantum circuits.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from modules.symbolic_core.vsa import SymbolicVector


def quantum_symbolic_vector(symbol: str, dim: int = 8) -> np.ndarray:
    """
    Generate a symbolic vector using a quantum circuit seeded by the symbol hash.
    The output is a vector of -1/+1 based on quantum measurement results.
    """
    # For demo, use small dim (e.g., 8 qubits)
    h = hash(symbol) % (2**32)
    np.random.seed(h)
    qc = QuantumCircuit(dim, dim)
    for i in range(dim):
        qc.h(i)  # Put each qubit in superposition
        if np.random.rand() > 0.5:
            qc.x(i)  # Flip some qubits based on hash
    qc.measure(range(dim), range(dim))
    backend = AerSimulator()
    result = backend.run(qc, shots=1).result()
    counts = list(result.get_counts().keys())[0]
    # Convert bitstring to -1/+1 vector
    vec = np.array([1 if b == "1" else -1 for b in counts[::-1]])
    return vec


class QuantumSymbolicVector(SymbolicVector):

    def __init__(self, symbol: str, dim: int = 8):
        vec = quantum_symbolic_vector(symbol, dim)
        super().__init__(symbol=symbol, dim=dim, vector=vec.tolist(), vector_type="bipolar")
        # store numpy array for convenience
        self.vector = vec
