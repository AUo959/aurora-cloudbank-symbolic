"""Pure candidate-state and relevance logic for Phase-1 corpus archaeology."""

from __future__ import annotations

from typing import Any

IMPLEMENTATION_EVIDENCE_KINDS = {"implementation_artifact", "test_result"}
RANKING_WEIGHTS = {
    "explicit_decision": 0.25,
    "requirement_strength": 0.20,
    "unresolved_commitment": 0.20,
    "implementation_gap": 0.20,
    "recurrence": 0.10,
    "evidence_confidence": 0.05,
}


def _canonical_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        claims,
        key=lambda item: (
            item["span"]["source_ref"],
            item["span"]["line_start"],
            item["claim_id"],
        ),
    )


def _human_claim_types(claims: list[dict[str, Any]]) -> set[str]:
    return {
        item["claim_type"]
        for item in claims
        if item["evidence_kind"] == "human_statement"
    }


def _is_implementation_claim(
    item: dict[str, Any], claim_type: str, authority: str | None
) -> bool:
    type_matches = item["claim_type"] == claim_type
    evidence_matches = item["evidence_kind"] in IMPLEMENTATION_EVIDENCE_KINDS
    authority_matches = authority is None or item["authority_status"] == authority
    return type_matches and evidence_matches and authority_matches


def _has_implementation_claim(
    claims: list[dict[str, Any]], claim_type: str, authority: str | None = None
) -> bool:
    return any(
        _is_implementation_claim(item, claim_type, authority) for item in claims
    )


def _candidate_flags(claims: list[dict[str, Any]]) -> dict[str, bool]:
    human_types = _human_claim_types(claims)
    commitment_types = {
        "approval",
        "decision",
        "requirement",
        "constraint",
        "todo",
        "unresolved_question",
        "proposed_patch",
    }
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
        "commitment": bool(commitment_types & human_types),
    }


def _candidate_state(flags: dict[str, bool]) -> tuple[str, str, str]:
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


def _implementation_gap(flags: dict[str, bool]) -> float:
    has_resolution = flags["implemented"] or flags["partial"] or flags["rejected"]
    return float(flags["commitment"] and not has_resolution)


def _components(
    flags: dict[str, bool], source_refs: list[str], claims: list[dict[str, Any]]
) -> dict[str, float]:
    return {
        "explicit_decision": float(flags["decision"]),
        "requirement_strength": float(flags["requirement"]),
        "unresolved_commitment": float(flags["unresolved"]),
        "implementation_gap": _implementation_gap(flags),
        "recurrence": min(len(source_refs) / 3.0, 1.0),
        "evidence_confidence": sum(item["confidence"] for item in claims) / len(claims),
    }


def _implementation_preserved(flags: dict[str, bool]) -> bool | None:
    if flags["current_implemented"]:
        return True
    if flags["current_partial"]:
        return False
    return None


def build_candidate(
    intent: str,
    claims: list[dict[str, Any]],
    make_id,
) -> dict[str, Any]:
    """Build one deterministic recovery candidate from keyed claims."""
    claims = _canonical_claims(claims)
    flags = _candidate_flags(claims)
    status, disposition, rationale = _candidate_state(flags)
    source_refs = sorted({item["span"]["source_ref"] for item in claims})
    source_ids = sorted({item["span"]["source_id"] for item in claims})
    components = _components(flags, source_refs, claims)
    score = round(
        sum(components[name] * weight for name, weight in RANKING_WEIGHTS.items()),
        6,
    )
    claim_ids = [item["claim_id"] for item in claims]
    candidate_id = make_id(
        "candidate",
        {
            "intent_key": intent,
            "claim_ids": claim_ids,
            "disposition": disposition,
        },
    )
    return {
        "candidate_id": candidate_id,
        "intent_key": intent,
        "source_refs": source_refs,
        "source_ids": source_ids,
        "claim_ids": claim_ids,
        "historical_state": {
            "status": status,
            "explicit_rejection": flags["rejected"],
            "implementation_evidence_present": flags["implemented"],
            "partial_implementation_evidence_present": flags["partial"],
        },
        "preservation": {
            "implementation_preserved": _implementation_preserved(flags),
            "capability_preserved": None,
            "intent_preserved": None,
            "intent_delta": None,
        },
        "recovery": {
            "disposition": disposition,
            "rationale": rationale,
            "confidence": round(components["evidence_confidence"], 6),
            "dependencies": [],
        },
        "ranking": {
            "relevance_score": score,
            "components": {
                name: round(value, 6) for name, value in components.items()
            },
        },
    }
