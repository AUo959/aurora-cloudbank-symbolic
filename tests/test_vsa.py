from modules.symbolic_core.vsa import SymbolicVector, encode_symbol, similarity


def test_symbolic_vector_encoding():
    sv1 = SymbolicVector.from_symbol("alpha")
    sv2 = SymbolicVector.from_symbol("alpha")
    sv3 = SymbolicVector.from_symbol("beta")
    
    # Check vectors are lists of expected length
    assert isinstance(sv1.vector, list) and len(sv1.vector) == 512
    
    # Deterministic encoding should produce same vectors for same symbols
    assert sv1.vector == sv2.vector, "Encoding should be deterministic for same symbol."
    assert sv1.vector != sv3.vector, "Different symbols should have different encodings."


def test_symbolic_vector_similarity():
    sv1 = SymbolicVector.from_symbol("alpha")
    sv2 = SymbolicVector.from_symbol("alpha")
    sv3 = SymbolicVector.from_symbol("beta")
    
    # Use the SymbolicVector similarity method (zero-dependency)
    sim_same = sv1.similarity(sv2)
    sim_diff = sv1.similarity(sv3)
    assert sim_same > sim_diff, "Similarity should be higher for same symbol."


def test_symbolic_vector_bind_superpose():
    sv1 = SymbolicVector.from_symbol("alpha")
    sv2 = SymbolicVector.from_symbol("beta")
    
    # Test bind operation
    bound = sv1.bind(sv2)
    assert isinstance(bound.vector, list)
    assert len(bound.vector) == len(sv1.vector)
    
    # Test superpose operation  
    superposed = sv1.superpose(sv2)
    assert isinstance(superposed.vector, list)
    assert len(superposed.vector) == len(sv1.vector)


def test_encode_symbol_utility():
    vec = encode_symbol("gamma")
    assert isinstance(vec, list)
    assert len(vec) == 512


def test_similarity_utility():
    v1 = encode_symbol("a")
    v2 = encode_symbol("a")
    v3 = encode_symbol("b")
    # Use zero-dependency similarity function
    assert similarity(v1, v2) > similarity(v1, v3)


def test_symbolicvector_pydantic_validation():
    # Valid vector
    sv = SymbolicVector(symbol="test", dim=4, vector=[-1, 1, -1, 1])
    assert sv.symbol == "test"
    # Invalid vector length
    try:
        SymbolicVector(symbol="fail", dim=3, vector=[-1, 1])
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    # Serialization roundtrip
    data = sv.to_json()
    sv2 = SymbolicVector.from_json(data)
    assert sv2 == sv
    
    # Flexible vector types
    sv_bin = SymbolicVector.from_symbol("bin", dim=4, vector_type="binary")
    assert set(sv_bin.vector).issubset({0.0, 1.0})
    
    sv_real = SymbolicVector.from_symbol("real", dim=4, vector_type="real")
    assert all(isinstance(x, float) for x in sv_real.vector)
