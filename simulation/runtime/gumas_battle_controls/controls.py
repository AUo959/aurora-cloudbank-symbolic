"""Phase-11 Control A/B/C and Run-0 execution under committed owner authority."""

from __future__ import annotations

import hashlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Mapping

from .authority import require
from .constants import (
    CAPABILITY_CONTROLS,
    CAPABILITY_RUN0,
    CONTROL_RECEIPT_SCHEMA,
    EVIDENCE_SCHEMA,
    HISTORICAL_CANON_STATUS,
    PHASE11_CONTRACT_ID,
    PHASE11_VERSION,
    VARIANT_CLASS,
    VARIANT_CONTROL,
    VARIANT_POLITY,
)
from .identity import Phase11Error, canonical_json_bytes, hash_without_field, json_diff_paths
from .inputs import check_input_deltas, resolve_inputs
from .runner import export_reports, run_receipt, run_to_termination

# Receipt fields that legitimately differ between Run 0 and its Control-A replay.
REPLAY_EXEMPT_FIELDS = frozenset({"authority", "run0_executed", "run_receipt_sha256"})


def _digest(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def execute_variant(
    canonrec_root: str,
    variant: str,
    authority: Mapping[str, Any],
    run0: bool,
    rendered_out: str | None = None,
) -> dict[str, Any]:
    """Resolve, run, and report one variant; return its sealed receipt and digests."""
    inputs = resolve_inputs(Path(canonrec_root), variant)
    run = run_to_termination(inputs)
    reports = export_reports(run)
    receipt = run_receipt(run, reports, authority=authority, run0=run0)
    first_decisions = run["packets"][0]["decisions_by_fleet"]
    if rendered_out:
        out = Path(rendered_out)
        out.mkdir(parents=True, exist_ok=True)
        for profile, report in sorted(reports.items()):
            text = report["rendered_report"].get("text")
            if isinstance(text, str):
                (out / f"{variant}{'_run0' if run0 else ''}__{profile}.txt").write_text(text, encoding="utf-8")
    return {
        "receipt": receipt,
        "artifact_digests": {
            "ledger_entries": [_digest(p["ledger_entry"]) for p in run["packets"]],
            "packets_sha256": _digest(run["packets"]),
            "reports": {profile: _digest(report) for profile, report in sorted(reports.items())},
        },
        "manifest": inputs.manifest,
        "t0_sha256": inputs.t0["t0_sha256"],
        "first_step_commander_q1000": {
            fleet: receipt_["command_team_numeric"]["commander"]["attributes_q1000"]
            for fleet, receipt_ in sorted(first_decisions.items())
        },
        "first_ledger_entry_sha256": run["packets"][0]["ledger_entry"]["ledger_entry_sha256"],
    }


def _strip(receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in receipt.items() if key not in REPLAY_EXEMPT_FIELDS}


def compare_control_a(run0: Mapping[str, Any], replay: Mapping[str, Any]) -> dict[str, Any]:
    diffs = json_diff_paths(_strip(run0["receipt"]), _strip(replay["receipt"]))
    artifact_diffs = json_diff_paths(run0["artifact_digests"], replay["artifact_digests"])
    passed = not diffs and not artifact_diffs
    return {
        "control": "A_same_input_exact_replay",
        "passed": passed,
        "receipt_diff_paths": diffs,
        "artifact_diff_paths": artifact_diffs,
        "macrosteps_compared": len(run0["artifact_digests"]["ledger_entries"]),
    }


def _roster_by_class(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(entry["class_id"]): entry for entry in manifest["roster"]}


def compare_substitution(control: Mapping[str, Any], variant: Mapping[str, Any], kind: str) -> dict[str, Any]:
    c_receipt, v_receipt = control["receipt"], variant["receipt"]
    checks: dict[str, bool] = {}
    checks["engine_source_identity_identical"] = (
        c_receipt["engine_source_identity"] == v_receipt["engine_source_identity"]
    )
    checks["canonrec_commit_identical"] = (
        c_receipt["input_identities"]["canonrec_commit"] == v_receipt["input_identities"]["canonrec_commit"]
    )
    c_roster, v_roster = _roster_by_class(control["manifest"]), _roster_by_class(variant["manifest"])
    if kind == VARIANT_CLASS:
        changed = sorted(
            cls
            for cls in set(c_roster) | set(v_roster)
            if cls not in c_roster or cls not in v_roster or c_roster[cls]["count"] != v_roster[cls]["count"]
        )
        checks["only_declared_classes_changed"] = changed == ["cls_bastion", "cls_peregrine"]
        checks["authority_identical"] = control["manifest"]["authority"] == variant["manifest"]["authority"]
        checks["aggregate_capability_changed"] = (
            control["manifest"]["aggregate_capability_vector"] != variant["manifest"]["aggregate_capability_vector"]
        )
    else:
        checks["roster_counts_identical"] = {k: v["count"] for k, v in c_roster.items()} == {
            k: v["count"] for k, v in v_roster.items()
        }
        checks["class_capability_vectors_identical"] = all(
            c_roster[k]["resolved"]["capability_vector"] == v_roster[k]["resolved"]["capability_vector"]
            for k in c_roster
        )
        checks["authority_changed"] = (
            control["manifest"]["authority"]["authority_id"] != variant["manifest"]["authority"]["authority_id"]
        )
        checks["doctrine_changed"] = c_receipt["authority_doctrine_by_side"] != v_receipt["authority_doctrine_by_side"]
        checks["commander_conditioning_changed"] = (
            control["first_step_commander_q1000"] != variant["first_step_commander_q1000"]
        )
    checks["t0_changed"] = control["t0_sha256"] != variant["t0_sha256"]
    checks["first_ledger_entry_changed"] = control["first_ledger_entry_sha256"] != variant["first_ledger_entry_sha256"]
    checks["ledger_head_changed"] = c_receipt["ledger_head_sha256"] != v_receipt["ledger_head_sha256"]
    return {
        "control": "B_class_substitution" if kind == VARIANT_CLASS else "C_polity_substitution",
        "passed": all(checks.values()),
        "checks": checks,
        "terminal_outcome_control": c_receipt["terminal_outcome"],
        "terminal_outcome_variant": v_receipt["terminal_outcome"],
        "terminal_outcome_identical": c_receipt["terminal_outcome"] == v_receipt["terminal_outcome"],
        "macrosteps_control": c_receipt["macrosteps_executed"],
        "macrosteps_variant": v_receipt["macrosteps_executed"],
    }


def execute_controls(
    canonrec_root: Path,
    authority: Mapping[str, Any],
    as_of: str,
    *,
    workers: int = 4,
    rendered_out: Path | None = None,
) -> dict[str, Any]:
    """Run 0, its Control-A replay, Control B, and Control C; seal the evidence."""
    run0_grant = require(authority, CAPABILITY_RUN0, as_of)
    controls_grant = require(authority, CAPABILITY_CONTROLS, as_of)
    for variant in (VARIANT_CLASS, VARIANT_POLITY):
        # Fail closed on input deltas before any macrostep executes.
        resolve_inputs(canonrec_root, variant)
    jobs = [
        (VARIANT_CONTROL, run0_grant, True),
        (VARIANT_CONTROL, controls_grant, False),
        (VARIANT_CLASS, controls_grant, False),
        (VARIANT_POLITY, controls_grant, False),
    ]
    out = str(rendered_out) if rendered_out else None
    with ProcessPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(execute_variant, str(canonrec_root), v, g, r, out) for v, g, r in jobs]
        run0, replay, class_run, polity_run = (future.result() for future in futures)
    control_a = compare_control_a(run0, replay)
    control_b = compare_substitution(replay, class_run, VARIANT_CLASS)
    control_c = compare_substitution(replay, polity_run, VARIANT_POLITY)
    evidence: dict[str, Any] = {
        "schema": EVIDENCE_SCHEMA,
        "phase11_contract_id": PHASE11_CONTRACT_ID,
        "phase11_version": PHASE11_VERSION,
        "historical_canon_status": HISTORICAL_CANON_STATUS,
        "authority_sha256": str(authority["authority_sha256"]),
        "as_of": as_of,
        "run0_receipt": run0["receipt"],
        "control_receipts": {
            "replay": replay["receipt"],
            VARIANT_CLASS: class_run["receipt"],
            VARIANT_POLITY: polity_run["receipt"],
        },
        "controls": {
            "schema": CONTROL_RECEIPT_SCHEMA,
            "A": control_a,
            "B": control_b,
            "C": control_c,
        },
        "all_controls_passed": bool(control_a["passed"] and control_b["passed"] and control_c["passed"]),
        "run0_executed": True,
        "canon_promotion": False,
    }
    evidence["evidence_sha256"] = hash_without_field(evidence, "evidence_sha256")
    if not evidence["all_controls_passed"]:
        raise Phase11Error(f"Phase-11 controls failed: {_failed(evidence)}")
    return evidence


def _failed(evidence: Mapping[str, Any]) -> list[str]:
    return [name for name in ("A", "B", "C") if not evidence["controls"][name]["passed"]]


def verify_evidence(evidence: Mapping[str, Any]) -> None:
    """Check a sealed evidence document's own hash and pass flags."""
    if str(evidence.get("evidence_sha256") or "") != hash_without_field(evidence, "evidence_sha256"):
        raise Phase11Error("Phase-11 evidence hash mismatch")
    if evidence.get("all_controls_passed") is not True:
        raise Phase11Error("Phase-11 evidence records a failed control")


__all__ = [
    "check_input_deltas",
    "compare_control_a",
    "compare_substitution",
    "execute_controls",
    "execute_variant",
    "verify_evidence",
]
