#!/usr/bin/env python3
"""Real-source Phase-8 deterministic morale/resolution acceptance smoke."""
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
from simulation.runtime.gumas_damage_disposition import step_phase7_state  # noqa:E402
from simulation.runtime.gumas_morale_resolution import step_phase8_state  # noqa:E402
from simulation.runtime.gumas_movement_geometry.geometry import mean_vector_round_half_even  # noqa:E402
from simulation.runtime.gumas_movement_geometry.kernel import initialize_motion_state, order_from_command_receipt, step_motion_state  # noqa:E402
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
    return [{"class_id": mapping[item["class_id"]], "count": int(item["count"])} for item in baseline["fleet_template"]["composition"]]


def _centroids(state):
    grouped = {}
    for vessel in state["vessels"]:
        grouped.setdefault(vessel["fleet_id"], []).append(vessel["position_um"])
    return {fleet: list(mean_vector_round_half_even(points)) for fleet, points in sorted(grouped.items())}


def _morale_view(state):
    return {v["ship_id"]: (v["morale_q1000"], v["cohesion_q1000"]) for v in state["vessels"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    args = parser.parse_args()

    baseline = _load(BASELINE)
    calibration = _load(CALIBRATION)
    resolver = CanonRecTacticalResolver.from_files(args.canonrec_root, SOURCE_SET)
    manifest = resolver.resolve_roster(calibration["identity_mapping"]["organization_id"], _control_roster(baseline, calibration))
    t0 = construct_t0_state(baseline, calibration, manifest)
    assert t0["t0_sha256"] == EXPECTED_T0_SHA256
    state0 = initialize_motion_state(t0)
    centroids = _centroids(state0)
    baseline_identity = {"baseline_id": baseline["baseline_id"], "baseline_version": str(baseline["version"])}

    decisions = {}
    motion_orders = {}
    for side in ("loyalist", "rebel"):
        fleet = baseline["sides"][side]
        decision = decide(fleet["command_team"], OBSERVATION, side_id=side, fleet_id=fleet["fleet_id"], decision_epoch=0, baseline_identity=baseline_identity)
        decisions[fleet["fleet_id"]] = decision
        motion_orders[fleet["fleet_id"]] = order_from_command_receipt(decision)

    loyal = baseline["sides"]["loyalist"]["fleet_id"]
    rebel = baseline["sides"]["rebel"]["fleet_id"]
    references = {
        loyal: {"reference_kind": "phase8_smoke_fixture", "position_um": centroids[rebel], "source_state_sha256": state0["state_sha256"], "source_receipt_sha256": "phase8-smoke", "confidence_q1000": 1000},
        rebel: {"reference_kind": "phase8_smoke_fixture", "position_um": centroids[loyal], "source_state_sha256": state0["state_sha256"], "source_receipt_sha256": "phase8-smoke", "confidence_q1000": 1000},
    }
    moved, movement_receipt = step_motion_state(state0, motion_orders, references)
    phase6_state, phase6_receipt = step_phase6_state(moved, decisions, int(baseline["determinism"]["seed_u64"]))
    phase7_state, phase7_receipt = step_phase7_state(phase6_state, phase6_receipt)
    assert phase7_receipt["effect_count"] == 0

    phase8_a, resolution_a, receipt_a = step_phase8_state(phase7_state, phase7_receipt, decisions, baseline)
    phase8_b, resolution_b, receipt_b = step_phase8_state(phase7_state, phase7_receipt, decisions, baseline)
    assert phase8_a == phase8_b
    assert resolution_a == resolution_b
    assert receipt_a == receipt_b
    assert _morale_view(phase8_a) == _morale_view(phase7_state)
    assert resolution_a["terminal_outcome"]["termination_mode"] == "ongoing"
    assert receipt_a["physical_state_mutated"] is False
    assert receipt_a["phase8_public_boundary_validated"] is True
    assert receipt_a["ambient_rng_used"] is False
    assert receipt_a["floating_authority_used"] is False
    assert receipt_a["prose_inputs_used"] is False

    output = {
        "status": "ok",
        "source_t0_sha256": t0["t0_sha256"],
        "movement_state_sha256": moved["state_sha256"],
        "movement_receipt_sha256": movement_receipt["movement_receipt_sha256"],
        "phase6_state_sha256": phase6_state["state_sha256"],
        "phase6_receipt_sha256": phase6_receipt["phase6_receipt_sha256"],
        "phase7_state_sha256": phase7_state["state_sha256"],
        "phase7_receipt_sha256": phase7_receipt["phase7_receipt_sha256"],
        "phase8_next_state_sha256": phase8_a["state_sha256"],
        "phase8_resolution_state_sha256": resolution_a["resolution_state_sha256"],
        "phase8_receipt_sha256": receipt_a["phase8_receipt_sha256"],
        "phase8_source_identity": receipt_a["phase8_source_identity"],
        "phase8_boundary_source_identity": receipt_a["phase8_boundary_source_identity"],
        "phase8_composite_source_sha256": receipt_a["phase8_composite_source_sha256"],
        "phase8_public_boundary_validated": receipt_a["phase8_public_boundary_validated"],
        "strategic_posture_by_side": {side: decisions[baseline["sides"][side]["fleet_id"]]["orders"]["strategic_posture"] for side in ("loyalist", "rebel")},
        "battle_shock_by_side": {side: resolution_a["shock_by_side"][side]["battle_shock_q1000"] for side in ("loyalist", "rebel")},
        "negotiation_signal_q1000_by_side": resolution_a["negotiation_signal_q1000_by_side"],
        "morale_cohesion_unchanged": True,
        "termination_mode": resolution_a["terminal_outcome"]["termination_mode"],
        "terminated": resolution_a["terminal_outcome"]["terminated"],
        "protected_ship_count": len(resolution_a["protected_ship_ids"]),
        "ambient_rng_used": receipt_a["ambient_rng_used"],
        "floating_authority_used": receipt_a["floating_authority_used"],
        "prose_inputs_used": receipt_a["prose_inputs_used"],
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
