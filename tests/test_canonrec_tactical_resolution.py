from __future__ import annotations

import pytest

from simulation.runtime.canonrec_tactical.resolver import (
    CanonRecResolutionError,
    derive_capability,
    derive_doctrine,
    sha256_json,
)


def test_capability_derivation_is_repeatable_and_order_independent() -> None:
    first = {
        "role": "Fast Patrol Frigate",
        "division": "Union Navy",
        "key_features": ["Advanced sensors", "Gravitic maneuver drive", "Point defense"],
    }
    second = {
        "key_features": ["Advanced sensors", "Gravitic maneuver drive", "Point defense"],
        "division": "Union Navy",
        "role": "Fast Patrol Frigate",
    }
    assert derive_capability(first) == derive_capability(second)


def test_scoped_doctrine_materially_changes_applicable_capability() -> None:
    record = {
        "role": "Special Operations Stealth Vessel",
        "division": "Marshal Command",
        "key_features": ["Stealth field", "Advanced sensors"],
    }
    base = derive_capability(record)
    scoped = derive_capability(record, "boarding sabotage pursuit hyperdrive")
    assert scoped["values"] != base["values"]
    assert scoped["values"]["boarding"] > base["values"]["boarding"]


def test_doctrine_derivation_is_deterministic_and_semantically_sensitive() -> None:
    union = derive_doctrine({"name": "Galactic Union", "description": "Federal council diplomacy and defense"})
    machine = derive_doctrine({"name": "Prime Construct", "government_type": "AI consensus", "military_doctrine": "machine precision autonomy"})
    assert union == derive_doctrine({"description": "Federal council diplomacy and defense", "name": "Galactic Union"})
    assert union["values"] != machine["values"]


def test_unknown_role_fails_closed_instead_of_guessing() -> None:
    with pytest.raises(CanonRecResolutionError):
        derive_capability({"role": "Unclassified Experimental Geometry"})


def test_canonical_hash_ignores_mapping_insertion_order() -> None:
    assert sha256_json({"a": 1, "b": {"x": 2, "y": 3}}) == sha256_json({"b": {"y": 3, "x": 2}, "a": 1})
