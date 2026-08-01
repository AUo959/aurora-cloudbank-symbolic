"""Regression coverage for the native VSA retrieval path."""

from src.aurora_fusion.memory import AuroraMemoryOptimizer
from src.core.native_vsa import NativeSymbolicVector


def test_symbol_hash_expands_across_requested_dimension():
    vector = NativeSymbolicVector.from_symbol("velar_imperium", dim=512)

    blocks = {tuple(vector.vector[offset + index] for index in range(32)) for offset in range(0, vector.dim, 32)}

    assert len(blocks) == 16


def test_nary_bundle_is_order_invariant_and_bipolar():
    vectors = [NativeSymbolicVector.from_symbol(f"symbol-{index}", dim=512) for index in range(12)]

    forward = NativeSymbolicVector.bundle(vectors)
    reverse = NativeSymbolicVector.bundle(list(reversed(vectors)))

    assert forward.vector == reverse.vector
    assert all(value in {-1.0, 1.0} for value in forward.vector)


def test_twelve_symbol_bundle_retains_every_constituent():
    members = [NativeSymbolicVector.from_symbol(f"member-{index}", dim=512) for index in range(12)]
    distractors = [NativeSymbolicVector.from_symbol(f"distractor-{index}", dim=512) for index in range(50)]

    bundle = NativeSymbolicVector.bundle(members)

    assert min(bundle.similarity(member) for member in members) > max(
        bundle.similarity(distractor) for distractor in distractors
    )


def test_memory_composition_uses_order_invariant_bundle():
    optimizer = AuroraMemoryOptimizer(symbolic_dim=512)
    symbols = [f"memory-{index}" for index in range(12)]

    forward = optimizer._compose_vector(symbols, [], [])
    reverse = optimizer._compose_vector(list(reversed(symbols)), [], [])

    assert forward.vector == reverse.vector
