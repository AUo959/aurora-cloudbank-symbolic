from modules.symbolic_core.quantum_vsa import (
    QuantumSymbolicVector,
    quantum_symbolic_vector,
)


def test_quantum_symbolic_vector_shape():
    vec = quantum_symbolic_vector("alpha", dim=8)
    assert isinstance(vec, list)  # Zero-dependency version returns list
    assert len(vec) == 8
    assert set(vec).issubset({-1.0, 1.0})


def test_quantum_symbolic_vector_class():
    qsv = QuantumSymbolicVector("beta", dim=8)
    # Zero-dependency version uses list for vector
    assert isinstance(qsv.vector, list)
    assert len(qsv.vector) == 8
    assert set(qsv.vector).issubset({-1.0, 1.0})
    
    # Test quantum-inspired features
    assert hasattr(qsv, 'quantum_inspired')
    assert qsv.quantum_inspired == True
    
    # Test superposition strength calculation
    strength = qsv.superposition_strength()
    assert isinstance(strength, float)
    assert 0.0 <= strength <= 1.0
