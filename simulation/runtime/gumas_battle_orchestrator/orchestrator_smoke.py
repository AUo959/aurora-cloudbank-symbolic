#!/usr/bin/env python3
"""Real-source one-step Phase-9 integration smoke; this is not Run 0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.runtime.gumas_acceptance_fixture import load_acceptance_fixture  # noqa:E402
from simulation.runtime.gumas_battle_orchestrator import (  # noqa:E402
    execute_macrostep,
    initialize_run_context,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    args = parser.parse_args()

    fixture = load_acceptance_fixture(args.canonrec_root)
    context = initialize_run_context(fixture.t0, fixture.initial_motion_state, fixture.baseline)
    first = execute_macrostep(fixture.initial_motion_state, fixture.baseline, context)
    replay = execute_macrostep(fixture.initial_motion_state, fixture.baseline, context)
    assert first == replay
    assert first["ledger_entry"]["macrostep_index"] == 1
    assert first["ledger_entry"]["previous_ledger_entry_sha256"] == "GENESIS"
    assert first["ledger_entry"]["reporter_invoked"] is False
    assert first["ledger_entry"]["run0_executed"] is False

    output = {
        "status": "ok",
        "historical_canon_status": "non_canon_simulation_instance",
        "macrosteps_executed": 1,
        "run0_executed": False,
        "source_t0_sha256": fixture.t0["t0_sha256"],
        "run_identity_sha256": context["run_identity_sha256"],
        "t0_roster_sha256": context["t0_roster_sha256"],
        "observation_sha256_by_side": first["ledger_entry"]["live_observation_sha256_by_side"],
        "decision_sha256_by_fleet": first["ledger_entry"]["phase4_decision_sha256_by_fleet"],
        "phase5_state_sha256": first["movement_state"]["state_sha256"],
        "phase6_state_sha256": first["phase6_state"]["state_sha256"],
        "phase7_state_sha256": first["phase7_state"]["state_sha256"],
        "phase8_state_sha256": first["committed_state"]["state_sha256"],
        "phase8_resolution_state_sha256": first["phase8_resolution_state"]["resolution_state_sha256"],
        "ledger_entry_sha256": first["ledger_entry"]["ledger_entry_sha256"],
        "termination_mode": first["phase8_resolution_state"]["terminal_outcome"]["termination_mode"],
        "can_continue": first["can_continue"],
        "reporter_invoked": False,
        "replay_exact": True,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
