from __future__ import annotations

import pytest

from simulation.runtime.canonrec_tactical.resolver import (
    CanonRecResolutionError,
    canonical_certainty,
    canonical_json_bytes,
    canonical_record_id,
    derive_capability,
    derive_doctrine,
    normalize_seed64,
    sha256_json,
    term_matches,
)


def test_capability_derivation_is_repeatable_and_order_independent() -> None:
    first = {
        "role": "Fast Patrol Frigate",
        "division": "Union Navy",
        "key_features": [
            "Advanced sensors",
            "Gravitic maneuver drive",
            "Point defense",
        ],
    }
    second = {
        "key_features": [
            "Advanced sensors",
            "Gravitic maneuver drive",
            "Point defense",
        ],
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
    union = derive_doctrine(
        {
            "name": "Galactic Union",
            "government": {
                "form": "Federal democracy",
                "principle": "planetary autonomy",
            },
        }
    )
    machine = derive_doctrine(
        {
            "name": "Prime Construct",
            "org_type": "sovereign_ai_polity",
            "nature": "network of AI consciousnesses",
        }
    )
    assert union == derive_doctrine(
        {
            "government": {
                "principle": "planetary autonomy",
                "form": "Federal democracy",
            },
            "name": "Galactic Union",
        }
    )
    assert union["values"] != machine["values"]


def test_unknown_role_fails_closed_instead_of_guessing() -> None:
    with pytest.raises(CanonRecResolutionError):
        derive_capability({"role": "Unclassified Experimental Geometry"})


def test_boundary_matching_does_not_fire_on_substrings() -> None:
    assert not term_matches("rail cannon", "ai")
    assert not term_matches("decentralized fleet", "central")
    assert term_matches("AI-assisted targeting", "ai assisted")
    assert term_matches("central command", "central")


def test_current_canonrec_schema_identity_and_certainty_are_supported() -> None:
    record = {
        "entity_id": "cls_peregrine",
        "certainty": "CANON",
        "status": "active",
    }
    assert canonical_record_id(record) == "cls_peregrine"
    assert canonical_certainty(record) == "CANON"


def test_lifecycle_status_is_not_misread_as_canonical_status() -> None:
    assert canonical_certainty({"status": "active"}) == ""


def test_canonical_hash_ignores_mapping_insertion_order() -> None:
    assert sha256_json({"a": 1, "b": {"x": 2, "y": 3}}) == sha256_json(
        {"b": {"y": 3, "x": 2}, "a": 1}
    )


def test_canonical_json_rejects_non_finite_numbers() -> None:
    with pytest.raises(ValueError):
        canonical_json_bytes({"bad": float("nan")})


def test_seed64_encoding_is_lossless_for_json_consumers() -> None:
    assert normalize_seed64(0) == "0x0000000000000000"
    assert normalize_seed64(2**64 - 1) == "0xffffffffffffffff"
    assert normalize_seed64("18446744073709551615") == "0xffffffffffffffff"
    assert normalize_seed64("0xffffffffffffffff") == "0xffffffffffffffff"
    with pytest.raises(CanonRecResolutionError):
        normalize_seed64(2**64)
