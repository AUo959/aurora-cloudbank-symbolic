"""
Aurora CloudBank - Quantum Processing Layer
Lightweight quantum computation integration (zero dependencies)
"""

import math
from ..core.native_quantum import NativeQuantumProcessingLayer


class QuantumProcessingLayer:
    """Legacy compatibility wrapper for native quantum processing"""
    
    def __init__(self, num_qubits=8):
        self.num_qubits = num_qubits
        self.native_processor = NativeQuantumProcessingLayer(num_qubits)
        self.quantum_circuits = {}

    def create_quantum_circuit(self, circuit_name, operations):
        """Create quantum circuit for symbolic processing"""
        circuit = self.native_processor.create_quantum_circuit(circuit_name, operations)
        self.quantum_circuits[circuit_name] = circuit
        return circuit

    def apply_quantum_operation(self, circuit, operation):
        """Apply quantum operations for symbolic processing"""
        # This method is now handled internally by native processor
        self.native_processor._apply_quantum_operation(circuit, operation)

    def execute_quantum_symbolic_computation(self, circuit_name, shots=1024):
        """Execute quantum computation for symbolic processing"""
        return self.native_processor.execute_quantum_symbolic_computation(circuit_name, shots)

    def interpret_quantum_results(self, counts):
        """Interpret quantum results for symbolic processing"""
        return self.native_processor._interpret_quantum_results(counts)

    def calculate_entropy(self, counts):
        """Calculate quantum entropy for symbolic analysis"""
        total = sum(counts.values())
        if total == 0:
            return 0.0
        probabilities = [count / total for count in counts.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)
        return entropy

    def extract_symbolic_patterns(self, counts):
        """Extract symbolic patterns from quantum measurements"""
        return self.native_processor._extract_symbolic_patterns(counts)

    def generate_hybrid_output(self, counts):
        """Generate hybrid quantum-symbolic output"""
        return self.native_processor._generate_hybrid_output(counts)
