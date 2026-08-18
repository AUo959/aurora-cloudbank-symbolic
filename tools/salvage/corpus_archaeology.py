#!/usr/bin/env python3
"""Deterministic, read-only corpus archaeology for prepared source records.

Phase 1 accepts only custody-cleared JSON records. It does not crawl repositories,
open archives, execute recovered content, mutate sources, promote canon, or write
to the Aurora work queue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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

RELATIONSHIPS = {
    "convergent", "successor", "parallel", "merged", "divergent", "superseded",
    "dormant", "lost_in_transition", "orphaned", "uncertain",
}
SOURCE_TYPES = {
    "chat", "document", "issue", "pull_request", "commit", "code", "test",
    "artifact", "report", "unknown",
}
CREATOR_TYPES = {"human", "assistant", "model", "system", "mixed", "unknown"}
AUTHORITY = {"current", "historical", "reference", "draft", "unknown"}
CONTENT_ACCESS = {"released", "metadata_only"}

RANKING_WEIGHTS = {
    "explicit_decision": 0.25,
    "requirement_strength": 0.20,
    "unresolved_commitment": 0.20,
    "implementation_gap": 0.20,
    "recurrence": 0.10,
    "evidence_confidence": 0.05,
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


def _timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise CorpusArchaeologyError("generated_at must be timezone-aware ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CorpusArchaeologyError("generated_at must include timezone information")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CorpusArchaeologyError(f"{name} must be a non-empty string")
    return value.strip()


def _enum(value: Any, name: str, allowed: set[str]) -> str:
    normalized = _string(value, name)
    if normalized not in allowed:
        raise CorpusArchaeologyError(
            f"{name} must be one of: {', '.join(sorted(allowed))}"
        )
    return normalized


def _confidence(value: Any, name: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise CorpusArchaeologyError(f"{name} must be between 0 and 1") from exc
    if not 0.0 <= result <= 1.0:
        raise CorpusArchaeologyError(f"{name} must be between 0 and 1")
    return result


def _source(raw: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CorpusArchaeologyError("every source must be an object")

    source_ref = _string(raw.get("source_ref"), "source_ref")
    source_type = _enum(raw.get("source_type", "unknown"), f"{source_ref}.source_type", SOURCE_TYPES)
    creator_type = _enum(raw.get("creator_type", "unknown"), f"{source_ref}.creator_type", CREATOR_TYPES)
    authority = _enum(raw.get("authority_status", "unknown"), f"{source_ref}.authority_status", AUTHORITY)
    access = _enum(raw.get("content_access", "released"), f"{source_ref}.content_access", CONTENT_ACCESS)
    confidence = _confidence(raw.get("confidence", 1.0), f"{source_ref}.confidence")

    artifact_id = raw.get("artifact_id")
    inventory_ref = raw.get("inventory_report_id")
    platform = raw.get("platform")
    for name, value in (
        ("artifact_id", artifact_id),
        ("inventory_report_id", inventory_ref),
        ("platform", platform),
    ):
        if value is not None:
            _string(value, f"{source_ref}.{name}")

    content = raw.get("content")
    supplied_digest = raw.get("sha256")
    if access == "metadata_only":
        if content not in (None, ""):
            raise CorpusArchaeologyError(f"{source_ref} is metadata_only and must not include content")
        digest = _string(supplied_digest, f"{source_ref}.sha256") if supplied_digest is not None else None
        content = None
    else:
        if not isinstance(content, str):
            raise CorpusArchaeologyError(f"{source_ref} requires string content")
        digest = _sha256(content)
        if supplied_digest is not None and _string(supplied_digest, f"{source_ref}.sha256") != digest:
            raise CorpusArchaeologyError(f"{source_ref}.sha256 does not match prepared content")

    stable_identity = {
        "source_ref": source_ref,
        "sha256": digest,
        "artifact_id": artifact_id,
        "inventory_report_id": inventory_ref,
    }
    return {
        "source_ref": source_ref,
        "source_id": _id("source", stable_identity),
        "title": _string(raw.get("title"), f"{source_ref}.title"),
        "source_type": source_type,
        "platform": platform,
        "creator_type": creator_type,
        "authority_status": authority,
        "confidence": confidence,
        "artifact_id": artifact_id,
        "inventory_report_id": inventory_ref,
        "content_access": access,
        "sha256": digest,
        "_content": content,
    }


def _evidence_kind(source: dict[str, Any], claim_type: str) -> str:
    if claim_type in {"implementation_evidence", "partial_implementation_evidence"}:
        if source["source_type"] == "test":
            return "test_result"
        if source["source_type"] in {"code", "commit", "pull_request", "artifact"}:
            return "implementation_artifact"
    return {
        "human": "human_statement",
        "assistant": "model_statement",
        "model": "model_statement",
        "system": "system_record",
        "mixed": "mixed_source",
        "unknown": "unknown",
    }[source["creator_type"]]


def _claims(source: dict[str, Any]) -> list[dict[str, Any]]:
    if source["_content"] is None:
        return []

    result = []
    for line_number, line in enumerate(source["_content"].splitlines(), start=1):
        match = CLAIM_RE.match(line)
        if not match:
            continue
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
        result.append(
            {
                "claim_id": _id("claim", material),
                "claim_type": claim_type,
                "intent_key": intent,
                "claim": match.group("body").strip(),
                "evidence_kind": _evidence_kind(source, claim_type),
                "authority_status": source["authority_status"],
                "confidence": source["confidence"],
                "span": span,
            }
        )
    return result


def _candidate(intent: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
    types = {item["claim_type"] for item in claims}
    rejected = "rejection" in types
    implemented = any(
        item["claim_type"] == "implementation_evidence"
        and item["evidence_kind"] in {"implementation_artifact", "test_result"}
        for item in claims
    )
    partial = any(
        item["claim_type"] == "partial_implementation_evidence"
        and item["evidence_kind"] in {"implementation_artifact", "test_result"}
        for item in claims
    )
    decision = bool({"approval", "decision"} & types)
    requirement = bool({"requirement", "constraint"} & types)
    unresolved = bool({"todo", "unresolved_question", "proposed_patch"} & types)
    commitment = bool(
        {"approval", "decision", "requirement", "constraint", "todo",
         "unresolved_question", "proposed_patch"} & types
    )

    if rejected:
        status, disposition = "rejected", "reject_with_evidence"
        rationale = "Explicit rejection evidence is present; preserve the record and do not restore automatically."
    elif implemented:
        status, disposition = "implemented", "preserve"
        rationale = "Explicit implementation evidence is present; preserve and verify the current successor."
    elif partial:
        status, disposition = "partial", "investigate"
        rationale = "Only partial implementation evidence is present; investigate intent and capability preservation."
    else:
        status = "approved" if decision else "proposed"
        disposition = "investigate"
        rationale = (
            "An explicit commitment is present without implementation or rejection evidence; preserve for investigation."
            if commitment
            else "No implementation or rejection evidence is established; retain as an uncertain recovery candidate."
        )

    source_refs = sorted({item["span"]["source_ref"] for item in claims})
    source_ids = sorted({item["span"]["source_id"] for item in claims})
    claims = sorted(
        claims,
        key=lambda item: (item["span"]["source_ref"], item["span"]["line_start"], item["claim_id"]),
    )
    gap = 1.0 if commitment and not (implemented or partial or rejected) else 0.0
    components = {
        "explicit_decision": 1.0 if decision else 0.0,
        "requirement_strength": 1.0 if requirement else 0.0,
        "unresolved_commitment": 1.0 if unresolved else 0.0,
        "implementation_gap": gap,
        "recurrence": min(len(source_refs) / 3.0, 1.0),
        "evidence_confidence": sum(item["confidence"] for item in claims) / len(claims),
    }
    score = round(sum(components[name] * weight for name, weight in RANKING_WEIGHTS.items()), 6)
    material = {"intent_key": intent, "claim_ids": [item["claim_id"] for item in claims], "disposition": disposition}

    return {
        "candidate_id": _id("candidate", material),
        "intent_key": intent,
        "source_refs": source_refs,
        "source_ids": source_ids,
        "claim_ids": [item["claim_id"] for item in claims],
        "historical_state": {
            "status": status,
            "explicit_rejection": rejected,
            "implementation_evidence_present": implemented,
            "partial_implementation_evidence_present": partial,
        },
        "preservation": {
            "implementation_preserved": True if implemented else (False if partial else None),
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
            "components": {name: round(value, 6) for name, value in components.items()},
        },
    }


def _relationships(
    hints: Any,
    known_intents: set[str],
    known_sources: set[str],
) -> list[dict[str, Any]]:
    if hints is None:
        return []
    if not isinstance(hints, list):
        raise CorpusArchaeologyError("relationship_hints must be an array")

    result = []
    for index, raw in enumerate(hints):
        if not isinstance(raw, dict):
            raise CorpusArchaeologyError(f"relationship_hints[{index}] must be an object")
        left = _string(raw.get("left_intent_key"), f"relationship_hints[{index}].left_intent_key")
        right = _string(raw.get("right_intent_key"), f"relationship_hints[{index}].right_intent_key")
        relationship = _enum(raw.get("relationship"), f"relationship_hints[{index}].relationship", RELATIONSHIPS)
        rationale = _string(raw.get("rationale"), f"relationship_hints[{index}].rationale")
        if left not in known_intents or right not in known_intents:
            raise CorpusArchaeologyError(f"relationship_hints[{index}] references an unknown intent key")

        refs = raw.get("evidence_source_refs", [])
        if not isinstance(refs, list):
            raise CorpusArchaeologyError(f"relationship_hints[{index}].evidence_source_refs must be an array")
        refs = sorted({_string(item, f"relationship_hints[{index}].evidence_source_refs") for item in refs})
        unknown = set(refs) - known_sources
        if unknown:
            raise CorpusArchaeologyError(
                f"relationship_hints[{index}] references unknown sources: {', '.join(sorted(unknown))}"
            )
        material = {
            "left_intent_key": left,
            "right_intent_key": right,
            "relationship": relationship,
            "rationale": rationale,
            "evidence_source_refs": refs,
        }
        result.append({"relationship_id": _id("relationship", material), **material})

    return sorted(
        result,
        key=lambda item: (
            item["left_intent_key"], item["right_intent_key"],
            item["relationship"], item["relationship_id"],
        ),
    )


def analyze_corpus(corpus: dict[str, Any], *, generated_at: str | None = None) -> dict[str, Any]:
    """Analyze a prepared corpus without mutating source or external state."""
    if not isinstance(corpus, dict):
        raise CorpusArchaeologyError("corpus input must be an object")
    if corpus.get("schema_version") != SCHEMA_VERSION:
        raise CorpusArchaeologyError(f"unsupported corpus schema_version: {corpus.get('schema_version')!r}")

    corpus_id = _string(corpus.get("corpus_id"), "corpus_id")
    raw_sources = corpus.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        raise CorpusArchaeologyError("sources must be a non-empty array")

    sources = [_source(raw) for raw in raw_sources]
    refs = [item["source_ref"] for item in sources]
    if len(refs) != len(set(refs)):
        raise CorpusArchaeologyError("source_ref values must be unique")
    sources.sort(key=lambda item: (item["source_ref"], item["source_id"]))

    claims = [claim for source in sources for claim in _claims(source)]
    claims.sort(key=lambda item: (item["span"]["source_ref"], item["span"]["line_start"], item["claim_id"]))

    by_intent: dict[str, list[dict[str, Any]]] = {}
    unkeyed = []
    for claim in claims:
        if claim["intent_key"] is None:
            unkeyed.append(claim["claim_id"])
        else:
            by_intent.setdefault(claim["intent_key"], []).append(claim)

    candidates = [_candidate(intent, by_intent[intent]) for intent in sorted(by_intent)]
    relationships = _relationships(corpus.get("relationship_hints"), set(by_intent), set(refs))
    public_sources = [{key: value for key, value in item.items() if key != "_content"} for item in sources]

    stable = {
        "corpus_id": corpus_id,
        "sources": public_sources,
        "claims": claims,
        "relationships": relationships,
        "candidates": candidates,
        "unkeyed_claim_ids": sorted(unkeyed),
        "ranking_weights": RANKING_WEIGHTS,
    }
    source_inventory_ref = corpus.get("source_inventory_ref")
    if source_inventory_ref is not None:
        source_inventory_ref = _string(source_inventory_ref, "source_inventory_ref")

    return {
        "schema_version": SCHEMA_VERSION,
        "report_id": f"corpus-report:{hashlib.sha256(_canonical_bytes(stable)).hexdigest()}",
        "generated_at": _timestamp(generated_at),
        "corpus_id": corpus_id,
        "source_inventory_ref": source_inventory_ref,
        "read_only": True,
        "mutation_performed": False,
        "analysis_profile": "explicit_markers_v1",
        "ranking_model": {"name": "explainable_relevance_v1", "weights": RANKING_WEIGHTS},
        "sources": public_sources,
        "claims": claims,
        "relationships": relationships,
        "candidates": candidates,
        "unkeyed_claim_ids": sorted(unkeyed),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Corpus Archaeology Report", "",
        f"- Report: `{report['report_id']}`",
        f"- Corpus: `{report['corpus_id']}`",
        f"- Sources: {len(report['sources'])}",
        f"- Claims: {len(report['claims'])}",
        f"- Candidates: {len(report['candidates'])}", "",
        "## Recovery candidates", "",
    ]
    if not report["candidates"]:
        lines.append("_No keyed recovery candidates were extracted._")
    for item in report["candidates"]:
        lines.extend([
            f"### `{item['intent_key']}`", "",
            f"- Disposition: `{item['recovery']['disposition']}`",
            f"- Historical state: `{item['historical_state']['status']}`",
            f"- Relevance: `{item['ranking']['relevance_score']:.6f}`",
            f"- Sources: {', '.join(f'`{source}`' for source in item['source_refs'])}",
            f"- Rationale: {item['recovery']['rationale']}", "",
        ])
    if report["unkeyed_claim_ids"]:
        lines.extend([
            "## Unkeyed claims", "",
            "These claims retain provenance but are not promoted because no deterministic intent key was supplied.", "",
            *[f"- `{claim_id}`" for claim_id in report["unkeyed_claim_ids"]],
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def _write_new(path: Path, payload: str) -> None:
    path = path.resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise CorpusArchaeologyError(f"output already exists and will not be replaced: {path}") from exc
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a custody-cleared prepared corpus without mutation")
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--generated-at")
    args = parser.parse_args()

    try:
        corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
        report = analyze_corpus(corpus, generated_at=args.generated_at)
        payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.output:
            if args.output.resolve(strict=False) == args.corpus.resolve():
                raise CorpusArchaeologyError("output path must not replace the source corpus")
            _write_new(args.output, payload)
        else:
            print(payload, end="")
        if args.markdown_output:
            if args.markdown_output.resolve(strict=False) == args.corpus.resolve():
                raise CorpusArchaeologyError("markdown output path must not replace the source corpus")
            _write_new(args.markdown_output, render_markdown(report))
    except (OSError, json.JSONDecodeError, CorpusArchaeologyError) as exc:
        print(f"INVALID: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
