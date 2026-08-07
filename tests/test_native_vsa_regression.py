"""Regression coverage for the native VSA retrieval path."""

import math

import pytest

from src.aurora_fusion.memory import AuroraMemoryOptimizer
from src.core.native_vsa import NativeSymbolicVector

pytestmark = [pytest.mark.unit, pytest.mark.native, pytest.mark.regression]


VECTOR_TYPES = ("bipolar", "binary", "real")
DISCRETE_DOMAINS = {
    "bipolar": {-1.0, 1.0},
    "binary": {0.0, 1.0},
}


def assert_mode_contract(vector, vector_type, dim):
    assert vector.vector_type == vector_type
    assert vector.dim == dim
    assert len(vector.vector) == dim
    if vector_type in DISCRETE_DOMAINS:
        assert set(vector.vector).issubset(DISCRETE_DOMAINS[vector_type])
    else:
        magnitude = math.sqrt(sum(value * value for value in vector.vector))
        assert math.isclose(magnitude, 1.0)


def test_symbol_hash_expands_across_requested_dimension():
    vector = NativeSymbolicVector.from_symbol("velar_imperium", dim=512)

    blocks = {tuple(vector.vector[offset + index] for index in range(32)) for offset in range(0, vector.dim, 32)}

    assert len(blocks) == 16


@pytest.mark.parametrize("vector_type", VECTOR_TYPES)
def test_nary_bundle_is_order_invariant_and_preserves_mode(vector_type):
    vectors = [
        NativeSymbolicVector.from_symbol(f"symbol-{index}", dim=512, vector_type=vector_type) for index in range(12)
    ]

    forward = NativeSymbolicVector.bundle(vectors)
    reverse = NativeSymbolicVector.bundle(list(reversed(vectors)))

    assert forward.vector == reverse.vector
    assert_mode_contract(forward, vector_type, 512)


@pytest.mark.parametrize("vector_type", VECTOR_TYPES)
def test_pairwise_superposition_is_order_invariant_and_preserves_mode(vector_type):
    left = NativeSymbolicVector.from_symbol("left", dim=64, vector_type=vector_type)
    right = NativeSymbolicVector.from_symbol("right", dim=64, vector_type=vector_type)

    forward = left.superpose(right)
    reverse = right.superpose(left)

    assert forward.vector == reverse.vector
    assert_mode_contract(forward, vector_type, 64)


def test_binary_ties_remain_in_binary_domain():
    left = NativeSymbolicVector("left", 4, [0.0, 1.0, 0.0, 1.0], "binary")
    right = NativeSymbolicVector("right", 4, [1.0, 0.0, 0.0, 1.0], "binary")

    bundle = NativeSymbolicVector.bundle([left, right])
    superposed = left.superpose(right)

    assert_mode_contract(bundle, "binary", 4)
    assert_mode_contract(superposed, "binary", 4)
    assert bundle.vector == NativeSymbolicVector.bundle([right, left]).vector
    assert superposed.vector == right.superpose(left).vector
    assert bundle.vector[2:] == [0.0, 1.0]
    assert superposed.vector[2:] == [0.0, 1.0]


@pytest.mark.parametrize("vector_type", VECTOR_TYPES)
def test_single_vector_bundle_preserves_payload(vector_type):
    original = NativeSymbolicVector.from_symbol("single", dim=64, vector_type=vector_type)

    bundle = NativeSymbolicVector.bundle([original])

    assert bundle.vector == original.vector
    assert bundle.vector is not original.vector
    assert bundle.vector_type == vector_type
    assert bundle.dim == original.dim


def test_empty_bundle_is_rejected():
    with pytest.raises(ValueError, match="At least one vector"):
        NativeSymbolicVector.bundle([])


@pytest.mark.parametrize("vector_type", VECTOR_TYPES)
def test_public_dictionary_round_trip_preserves_mode(vector_type):
    original = NativeSymbolicVector.from_symbol("round-trip", dim=64, vector_type=vector_type)

    restored = NativeSymbolicVector.from_dict(original.to_dict())

    assert restored.symbol == original.symbol
    assert restored.dim == original.dim
    assert restored.vector == original.vector
    assert restored.vector_type == vector_type


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
