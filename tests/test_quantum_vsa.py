import numpy as np
from modules.symbolic_core.quantum_vsa import quantum_symbolic_vector, QuantumSymbolicVector


def test_quantum_symbolic_vector_shape():
    vec = quantum_symbolic_vector('alpha', dim=8)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (8,)
    assert set(np.unique(vec)).issubset({-1, 1})


def test_quantum_symbolic_vector_class():
    qsv = QuantumSymbolicVector('beta', dim=8)
    assert isinstance(qsv.vector, np.ndarray)
    assert qsv.vector.shape == (8,)
    assert set(np.unique(qsv.vector)).issubset({-1, 1})
