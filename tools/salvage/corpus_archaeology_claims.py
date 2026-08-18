"""Exact-span explicit claim extraction for Phase-1 corpus archaeology."""

from __future__ import annotations

import re
from typing import Any

try:
    from tools.salvage.corpus_archaeology_shared import make_id, sha256_text
except ModuleNotFoundError as exc:
    if exc.name not in {"tools", "tools.salvage"}:
        raise
    from corpus_archaeology_shared import make_id, sha256_text

CLAIM_RE = re.compile(
    r"^\s*(?P<label>DECISION|APPROVED|REJECTED|REQUIREMENT|CONSTRAINT|QUESTION|"
    r"TODO|PATCH|RATIONALE|IMPLEMENTED|PARTIAL_IMPLEMENTATION)"
    r"(?:\[(?P<intent>[A-Za-z0-9_.:/-]+)\])?\s*:\s*(?P<body>.+?)\s*$",
    re.IGNORECASE,
)
CLAIM_TYPES = {
    "DECISION": "decision",
    "APPROVED": "approval",
    "REJECTED": "rejection",
    "REQUIREMENT": "requirement",
    "CONSTRAINT": "constraint",
    "QUESTION": "unresolved_question",
    "TODO": "todo",
    "PATCH": "proposed_patch",
    "RATIONALE": "rationale",
    "IMPLEMENTED": "implementation_evidence",
    "PARTIAL_IMPLEMENTATION": "partial_implementation_evidence",
}
IMPLEMENTATION_CLAIM_TYPES = {
    "implementation_evidence",
    "partial_implementation_evidence",
}
IMPLEMENTATION_SOURCE_KINDS = {
    "test": "test_result",
    "code": "implementation_artifact",
    "commit": "implementation_artifact",
    "pull_request": "implementation_artifact",
    "artifact": "implementation_artifact",
}
CREATOR_EVIDENCE_KINDS = {
    "human": "human_statement",
    "assistant": "model_statement",
    "model": "model_statement",
    "system": "system_record",
    "mixed": "mixed_source",
    "unknown": "unknown",
}


def evidence_kind(source: dict[str, Any], claim_type: str) -> str:
    creator_kind = CREATOR_EVIDENCE_KINDS[source["creator_type"]]
    if claim_type not in IMPLEMENTATION_CLAIM_TYPES:
        return creator_kind
    return IMPLEMENTATION_SOURCE_KINDS.get(source["source_type"], creator_kind)


def claim_from_line(
    source: dict[str, Any], line_number: int, line: str
) -> dict[str, Any] | None:
    match = CLAIM_RE.match(line)
    if match is None:
        return None
    claim_type = CLAIM_TYPES[match.group("label").upper()]
    intent = match.group("intent")
    span = {
        "source_id": source["source_id"],
        "source_ref": source["source_ref"],
        "line_start": line_number,
        "line_end": line_number,
        "text_sha256": sha256_text(line),
        "excerpt": line,
    }
    material = {
        "source_id": source["source_id"],
        "line": line_number,
        "claim_type": claim_type,
        "intent_key": intent,
        "text_sha256": span["text_sha256"],
    }
    return {
        "claim_id": make_id("claim", material),
        "claim_type": claim_type,
        "intent_key": intent,
        "claim": match.group("body").strip(),
        "evidence_kind": evidence_kind(source, claim_type),
        "authority_status": source["authority_status"],
        "confidence": source["confidence"],
        "span": span,
    }


def claims_for_source(source: dict[str, Any]) -> list[dict[str, Any]]:
    content = source["_content"]
    if content is None:
        return []
    extracted = (
        claim_from_line(source, line_number, line)
        for line_number, line in enumerate(content.splitlines(), start=1)
    )
    return [claim for claim in extracted if claim is not None]


def sorted_claims(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claims = [claim for source in sources for claim in claims_for_source(source)]
    return sorted(
        claims,
        key=lambda item: (
            item["span"]["source_ref"],
            item["span"]["line_start"],
            item["claim_id"],
        ),
    )


def claims_by_intent(
    claims: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    by_intent: dict[str, list[dict[str, Any]]] = {}
    unkeyed: list[str] = []
    for claim in claims:
        intent = claim["intent_key"]
        if intent is None:
            unkeyed.append(claim["claim_id"])
        else:
            by_intent.setdefault(intent, []).append(claim)
    return by_intent, unkeyed
