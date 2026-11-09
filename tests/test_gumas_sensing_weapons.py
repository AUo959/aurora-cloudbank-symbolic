from __future__ import annotations

import copy

import pytest

from simulation.runtime.gumas_command_policy.policy import (
    _source_identity as command_source,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    _hash_without_field as movement_hash_without_field,
    _source_identity as movement_source,
)
from simulation.runtime.gumas_sensing_weapons.kernel import (
    _child_draw,
    build_observation_state,
    sha256_canonical,
    step_phase6_state,
)

pytestmark = pytest.mark.unit


def _command(
    fleet_id,
    *,
    tactical="MAX_EFFECT_FIRE",
    ew="PASSIVE_TRACK",
    logistics="SURGE_EXPENDITURE",
    navigation="HOLD_VECTOR",
):
    receipt = {
        "schema": "aurora://simulation/gumas/command_decision_receipt/v1.0",
        "policy_id": "GUMAS_COMMAND_POLICY_v1_0",
        "policy_version": "1.0.0",
        "policy_source_sha256": command_source()["bundle_sha256"],
        "fleet_id": fleet_id,
        "orders": {
            "strategic_posture": "PRESS",
            "specialist_intents": {
                "tactical": tactical,
                "ew_sensors": ew,
                "logistics": logistics,
                "navigation": navigation,
            },
        },
    }
    receipt["decision_sha256"] = sha256_canonical(receipt)
    return receipt


def _vessel(
    ship_id,
    side,
    fleet,
    position_um,
    *,
    sensor_range_m=2_000_000,
    weapon_range_m=1_500_000,
    sensors=900,
    stealth=100,
    ew=400,
    mobility=300,
    firepower=10_000,
    disposition="combat_capable",
):
    return {
        "ship_id": ship_id,
        "side_id": side,
        "fleet_id": fleet,
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
            "firepower_milliunits": firepower,
            "shield_capacity_milliunits": 10_000,
            "shield_current_milliunits": 10_000,
            "armor_integrity_milliunits": 10_000,
            "armor_current_milliunits": 10_000,
            "hull_integrity_milliunits": 10_000,
            "hull_current_milliunits": 10_000,
            "effective_weapon_range_m": weapon_range_m,
            "sensor_range_m": sensor_range_m,
        },
        "capability_q1000": {
            "sensors": sensors,
            "stealth": stealth,
            "electronic_warfare": ew,
            "mobility": mobility,
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
        "disposition": disposition,
        "provenance": {"test_fixture": True},
        "position_um": list(position_um),
        "velocity_um_s": [0, 0, 0],
        "motion_status": "nominal",
    }


def _state(vessels, *, elapsed_ms=0, macrostep_index=1):
    result = {
        "schema": "aurora://simulation/gumas/movement_state/v1.0",
        "movement_contract_id": "GUMAS_MOVEMENT_GEOMETRY_v1_0",
        "movement_version": "1.0.0",
        "canonical_json_profile": "aurora-canonical-json-v1",
        "movement_source_identity": movement_source(),
        "source_t0_sha256": "synthetic-t0",
        "parent_state_sha256": "synthetic-parent",
        "macrostep_index": macrostep_index,
        "elapsed_ms": elapsed_ms,
        "planetoid": {"test_fixture": True},
        "vessels": sorted(vessels, key=lambda item: item["ship_id"]),
        "last_command_decision_sha256_by_fleet": {},
    }
    result["state_sha256"] = movement_hash_without_field(result, "state_sha256")
    return result


def _commands(**overrides):
    a = _command("F-A", **overrides.get("a", {}))
    b = _command("F-B", **overrides.get("b", {}))
    return {"F-A": a, "F-B": b}


def test_contact_sensor_and_stealth_monotonicity():
    a = _vessel(
        "A", "a", "F-A", (-700_000_000_000, 400_000_000_000, 0), sensors=700
    )
    b = _vessel(
        "B", "b", "F-B", (700_000_000_000, 400_000_000_000, 0), stealth=300
    )
    base = build_observation_state(_state([a, b]), _commands())
    q0 = base["contacts"][0]["contact_quality_q1000"]
    stronger = copy.deepcopy(a)
    stronger["capability_q1000"]["sensors"] = 900
    q1 = build_observation_state(_state([stronger, b]), _commands())["contacts"][0][
        "contact_quality_q1000"
    ]
    weaker_stealth = copy.deepcopy(b)
    weaker_stealth["capability_q1000"]["stealth"] = 100
    q2 = build_observation_state(_state([a, weaker_stealth]), _commands())[
        "contacts"
    ][0]["contact_quality_q1000"]
    assert q1 >= q0
    assert q2 >= q0


def test_p17_occultation_removes_contact():
    a = _vessel(
        "A", "a", "F-A", (-300_000_000_000, 0, 0), sensor_range_m=1_000_000
    )
    b = _vessel(
        "B", "b", "F-B", (300_000_000_000, 0, 0), sensor_range_m=1_000_000
    )
    observation = build_observation_state(_state([a, b]), _commands())
    assert observation["contacts"] == []


def test_active_jam_degrades_and_protect_network_does_not_worsen():
    a = _vessel(
        "A", "a", "F-A", (-700_000_000_000, 400_000_000_000, 0), ew=300
    )
    b = _vessel(
        "B", "b", "F-B", (700_000_000_000, 400_000_000_000, 0), ew=900
    )
    passive = build_observation_state(
        _state([a, b]),
        _commands(a={"ew": "ACTIVE_JAM"}, b={"ew": "PASSIVE_TRACK"}),
    )
    jammed = build_observation_state(
        _state([a, b]),
        _commands(a={"ew": "ACTIVE_JAM"}, b={"ew": "ACTIVE_JAM"}),
    )
    protected = build_observation_state(
        _state([a, b]),
        _commands(a={"ew": "PROTECT_NETWORK"}, b={"ew": "ACTIVE_JAM"}),
    )

    def _quality(observation):
        return next(
            contact["contact_quality_q1000"]
            for contact in observation["contacts"]
            if contact["observer_ship_id"] == "A"
        )

    assert _quality(jammed) <= _quality(passive)
    assert _quality(protected) >= _quality(jammed)


def test_hold_fire_and_protected_target_never_fire():
    a = _vessel(
        "A",
        "a",
        "F-A",
        (-700_000_000_000, 400_000_000_000, 0),
        weapon_range_m=2_000_000,
    )
    b = _vessel(
        "B",
        "b",
        "F-B",
        (700_000_000_000, 400_000_000_000, 0),
        weapon_range_m=2_000_000,
    )
    _, receipt = step_phase6_state(
        _state([a, b]),
        _commands(
            a={"tactical": "HOLD_FIRE"}, b={"tactical": "HOLD_FIRE"}
        ),
        42,
    )
    assert receipt["weapon_attempts"] == []

    surrendered = copy.deepcopy(b)
    surrendered["disposition"] = "surrendered"
    _, receipt2 = step_phase6_state(
        _state([a, surrendered]),
        _commands(
            a={"tactical": "MAX_EFFECT_FIRE"}, b={"tactical": "HOLD_FIRE"}
        ),
        42,
    )
    assert not any(
        item.get("shooter_ship_id") == "A"
        for item in receipt2["weapon_attempts"]
    )


def test_weapon_range_boundary_exact():
    a = _vessel(
        "A",
        "a",
        "F-A",
        (0, 500_000_000_000, 0),
        sensor_range_m=2_000_000,
        weapon_range_m=1_000_000,
        sensors=1000,
        stealth=0,
    )
    b = _vessel(
        "B",
        "b",
        "F-B",
        (1_000_000_000_000, 500_000_000_000, 0),
        sensor_range_m=2_000_000,
        weapon_range_m=1_000_000,
        sensors=1000,
        stealth=0,
    )
    _, at_boundary = step_phase6_state(_state([a, b]), _commands(), 42)
    assert any(
        item.get("shooter_ship_id") == "A" and item.get("fired")
        for item in at_boundary["weapon_attempts"]
    )

    b_outside = copy.deepcopy(b)
    b_outside["position_um"][0] += 1
    _, outside = step_phase6_state(_state([a, b_outside]), _commands(), 42)
    assert not any(
        item.get("shooter_ship_id") == "A" and item.get("fired")
        for item in outside["weapon_attempts"]
    )


def test_replay_order_independence_and_no_damage_application():
    a = _vessel(
        "A",
        "a",
        "F-A",
        (-700_000_000_000, 400_000_000_000, 0),
        weapon_range_m=2_000_000,
        sensors=1000,
        stealth=0,
    )
    b = _vessel(
        "B",
        "b",
        "F-B",
        (700_000_000_000, 400_000_000_000, 0),
        weapon_range_m=2_000_000,
        sensors=1000,
        stealth=0,
    )
    initial = _state([a, b])
    command_map = _commands()
    next_a, receipt_a = step_phase6_state(
        initial, command_map, 1593560554842931876
    )
    next_b, receipt_b = step_phase6_state(
        copy.deepcopy(initial),
        dict(reversed(list(command_map.items()))),
        1593560554842931876,
    )
    assert next_a == next_b
    assert receipt_a == receipt_b

    before = {
        vessel["ship_id"]: (
            vessel["physical"]["shield_current_milliunits"],
            vessel["physical"]["armor_current_milliunits"],
            vessel["physical"]["hull_current_milliunits"],
        )
        for vessel in initial["vessels"]
    }
    after = {
        vessel["ship_id"]: (
            vessel["physical"]["shield_current_milliunits"],
            vessel["physical"]["armor_current_milliunits"],
            vessel["physical"]["hull_current_milliunits"],
        )
        for vessel in next_a["vessels"]
    }
    assert before == after


def test_child_draw_stable_and_unrelated_attempt_independent():
    first = _child_draw(42, 1, "A", "B", 0, "source")
    replay = _child_draw(42, 1, "A", "B", 0, "source")
    unrelated = _child_draw(42, 1, "X", "Y", 0, "source")
    assert first == replay
    assert unrelated != first
    assert _child_draw(42, 1, "A", "B", 0, "source") == first


def test_higher_mobility_cannot_increase_hit_chance_and_firepower_increases_base_effect():
    a = _vessel(
        "A",
        "a",
        "F-A",
        (-700_000_000_000, 400_000_000_000, 0),
        weapon_range_m=2_000_000,
        sensors=1000,
        stealth=0,
        firepower=8_000,
    )
    b = _vessel(
        "B",
        "b",
        "F-B",
        (700_000_000_000, 400_000_000_000, 0),
        weapon_range_m=2_000_000,
        sensors=1000,
        stealth=0,
        mobility=200,
    )
    _, low = step_phase6_state(_state([a, b]), _commands(), 42)
    low_attempt = next(
        item for item in low["weapon_attempts"] if item["shooter_ship_id"] == "A"
    )

    fast_b = copy.deepcopy(b)
    fast_b["capability_q1000"]["mobility"] = 800
    _, high = step_phase6_state(_state([a, fast_b]), _commands(), 42)
    high_attempt = next(
        item for item in high["weapon_attempts"] if item["shooter_ship_id"] == "A"
    )
    assert high_attempt["hit_chance_q1000"] <= low_attempt["hit_chance_q1000"]

    strong_a = copy.deepcopy(a)
    strong_a["physical"]["firepower_milliunits"] = 16_000
    _, strong = step_phase6_state(_state([strong_a, b]), _commands(), 42)
    strong_attempt = next(
        item
        for item in strong["weapon_attempts"]
        if item["shooter_ship_id"] == "A"
    )
    assert (
        strong_attempt["base_effect_milliunits"]
        >= low_attempt["base_effect_milliunits"]
    )
