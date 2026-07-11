from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Mapping

from .engine import NarrativeValidationEngine
from .evidence import ContinuityVerdictReceipt, StateBuildReceipt, stable_receipt_id
from .router import build_request
from .types import CanonicalState, Strictness, TaskKind, Verdict

_VERDICT_GATE = {
    Verdict.SUPPORTED: "candidate",
    Verdict.PLAUSIBLE: "candidate",
    Verdict.POSSIBLE_WITH_SETUP: "hold_staging",
    Verdict.STRAINED: "owner_review_required",
    Verdict.CONTRADICTORY: "block_promotion",
}
_CANONICAL_INVARIANTS = {
    "anchor_seed": "EOS_SEED_ORION",
    "continuity_seal": "Aurora_Continuity_Seal_v2.2.5",
    "ethics_protocol": "Picard_Delta_3",
    "drift_lock": 0.0,
}
_CURRENT_FLIGHT_STATES = frozenset({"current", "flown", "passed", "success"})
_FALSE_LIKE_VALUES = frozenset(
    {"0", "bypass", "disabled", "false", "no", "none", "off", "skip", "skipped"}
)
_ARBITRATION_INPUTS = (
    "aurora_arbitration",
    "ethics_validation",
    "arbitration",
    "proposal_text",
)


def next_event_continuity_check(
    state: CanonicalState,
    proposed_event: Mapping[str, Any],
    state_build_receipt: StateBuildReceipt,
    *,
    strictness: Strictness | str = Strictness.DEFAULT,
    flight_status: Mapping[str, Any] | None = None,
) -> ContinuityVerdictReceipt:
    """Evaluate a proposed next event and return a deterministic promotion gate."""
    request, _, proposal = build_request(
        {
            "task_hint": TaskKind.NEXT_EVENT_CONTINUITY_CHECK.value,
            "question": "Can this proposed event happen next without breaking continuity?",
        },
        proposed_event,
        strictness,
    )
    hard_blocks, constraints_checked = _hard_constraint_findings(
        state, proposal, state_build_receipt
    )
    run = NarrativeValidationEngine().run_state(
        state,
        request,
        proposal,
        additional_hard_blocks=hard_blocks,
    )
    verdict = run.response.verdict or Verdict.CONTRADICTORY
    promotion_safety = dict(state_build_receipt.promotion_safety)
    promotion_gate = _VERDICT_GATE[verdict]

    if _promotion_safety_requires_hold(promotion_safety):
        promotion_gate = _at_least_hold_staging(promotion_gate)

    normalized_flight_status = _normalize_flight_status(flight_status)
    if not normalized_flight_status["current"]:
        promotion_gate = _degrade_for_freshness(promotion_gate)

    proposal_hash = stable_receipt_id({"proposal": proposal})
    gate_results = {
        "active_layers": tuple(run.evaluation.active_layers),
        "blockers": tuple(run.response.main_blockers),
        "bundle_id": state_build_receipt.bundle_id,
        "confidence": run.response.confidence,
        "flight_status": normalized_flight_status,
        "hard_blocks": tuple(run.evaluation.hard_blocks),
        "hard_constraints_checked": constraints_checked,
        "missing_bridges": tuple(run.response.missing_bridges),
        "missing_layers": tuple(run.evaluation.missing_layers),
        "promotion_gate": promotion_gate,
        "proposal_hash": proposal_hash,
        "smallest_fix": tuple(run.response.smallest_fix),
        "soft_blocks": tuple(run.evaluation.soft_blocks),
        "supports": tuple(run.response.main_supports),
        "state_id": state.state_id,
    }
    receipt_payload = {
        "gate_results": gate_results,
        "promotion_safety": promotion_safety,
        "state_build_receipt_id": state_build_receipt.receipt_id,
        "task_kind": request.task_kind.value,
        "verdict": verdict.value,
    }
    return ContinuityVerdictReceipt(
        receipt_id=stable_receipt_id(receipt_payload),
        state_build_receipt_id=state_build_receipt.receipt_id,
        task_kind=request.task_kind.value,
        verdict=verdict.value,
        gate_results=gate_results,
        promotion_safety=promotion_safety,
    )


def build_canon_reconciler_packet(
    receipt: ContinuityVerdictReceipt,
    *,
    source_bundle_hash: str,
    proposed_files: Iterable[str],
    owner_approved: bool = False,
) -> dict[str, Any]:
    """Build an owner-approved reconciliation candidate; never promote canon."""
    if receipt.promotion_gate != "candidate":
        raise ValueError(
            "continuity receipt is not eligible for a canon candidate packet"
        )
    if not owner_approved:
        raise PermissionError("owner approval is required before packet assembly")

    expected_bundle_hash = str(receipt.gate_results.get("bundle_id", ""))
    if str(source_bundle_hash) != expected_bundle_hash:
        raise ValueError("source bundle hash does not match the continuity receipt")
    normalized_files = tuple(sorted({str(path) for path in proposed_files}))
    if not normalized_files:
        raise ValueError("at least one proposed canon file is required")

    packet_payload = {
        "continuity_receipt": receipt.to_dict(),
        "owner_approved": True,
        "packet_kind": "canon_reconciler_candidate",
        "proposed_files": normalized_files,
        "source_bundle_hash": str(source_bundle_hash),
    }
    return {
        "packet_id": stable_receipt_id(packet_payload),
        **packet_payload,
    }


def _hard_constraint_findings(
    state: CanonicalState,
    proposal: Mapping[str, Any],
    state_build_receipt: StateBuildReceipt,
) -> tuple[list[str], tuple[str, ...]]:
    findings: list[str] = []
    contexts = (state.continuity, state.narrative_context, state.input_profile)

    if state.state_id != state_build_receipt.state_id:
        findings.append(
            "State-build receipt does not match the evaluated canonical state."
        )

    for key, expected in _CANONICAL_INVARIANTS.items():
        actual = _find_nested_value(contexts, key)
        if actual is not None and not _invariant_matches(actual, expected):
            findings.append(
                f"Canonical invariant {key} conflicts with the required value {expected}."
            )

    if _bypasses_aurora_arbitration(proposal):
        findings.append(
            "The proposed event bypasses required Aurora arbitration and ethics validation."
        )

    checked = tuple((*_CANONICAL_INVARIANTS, *_ARBITRATION_INPUTS))
    return findings, checked


def _find_nested_value(mappings: Iterable[Mapping[str, Any]], key: str) -> Any | None:
    for mapping in mappings:
        found = _find_in_mapping(mapping, key)
        if found is not None:
            return found
    return None


def _find_in_mapping(mapping: Mapping[str, Any], key: str) -> Any | None:
    for candidate_key, value in mapping.items():
        if str(candidate_key).casefold() == key.casefold():
            return value
        if isinstance(value, Mapping):
            nested = _find_in_mapping(value, key)
            if nested is not None:
                return nested
    return None


def _invariant_matches(actual: Any, expected: Any) -> bool:
    if isinstance(expected, float):
        try:
            return float(actual) == expected
        except (TypeError, ValueError):
            return False
    return str(actual).casefold() == str(expected).casefold()


def _bypasses_aurora_arbitration(proposal: Mapping[str, Any]) -> bool:
    if _proposal_flag_is_false_like(proposal, "aurora_arbitration"):
        return True
    if _proposal_flag_is_false_like(proposal, "ethics_validation"):
        return True
    arbitration = str(proposal.get("arbitration", "")).casefold()
    if arbitration in _FALSE_LIKE_VALUES:
        return True
    return _proposal_text_bypasses_arbitration(proposal)


def _proposal_flag_is_false_like(proposal: Mapping[str, Any], field_name: str) -> bool:
    if field_name not in proposal:
        return False
    value = proposal[field_name]
    if value is False:
        return True
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 0
    return isinstance(value, str) and value.strip().casefold() in _FALSE_LIKE_VALUES


def _proposal_text_bypasses_arbitration(proposal: Mapping[str, Any]) -> bool:
    text = " ".join(
        str(proposal.get(key, "")) for key in ("action", "event", "label", "notes")
    ).casefold()
    bypass_phrases = (
        "bypass aurora",
        "skip aurora arbitration",
        "without aurora arbitration",
    )
    if any(phrase in text for phrase in bypass_phrases):
        return True
    major_action_tokens = ("deploy", "hot-patch", "mesh patch", "promote")
    return "unilaterally" in text and any(
        token in text for token in major_action_tokens
    )


def _promotion_safety_requires_hold(promotion_safety: Mapping[str, Any]) -> bool:
    return bool(promotion_safety.get("blocked_fact_ids")) or not bool(
        promotion_safety.get("canon_promotion_allowed", False)
    )


def _at_least_hold_staging(gate: str) -> str:
    if gate == "block_promotion":
        return gate
    return "hold_staging"


def _degrade_for_freshness(gate: str) -> str:
    if gate == "candidate":
        return "owner_review_required"
    if gate == "owner_review_required":
        return "hold_staging"
    return gate


def _normalize_flight_status(
    flight_status: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if flight_status is None:
        return {"current": False, "reason": "missing", "status": "missing"}
    status = str(flight_status.get("status", "unknown")).casefold()
    stale = bool(flight_status.get("stale", False))
    current = status in _CURRENT_FLIGHT_STATES and not stale
    reason = "current" if current else ("stale" if stale else "not_current")
    return {"current": current, "reason": reason, "status": status}
