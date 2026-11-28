"""Run one resolved variant from T0 to its Phase-8 terminal outcome.

The runner only sequences the accepted Phase-9 ``execute_macrostep`` and then
hands the complete genesis-to-head artifact chain to the accepted Phase-10
reporter. It makes no decision of its own: Phase 8 alone ends the run.
"""

from __future__ import annotations

import copy
import hashlib
from pathlib import Path
from typing import Any, Mapping

from simulation.runtime.gumas_battle_orchestrator import (
    accepted_source_identities,
    execute_macrostep,
)
from simulation.runtime.gumas_factual_reporter import (
    PUBLIC_SUMMARY_PROFILE,
    SIMULATION_TRUTH_PROFILE,
    export_factual_report,
)
from simulation.runtime.gumas_factual_reporter import source_identity as phase10_source_identity
from simulation.runtime.gumas_factual_reporter.constants import (
    INPUT_SCHEMA,
    MACROSTEP_PACKET_SCHEMA,
)

from .constants import (
    HISTORICAL_CANON_STATUS,
    MAX_MACROSTEPS,
    PHASE11_CONTRACT_ID,
    PHASE11_VERSION,
    RUN_RECEIPT_SCHEMA,
)
from .identity import Phase11Error, hash_without_field, source_identity
from .inputs import ControlInputs

ROOT = Path(__file__).resolve().parents[3]
FROZEN_INPUT_SOURCES = (
    "simulation/runtime/canonrec_tactical/resolver.py",
    "simulation/runtime/gumas_physical_t0/constructor.py",
)


def frozen_input_source_identity() -> dict[str, str]:
    """Identity of the resolver and T0 constructor, which must not vary by control."""
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FROZEN_INPUT_SOURCES
    }


def engine_source_identity() -> dict[str, Any]:
    return {
        "phase4_to_phase9": accepted_source_identities(),
        "phase10_reporter": phase10_source_identity(),
        "phase11_controls": source_identity(),
        "frozen_input_sources": frozen_input_source_identity(),
    }


def _packet(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": MACROSTEP_PACKET_SCHEMA,
        "ledger_entry": result["ledger_entry"],
        "observation_receipts_by_side": result["observation_receipts_by_side"],
        "decisions_by_fleet": result["decisions_by_fleet"],
        "movement_receipt": result["movement_receipt"],
        "phase6_receipt": result["phase6_receipt"],
        "phase7_receipt": result["phase7_receipt"],
        "phase8_resolution_state": result["phase8_resolution_state"],
        "phase8_receipt": result["phase8_receipt"],
    }


def run_to_termination(inputs: ControlInputs, *, max_macrosteps: int = MAX_MACROSTEPS) -> dict[str, Any]:
    """Execute macrosteps until Phase 8 reports a terminal outcome."""
    state: Mapping[str, Any] = inputs.initial_state
    checkpoint: Mapping[str, Any] | None = None
    packets: list[dict[str, Any]] = []
    final: Mapping[str, Any] | None = None
    while True:
        if len(packets) >= max_macrosteps:
            raise Phase11Error(f"run exceeded {max_macrosteps} macrosteps without a terminal outcome")
        result = execute_macrostep(state, inputs.baseline, inputs.run_context, checkpoint)
        packets.append(_packet(result))
        state, checkpoint, final = result["committed_state"], result["checkpoint"], result
        if not result["can_continue"]:
            break
    assert final is not None
    return {
        "inputs": inputs,
        "packets": packets,
        "final_state": final["committed_state"],
        "terminal_outcome": copy.deepcopy(final["phase8_resolution_state"]["terminal_outcome"]),
        "ledger_head_sha256": str(final["ledger_entry"]["ledger_entry_sha256"]),
    }


def report_input(run: Mapping[str, Any]) -> dict[str, Any]:
    inputs: ControlInputs = run["inputs"]
    return {
        "schema": INPUT_SCHEMA,
        "expected_run_identity_sha256": inputs.run_context["run_identity_sha256"],
        "expected_ledger_head_sha256": run["ledger_head_sha256"],
        "run_context": inputs.run_context,
        "macrosteps": run["packets"],
    }


def export_reports(run: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    packet = report_input(run)
    return {
        SIMULATION_TRUTH_PROFILE: export_factual_report(packet),
        PUBLIC_SUMMARY_PROFILE: export_factual_report(packet, profile_id=PUBLIC_SUMMARY_PROFILE),
    }


def _report_identity(report: Mapping[str, Any]) -> dict[str, str]:
    return {
        "normalized_report_sha256": str(report["normalized_report"]["normalized_report_sha256"]),
        "rendered_report_sha256": str(report["rendered_report"]["rendered_report_sha256"]),
        "evidence_index_sha256": str(report["evidence_index"]["evidence_index_sha256"]),
        "export_receipt_sha256": str(report["export_receipt"]["export_receipt_sha256"]),
    }


def run_receipt(
    run: Mapping[str, Any],
    reports: Mapping[str, Mapping[str, Any]],
    *,
    authority: Mapping[str, Any],
    run0: bool,
) -> dict[str, Any]:
    """Seal the identities and terminal outcome of one completed run."""
    inputs: ControlInputs = run["inputs"]
    ledger = [packet["ledger_entry"] for packet in run["packets"]]
    receipt: dict[str, Any] = {
        "schema": RUN_RECEIPT_SCHEMA,
        "phase11_contract_id": PHASE11_CONTRACT_ID,
        "phase11_version": PHASE11_VERSION,
        "historical_canon_status": HISTORICAL_CANON_STATUS,
        "variant": inputs.variant,
        "input_identities": inputs.identities(),
        "authority_doctrine_by_side": copy.deepcopy(inputs.run_context["authority_doctrine_by_side"]),
        "engine_source_identity": engine_source_identity(),
        "macrosteps_executed": len(ledger),
        "final_elapsed_ms": int(run["final_state"]["elapsed_ms"]),
        "final_state_sha256": str(run["final_state"]["state_sha256"]),
        "ledger_genesis_sha256": str(ledger[0]["ledger_entry_sha256"]),
        "ledger_head_sha256": str(run["ledger_head_sha256"]),
        "ledger_chain_sha256": hashlib.sha256(
            "\n".join(str(entry["ledger_entry_sha256"]) for entry in ledger).encode("ascii")
        ).hexdigest(),
        "terminal_outcome": copy.deepcopy(run["terminal_outcome"]),
        "reports": {profile: _report_identity(report) for profile, report in sorted(reports.items())},
        "authority": {
            "authority_id": str(authority["authority_id"]),
            "authority_sha256": str(authority["authority_sha256"]),
            "capability": str(authority["capability"]),
            "as_of": str(authority["as_of"]),
        },
        "run0_executed": bool(run0),
        "canon_promotion": False,
    }
    receipt["run_receipt_sha256"] = hash_without_field(receipt, "run_receipt_sha256")
    return receipt
