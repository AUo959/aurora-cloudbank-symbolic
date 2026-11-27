"""Candidate relevance and report projection for Phase-1 corpus archaeology."""

from __future__ import annotations

from typing import Any

from tools.salvage.corpus_archaeology_candidate_state import (
    candidate_flags,
    candidate_state,
    implementation_preserved,
)
from tools.salvage.corpus_archaeology_shared import make_id

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


def _relevance_score(components: dict[str, float]) -> float:
    weighted = (
        components[name] * weight for name, weight in RANKING_WEIGHTS.items()
    )
    return round(sum(weighted), 6)


def build_candidate(intent: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
    """Build one deterministic recovery candidate from keyed claims."""
    claims = _canonical_claims(claims)
    flags = candidate_flags(claims)
    status, disposition, rationale = candidate_state(flags)
    source_refs = sorted({item["span"]["source_ref"] for item in claims})
    source_ids = sorted({item["span"]["source_id"] for item in claims})
    components = _components(flags, source_refs, claims)
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
            "implementation_preserved": implementation_preserved(flags),
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
            "relevance_score": _relevance_score(components),
            "components": {
                name: round(value, 6) for name, value in components.items()
            },
        },
    }
