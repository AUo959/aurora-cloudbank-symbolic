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

from simulation.runtime.gumas_acceptance_fixture import (  # noqa: E402
    load_acceptance_fixture,
    step_control_movement,
)
from simulation.runtime.gumas_damage_disposition import step_phase7_state  # noqa:E402
from simulation.runtime.gumas_morale_resolution import step_phase8_state  # noqa:E402
from simulation.runtime.gumas_sensing_weapons.kernel import step_phase6_state  # noqa:E402


def _morale_view(state):
    return {
        v["ship_id"]: (v["morale_q1000"], v["cohesion_q1000"]) for v in state["vessels"]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    args = parser.parse_args()

    fixture = load_acceptance_fixture(args.canonrec_root)
    baseline = fixture.baseline
    t0 = fixture.t0
    decisions = fixture.decisions_by_fleet
    moved, movement_receipt = step_control_movement(
        fixture,
        reference_kind="phase8_smoke_fixture",
        source_receipt_sha256="phase8-smoke",
    )
    phase6_state, phase6_receipt = step_phase6_state(
        moved, decisions, int(baseline["determinism"]["seed_u64"])
    )
    phase7_state, phase7_receipt = step_phase7_state(phase6_state, phase6_receipt)
    assert phase7_receipt["effect_count"] == 0

    phase8_a, resolution_a, receipt_a = step_phase8_state(
        phase7_state, phase7_receipt, decisions, baseline
    )
    phase8_b, resolution_b, receipt_b = step_phase8_state(
        phase7_state, phase7_receipt, decisions, baseline
    )
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
        "phase8_public_boundary_validated": receipt_a[
            "phase8_public_boundary_validated"
        ],
        "strategic_posture_by_side": {
            side: decisions[baseline["sides"][side]["fleet_id"]]["orders"][
                "strategic_posture"
            ]
            for side in ("loyalist", "rebel")
        },
        "battle_shock_by_side": {
            side: resolution_a["shock_by_side"][side]["battle_shock_q1000"]
            for side in ("loyalist", "rebel")
        },
        "negotiation_signal_q1000_by_side": resolution_a[
            "negotiation_signal_q1000_by_side"
        ],
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
