#!/usr/bin/env python3
"""Real-source Phase-7 deterministic damage/disposition acceptance smoke."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.runtime.gumas_acceptance_fixture import (  # noqa:E402
    load_acceptance_fixture,
    step_control_movement,
)
from simulation.runtime.gumas_damage_disposition import step_phase7_state  # noqa:E402
from simulation.runtime.gumas_damage_disposition.normalization import (  # noqa: E402
    normalize_phase6_receipt,
)
from simulation.runtime.gumas_sensing_weapons.kernel import step_phase6_state  # noqa:E402


def _material_view(state):
    return {
        vessel["ship_id"]: {
            "physical": vessel["physical"],
            "readiness_q1000": vessel["readiness_q1000"],
            "morale_q1000": vessel["morale_q1000"],
            "cohesion_q1000": vessel["cohesion_q1000"],
            "damage_state": vessel["damage_state"],
            "disposition": vessel["disposition"],
        }
        for vessel in state["vessels"]
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
        reference_kind="phase7_smoke_fixture",
        source_receipt_sha256="phase7-smoke",
    )
    seed_u64 = int(baseline["determinism"]["seed_u64"])
    phase6_state, phase6_receipt = step_phase6_state(moved, decisions, seed_u64)
    assert len(phase6_receipt["effect_descriptors"]) == 0
    normalized_phase6 = normalize_phase6_receipt(phase6_receipt)

    phase7_a, damage_a = step_phase7_state(phase6_state, phase6_receipt)
    phase7_b, damage_b = step_phase7_state(phase6_state, phase6_receipt)
    assert phase7_a == phase7_b
    assert damage_a == damage_b
    assert damage_a["effect_count"] == 0
    assert damage_a["affected_target_count"] == 0
    assert _material_view(phase7_a) == _material_view(phase6_state)
    assert damage_a["termination_decision_made"] is False
    assert damage_a["phase6_raw_receipt_validated_before_normalization"] is True

    output = {
        "status": "ok",
        "source_t0_sha256": t0["t0_sha256"],
        "movement_state_sha256": moved["state_sha256"],
        "movement_receipt_sha256": movement_receipt["movement_receipt_sha256"],
        "phase6_state_sha256": phase6_state["state_sha256"],
        "phase6_raw_receipt_sha256": phase6_receipt["phase6_receipt_sha256"],
        "phase7_bound_phase6_receipt_sha256": normalized_phase6[
            "phase6_receipt_sha256"
        ],
        "phase6_raw_receipt_validated_before_normalization": damage_a[
            "phase6_raw_receipt_validated_before_normalization"
        ],
        "phase6_effect_descriptors": len(phase6_receipt["effect_descriptors"]),
        "phase7_next_state_sha256": phase7_a["state_sha256"],
        "phase7_receipt_sha256": damage_a["phase7_receipt_sha256"],
        "damage_ledger_sha256": damage_a["damage_ledger_sha256"],
        "phase7_source_identity": damage_a["phase7_source_identity"],
        "phase7_semantic_normalizer_source_identity": damage_a[
            "phase7_semantic_normalizer_source_identity"
        ],
        "phase7_composite_source_sha256": damage_a["phase7_composite_source_sha256"],
        "affected_targets": damage_a["affected_target_count"],
        "material_state_unchanged": True,
        "morale_mutated": damage_a["morale_mutated"],
        "cohesion_mutated": damage_a["cohesion_mutated"],
        "termination_decision_made": damage_a["termination_decision_made"],
        "ambient_rng_used": damage_a["ambient_rng_used"],
        "floating_authority_used": damage_a["floating_authority_used"],
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
