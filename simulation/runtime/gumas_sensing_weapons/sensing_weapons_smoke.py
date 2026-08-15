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

from simulation.runtime.gumas_acceptance_fixture import (  # noqa:E402
    load_acceptance_fixture,
    step_control_movement,
)
from simulation.runtime.gumas_sensing_weapons.kernel import step_phase6_state  # noqa:E402


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
        reference_kind="phase6_smoke_fixture",
        source_receipt_sha256="phase6-smoke",
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
