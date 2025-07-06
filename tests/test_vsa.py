import numpy as np
import pytest

from modules.symbolic_core.vsa import SymbolicVector, encode_symbol, similarity


def test_symbolic_vector_encoding():
    sv1 = SymbolicVector.from_symbol("alpha")
    sv2 = SymbolicVector.from_symbol("alpha")
    sv3 = SymbolicVector.from_symbol("beta")
    assert np.allclose(
        sv1.vector, sv2.vector
    ), "Encoding should be deterministic for same symbol."
    assert not np.allclose(
        sv1.vector, sv3.vector
    ), "Different symbols should have different encodings."


def test_symbolic_vector_similarity():
    sv1 = SymbolicVector.from_symbol("alpha")
    sv2 = SymbolicVector.from_symbol("alpha")
    sv3 = SymbolicVector.from_symbol("beta")
    sim_same = similarity(sv1.vector, sv2.vector)
    sim_diff = similarity(sv1.vector, sv3.vector)
    assert sim_same > sim_diff, "Similarity should be higher for same symbol."


def test_symbolic_vector_bind_superpose():
    sv1 = SymbolicVector.from_symbol("alpha")
    sv2 = SymbolicVector.from_symbol("beta")
    # For bind and superpose, just check vector shape and type
    bound = np.multiply(sv1.vector, sv2.vector)
    superposed = np.sign(np.add(sv1.vector, sv2.vector))
    assert np.array(bound).shape == np.array(sv1.vector).shape
    assert np.array(superposed).shape == np.array(sv1.vector).shape


def test_encode_symbol_utility():
    vec = encode_symbol("gamma")
    assert isinstance(vec, list)
    assert len(vec) == 512


def test_similarity_utility():
    v1 = encode_symbol("a")
    v2 = encode_symbol("a")
    v3 = encode_symbol("b")
    assert similarity(np.array(v1), np.array(v2)) > similarity(
        np.array(v1), np.array(v3)
    )


def test_symbolicvector_pydantic_validation():
    # Valid vector
    sv = SymbolicVector(symbol="test", dim=4, vector=[-1, 1, -1, 1])
    assert sv.symbol == "test"
    # Invalid vector length
    with pytest.raises(ValueError):
        SymbolicVector(symbol="fail", dim=3, vector=[-1, 1])
    # Serialization roundtrip
    data = sv.to_json()
    sv2 = SymbolicVector.from_json(data)
    assert sv2 == sv
    # Flexible vector types
    sv_bin = SymbolicVector.from_symbol("bin", dim=4, vector_type="binary")
    assert set(sv_bin.vector).issubset({0, 1})
    sv_real = SymbolicVector.from_symbol("real", dim=4, vector_type="real")
    import numpy as np

    assert all(
        isinstance(x, float) or isinstance(x, np.floating) for x in sv_real.vector
    )
