import numpy as np

from modules.symbolic_core.quantum_vsa import QuantumSymbolicVector, quantum_symbolic_vector


def test_quantum_symbolic_vector_shape():
    vec = quantum_symbolic_vector("alpha", dim=8)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (8,)
    assert set(np.unique(vec)).issubset({-1, 1})


def test_quantum_symbolic_vector_class():
    qsv = QuantumSymbolicVector("beta", dim=8)
    # Accept either list or np.ndarray for vector, but check shape and values
    arr = np.array(qsv.vector)
    assert arr.shape == (8,)
    assert set(np.unique(arr)).issubset({-1, 1})
