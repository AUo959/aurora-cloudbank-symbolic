"""Authoritative pure Phase-10 factual reporter and evidence exporter."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .constants import (
    CANONICAL_JSON_PROFILE,
    EVIDENCE_INDEX_SCHEMA,
    EXPORT_RECEIPT_SCHEMA,
    HISTORICAL_CANON_STATUS,
    PHASE10_CONTRACT_ID,
    PHASE10_VERSION,
    REPORT_PROFILES,
    SIMULATION_TRUTH_PROFILE,
)
from .identity import Phase10Error, hash_without_field, sha256_canonical, source_identity
from .projection import build_truth_projection, select_profile
from .rendering import render_report
from .validation import validate_report_input


def _evidence_index(
    report: Mapping[str, Any],
    evidence_records: Sequence[Mapping[str, Any]],
    rendered: Mapping[str, Any],
) -> dict[str, Any]:
    event_to_refs = {
        str(event["event_id"]): sorted(set(str(item) for item in event["evidence_ref_ids"]))
        for event in report["events"]
    }
    rendered_to_events = {
        str(statement["statement_id"]): sorted(
            set(str(item) for item in statement["event_ids"])
        )
        for statement in rendered["statements"]
    }
    known_events = set(event_to_refs)
    known_refs = {str(item["evidence_ref_id"]) for item in evidence_records}
    if any(not refs for refs in event_to_refs.values()):
        raise Phase10Error("normalized factual event lacks evidence")
    if any(not set(refs).issubset(known_refs) for refs in event_to_refs.values()):
        raise Phase10Error("normalized factual event references unknown evidence")
    if any(not events for events in rendered_to_events.values()):
        raise Phase10Error("factual rendered statement lacks event provenance")
    if any(not set(events).issubset(known_events) for events in rendered_to_events.values()):
        raise Phase10Error("rendered statement references unknown event")
    index = {
        "schema": EVIDENCE_INDEX_SCHEMA,
        "phase10_contract_id": PHASE10_CONTRACT_ID,
        "phase10_version": PHASE10_VERSION,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "profile_id": report["profile_id"],
        "run_identity_sha256": report["run_identity_sha256"],
        "ledger_head_sha256": report["ledger_head_sha256"],
        "evidence_references": sorted(
            [dict(item) for item in evidence_records],
            key=lambda item: item["evidence_ref_id"],
        ),
        "event_to_evidence_ref_ids": dict(sorted(event_to_refs.items())),
        "rendered_statement_to_event_ids": dict(sorted(rendered_to_events.items())),
    }
    index["evidence_index_sha256"] = hash_without_field(index, "evidence_index_sha256")
    return index


def export_factual_report(
    report_input: Mapping[str, Any],
    *,
    profile_id: str = SIMULATION_TRUTH_PROFILE,
) -> dict[str, Any]:
    """Validate accepted artifacts and deterministically project factual output."""
    if profile_id not in REPORT_PROFILES:
        raise Phase10Error(f"unsupported Phase-10 profile: {profile_id}")
    validated = validate_report_input(report_input)
    reporter_identity = source_identity()
    truth_report, truth_evidence = build_truth_projection(validated, reporter_identity)
    selected_report, selected_evidence = select_profile(
        truth_report,
        truth_evidence,
        profile_id,
    )
    rendered = render_report(selected_report)
    evidence_index = _evidence_index(selected_report, selected_evidence, rendered)
    receipt = {
        "schema": EXPORT_RECEIPT_SCHEMA,
        "phase10_contract_id": PHASE10_CONTRACT_ID,
        "phase10_version": PHASE10_VERSION,
        "canonical_json_profile": CANONICAL_JSON_PROFILE,
        "reporter_source_identity": reporter_identity,
        "profile_id": profile_id,
        "historical_canon_status": HISTORICAL_CANON_STATUS,
        "run0_executed": False,
        "run_identity_sha256": validated["expected_run_identity_sha256"],
        "t0_roster_sha256": validated["run_context"]["t0_roster_sha256"],
        "input_ledger_head_sha256": validated["expected_ledger_head_sha256"],
        "report_input_sha256": sha256_canonical(validated),
        "truth_normalized_report_sha256": truth_report["normalized_report_sha256"],
        "selected_normalized_report_sha256": selected_report[
            "normalized_report_sha256"
        ],
        "evidence_index_sha256": evidence_index["evidence_index_sha256"],
        "rendered_report_sha256": rendered["rendered_report_sha256"],
        "macrostep_count": selected_report["macrostep_count"],
        "event_count": len(selected_report["events"]),
        "rendered_statement_count": len(rendered["statements"]),
        "transition_execution_imported": False,
        "transition_execution_called": False,
        "report_feedback_applied": False,
        "wall_clock_used": False,
        "network_used": False,
        "llm_used": False,
        "ambient_rng_used": False,
    }
    receipt["export_receipt_sha256"] = hash_without_field(
        receipt,
        "export_receipt_sha256",
    )
    return {
        "normalized_report": selected_report,
        "evidence_index": evidence_index,
        "rendered_report": rendered,
        "export_receipt": receipt,
    }
