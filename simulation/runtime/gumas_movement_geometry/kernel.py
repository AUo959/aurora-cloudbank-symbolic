"""Deterministic Phase-5 movement/geometry kernel for GUMAS."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .constants import (
    CANONICAL_JSON_PROFILE,
    ENGINEERING_PROPULSION_CAP_Q1000,
    MACROSTEP_MS,
    MAX_RUN_DURATION_MS,
    MOVEMENT_CONTRACT_ID,
    MOVEMENT_VERSION,
    NAVIGATION_THROTTLE_DEMAND_Q1000,
    NEWTONIAN_SPEED_CEILING_UM_S,
    P17_AXES_UM,
    P17_WITHDRAWAL_RADIUS_UM,
    Q12,
    STRATEGIC_THROTTLE_CAP_Q1000,
    SUBSTEP_MS,
    SUBSTEPS_PER_MACROSTEP,
)
from .geometry import (
    GeometryError,
    add,
    clamp_vector_magnitude,
    closing_rate_um_s,
    cross,
    gravity_acceleration_um_s2,
    inertial_to_body,
    interpolate_q12,
    mean_vector_round_half_even,
    norm_nearest,
    normalize_q12,
    phase_at_elapsed_ms,
    round_half_even_fraction,
    scale_q12,
    segment_ellipsoid_first_contact_t_q12,
    segment_ellipsoid_occulted,
    segment_sphere_exit_t_q12,
    separation_um,
    subtract,
    vec3,
)


class MovementError(RuntimeError):
    """Raised when movement cannot be advanced under the pinned contract."""


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _source_identity() -> dict[str, Any]:
    directory = Path(__file__).resolve().parent
    names = ("constants.py", "geometry.py", "kernel.py")
    modules: dict[str, str] = {}
    bundle = hashlib.sha256()
    for name in names:
        data = (directory / name).read_bytes()
        modules[name] = hashlib.sha256(data).hexdigest()
        bundle.update(name.encode("ascii"))
        bundle.update(b"\0")
        bundle.update(data)
        bundle.update(b"\0")
    return {"module_sha256": modules, "bundle_sha256": bundle.hexdigest()}


def _hash_without_field(value: Mapping[str, Any], field: str) -> str:
    return sha256_canonical({key: item for key, item in value.items() if key != field})


def _verify_t0_snapshot(snapshot: Mapping[str, Any]) -> None:
    if snapshot.get("schema") != "aurora://simulation/gumas/deterministic_t0_physical_state/v1.0":
        raise MovementError("unsupported T0 snapshot schema")
    recorded = str(snapshot.get("t0_sha256") or "")
    actual = _hash_without_field(snapshot, "t0_sha256")
    if recorded != actual:
        raise MovementError(f"T0 hash mismatch: {recorded} != {actual}")
    planetoid = snapshot.get("planetoid") or {}
    axes = planetoid.get("semi_axes_m") or {}
    if [int(axes.get(key, 0)) * 1_000_000 for key in ("a", "b", "c")] != list(
        P17_AXES_UM
    ):
        raise MovementError("P17 semi-axis identity mismatch")
    if int(planetoid.get("integration_step_ms", 0)) != MACROSTEP_MS:
        raise MovementError("unsupported macro integration step")


def initialize_motion_state(t0_snapshot: Mapping[str, Any]) -> dict[str, Any]:
    _verify_t0_snapshot(t0_snapshot)
    source = _source_identity()
    vessels = []
    for raw in sorted(t0_snapshot.get("vessels", []), key=lambda item: item["ship_id"]):
        vessel = {
            key: copy.deepcopy(raw[key])
            for key in (
                "ship_id",
                "side_id",
                "fleet_id",
                "baseline_class_id",
                "canonrec_class_id",
                "organization_id",
                "role",
                "formation_slot",
                "attitude",
                "physical",
                "capability_q1000",
                "resources_q1000",
                "readiness_q1000",
                "command",
                "morale_q1000",
                "cohesion_q1000",
                "damage_state",
                "disposition",
                "provenance",
            )
        }
        vessel["position_um"] = [int(value) * 1_000_000 for value in raw["position_m"]]
        vessel["velocity_um_s"] = [int(value) * 1_000 for value in raw["velocity_mm_s"]]
        vessel["motion_status"] = "nominal"
        vessels.append(vessel)
    if len(vessels) != 38:
        raise MovementError(f"Run-0 movement state requires 38 vessels; got {len(vessels)}")

    state: dict[str, Any] = {
        "schema": "aurora://simulation/gumas/movement_state/v1.0",
        "movement_contract_id": MOVEMENT_CONTRACT_ID,
        "movement_version": MOVEMENT_VERSION,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "movement_source_identity": source,
        "source_t0_sha256": str(t0_snapshot["t0_sha256"]),
        "parent_state_sha256": None,
        "macrostep_index": 0,
        "elapsed_ms": 0,
        "planetoid": copy.deepcopy(t0_snapshot["planetoid"]),
        "vessels": vessels,
        "last_command_decision_sha256_by_fleet": {},
    }
    state["state_sha256"] = _hash_without_field(state, "state_sha256")
    return state


def _verify_motion_state(state: Mapping[str, Any]) -> None:
    if state.get("schema") != "aurora://simulation/gumas/movement_state/v1.0":
        raise MovementError("unsupported movement-state schema")
    recorded = str(state.get("state_sha256") or "")
    actual = _hash_without_field(state, "state_sha256")
    if recorded != actual:
        raise MovementError(f"movement state hash mismatch: {recorded} != {actual}")
    if state.get("movement_source_identity") != _source_identity():
        raise MovementError("movement source identity differs from current kernel")


def order_from_command_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    recorded = str(receipt.get("decision_sha256") or "")
    actual = _hash_without_field(receipt, "decision_sha256")
    if not recorded or recorded != actual:
        raise MovementError("command decision receipt hash mismatch")
    orders = receipt.get("orders") or {}
    specialist = orders.get("specialist_intents") or {}
    fleet_id = str(receipt.get("fleet_id") or "")
    strategic = str(orders.get("strategic_posture") or "")
    navigation = str(specialist.get("navigation") or "")
    engineering = str(specialist.get("engineering") or "")
    if strategic not in STRATEGIC_THROTTLE_CAP_Q1000:
        raise MovementError(f"unsupported strategic posture: {strategic}")
    if navigation not in NAVIGATION_THROTTLE_DEMAND_Q1000:
        raise MovementError(f"unsupported navigation intent: {navigation}")
    if engineering not in ENGINEERING_PROPULSION_CAP_Q1000:
        raise MovementError(f"unsupported engineering intent: {engineering}")
    if not fleet_id:
        raise MovementError("command receipt missing fleet_id")
    return {
        "fleet_id": fleet_id,
        "command_decision_sha256": recorded,
        "strategic_posture": strategic,
        "navigation_intent": navigation,
        "engineering_intent": engineering,
    }


def normalize_motion_reference(reference: Mapping[str, Any]) -> dict[str, Any]:
    kind = str(reference.get("reference_kind") or "")
    if not kind:
        raise MovementError("motion reference missing kind")
    position = list(vec3(reference.get("position_um") or ()))
    confidence = int(reference.get("confidence_q1000", 0))
    if not 0 <= confidence <= 1000:
        raise MovementError("motion reference confidence outside q1000 bounds")
    normalized = {
        "schema": "aurora://simulation/gumas/motion_reference/v1.0",
        "reference_kind": kind,
        "position_um": position,
        "source_state_sha256": str(reference.get("source_state_sha256") or ""),
        "source_receipt_sha256": str(reference.get("source_receipt_sha256") or ""),
        "confidence_q1000": confidence,
    }
    normalized["reference_sha256"] = sha256_canonical(normalized)
    return normalized


def applied_throttle_q1000(order: Mapping[str, Any]) -> int:
    try:
        strategic = STRATEGIC_THROTTLE_CAP_Q1000[str(order["strategic_posture"])]
        navigation = NAVIGATION_THROTTLE_DEMAND_Q1000[str(order["navigation_intent"])]
        engineering = ENGINEERING_PROPULSION_CAP_Q1000[str(order["engineering_intent"])]
    except KeyError as exc:
        raise MovementError(f"unsupported movement order component: {exc}") from exc
    return min(strategic, navigation, engineering)


def _guidance_direction_q12(
    position_um: Sequence[int],
    order: Mapping[str, Any],
    reference: Mapping[str, Any] | None,
) -> tuple[int, int, int]:
    navigation = str(order["navigation_intent"])
    position = vec3(position_um)
    spin = (0, 0, Q12)
    if navigation == "HOLD_VECTOR":
        return (0, 0, 0)
    if navigation == "WITHDRAW_VECTOR":
        return normalize_q12(position)
    tangent = cross(spin, position)
    if navigation == "POSITION_FOR_ADVANTAGE":
        if norm_nearest(tangent) == 0:
            return (Q12, 0, 0)
        return normalize_q12(tangent)
    if navigation == "EVASIVE_VECTOR":
        if reference is None:
            raise MovementError("EVASIVE_VECTOR requires MotionReferenceV1")
        threat = subtract(reference["position_um"], position)
        lateral = cross(spin, threat)
        if norm_nearest(lateral) != 0:
            return normalize_q12(lateral)
        if norm_nearest(tangent) != 0:
            return normalize_q12(tangent)
        return (Q12, 0, 0)
    raise MovementError(f"unsupported navigation intent: {navigation}")


def thrust_acceleration_um_s2(
    vessel: Mapping[str, Any],
    order: Mapping[str, Any],
    reference: Mapping[str, Any] | None,
    position_um: Sequence[int] | None = None,
) -> tuple[tuple[int, int, int], int]:
    max_accel = int(vessel["physical"]["max_accel_mm_s2"]) * 1_000
    if max_accel < 0:
        raise MovementError("negative vessel acceleration cap")
    throttle = applied_throttle_q1000(order)
    magnitude = round_half_even_fraction(max_accel * throttle, 1000)
    direction = _guidance_direction_q12(
        position_um if position_um is not None else vessel["position_um"],
        order,
        reference,
    )
    if direction == (0, 0, 0) or magnitude == 0:
        return (0, 0, 0), throttle
    vector = scale_q12(direction, magnitude)
    return clamp_vector_magnitude(vector, max_accel), throttle


def _position_verlet_predict(
    position: Sequence[int], velocity: Sequence[int], acceleration: Sequence[int]
) -> tuple[int, int, int]:
    p = vec3(position)
    v = vec3(velocity)
    a = vec3(acceleration)
    denominator = 2_000_000
    return tuple(
        p[index]
        + round_half_even_fraction(
            2_000 * v[index] * SUBSTEP_MS
            + a[index] * SUBSTEP_MS * SUBSTEP_MS,
            denominator,
        )
        for index in range(3)
    )


def _velocity_verlet_finish(
    velocity: Sequence[int], acceleration0: Sequence[int], acceleration1: Sequence[int]
) -> tuple[int, int, int]:
    v = vec3(velocity)
    a0 = vec3(acceleration0)
    a1 = vec3(acceleration1)
    return tuple(
        v[index]
        + round_half_even_fraction(
            (a0[index] + a1[index]) * SUBSTEP_MS,
            2_000,
        )
        for index in range(3)
    )


def _collision_velocity(
    velocity: Sequence[int], acceleration: Sequence[int], fraction_q12: int
) -> tuple[int, int, int]:
    v = vec3(velocity)
    a = vec3(acceleration)
    denominator = 1_000 * Q12
    return tuple(
        v[index]
        + round_half_even_fraction(
            a[index] * SUBSTEP_MS * fraction_q12,
            denominator,
        )
        for index in range(3)
    )


def _macro_fraction_q12(substep_index: int, fraction_q12: int) -> int:
    numerator = (
        substep_index * SUBSTEP_MS * Q12 + SUBSTEP_MS * fraction_q12
    )
    return round_half_even_fraction(numerator, MACROSTEP_MS)


def _inside_withdrawal_boundary(position_um: Sequence[int]) -> bool:
    return norm_nearest(position_um) <= P17_WITHDRAWAL_RADIUS_UM


def _advance_vessel(
    vessel: Mapping[str, Any],
    order: Mapping[str, Any],
    reference: Mapping[str, Any] | None,
    macro_start_ms: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    current = copy.deepcopy(vessel)
    start_position = vec3(current["position_um"])
    start_velocity = vec3(current["velocity_um_s"])
    position = start_position
    velocity = start_velocity
    collision = None
    boundary_crossing = None
    last_thrust = (0, 0, 0)
    throttle = applied_throttle_q1000(order)

    if current.get("motion_status") == "collision_contact":
        summary = {
            "ship_id": current["ship_id"],
            "start_position_um": list(start_position),
            "end_position_um": list(start_position),
            "start_velocity_um_s": list(start_velocity),
            "end_velocity_um_s": list(start_velocity),
            "max_accel_um_s2": int(current["physical"]["max_accel_mm_s2"]) * 1_000,
            "applied_throttle_q1000": 0,
            "final_thrust_um_s2": [0, 0, 0],
            "collision": "already_in_contact",
            "boundary_crossing": None,
        }
        return current, summary

    for substep_index in range(SUBSTEPS_PER_MACROSTEP):
        substep_start_ms = macro_start_ms + substep_index * SUBSTEP_MS
        thrust0, throttle = thrust_acceleration_um_s2(
            current, order, reference, position
        )
        gravity0 = gravity_acceleration_um_s2(position)
        acceleration0 = add(thrust0, gravity0)
        predicted_position = _position_verlet_predict(
            position, velocity, acceleration0
        )

        midpoint_ms = substep_start_ms + SUBSTEP_MS // 2
        phase_mid = phase_at_elapsed_ms(midpoint_ms)
        body0 = inertial_to_body(position, phase_mid)
        body1 = inertial_to_body(predicted_position, phase_mid)
        contact_t = segment_ellipsoid_first_contact_t_q12(
            body0, body1, P17_AXES_UM
        )
        if contact_t is not None:
            contact_position = interpolate_q12(
                position, predicted_position, contact_t
            )
            contact_velocity = _collision_velocity(
                velocity, acceleration0, contact_t
            )
            position = contact_position
            velocity = contact_velocity
            current["motion_status"] = "collision_contact"
            collision = {
                "body_id": "PLANETOID-P17",
                "substep_index": substep_index,
                "substep_fraction_q12": contact_t,
                "macro_fraction_q12": _macro_fraction_q12(
                    substep_index, contact_t
                ),
                "contact_position_um": list(contact_position),
                "pre_contact_velocity_um_s": list(start_velocity if substep_index == 0 else current["velocity_um_s"]),
                "contact_velocity_um_s": list(contact_velocity),
                "phase_mid_turn_q12": phase_mid,
            }
            last_thrust = thrust0
            break

        if boundary_crossing is None:
            crossing_t = segment_sphere_exit_t_q12(
                position, predicted_position, P17_WITHDRAWAL_RADIUS_UM
            )
            if crossing_t is not None:
                boundary_crossing = {
                    "substep_index": substep_index,
                    "substep_fraction_q12": crossing_t,
                    "macro_fraction_q12": _macro_fraction_q12(
                        substep_index, crossing_t
                    ),
                }

        thrust1, _ = thrust_acceleration_um_s2(
            current, order, reference, predicted_position
        )
        gravity1 = gravity_acceleration_um_s2(predicted_position)
        acceleration1 = add(thrust1, gravity1)
        next_velocity = _velocity_verlet_finish(
            velocity, acceleration0, acceleration1
        )
        if norm_nearest(next_velocity) >= NEWTONIAN_SPEED_CEILING_UM_S:
            raise MovementError(
                f"Newtonian validity ceiling exceeded by {current['ship_id']}"
            )
        position = predicted_position
        velocity = next_velocity
        last_thrust = thrust1
        current["position_um"] = list(position)
        current["velocity_um_s"] = list(velocity)

    current["position_um"] = list(position)
    current["velocity_um_s"] = list(velocity)
    summary = {
        "ship_id": current["ship_id"],
        "start_position_um": list(start_position),
        "end_position_um": list(position),
        "start_velocity_um_s": list(start_velocity),
        "end_velocity_um_s": list(velocity),
        "max_accel_um_s2": int(current["physical"]["max_accel_mm_s2"]) * 1_000,
        "applied_throttle_q1000": throttle,
        "final_thrust_um_s2": list(last_thrust),
        "collision": collision,
        "boundary_crossing": boundary_crossing,
    }
    return current, summary


def _fleet_centroids(vessels: Sequence[Mapping[str, Any]]) -> dict[str, list[int]]:
    grouped: dict[str, list[Sequence[int]]] = {}
    for vessel in sorted(vessels, key=lambda item: item["ship_id"]):
        if vessel.get("disposition") in {"destroyed", "surrendered"}:
            continue
        grouped.setdefault(str(vessel["fleet_id"]), []).append(vessel["position_um"])
    return {
        fleet_id: list(mean_vector_round_half_even(positions))
        for fleet_id, positions in sorted(grouped.items())
    }


def _boundary_summary(vessels: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for vessel in sorted(vessels, key=lambda item: item["ship_id"]):
        radius = norm_nearest(vessel["position_um"])
        result.append(
            {
                "ship_id": vessel["ship_id"],
                "radius_from_p17_um": radius,
                "inside_combat_volume": radius <= P17_WITHDRAWAL_RADIUS_UM,
                "outside_withdrawal_boundary": radius > P17_WITHDRAWAL_RADIUS_UM,
            }
        )
    return result


def step_motion_state(
    state: Mapping[str, Any],
    orders_by_fleet: Mapping[str, Mapping[str, Any]],
    motion_references_by_fleet: Mapping[str, Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _verify_motion_state(state)
    elapsed_ms = int(state["elapsed_ms"])
    if elapsed_ms + MACROSTEP_MS > MAX_RUN_DURATION_MS:
        raise MovementError("movement step would exceed hard run duration")

    normalized_orders: dict[str, dict[str, Any]] = {}
    for fleet_id, order in sorted(orders_by_fleet.items()):
        normalized = dict(order)
        if str(normalized.get("fleet_id") or "") != fleet_id:
            raise MovementError("movement order fleet key mismatch")
        # Validates all three action IDs and returns deterministic throttle.
        applied_throttle_q1000(normalized)
        normalized_orders[fleet_id] = normalized

    references: dict[str, dict[str, Any]] = {}
    for fleet_id, reference in sorted((motion_references_by_fleet or {}).items()):
        references[fleet_id] = normalize_motion_reference(reference)

    start_state_sha = str(state["state_sha256"])
    summaries = []
    next_vessels = []
    for vessel in sorted(state["vessels"], key=lambda item: item["ship_id"]):
        fleet_id = str(vessel["fleet_id"])
        if fleet_id not in normalized_orders:
            raise MovementError(f"missing movement order for fleet {fleet_id}")
        order = normalized_orders[fleet_id]
        reference = references.get(fleet_id)
        advanced, summary = _advance_vessel(
            vessel, order, reference, elapsed_ms
        )
        next_vessels.append(advanced)
        summaries.append(summary)

    next_state = copy.deepcopy(dict(state))
    next_state.pop("state_sha256", None)
    next_state["parent_state_sha256"] = start_state_sha
    next_state["macrostep_index"] = int(state["macrostep_index"]) + 1
    next_state["elapsed_ms"] = elapsed_ms + MACROSTEP_MS
    next_state["vessels"] = next_vessels
    next_state["last_command_decision_sha256_by_fleet"] = {
        fleet_id: str(order["command_decision_sha256"])
        for fleet_id, order in sorted(normalized_orders.items())
    }
    next_state["state_sha256"] = _hash_without_field(next_state, "state_sha256")

    source_identity = _source_identity()
    receipt: dict[str, Any] = {
        "schema": "aurora://simulation/gumas/movement_step_receipt/v1.0",
        "movement_contract_id": MOVEMENT_CONTRACT_ID,
        "movement_version": MOVEMENT_VERSION,
        "movement_source_identity": source_identity,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "prior_state_sha256": start_state_sha,
        "next_state_sha256": next_state["state_sha256"],
        "macrostep_index": next_state["macrostep_index"],
        "start_elapsed_ms": elapsed_ms,
        "end_elapsed_ms": next_state["elapsed_ms"],
        "substep_ms": SUBSTEP_MS,
        "substeps": SUBSTEPS_PER_MACROSTEP,
        "command_decision_sha256_by_fleet": next_state[
            "last_command_decision_sha256_by_fleet"
        ],
        "motion_reference_sha256_by_fleet": {
            fleet_id: reference["reference_sha256"]
            for fleet_id, reference in sorted(references.items())
        },
        "per_vessel": summaries,
        "geometry": {
            "p17_phase_start_turn_q12": phase_at_elapsed_ms(elapsed_ms),
            "p17_phase_end_turn_q12": phase_at_elapsed_ms(
                next_state["elapsed_ms"]
            ),
            "fleet_centroid_um": _fleet_centroids(next_vessels),
            "boundary": _boundary_summary(next_vessels),
        },
        "rng_used": False,
        "floating_authority_used": False,
    }
    receipt["movement_receipt_sha256"] = _hash_without_field(
        receipt, "movement_receipt_sha256"
    )
    return next_state, receipt


def occulted_by_p17(
    observer_position_um: Sequence[int],
    target_position_um: Sequence[int],
    elapsed_ms: int,
) -> bool:
    phase = phase_at_elapsed_ms(elapsed_ms)
    observer_body = inertial_to_body(observer_position_um, phase)
    target_body = inertial_to_body(target_position_um, phase)
    return segment_ellipsoid_occulted(
        observer_body, target_body, P17_AXES_UM
    )


def pair_geometry(
    left: Mapping[str, Any], right: Mapping[str, Any]
) -> dict[str, int]:
    return {
        "separation_um": separation_um(
            left["position_um"], right["position_um"]
        ),
        "closing_rate_um_s": closing_rate_um_s(
            left["position_um"],
            left["velocity_um_s"],
            right["position_um"],
            right["velocity_um_s"],
        ),
    }
