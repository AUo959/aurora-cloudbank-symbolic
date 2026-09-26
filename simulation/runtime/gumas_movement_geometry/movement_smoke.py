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

from simulation.runtime.gumas_acceptance_fixture import (  # noqa: E402
    load_acceptance_fixture,
    opposing_references,
)
from simulation.runtime.gumas_movement_geometry.geometry import (  # noqa: E402
    separation_um,
)
from simulation.runtime.gumas_movement_geometry.kernel import (  # noqa: E402
    step_motion_state,
)

EXPECTED_COMMAND_POLICY_SHA256 = (
    "8c9ba9d413945404e7648c8f427b660576b0e85887c7639a0944f56b38585b3f"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    args = parser.parse_args()

    fixture = load_acceptance_fixture(args.canonrec_root)
    baseline = fixture.baseline
    state0 = fixture.initial_motion_state
    centroids0 = fixture.fleet_centroids
    decisions = fixture.decisions_by_side
    for decision in decisions.values():
        assert decision["policy_source_sha256"] == EXPECTED_COMMAND_POLICY_SHA256

    loyal_fleet = baseline["sides"]["loyalist"]["fleet_id"]
    rebel_fleet = baseline["sides"]["rebel"]["fleet_id"]
    references = opposing_references(
        fixture,
        reference_kind="test_fixture",
        source_receipt_sha256="phase5-test-fixture",
    )

    first_state, first_receipt = step_motion_state(
        state0, fixture.motion_orders, references
    )
    replay_state, replay_receipt = step_motion_state(
        state0, fixture.motion_orders, references
    )
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
            side: decisions[side]["decision_sha256"] for side in ("loyalist", "rebel")
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
