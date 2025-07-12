"""
Quantum-Inspired VSA using Native Implementation
Optimized zero-dependency quantum-symbolic vector generation.
"""

import math
import hashlib
from typing import List
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.core.native_quantum import NativeQuantumCircuit, NativeQuantumSimulator
from .vsa import SymbolicVector


def quantum_symbolic_vector(symbol: str, dim: int = 8) -> List[float]:
    """
    Generate a symbolic vector using native quantum circuit seeded by the symbol hash.
    The output is a vector of -1/+1 based on quantum measurement results.
    """
    # Use symbol hash as seed for quantum circuit
    symbol_hash = hashlib.sha256(symbol.encode()).digest()
    seed = int.from_bytes(symbol_hash[:4], "big") % (2**16)
    
    # Ensure dim doesn't exceed quantum capabilities (max 8 qubits = 256 states)
    num_qubits = min(dim, 8)
    
    # Create quantum circuit
    circuit = NativeQuantumCircuit(num_qubits)
    
    # Apply quantum operations based on symbol characteristics
    for i in range(num_qubits):
        if (seed >> i) & 1:
            circuit.h(i)  # Hadamard for superposition
        
        if (seed >> (i + 8)) & 1:
            circuit.ry(math.pi / 4, i)  # Y-rotation
    
    # Add entanglement based on symbol
    for i in range(num_qubits - 1):
        if (seed >> (i + 16)) & 1:
            circuit.cx(i, i + 1)
    
    # Simulate measurement
    simulator = NativeQuantumSimulator()
    result = simulator.run(circuit, shots=1024)
    counts = result.get_counts()
    
    # Convert measurement results to symbolic vector
    vector = []
    if not counts:
        # Fallback to deterministic generation if no measurements
        return [(1.0 if (seed >> i) & 1 else -1.0) for i in range(dim)]
    
    # Use measurement probabilities to generate vector elements
    total_shots = sum(counts.values())
    state_probs = {state: count / total_shots for state, count in counts.items()}
    
    for i in range(dim):
        if i < len(list(state_probs.keys())):
            # Use quantum measurement results
            state_key = list(state_probs.keys())[i % len(state_probs)]
            prob = state_probs[state_key]
            vector.append(1.0 if prob > 0.5 else -1.0)
        else:
            # Extend deterministically for larger dimensions
            vector.append(1.0 if (seed >> i) & 1 else -1.0)
    
    return vector[:dim]


def create_quantum_symbolic_vector(symbol: str, dim: int = 512) -> SymbolicVector:
    """
    Create a SymbolicVector using quantum-inspired generation.
    """
    if dim <= 8:
        # Use quantum generation for small dimensions
        quantum_vec = quantum_symbolic_vector(symbol, dim)
        return SymbolicVector(symbol, dim, quantum_vec, "bipolar")
    else:
        # For larger dimensions, use hybrid approach
        # Generate quantum seed vector
        quantum_seed = quantum_symbolic_vector(symbol, 8)
        
        # Extend using deterministic expansion based on quantum seed
        extended_vector = []
        for i in range(dim):
            # Use quantum seed to influence deterministic generation
            seed_idx = i % len(quantum_seed)
            seed_val = quantum_seed[seed_idx]
            
            # Combine with symbol hash for deterministic expansion
            symbol_hash = hashlib.sha256(f"{symbol}_{i}".encode()).digest()
            hash_val = int.from_bytes(symbol_hash[:4], "big")
            
            # Generate element based on quantum seed and hash
            if seed_val > 0:
                extended_vector.append(1.0 if hash_val & 1 else -1.0)
            else:
                extended_vector.append(-1.0 if hash_val & 1 else 1.0)
        
        return SymbolicVector(symbol, dim, extended_vector, "bipolar")


class QuantumVSAProcessor:
    """Quantum-inspired VSA processor using native implementations"""
    
    def __init__(self, max_qubits: int = 8):
        self.max_qubits = max_qubits
        self.simulator = NativeQuantumSimulator()
    
    def generate_quantum_concept_space(self, concepts: List[str], dim: int = 512) -> List[SymbolicVector]:
        """Generate quantum-inspired concept space"""
        concept_vectors = []
        
        for concept in concepts:
            quantum_vector = create_quantum_symbolic_vector(concept, dim)
            concept_vectors.append(quantum_vector)
        
        return concept_vectors
    
    def quantum_bind_concepts(self, concept1: str, concept2: str, dim: int = 512) -> SymbolicVector:
        """Quantum-inspired binding of two concepts"""
        vec1 = create_quantum_symbolic_vector(concept1, dim)
        vec2 = create_quantum_symbolic_vector(concept2, dim)
        
        # Perform binding operation
        bound_vector = vec1.bind(vec2)
        return bound_vector
    
    def quantum_superpose_concepts(self, concepts: List[str], dim: int = 512) -> SymbolicVector:
        """Quantum-inspired superposition of multiple concepts"""
        if not concepts:
            raise ValueError("At least one concept required")
        
        result_vector = create_quantum_symbolic_vector(concepts[0], dim)
        
        for concept in concepts[1:]:
            concept_vector = create_quantum_symbolic_vector(concept, dim)
            result_vector = result_vector.superpose(concept_vector)
        
        return result_vector


class QuantumSymbolicVector(SymbolicVector):
    """Quantum-inspired symbolic vector using native implementation"""
    
    def __init__(self, symbol: str, dim: int = 8):
        vec = quantum_symbolic_vector(symbol, dim)
        # Call parent constructor
        SymbolicVector.__init__(self, symbol, dim, vec, "bipolar")