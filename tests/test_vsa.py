import pytest
import numpy as np
from modules.symbolic_core.vsa import SymbolicVector, encode_symbol, similarity


def test_symbolic_vector_encoding():
    sv1 = SymbolicVector('alpha')
    sv2 = SymbolicVector('alpha')
    sv3 = SymbolicVector('beta')
    assert np.allclose(sv1.vector, sv2.vector), "Encoding should be deterministic for same symbol."
    assert not np.allclose(sv1.vector, sv3.vector), "Different symbols should have different encodings."


def test_symbolic_vector_similarity():
    sv1 = SymbolicVector('alpha')
    sv2 = SymbolicVector('alpha')
    sv3 = SymbolicVector('beta')
    sim_same = sv1.similarity(sv2)
    sim_diff = sv1.similarity(sv3)
    assert sim_same > sim_diff, "Similarity should be higher for same symbol."


def test_symbolic_vector_bind_superpose():
    sv1 = SymbolicVector('alpha')
    sv2 = SymbolicVector('beta')
    bound = sv1.bind(sv2)
    superposed = sv1.superpose(sv2)
    assert bound.vector.shape == sv1.vector.shape
    assert superposed.vector.shape == sv1.vector.shape


def test_encode_symbol_utility():
    vec = encode_symbol('gamma')
    assert isinstance(vec, np.ndarray)
    assert vec.shape[0] == 512


def test_similarity_utility():
    v1 = encode_symbol('a')
    v2 = encode_symbol('a')
    v3 = encode_symbol('b')
    assert similarity(v1, v2) > similarity(v1, v3)
