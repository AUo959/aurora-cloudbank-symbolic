#!/usr/bin/env python3
"""Real-source Phase-6 deterministic sensing/EW/targeting/weapons acceptance smoke."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.runtime.canonrec_tactical.resolver import CanonRecTacticalResolver  # noqa:E402
from simulation.runtime.gumas_command_policy.policy import decide  # noqa:E402
from simulation.runtime.gumas_movement_geometry.geometry import mean_vector_round_half_even  # noqa:E402
from simulation.runtime.gumas_movement_geometry.kernel import (  # noqa:E402
    initialize_motion_state,
    order_from_command_receipt,
    step_motion_state,
)
from simulation.runtime.gumas_physical_t0.constructor import construct_t0_state  # noqa:E402
from simulation.runtime.gumas_sensing_weapons.kernel import step_phase6_state  # noqa:E402

EXPECTED_T0_SHA256 = "47d31a29d882e565d15ba074e84c999952a689f06242362e14210e8777a548ec"
BASELINE = ROOT / "simulation/baselines/gumas/GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
CALIBRATION = ROOT / "simulation/calibration/gumas/GUMAS__CALIBRATION__CANONREC_TO_PHYSICAL_TACTICAL_STATE__v1.0__2026-08-13.json"
SOURCE_SET = ROOT / "simulation/canon_snapshots/canonrec/CANONREC__SOURCE_SET__GUMAS_RUN0_PHASE2__v1.0__2026-08-12.json"
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


def _centroids(state):
    grouped = {}
    for vessel in state["vessels"]:
        grouped.setdefault(vessel["fleet_id"], []).append(vessel["position_um"])
    return {
        fleet: list(mean_vector_round_half_even(points))
        for fleet, points in sorted(grouped.items())
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
    centroids0 = _centroids(state0)
    baseline_identity = {
        "baseline_id": baseline["baseline_id"],
        "baseline_version": str(baseline["version"]),
    }

    decisions = {}
    motion_orders = {}
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
        decisions[fleet["fleet_id"]] = decision
        motion_orders[fleet["fleet_id"]] = order_from_command_receipt(decision)

    loyal = baseline["sides"]["loyalist"]["fleet_id"]
    rebel = baseline["sides"]["rebel"]["fleet_id"]
    references = {
        loyal: {
            "reference_kind": "phase6_smoke_fixture",
            "position_um": centroids0[rebel],
            "source_state_sha256": state0["state_sha256"],
            "source_receipt_sha256": "phase6-smoke",
            "confidence_q1000": 1000,
        },
        rebel: {
            "reference_kind": "phase6_smoke_fixture",
            "position_um": centroids0[loyal],
            "source_state_sha256": state0["state_sha256"],
            "source_receipt_sha256": "phase6-smoke",
            "confidence_q1000": 1000,
        },
    }
    moved, movement_receipt = step_motion_state(
        state0, motion_orders, references
    )
    seed_u64 = int(baseline["determinism"]["seed_u64"])
    next_a, receipt_a = step_phase6_state(moved, decisions, seed_u64)
    next_b, receipt_b = step_phase6_state(
        moved, dict(reversed(list(decisions.items()))), seed_u64
    )
    assert next_a == next_b
    assert receipt_a == receipt_b
    assert receipt_a["damage_applied"] is False
    assert len(next_a["vessels"]) == 38

    hits = sum(1 for item in receipt_a["weapon_attempts"] if item.get("hit"))
    fired = sum(1 for item in receipt_a["weapon_attempts"] if item.get("fired"))
    output = {
        "status": "ok",
        "source_t0_sha256": t0["t0_sha256"],
        "movement_state_sha256": moved["state_sha256"],
        "movement_receipt_sha256": movement_receipt["movement_receipt_sha256"],
        "phase6_next_state_sha256": next_a["state_sha256"],
        "phase6_receipt_sha256": receipt_a["phase6_receipt_sha256"],
        "phase6_source_identity": receipt_a["phase6_source_identity"],
        "observation_state_sha256": receipt_a["observation_state_sha256"],
        "fire_control_state_sha256": receipt_a["fire_control_state_sha256"],
        "contacts": len(receipt_a["contacts"]),
        "hostile_confirmed_contacts": sum(
            1
            for contact in receipt_a["contacts"]
            if contact["classification"] == "hostile_confirmed"
        ),
        "weapon_attempts_fired": fired,
        "weapon_hits": hits,
        "effect_descriptors": len(receipt_a["effect_descriptors"]),
        "damage_applied": False,
        "ambient_rng_used": receipt_a["ambient_rng_used"],
        "floating_authority_used": receipt_a["floating_authority_used"],
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
