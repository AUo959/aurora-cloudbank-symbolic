from __future__ import annotations

from simulation.runtime.gumas_command_policy.policy import (
    _source_identity as command_source,
)
from simulation.runtime.gumas_damage_disposition import step_phase7_state
from simulation.runtime.gumas_damage_disposition.kernel import (
    _readiness_after_hull_loss,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as movement_hash_without_field,
    _source_identity as movement_source,
)
from simulation.runtime.gumas_sensing_weapons.kernel import (
    sha256_canonical,
    step_phase6_state,
)


def _command(fleet_id: str) -> dict:
    receipt = {
        "schema": "aurora://simulation/gumas/command_decision_receipt/v1.0",
        "policy_id": "GUMAS_COMMAND_POLICY_v1_0",
        "policy_version": "1.0.0",
        "policy_source_sha256": command_source()["bundle_sha256"],
        "fleet_id": fleet_id,
        "orders": {
            "strategic_posture": "PRESS",
            "specialist_intents": {
                "tactical": "MAX_EFFECT_FIRE",
                "ew_sensors": "PASSIVE_TRACK",
                "logistics": "SURGE_EXPENDITURE",
                "navigation": "HOLD_VECTOR",
            },
        },
    }
    receipt["decision_sha256"] = sha256_canonical(receipt)
    return receipt


def _vessel(ship_id: str, side_id: str, fleet_id: str, x_um: int) -> dict:
    return {
        "ship_id": ship_id,
        "side_id": side_id,
        "fleet_id": fleet_id,
        "baseline_class_id": "synthetic",
        "canonrec_class_id": "synthetic",
        "organization_id": "synthetic",
        "role": "synthetic",
        "formation_slot": 0,
        "attitude": {
            "frame": "P17_SCENARIO_INERTIAL_XYZ",
            "forward_q12": [1_000_000_000_000, 0, 0],
            "up_q12": [0, 0, 1_000_000_000_000],
        },
        "physical": {
            "max_accel_mm_s2": 50_000,
            "firepower_milliunits": 10_000,
            "shield_capacity_milliunits": 10_000,
            "shield_current_milliunits": 10_000,
            "armor_integrity_milliunits": 10_000,
            "armor_current_milliunits": 10_000,
            "hull_integrity_milliunits": 10_000,
            "hull_current_milliunits": 10_000,
            "effective_weapon_range_m": 2_000_000,
            "sensor_range_m": 2_000_000,
        },
        "capability_q1000": {
            "sensors": 1000,
            "stealth": 0,
            "electronic_warfare": 400,
            "mobility": 300,
        },
        "resources_q1000": {
            "fuel": 1000,
            "energy": 1000,
            "ammunition": 1000,
            "supply": 1000,
        },
        "readiness_q1000": {
            "overall": 1000,
            "sensors": 1000,
            "ew": 1000,
            "propulsion": 1000,
            "weapons": 1000,
            "damage_control": 1000,
        },
        "command": {},
        "morale_q1000": 1000,
        "cohesion_q1000": 1000,
        "damage_state": "undamaged",
        "disposition": "combat_capable",
        "provenance": {"test_fixture": True},
        "position_um": [x_um, 400_000_000_000, 0],
        "velocity_um_s": [0, 0, 0],
        "motion_status": "nominal",
    }


def _motion_state() -> dict:
    state = {
        "schema": "aurora://simulation/gumas/movement_state/v1.0",
        "movement_contract_id": "GUMAS_MOVEMENT_GEOMETRY_v1_0",
        "movement_version": "1.0.0",
        "canonical_json_profile": "aurora-canonical-json-v1",
        "movement_source_identity": movement_source(),
        "source_t0_sha256": "synthetic-t0",
        "parent_state_sha256": "synthetic-parent",
        "macrostep_index": 1,
        "elapsed_ms": 10_000,
        "planetoid": {"test_fixture": True},
        "vessels": [
            _vessel("A", "a", "F-A", -700_000_000_000),
            _vessel("B", "b", "F-B", 700_000_000_000),
        ],
        "last_command_decision_sha256_by_fleet": {},
    }
    state["vessels"] = sorted(state["vessels"], key=lambda item: item["ship_id"])
    state["state_sha256"] = movement_hash_without_field(state, "state_sha256")
    return state


def test_greater_hull_loss_cannot_reduce_readiness_degradation() -> None:
    prior = {
        "overall": 1000,
        "sensors": 1000,
        "ew": 1000,
        "propulsion": 1000,
        "weapons": 1000,
        "damage_control": 1000,
    }
    low_after, _, low_shock = _readiness_after_hull_loss(prior, 100)
    high_after, _, high_shock = _readiness_after_hull_loss(prior, 500)

    assert high_shock >= low_shock
    for field in prior:
        assert high_after[field] <= low_after[field]


def test_phase7_consumes_effect_descriptors_emitted_by_phase6() -> None:
    state = _motion_state()
    commands = {"F-A": _command("F-A"), "F-B": _command("F-B")}

    phase6_state, phase6_receipt = step_phase6_state(state, commands, 42)
    assert phase6_receipt["effect_descriptors"]
    assert any(item.get("hit") for item in phase6_receipt["weapon_attempts"])

    phase7_state, phase7_receipt = step_phase7_state(phase6_state, phase6_receipt)

    assert phase7_receipt["effect_count"] == len(phase6_receipt["effect_descriptors"])
    assert phase7_receipt["affected_target_count"] >= 1
    assert phase7_receipt["phase6_raw_receipt_validated_before_normalization"] is True
    assert phase7_receipt["termination_decision_made"] is False
    assert phase7_state["state_sha256"] == phase7_receipt["next_state_sha256"]
