"""Pure semantic core for deterministic Phase-1 corpus archaeology."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

try:
    from tools.salvage.corpus_archaeology_candidates import (
        RANKING_WEIGHTS,
        build_candidate,
    )
except ModuleNotFoundError as exc:
    if exc.name not in {"tools", "tools.salvage"}:
        raise
    from corpus_archaeology_candidates import RANKING_WEIGHTS, build_candidate

SCHEMA_VERSION = "0.1.0"
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


class CorpusArchaeologyError(ValueError):
    """Prepared corpus is invalid or violates a Phase-1 safety boundary."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _id(prefix: str, value: Any, length: int = 24) -> str:
    return f"{prefix}:{hashlib.sha256(_canonical_bytes(value)).hexdigest()[:length]}"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CorpusArchaeologyError(f"{name} must be a non-empty string")
    return value.strip()


def _parse_timestamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise CorpusArchaeologyError(
            "generated_at must be timezone-aware ISO-8601"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CorpusArchaeologyError("generated_at must include timezone information")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return _parse_timestamp(value)


def _validate_optional_source_strings(source_ref: str, raw: dict[str, Any]) -> None:
    for name in ("artifact_id", "inventory_report_id", "platform"):
        value = raw.get(name)
        if value is not None:
            _string(value, f"{source_ref}.{name}")


def _released_content(raw: dict[str, Any], source_ref: str) -> tuple[str, str]:
    content = raw["content"]
    digest = _sha256(content)
    supplied_digest = raw.get("sha256")
    if supplied_digest is not None and supplied_digest != digest:
        raise CorpusArchaeologyError(
            f"{source_ref}.sha256 does not match prepared content"
        )
    return content, digest


def _prepared_content(
    raw: dict[str, Any], source_ref: str
) -> tuple[str | None, str | None]:
    if raw["content_access"] == "released":
        return _released_content(raw, source_ref)
    return None, raw.get("sha256")


def _source(raw: dict[str, Any]) -> dict[str, Any]:
    source_ref = _string(raw["source_ref"], "source_ref")
    _validate_optional_source_strings(source_ref, raw)
    content, digest = _prepared_content(raw, source_ref)
    artifact_id = raw.get("artifact_id")
    inventory_ref = raw.get("inventory_report_id")
    stable_identity = {
        "source_ref": source_ref,
        "sha256": digest,
        "artifact_id": artifact_id,
        "inventory_report_id": inventory_ref,
    }
    return {
        "source_ref": source_ref,
        "source_id": _id("source", stable_identity),
        "title": _string(raw["title"], f"{source_ref}.title"),
        "source_type": raw["source_type"],
        "platform": raw.get("platform"),
        "creator_type": raw["creator_type"],
        "authority_status": raw["authority_status"],
        "confidence": float(raw.get("confidence", 1.0)),
        "artifact_id": artifact_id,
        "inventory_report_id": inventory_ref,
        "content_access": raw["content_access"],
        "sha256": digest,
        "_content": content,
    }


def _evidence_kind(source: dict[str, Any], claim_type: str) -> str:
    creator_kind = CREATOR_EVIDENCE_KINDS[source["creator_type"]]
    if claim_type not in IMPLEMENTATION_CLAIM_TYPES:
        return creator_kind
    return IMPLEMENTATION_SOURCE_KINDS.get(source["source_type"], creator_kind)


def _claim_from_line(
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
        "text_sha256": _sha256(line),
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
        "claim_id": _id("claim", material),
        "claim_type": claim_type,
        "intent_key": intent,
        "claim": match.group("body").strip(),
        "evidence_kind": _evidence_kind(source, claim_type),
        "authority_status": source["authority_status"],
        "confidence": source["confidence"],
        "span": span,
    }


def _claims(source: dict[str, Any]) -> list[dict[str, Any]]:
    content = source["_content"]
    if content is None:
        return []
    extracted = (
        _claim_from_line(source, line_number, line)
        for line_number, line in enumerate(content.splitlines(), start=1)
    )
    return [claim for claim in extracted if claim is not None]


def _known_relationship_intents(
    raw: dict[str, Any], known_intents: set[str], index: int
) -> tuple[str, str]:
    left = raw["left_intent_key"]
    right = raw["right_intent_key"]
    if {left, right} - known_intents:
        raise CorpusArchaeologyError(
            f"relationship_hints[{index}] references an unknown intent key"
        )
    return left, right


def _known_relationship_sources(
    raw: dict[str, Any], known_sources: set[str], index: int
) -> list[str]:
    refs = sorted(set(raw["evidence_source_refs"]))
    unknown = set(refs) - known_sources
    if unknown:
        raise CorpusArchaeologyError(
            f"relationship_hints[{index}] references unknown sources: "
            f"{', '.join(sorted(unknown))}"
        )
    return refs


def _relationship(
    raw: dict[str, Any],
    index: int,
    known_intents: set[str],
    known_sources: set[str],
) -> dict[str, Any]:
    left, right = _known_relationship_intents(raw, known_intents, index)
    refs = _known_relationship_sources(raw, known_sources, index)
    material = {
        "left_intent_key": left,
        "right_intent_key": right,
        "relationship": raw["relationship"],
        "rationale": raw["rationale"],
        "evidence_source_refs": refs,
    }
    return {"relationship_id": _id("relationship", material), **material}


def _relationships(
    hints: list[dict[str, Any]] | None,
    known_intents: set[str],
    known_sources: set[str],
) -> list[dict[str, Any]]:
    result = [
        _relationship(raw, index, known_intents, known_sources)
        for index, raw in enumerate(hints or [])
    ]
    return sorted(
        result,
        key=lambda item: (
            item["left_intent_key"],
            item["right_intent_key"],
            item["relationship"],
            item["relationship_id"],
        ),
    )


def _normalized_sources(raw_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = [_source(raw) for raw in raw_sources]
    refs = [item["source_ref"] for item in sources]
    if len(refs) != len(set(refs)):
        raise CorpusArchaeologyError("source_ref values must be unique")
    return sorted(sources, key=lambda item: (item["source_ref"], item["source_id"]))


def _sorted_claims(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claims = [claim for source in sources for claim in _claims(source)]
    return sorted(
        claims,
        key=lambda item: (
            item["span"]["source_ref"],
            item["span"]["line_start"],
            item["claim_id"],
        ),
    )


def _claims_by_intent(
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


def _public_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {key: value for key, value in item.items() if key != "_content"}
        for item in sources
    ]


def _stable_report_material(
    corpus_id: str,
    source_inventory_ref: str | None,
    public_sources: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    unkeyed: list[str],
) -> dict[str, Any]:
    return {
        "corpus_id": corpus_id,
        "source_inventory_ref": source_inventory_ref,
        "sources": public_sources,
        "claims": claims,
        "relationships": relationships,
        "candidates": candidates,
        "unkeyed_claim_ids": sorted(unkeyed),
        "ranking_weights": RANKING_WEIGHTS,
    }


def _report(
    *,
    corpus_id: str,
    source_inventory_ref: str | None,
    generated_at: str | None,
    public_sources: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    unkeyed: list[str],
) -> dict[str, Any]:
    stable = _stable_report_material(
        corpus_id,
        source_inventory_ref,
        public_sources,
        claims,
        relationships,
        candidates,
        unkeyed,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "report_id": (
            "corpus-report:"
            f"{hashlib.sha256(_canonical_bytes(stable)).hexdigest()}"
        ),
        "generated_at": _timestamp(generated_at),
        "corpus_id": corpus_id,
        "source_inventory_ref": source_inventory_ref,
        "read_only": True,
        "mutation_performed": False,
        "analysis_profile": "explicit_markers_v1",
        "ranking_model": {
            "name": "explainable_relevance_v1",
            "weights": RANKING_WEIGHTS,
        },
        "sources": public_sources,
        "claims": claims,
        "relationships": relationships,
        "candidates": candidates,
        "unkeyed_claim_ids": sorted(unkeyed),
    }


def analyze_validated_corpus(
    corpus: dict[str, Any], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Analyze a structurally validated prepared corpus without external mutation."""
    corpus_id = _string(corpus["corpus_id"], "corpus_id")
    source_inventory_ref = corpus.get("source_inventory_ref")
    if source_inventory_ref is not None:
        source_inventory_ref = _string(source_inventory_ref, "source_inventory_ref")

    sources = _normalized_sources(corpus["sources"])
    claims = _sorted_claims(sources)
    by_intent, unkeyed = _claims_by_intent(claims)
    candidates = [
        build_candidate(intent, by_intent[intent], _id) for intent in sorted(by_intent)
    ]
    relationships = _relationships(
        corpus.get("relationship_hints"),
        set(by_intent),
        {item["source_ref"] for item in sources},
    )
    return _report(
        corpus_id=corpus_id,
        source_inventory_ref=source_inventory_ref,
        generated_at=generated_at,
        public_sources=_public_sources(sources),
        claims=claims,
        relationships=relationships,
        candidates=candidates,
        unkeyed=unkeyed,
    )


def _candidate_markdown_lines(item: dict[str, Any]) -> list[str]:
    return [
        f"### `{item['intent_key']}`",
        "",
        f"- Disposition: `{item['recovery']['disposition']}`",
        f"- Historical state: `{item['historical_state']['status']}`",
        f"- Relevance: `{item['ranking']['relevance_score']:.6f}`",
        f"- Sources: {', '.join(f'`{source}`' for source in item['source_refs'])}",
        f"- Rationale: {item['recovery']['rationale']}",
        "",
    ]


def _candidate_markdown_section(candidates: list[dict[str, Any]]) -> list[str]:
    if not candidates:
        return ["_No keyed recovery candidates were extracted._"]
    return [line for item in candidates for line in _candidate_markdown_lines(item)]


def _unkeyed_markdown_section(claim_ids: list[str]) -> list[str]:
    if not claim_ids:
        return []
    return [
        "## Unkeyed claims",
        "",
        "These claims retain provenance but are not promoted because no deterministic "
        "intent key was supplied.",
        "",
        *[f"- `{claim_id}`" for claim_id in claim_ids],
        "",
    ]


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Corpus Archaeology Report",
        "",
        f"- Report: `{report['report_id']}`",
        f"- Corpus: `{report['corpus_id']}`",
        f"- Sources: {len(report['sources'])}",
        f"- Claims: {len(report['claims'])}",
        f"- Candidates: {len(report['candidates'])}",
        "",
        "## Recovery candidates",
        "",
        *_candidate_markdown_section(report["candidates"]),
        *_unkeyed_markdown_section(report["unkeyed_claim_ids"]),
    ]
    return "\n".join(lines).rstrip() + "\n"
