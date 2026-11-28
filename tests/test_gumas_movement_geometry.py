from __future__ import annotations

import copy

import pytest

from simulation.runtime.gumas_movement_geometry.constants import (
    P17_AXES_UM,
    P17_WITHDRAWAL_RADIUS_UM,
    Q12,
)
from simulation.runtime.gumas_movement_geometry.geometry import (
    ellipsoid_implicit_scaled,
    gravity_acceleration_um_s2,
    inertial_to_body,
    norm_nearest,
    phase_at_elapsed_ms,
    segment_ellipsoid_first_contact_t_q12,
    segment_ellipsoid_occulted,
)
from simulation.runtime.gumas_movement_geometry.kernel import (
    MovementError,
    _hash_without_field,
    _source_identity,
    applied_throttle_q1000,
    occulted_by_p17,
    step_motion_state,
    thrust_acceleration_um_s2,
)

pytestmark = pytest.mark.unit


def _order(fleet_id: str, strategic: str, navigation: str, engineering: str):
    return {
        "fleet_id": fleet_id,
        "command_decision_sha256": f"decision-{fleet_id}",
        "strategic_posture": strategic,
        "navigation_intent": navigation,
        "engineering_intent": engineering,
    }


def _vessel(ship_id: str, fleet_id: str, position, velocity, max_accel):
    return {
        "ship_id": ship_id,
        "side_id": fleet_id,
        "fleet_id": fleet_id,
        "baseline_class_id": "synthetic",
        "canonrec_class_id": "synthetic",
        "organization_id": "synthetic",
        "role": "synthetic",
        "formation_slot": 0,
        "attitude": {
            "frame": "P17_SCENARIO_INERTIAL_XYZ",
            "forward_q12": [Q12, 0, 0],
            "up_q12": [0, 0, Q12],
        },
        "physical": {"max_accel_mm_s2": max_accel},
        "capability_q1000": {},
        "resources_q1000": {},
        "readiness_q1000": {},
        "command": {},
        "morale_q1000": 1000,
        "cohesion_q1000": 1000,
        "damage_state": "undamaged",
        "disposition": "combat_capable",
        "provenance": {"test_fixture": True},
        "position_um": list(position),
        "velocity_um_s": list(velocity),
        "motion_status": "nominal",
    }


def _state(vessels):
    state = {
        "schema": "aurora://simulation/gumas/movement_state/v1.0",
        "movement_contract_id": "GUMAS_MOVEMENT_GEOMETRY_v1_0",
        "movement_version": "1.0.0",
        "canonical_json_profile": "aurora-canonical-json-v1",
        "movement_source_identity": _source_identity(),
        "source_t0_sha256": "synthetic-test-t0",
        "parent_state_sha256": None,
        "macrostep_index": 0,
        "elapsed_ms": 0,
        "planetoid": {"test_fixture": True},
        "vessels": sorted(vessels, key=lambda item: item["ship_id"]),
        "last_command_decision_sha256_by_fleet": {},
    }
    state["state_sha256"] = _hash_without_field(state, "state_sha256")
    return state


def test_cordic_cardinal_rotation_and_rotated_ellipsoid_effect():
    point = (160_000_000_000, 0, 0)
    body0 = inertial_to_body(point, 0)
    body_quarter = inertial_to_body(point, Q12 // 4)
    assert body0 == point
    assert body_quarter == (0, -160_000_000_000, 0)
    assert ellipsoid_implicit_scaled(body0, P17_AXES_UM) < 0
    assert ellipsoid_implicit_scaled(body_quarter, P17_AXES_UM) > 0
    assert phase_at_elapsed_ms(0) == 0


def test_gravity_is_mirrored_and_points_inward():
    positive = (6_000_000_000_000, 0, 0)
    negative = (-6_000_000_000_000, 0, 0)
    g_positive = gravity_acceleration_um_s2(positive)
    g_negative = gravity_acceleration_um_s2(negative)
    assert g_positive[0] < 0
    assert g_positive == tuple(-value for value in g_negative)


def test_ellipsoid_swept_collision_and_occultation():
    p0 = (300_000_000_000, 0, 0)
    p1 = (0, 0, 0)
    contact = segment_ellipsoid_first_contact_t_q12(p0, p1, P17_AXES_UM)
    assert contact is not None
    assert 0 < contact < Q12

    miss0 = (-300_000_000_000, 250_000_000_000, 0)
    miss1 = (300_000_000_000, 250_000_000_000, 0)
    assert segment_ellipsoid_occulted(p0, (-300_000_000_000, 0, 0), P17_AXES_UM)
    assert not segment_ellipsoid_occulted(miss0, miss1, P17_AXES_UM)
    assert occulted_by_p17(
        (-300_000_000_000, 0, 0), (300_000_000_000, 0, 0), 0
    )


def test_throttle_tables_and_acceleration_caps_are_causal():
    loyal = _order(
        "loyal",
        "POSITIONAL_MANEUVER",
        "POSITION_FOR_ADVANTAGE",
        "PRIORITIZE_PROPULSION",
    )
    rebel = _order(
        "rebel",
        "PRESS",
        "EVASIVE_VECTOR",
        "REINFORCE_DEFENSE",
    )
    assert applied_throttle_q1000(loyal) == 800
    assert applied_throttle_q1000(rebel) == 650

    slow = _vessel(
        "A", "loyal", (6_000_000_000_000, 0, 0), (0, 0, 0), 50_000
    )
    fast = _vessel(
        "B", "loyal", (6_000_000_000_000, 0, 0), (0, 0, 0), 100_000
    )
    slow_thrust, _ = thrust_acceleration_um_s2(slow, loyal, None)
    fast_thrust, _ = thrust_acceleration_um_s2(fast, loyal, None)
    assert norm_nearest(slow_thrust) <= 50_000_000
    assert norm_nearest(fast_thrust) <= 100_000_000
    assert norm_nearest(fast_thrust) > norm_nearest(slow_thrust)


def test_evasive_vector_without_reference_falls_back_to_tangent():
    vessel = _vessel(
        "A", "rebel", (6_000_000_000_000, 0, 0), (0, 0, 0), 100_000
    )
    order = _order("rebel", "PRESS", "EVASIVE_VECTOR", "BALANCED_POWER")
    thrust, _ = thrust_acceleration_um_s2(vessel, order, None)
    assert thrust[0] == 0
    assert thrust[1] > 0
    assert thrust[2] == 0


def test_one_step_replay_and_insertion_order_independence():
    vessels = [
        _vessel(
            "A", "fleet-a", (-6_000_000_000_000, 0, 0), (1_000_000_000, 0, 0), 60_000
        ),
        _vessel(
            "B", "fleet-b", (6_000_000_000_000, 0, 0), (-1_000_000_000, 0, 0), 60_000
        ),
    ]
    state = _state(vessels)
    orders = {
        "fleet-a": _order(
            "fleet-a", "POSITIONAL_MANEUVER", "POSITION_FOR_ADVANTAGE", "BALANCED_POWER"
        ),
        "fleet-b": _order(
            "fleet-b", "POSITIONAL_MANEUVER", "POSITION_FOR_ADVANTAGE", "BALANCED_POWER"
        ),
    }
    first_state, first_receipt = step_motion_state(state, orders)
    replay_state, replay_receipt = step_motion_state(
        copy.deepcopy(state), dict(reversed(list(orders.items())))
    )
    assert first_state == replay_state
    assert first_receipt == replay_receipt
    assert first_state["vessels"][0]["position_um"] == [
        -value for value in first_state["vessels"][1]["position_um"]
    ]
    assert first_state["vessels"][0]["velocity_um_s"] == [
        -value for value in first_state["vessels"][1]["velocity_um_s"]
    ]


def test_multi_step_replay_100_macrosteps():
    vessel = _vessel(
        "A",
        "fleet-a",
        (8_000_000_000_000, 0, 0),
        (0, 500_000_000, 0),
        50_000,
    )
    initial = _state([vessel])
    orders = {
        "fleet-a": _order(
            "fleet-a", "HOLD", "HOLD_VECTOR", "BALANCED_POWER"
        )
    }

    def run(state):
        receipts = []
        for _ in range(100):
            state, receipt = step_motion_state(state, orders)
            receipts.append(receipt["movement_receipt_sha256"])
        return state, receipts

    end_a, receipts_a = run(copy.deepcopy(initial))
    end_b, receipts_b = run(copy.deepcopy(initial))
    assert end_a == end_b
    assert receipts_a == receipts_b


def test_withdrawal_boundary_semantics():
    at_boundary = (P17_WITHDRAWAL_RADIUS_UM, 0, 0)
    outside = (P17_WITHDRAWAL_RADIUS_UM + 1, 0, 0)
    assert norm_nearest(at_boundary) <= P17_WITHDRAWAL_RADIUS_UM
    assert norm_nearest(outside) > P17_WITHDRAWAL_RADIUS_UM


def _advantage_reference(position, velocity, standoff):
    return {
        "reference_kind": "phase9_side_local_contact_centroid",
        "position_um": list(position),
        "velocity_um_s": list(velocity),
        "standoff_um": standoff,
        "source_state_sha256": "s",
        "source_receipt_sha256": "r",
        "confidence_q1000": 700,
    }


def _advantage_order(fleet_id: str):
    return _order(fleet_id, "POSITIONAL_MANEUVER", "POSITION_FOR_ADVANTAGE", "PRIORITIZE_PROPULSION")


def test_position_for_advantage_closes_toward_standoff_with_a_contact_reference():
    vessel = _vessel("A", "fleet-a", (-8_000_000_000_000, 0, 0), (0, 0, 0), 50_000)
    reference = _advantage_reference((8_000_000_000_000, 0, 0), (0, 0, 0), 4_000_000_000_000)
    thrust, _ = thrust_acceleration_um_s2(vessel, _advantage_order("fleet-a"), reference)
    assert thrust[0] > 0
    assert thrust[1] == 0
    assert thrust[2] == 0
    assert norm_nearest(thrust) <= 40_000_000

    inside = _vessel("A", "fleet-a", (6_000_000_000_000, 0, 0), (0, 0, 0), 50_000)
    retreat, _ = thrust_acceleration_um_s2(inside, _advantage_order("fleet-a"), reference)
    assert retreat[0] < 0


def test_position_for_advantage_holds_when_already_matched_at_standoff():
    vessel = _vessel("A", "fleet-a", (4_000_000_000_000, 0, 0), (1_000_000, 0, 0), 50_000)
    reference = _advantage_reference((8_000_000_000_000, 0, 0), (1_000_000, 0, 0), 4_000_000_000_000)
    thrust, _ = thrust_acceleration_um_s2(vessel, _advantage_order("fleet-a"), reference)
    assert thrust == (0, 0, 0)


def test_position_for_advantage_without_reference_keeps_v1_tangent():
    vessel = _vessel("A", "fleet-a", (6_000_000_000_000, 0, 0), (0, 0, 0), 50_000)
    thrust, _ = thrust_acceleration_um_s2(vessel, _advantage_order("fleet-a"), None)
    assert thrust[0] == 0
    assert thrust[1] > 0


def test_closing_fleets_converge_to_standoff_and_replay():
    vessels = [
        _vessel("A", "fleet-a", (-8_000_000_000_000, 0, 0), (0, 0, 0), 50_000),
        _vessel("B", "fleet-b", (8_000_000_000_000, 0, 0), (0, 0, 0), 50_000),
    ]
    state = _state(vessels)
    orders = {fleet: _advantage_order(fleet) for fleet in ("fleet-a", "fleet-b")}
    start = norm_nearest([16_000_000_000_000, 0, 0])
    for _ in range(40):
        by_id = {v["ship_id"]: v for v in state["vessels"]}
        refs = {
            "fleet-a": _advantage_reference(by_id["B"]["position_um"], by_id["B"]["velocity_um_s"], 4_000_000_000_000),
            "fleet-b": _advantage_reference(by_id["A"]["position_um"], by_id["A"]["velocity_um_s"], 4_000_000_000_000),
        }
        replay, _ = step_motion_state(copy.deepcopy(state), orders, copy.deepcopy(refs))
        state, _ = step_motion_state(state, orders, refs)
        assert replay == state
    by_id = {v["ship_id"]: v for v in state["vessels"]}
    separation = norm_nearest([b - a for a, b in zip(by_id["A"]["position_um"], by_id["B"]["position_um"])])
    assert separation < start
    assert by_id["A"]["position_um"] == [-value for value in by_id["B"]["position_um"]]


def test_advantage_reference_requires_positive_standoff():
    vessels = [_vessel("A", "fleet-a", (-8_000_000_000_000, 0, 0), (0, 0, 0), 50_000)]
    state = _state(vessels)
    reference = _advantage_reference((8_000_000_000_000, 0, 0), (0, 0, 0), 0)
    orders = {"fleet-a": _advantage_order("fleet-a")}
    references = {"fleet-a": reference}
    with pytest.raises(MovementError):
        step_motion_state(state, orders, references)


def test_wrecks_coast_and_propulsion_readiness_scales_thrust():
    order = _advantage_order("fleet-a")
    healthy = _vessel("A", "fleet-a", (6_000_000_000_000, 0, 0), (0, 0, 0), 50_000)
    full, _ = thrust_acceleration_um_s2(healthy, order, None)
    for disposition in ("destroyed", "disabled"):
        wreck = copy.deepcopy(healthy)
        wreck["disposition"] = disposition
        assert thrust_acceleration_um_s2(wreck, order, None) == ((0, 0, 0), 0)
    damaged = copy.deepcopy(healthy)
    damaged["readiness_q1000"] = {"propulsion": 500}
    half, _ = thrust_acceleration_um_s2(damaged, order, None)
    assert norm_nearest(half) * 2 == pytest.approx(norm_nearest(full), abs=2)
