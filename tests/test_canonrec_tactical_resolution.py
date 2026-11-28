from __future__ import annotations

import pytest

from simulation.runtime.canonrec_tactical.resolver import (
    CanonRecResolutionError,
    canonical_certainty,
    canonical_json_bytes,
    DIVISION_PROFILES,
    ROLE_PROFILES,
    canonical_record_id,
    classify_role_profile,
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


# Verbatim CanonRec cls_aegis fields (CanonRec@dc629a5). The prose role lists a
# secondary "fleet support" duty; before derivation v1.2 the bare "support"
# logistics rule fired first and binned this battlecruiser as logistics.
AEGIS = {
    "entity_id": "cls_aegis",
    "name": "Aegis-Class",
    "division": "battlecruiser",
    "role": "Frontline combat, planetary defense, fleet support",
    "key_features": [
        "Long-range rail cannons",
        "Modular armor plating",
        "Adaptive energy shielding",
    ],
}


def test_aegis_battlecruiser_is_a_heavy_combatant_not_logistics() -> None:
    derived = derive_capability(AEGIS)
    assert derived["role_profile"] == "heavy_combatant"
    assert derived["role_profile_basis"] == "division"
    assert derived["values"]["firepower"] > derived["values"]["support"]


def test_division_outranks_scoped_doctrine_and_prose_role_words() -> None:
    noisy = derive_capability(AEGIS, "logistics resupply medical repair support")
    assert noisy["role_profile"] == "heavy_combatant"


@pytest.mark.parametrize(
    ("division", "role", "expected"),
    [
        # CanonRec ship-class division tokens with their canon role prose.
        ("battlecruiser", "Frontline combat, planetary defense, fleet support", "heavy_combatant"),
        ("frigate", "Patrol, anti-piracy, high-speed interception, frontier security", "frigate_escort"),
        ("escort_destroyer", "General-purpose fleet escort, screening, interception", "frigate_escort"),
        ("heavy_carrier", "Carrier for fighters, bombers, fleet support units", "carrier"),
        ("logistics", "Fleet resupply, mobile command, battlefield medical support", "logistics_support"),
        ("fleet_bulker", "High-capacity fleet replenishment", "logistics_support"),
        ("stealth_destroyer", "Black-ops, deep-space reconnaissance", "stealth_combatant"),
        ("flagship_command", "Strategic fleet coordination", "flagship"),
        ("defense_platform", "Orbital defense, station-to-surface fire support", "fortress"),
    ],
)
def test_canon_divisions_map_to_hull_profiles(division: str, role: str, expected: str) -> None:
    derived = derive_capability({"division": division, "role": role})
    assert (derived["role_profile"], derived["role_profile_basis"]) == (expected, "division")


def test_division_lookup_normalizes_case_and_separators() -> None:
    assert classify_role_profile({"division": "Escort Destroyer"}, "")[0] == "frigate_escort"
    assert classify_role_profile({"division": "heavy-carrier"}, "")[0] == "carrier"


def test_unmapped_division_falls_back_to_role_text() -> None:
    derived = derive_capability({"division": "raider", "role": "Mobile fortress, command nexus"})
    assert (derived["role_profile"], derived["role_profile_basis"]) == ("fortress", "role_text")


def test_bare_support_in_prose_no_longer_means_logistics() -> None:
    derived = derive_capability({"role": "Heavy cruiser providing fleet support"})
    assert derived["role_profile"] == "heavy_combatant"
    assert derive_capability({"role": "Fleet resupply tender"})["role_profile"] == "logistics_support"


def test_every_division_profile_exists() -> None:
    assert set(DIVISION_PROFILES.values()) <= set(ROLE_PROFILES)
