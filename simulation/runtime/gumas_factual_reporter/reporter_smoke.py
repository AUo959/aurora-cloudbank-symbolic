#!/usr/bin/env python3
"""Real-source one-step Phase-10 reporting smoke; this is not Run 0."""

from __future__ import annotations

import argparse
import copy
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
from simulation.runtime.gumas_factual_reporter import (  # noqa:E402
    PUBLIC_SUMMARY_PROFILE,
    export_factual_report,
)
from simulation.runtime.gumas_factual_reporter.constants import (  # noqa:E402
    INPUT_SCHEMA,
    MACROSTEP_PACKET_SCHEMA,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonrec-root", required=True, type=Path)
    args = parser.parse_args()

    fixture = load_acceptance_fixture(args.canonrec_root)
    context = initialize_run_context(
        fixture.t0,
        fixture.initial_motion_state,
        fixture.baseline,
    )
    result = execute_macrostep(
        fixture.initial_motion_state,
        fixture.baseline,
        context,
    )
    assert result["ledger_entry"]["macrostep_index"] == 1
    assert result["ledger_entry"]["previous_ledger_entry_sha256"] == "GENESIS"
    assert result["ledger_entry"]["reporter_invoked"] is False
    assert result["ledger_entry"]["run0_executed"] is False

    packet = {
        "schema": INPUT_SCHEMA,
        "expected_run_identity_sha256": context["run_identity_sha256"],
        "expected_ledger_head_sha256": result["ledger_entry"][
            "ledger_entry_sha256"
        ],
        "run_context": copy.deepcopy(context),
        "macrosteps": [
            {
                "schema": MACROSTEP_PACKET_SCHEMA,
                "ledger_entry": copy.deepcopy(result["ledger_entry"]),
                "observation_receipts_by_side": copy.deepcopy(
                    result["observation_receipts_by_side"]
                ),
                "decisions_by_fleet": copy.deepcopy(result["decisions_by_fleet"]),
                "movement_receipt": copy.deepcopy(result["movement_receipt"]),
                "phase6_receipt": copy.deepcopy(result["phase6_receipt"]),
                "phase7_receipt": copy.deepcopy(result["phase7_receipt"]),
                "phase8_resolution_state": copy.deepcopy(
                    result["phase8_resolution_state"]
                ),
                "phase8_receipt": copy.deepcopy(result["phase8_receipt"]),
            }
        ],
    }

    truth = export_factual_report(packet)
    truth_replay = export_factual_report(copy.deepcopy(packet))
    public = export_factual_report(packet, profile_id=PUBLIC_SUMMARY_PROFILE)
    public_replay = export_factual_report(
        copy.deepcopy(packet),
        profile_id=PUBLIC_SUMMARY_PROFILE,
    )
    assert truth == truth_replay
    assert public == public_replay
    assert truth["normalized_report"]["macrostep_count"] == 1
    assert truth["normalized_report"]["run0_executed"] is False
    assert (
        public["export_receipt"]["truth_normalized_report_sha256"]
        == truth["normalized_report"]["normalized_report_sha256"]
    )

    output = {
        "status": "ok",
        "historical_canon_status": "non_canon_simulation_instance",
        "macrosteps_executed_for_witness": 1,
        "phase9_execute_macrostep_call_count": 1,
        "run0_executed": False,
        "source_t0_sha256": fixture.t0["t0_sha256"],
        "run_identity_sha256": context["run_identity_sha256"],
        "t0_roster_sha256": context["t0_roster_sha256"],
        "ledger_entry_sha256": result["ledger_entry"]["ledger_entry_sha256"],
        "termination_mode": result["phase8_resolution_state"]["terminal_outcome"][
            "termination_mode"
        ],
        "truth_normalized_report_sha256": truth["normalized_report"][
            "normalized_report_sha256"
        ],
        "truth_rendered_report_sha256": truth["rendered_report"][
            "rendered_report_sha256"
        ],
        "truth_evidence_index_sha256": truth["evidence_index"][
            "evidence_index_sha256"
        ],
        "truth_export_receipt_sha256": truth["export_receipt"][
            "export_receipt_sha256"
        ],
        "public_normalized_report_sha256": public["normalized_report"][
            "normalized_report_sha256"
        ],
        "public_rendered_report_sha256": public["rendered_report"][
            "rendered_report_sha256"
        ],
        "reporter_replay_exact": True,
        "transition_reporter_invoked": False,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
