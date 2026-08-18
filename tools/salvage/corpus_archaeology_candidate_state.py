"""Candidate state resolution rules for Phase-1 corpus archaeology."""

from __future__ import annotations

from typing import Any

IMPLEMENTATION_EVIDENCE_KINDS = {"implementation_artifact", "test_result"}
COMMITMENT_TYPES = {
    "approval",
    "decision",
    "requirement",
    "constraint",
    "todo",
    "unresolved_question",
    "proposed_patch",
}


def _human_claim_types(claims: list[dict[str, Any]]) -> set[str]:
    return {
        item["claim_type"]
        for item in claims
        if item["evidence_kind"] == "human_statement"
    }


def _is_implementation_claim(
    item: dict[str, Any], claim_type: str, authority: str | None
) -> bool:
    return (
        item["claim_type"] == claim_type
        and item["evidence_kind"] in IMPLEMENTATION_EVIDENCE_KINDS
        and (authority is None or item["authority_status"] == authority)
    )


def _has_implementation_claim(
    claims: list[dict[str, Any]], claim_type: str, authority: str | None = None
) -> bool:
    return any(
        _is_implementation_claim(item, claim_type, authority) for item in claims
    )


def candidate_flags(claims: list[dict[str, Any]]) -> dict[str, bool]:
    human_types = _human_claim_types(claims)
    return {
        "rejected": "rejection" in human_types,
        "implemented": _has_implementation_claim(claims, "implementation_evidence"),
        "partial": _has_implementation_claim(
            claims, "partial_implementation_evidence"
        ),
        "current_implemented": _has_implementation_claim(
            claims, "implementation_evidence", "current"
        ),
        "current_partial": _has_implementation_claim(
            claims, "partial_implementation_evidence", "current"
        ),
        "decision": bool({"approval", "decision"} & human_types),
        "requirement": bool({"requirement", "constraint"} & human_types),
        "unresolved": bool(
            {"todo", "unresolved_question", "proposed_patch"} & human_types
        ),
        "commitment": bool(COMMITMENT_TYPES & human_types),
    }


def candidate_state(flags: dict[str, bool]) -> tuple[str, str, str]:
    if flags["rejected"] and (flags["implemented"] or flags["partial"]):
        return (
            "unknown",
            "investigate",
            "Explicit human rejection and implementation evidence coexist; preserve both "
            "histories and investigate chronology, scope, and authority.",
        )
    if flags["rejected"]:
        return (
            "rejected",
            "reject_with_evidence",
            "Explicit human rejection evidence is present; preserve the record and do not "
            "restore automatically.",
        )
    if flags["implemented"]:
        return (
            "implemented",
            "preserve",
            "Implementation evidence is present; preserve the implementation record and "
            "verify whether a current successor remains.",
        )
    if flags["partial"]:
        return (
            "partial",
            "investigate",
            "Only partial implementation evidence is present; investigate intent and "
            "capability preservation.",
        )
    status = "approved" if flags["decision"] else "proposed"
    rationale = (
        "An explicit human commitment is present without implementation or rejection "
        "evidence; preserve for investigation."
        if flags["commitment"]
        else "No authoritative commitment, implementation, or rejection evidence is "
        "established; retain as an uncertain recovery candidate."
    )
    return status, "investigate", rationale


def implementation_preserved(flags: dict[str, bool]) -> bool | None:
    if flags["current_implemented"]:
        return True
    if flags["current_partial"]:
        return False
    return None
