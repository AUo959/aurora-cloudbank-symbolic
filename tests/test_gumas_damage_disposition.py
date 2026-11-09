from __future__ import annotations

import copy

import pytest

from simulation.runtime.gumas_damage_disposition.kernel import (
    Phase7Error,
    step_phase7_state,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as movement_hash_without_field,
)
from simulation.runtime.gumas_sensing_weapons.kernel import (
    _hash_without_field as phase6_hash_without_field,
    _source_identity as phase6_source_identity,
    sha256_canonical,
)

pytestmark = pytest.mark.unit


def _vessel(ship_id: str, *, shield=1000, armor=1000, hull=1000, dc=1000, disposition="combat_capable"):
    return {
        "ship_id": ship_id,
        "side_id": "a" if ship_id == "A" else "b",
        "fleet_id": "F-A" if ship_id == "A" else "F-B",
        "physical": {
            "shield_capacity_milliunits": shield,
            "shield_current_milliunits": shield,
            "armor_integrity_milliunits": armor,
            "armor_current_milliunits": armor,
            "hull_integrity_milliunits": hull,
            "hull_current_milliunits": hull,
            "firepower_milliunits": 1000,
            "max_accel_mm_s2": 10000,
            "effective_weapon_range_m": 1000000,
            "sensor_range_m": 2000000,
        },
        "readiness_q1000": {
            "overall": 1000,
            "sensors": 1000,
            "ew": 1000,
            "propulsion": 1000,
            "weapons": 1000,
            "damage_control": dc,
        },
        "resources_q1000": {"fuel": 1000, "energy": 1000, "ammunition": 1000, "supply": 1000},
        "capability_q1000": {},
        "morale_q1000": 900,
        "cohesion_q1000": 850,
        "damage_state": "undamaged",
        "disposition": disposition,
        "position_um": [0, 0, 0],
        "velocity_um_s": [0, 0, 0],
        "motion_status": "nominal",
    }


def _state(*, b=None):
    result = {
        "schema": "aurora://simulation/gumas/movement_state/v1.0",
        "movement_contract_id": "GUMAS_MOVEMENT_GEOMETRY_v1_0",
        "movement_version": "1.0.0",
        "canonical_json_profile": "aurora-canonical-json-v1",
        "source_t0_sha256": "synthetic-t0",
        "parent_state_sha256": "synthetic-parent",
        "macrostep_index": 1,
        "elapsed_ms": 10000,
        "planetoid": {"test_fixture": True},
        "vessels": [_vessel("A"), b or _vessel("B")],
        "last_command_decision_sha256_by_fleet": {},
    }
    result["vessels"] = sorted(result["vessels"], key=lambda item: item["ship_id"])
    result["state_sha256"] = movement_hash_without_field(result, "state_sha256")
    return result


def _effect(prior_sha: str, delivered: int, *, ordinal=0, target="B"):
    attempt_id = sha256_canonical({"attempt": ordinal, "target": target})
    return {
        "effect_id": sha256_canonical(
            {"attempt_id": attempt_id, "delivered_effect_milliunits": delivered}
        ),
        "attempt_id": attempt_id,
        "source_ship_id": "A",
        "target_ship_id": target,
        "delivered_effect_milliunits": delivered,
        "impact_quality_q1000": 800,
        "source_state_sha256": prior_sha,
    }


def _receipt(state, delivered=(), *, effects=None):
    prior_sha = "synthetic-phase6-prior"
    if effects is None:
        effects = [_effect(prior_sha, value, ordinal=i) for i, value in enumerate(delivered)]
    receipt = {
        "schema": "aurora://simulation/gumas/phase6_step_receipt/v1.0",
        "phase6_contract_id": "GUMAS_SENSING_EW_TARGETING_WEAPONS_v1_0",
        "phase6_version": "1.0.0",
        "phase6_source_identity": phase6_source_identity(),
        "prior_state_sha256": prior_sha,
        "next_state_sha256": state["state_sha256"],
        "macrostep_index": 1,
        "elapsed_ms": 10000,
        "observation_state_sha256": "observation",
        "fire_control_state_sha256": "fire-control",
        "command_decision_sha256_by_fleet": {},
        "contacts": [],
        "selections": [],
        "weapon_attempts": [],
        "effect_descriptors": list(effects),
        "deterministic_child_draw_used": bool(effects),
        "ambient_rng_used": False,
        "floating_authority_used": False,
        "damage_applied": False,
    }
    receipt["phase6_receipt_sha256"] = phase6_hash_without_field(
        receipt, "phase6_receipt_sha256"
    )
    return receipt


def _ship(state, ship_id="B"):
    return next(item for item in state["vessels"] if item["ship_id"] == ship_id)


def test_zero_effect_replay_is_exact_and_material_state_is_unchanged():
    state = _state()
    receipt = _receipt(state)
    next_a, damage_a = step_phase7_state(state, receipt)
    next_b, damage_b = step_phase7_state(copy.deepcopy(state), copy.deepcopy(receipt))
    assert next_a == next_b
    assert damage_a == damage_b
    assert damage_a["effect_count"] == 0
    assert damage_a["target_damage_receipts"] == []
    for field in ("physical", "readiness_q1000", "morale_q1000", "cohesion_q1000", "damage_state", "disposition"):
        assert _ship(next_a)[field] == _ship(state)[field]


def test_shield_then_armor_then_hull_boundaries_are_exact():
    state = _state()
    next_state, receipt = step_phase7_state(state, _receipt(state, [1000]))
    b = _ship(next_state)
    assert b["physical"]["shield_current_milliunits"] == 0
    assert b["physical"]["armor_current_milliunits"] == 1000
    assert b["physical"]["hull_current_milliunits"] == 1000
    assert b["readiness_q1000"]["weapons"] == 1000
    assert receipt["target_damage_receipts"][0]["damage_state"]["after"] == "shield_damaged"

    state2 = _state()
    next_state2, receipt2 = step_phase7_state(state2, _receipt(state2, [1850]))
    b2 = _ship(next_state2)
    assert b2["physical"]["shield_current_milliunits"] == 0
    assert b2["physical"]["armor_current_milliunits"] == 0
    assert b2["physical"]["hull_current_milliunits"] == 1000
    assert receipt2["target_damage_receipts"][0]["hull"]["lost"] == 0

    state3 = _state()
    next_state3, receipt3 = step_phase7_state(state3, _receipt(state3, [1851]))
    assert _ship(next_state3)["physical"]["hull_current_milliunits"] == 999
    assert receipt3["target_damage_receipts"][0]["readiness"]["effective_shock_q1000"] > 0


def test_simultaneous_effect_order_is_inert_and_overkill_clamps_hull():
    state = _state()
    effects = [_effect("synthetic-phase6-prior", 2500, ordinal=0), _effect("synthetic-phase6-prior", 2500, ordinal=1)]
    first = _receipt(state, effects=effects)
    second = _receipt(state, effects=list(reversed(effects)))
    next_a, receipt_a = step_phase7_state(state, first)
    next_b, receipt_b = step_phase7_state(state, second)
    assert next_a == next_b
    assert receipt_a == receipt_b
    b = _ship(next_a)
    assert b["physical"]["hull_current_milliunits"] == 0
    target = receipt_a["target_damage_receipts"][0]
    assert target["hull"]["overkill"] > 0
    assert b["disposition"] == "destroyed"


def test_hull_penetration_degrades_readiness_but_preserves_morale_and_cohesion():
    state = _state()
    next_state, receipt = step_phase7_state(state, _receipt(state, [2350]))
    before = _ship(state)
    after = _ship(next_state)
    assert after["readiness_q1000"]["weapons"] < before["readiness_q1000"]["weapons"]
    assert after["morale_q1000"] == before["morale_q1000"]
    assert after["cohesion_q1000"] == before["cohesion_q1000"]
    assert receipt["morale_mutated"] is False
    assert receipt["cohesion_mutated"] is False
    assert receipt["termination_decision_made"] is False


def test_higher_damage_control_cannot_increase_readiness_loss():
    weak = _state(b=_vessel("B", dc=200))
    strong = _state(b=_vessel("B", dc=1000))
    weak_next, _ = step_phase7_state(weak, _receipt(weak, [2350]))
    strong_next, _ = step_phase7_state(strong, _receipt(strong, [2350]))
    weak_loss = 1000 - _ship(weak_next)["readiness_q1000"]["weapons"]
    strong_loss = 1000 - _ship(strong_next)["readiness_q1000"]["weapons"]
    assert strong_loss <= weak_loss


def test_higher_capacity_cannot_increase_downstream_loss():
    low_shield = _state(b=_vessel("B", shield=500, armor=1000, hull=1000))
    high_shield = _state(b=_vessel("B", shield=1500, armor=1000, hull=1000))
    low_next, _ = step_phase7_state(low_shield, _receipt(low_shield, [2200]))
    high_next, _ = step_phase7_state(high_shield, _receipt(high_shield, [2200]))
    assert _ship(high_next)["physical"]["hull_current_milliunits"] >= _ship(low_next)["physical"]["hull_current_milliunits"]

    low_armor = _state(b=_vessel("B", shield=1, armor=500, hull=1000))
    high_armor = _state(b=_vessel("B", shield=1, armor=1500, hull=1000))
    low_armor_next, _ = step_phase7_state(low_armor, _receipt(low_armor, [1001]))
    high_armor_next, _ = step_phase7_state(high_armor, _receipt(high_armor, [1001]))
    assert _ship(high_armor_next)["physical"]["hull_current_milliunits"] >= _ship(low_armor_next)["physical"]["hull_current_milliunits"]


def test_disabled_is_distinct_from_destroyed():
    state = _state()
    disabled_next, _ = step_phase7_state(state, _receipt(state, [2700]))
    b = _ship(disabled_next)
    assert b["physical"]["hull_current_milliunits"] > 0
    assert b["disposition"] == "disabled"

    state2 = _state()
    destroyed_next, _ = step_phase7_state(state2, _receipt(state2, [5000]))
    b2 = _ship(destroyed_next)
    assert b2["physical"]["hull_current_milliunits"] == 0
    assert b2["damage_state"] == "destroyed"
    assert b2["disposition"] == "destroyed"


def test_duplicate_effect_and_pre_destroyed_target_fail_closed():
    state = _state()
    effect = _effect("synthetic-phase6-prior", 100, ordinal=0)
    duplicate = _receipt(state, effects=[effect, copy.deepcopy(effect)])
    with pytest.raises(Phase7Error):
        step_phase7_state(state, duplicate)

    destroyed_state = _state(b=_vessel("B", disposition="destroyed"))
    with pytest.raises(Phase7Error):
        step_phase7_state(destroyed_state, _receipt(destroyed_state, [100]))
