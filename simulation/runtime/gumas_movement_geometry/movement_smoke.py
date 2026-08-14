#!/usr/bin/env python3
"""Real-source Phase-5 deterministic movement/geometry acceptance smoke."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.runtime.canonrec_tactical.resolver import (  # noqa: E402
    CanonRecTacticalResolver,
)
from simulation.runtime.gumas_command_policy.policy import decide  # noqa: E402
from simulation.runtime.gumas_movement_geometry.geometry import (  # noqa: E402
    mean_vector_round_half_even,
    separation_um,
)
from simulation.runtime.gumas_movement_geometry.kernel import (  # noqa: E402
    initialize_motion_state,
    order_from_command_receipt,
    step_motion_state,
)
from simulation.runtime.gumas_physical_t0.constructor import (  # noqa: E402
    construct_t0_state,
)

EXPECTED_T0_SHA256 = "47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec"
EXPECTED_COMMAND_POLICY_SHA256 = (
    "8c9ba9d413945404e7648c8f427b660576b0e85887c7639a0944f56b38585b3f"
)
BASELINE = (
    ROOT
    / "simulation/baselines/gumas/"
    "GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
)
CALIBRATION = (
    ROOT
    / "simulation/calibration/gumas/"
    "GUMAS__CALIBRATION__CANONREC_TO_PHYSICAL_TACTICAL_STATE__v1.0__2026-08-13.json"
)
SOURCE_SET = (
    ROOT
    / "simulation/canon_snapshots/canonrec/"
    "CANONREC__SOURCE_SET__GUMAS_RUN0_PHASE2__v1.0__2026-08-12.json"
)
OBSERVATION = {
    "contact_quality": 800,
    "relative_advantage": 400,
    "own_damage": 150,
    "enemy_damage_estimate": 150,
    "logistics_strain": 150,
    "mobility_margin": 800,
    "geometry_opportunity": 100,
    "withdrawal_viability": 700,
    "mission_pressure": 750,
    "time_pressure": 500,
    "negotiation_signal": 0,
    "ew_opportunity": 500,
    "carrier_opportunity": 600,
    "repair_need": 100,
    "enemy_closing_pressure": 600,
    "uncertainty": 250,
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _control_roster(baseline, calibration):
    mapping = calibration["identity_mapping"]["baseline_class_to_canonrec"]
    return [
        {"class_id": mapping[item["class_id"]], "count": int(item["count"])}
        for item in baseline["fleet_template"]["composition"]
    ]


def _fleet_centroids(state):
    grouped = {}
    for vessel in state["vessels"]:
        grouped.setdefault(vessel["fleet_id"], []).append(vessel["position_um"])
    return {
        fleet_id: list(mean_vector_round_half_even(positions))
        for fleet_id, positions in sorted(grouped.items())
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    args = parser.parse_args()

    baseline = _load(BASELINE)
    calibration = _load(CALIBRATION)
    resolver = CanonRecTacticalResolver.from_files(args.canonrec_root, SOURCE_SET)
    manifest = resolver.resolve_roster(
        calibration["identity_mapping"]["organization_id"],
        _control_roster(baseline, calibration),
    )
    t0 = construct_t0_state(baseline, calibration, manifest)
    assert t0["t0_sha256"] == EXPECTED_T0_SHA256
    state0 = initialize_motion_state(t0)
    centroids0 = _fleet_centroids(state0)

    baseline_identity = {
        "baseline_id": baseline["baseline_id"],
        "baseline_version": str(baseline["version"]),
    }
    decisions = {}
    orders = {}
    for side in ("loyalist", "rebel"):
        fleet = baseline["sides"][side]
        decision = decide(
            fleet["command_team"],
            OBSERVATION,
            side_id=side,
            fleet_id=fleet["fleet_id"],
            decision_epoch=0,
            baseline_identity=baseline_identity,
        )
        assert decision["policy_source_sha256"] == EXPECTED_COMMAND_POLICY_SHA256
        decisions[side] = decision
        orders[fleet["fleet_id"]] = order_from_command_receipt(decision)

    loyal_fleet = baseline["sides"]["loyalist"]["fleet_id"]
    rebel_fleet = baseline["sides"]["rebel"]["fleet_id"]
    references = {
        loyal_fleet: {
            "reference_kind": "test_fixture",
            "position_um": centroids0[rebel_fleet],
            "source_state_sha256": state0["state_sha256"],
            "source_receipt_sha256": "phase5-test-fixture",
            "confidence_q1000": 1000,
        },
        rebel_fleet: {
            "reference_kind": "test_fixture",
            "position_um": centroids0[loyal_fleet],
            "source_state_sha256": state0["state_sha256"],
            "source_receipt_sha256": "phase5-test-fixture",
            "confidence_q1000": 1000,
        },
    }

    first_state, first_receipt = step_motion_state(state0, orders, references)
    replay_state, replay_receipt = step_motion_state(state0, orders, references)
    assert first_state == replay_state
    assert first_receipt == replay_receipt
    assert len(first_state["vessels"]) == 38
    assert not any(item["collision"] for item in first_receipt["per_vessel"])

    throttles = {"loyalist": set(), "rebel": set()}
    for item in first_receipt["per_vessel"]:
        side = "loyalist" if item["ship_id"].startswith("LOY-") else "rebel"
        throttles[side].add(item["applied_throttle_q1000"])
    assert throttles["loyalist"] == {800}
    assert throttles["rebel"] == {650}

    centroids1 = first_receipt["geometry"]["fleet_centroid_um"]
    output = {
        "status": "ok",
        "source_t0_sha256": state0["source_t0_sha256"],
        "initial_movement_state_sha256": state0["state_sha256"],
        "next_movement_state_sha256": first_state["state_sha256"],
        "movement_receipt_sha256": first_receipt["movement_receipt_sha256"],
        "movement_source_identity": first_receipt["movement_source_identity"],
        "command_decision_sha256": {
            side: decisions[side]["decision_sha256"]
            for side in ("loyalist", "rebel")
        },
        "strategic_posture": {
            side: decisions[side]["orders"]["strategic_posture"]
            for side in ("loyalist", "rebel")
        },
        "navigation_intent": {
            side: decisions[side]["orders"]["specialist_intents"]["navigation"]
            for side in ("loyalist", "rebel")
        },
        "engineering_intent": {
            side: decisions[side]["orders"]["specialist_intents"]["engineering"]
            for side in ("loyalist", "rebel")
        },
        "applied_throttle_q1000": {
            "loyalist": 800,
            "rebel": 650,
        },
        "fleet_centroid_start_um": centroids0,
        "fleet_centroid_end_um": centroids1,
        "fleet_centroid_separation_start_um": separation_um(
            centroids0[loyal_fleet], centroids0[rebel_fleet]
        ),
        "fleet_centroid_separation_end_um": separation_um(
            centroids1[loyal_fleet], centroids1[rebel_fleet]
        ),
        "collisions": 0,
        "rng_used": first_receipt["rng_used"],
        "floating_authority_used": first_receipt["floating_authority_used"],
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
