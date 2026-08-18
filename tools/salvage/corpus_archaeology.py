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
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema

SCHEMA_VERSION = "0.1.0"
INPUT_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "salvage"
    / "corpus_archaeology_input.schema.json"
)

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
IMPLEMENTATION_EVIDENCE_KINDS = {"implementation_artifact", "test_result"}
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


def _load_input_validator() -> jsonschema.Draft202012Validator:
    try:
        schema = json.loads(INPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError) as exc:
        raise CorpusArchaeologyError(
            "committed prepared-corpus input schema is unavailable or invalid"
        ) from exc
    return jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )


def _first_schema_error(
    validator: jsonschema.Draft202012Validator,
    corpus: dict[str, Any],
) -> jsonschema.ValidationError | None:
    errors = sorted(
        validator.iter_errors(corpus),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    return errors[0] if errors else None


def _schema_error_message(error: jsonschema.ValidationError) -> str:
    path = ".".join(str(part) for part in error.absolute_path) or "<root>"
    detail = (
        error.message
        if error.validator in {"required", "additionalProperties"}
        else f"violates {error.validator}"
    )
    return f"input schema validation failed at {path}: {detail}"


def _validate_input_contract(corpus: dict[str, Any]) -> None:
    """Bind runtime validation to the committed prepared-corpus JSON Schema."""
    error = _first_schema_error(_load_input_validator(), corpus)
    if error is not None:
        raise CorpusArchaeologyError(_schema_error_message(error))


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _id(prefix: str, value: Any, length: int = 24) -> str:
    return f"{prefix}:{hashlib.sha256(_canonical_bytes(value)).hexdigest()[:length]}"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CorpusArchaeologyError(f"{name} must be a non-empty string")
    return value.strip()


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


def _human_claim_types(claims: list[dict[str, Any]]) -> set[str]:
    return {
        item["claim_type"]
        for item in claims
        if item["evidence_kind"] == "human_statement"
    }


def _matches_implementation_claim(
    item: dict[str, Any], claim_type: str, authority: str | None
) -> bool:
    if item["claim_type"] != claim_type:
        return False
    if item["evidence_kind"] not in IMPLEMENTATION_EVIDENCE_KINDS:
        return False
    return authority is None or item["authority_status"] == authority


def _has_implementation_claim(
    claims: list[dict[str, Any]], claim_type: str, authority: str | None = None
) -> bool:
    return any(
        _matches_implementation_claim(item, claim_type, authority) for item in claims
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


def _candidate_conflict(flags: dict[str, bool]) -> bool:
    return flags["rejected"] and (flags["implemented"] or flags["partial"])


def _default_candidate_state(flags: dict[str, bool]) -> tuple[str, str, str]:
    status = "approved" if flags["decision"] else "proposed"
    rationale = (
        "An explicit human commitment is present without implementation or "
        "rejection evidence; preserve for investigation."
        if flags["commitment"]
        else "No authoritative commitment, implementation, or rejection evidence "
        "is established; retain as an uncertain recovery candidate."
    )
    return status, "investigate", rationale


def _state_conflict(_: dict[str, bool]) -> tuple[str, str, str]:
    return (
        "unknown",
        "investigate",
        "Explicit human rejection and implementation evidence coexist; preserve both "
        "histories and investigate chronology, scope, and authority.",
    )


def _state_rejected(_: dict[str, bool]) -> tuple[str, str, str]:
    return (
        "rejected",
        "reject_with_evidence",
        "Explicit human rejection evidence is present; preserve the record and do not "
        "restore automatically.",
    )


def _state_implemented(_: dict[str, bool]) -> tuple[str, str, str]:
    return (
        "implemented",
        "preserve",
        "Implementation evidence is present; preserve the implementation record and "
        "verify whether a current successor remains.",
    )


def _state_partial(_: dict[str, bool]) -> tuple[str, str, str]:
    return (
        "partial",
        "investigate",
        "Only partial implementation evidence is present; investigate intent and "
        "capability preservation.",
    )


def _candidate_state(flags: dict[str, bool]) -> tuple[str, str, str]:
    rules: tuple[
        tuple[Callable[[dict[str, bool]], bool], Callable[[dict[str, bool]], tuple[str, str, str]]],
        ...,
    ] = (
        (_candidate_conflict, _state_conflict),
        (lambda state: state["rejected"], _state_rejected),
        (lambda state: state["implemented"], _state_implemented),
        (lambda state: state["partial"], _state_partial),
    )
    for predicate, result in rules:
        if predicate(flags):
            return result(flags)
    return _default_candidate_state(flags)


def _implementation_gap(flags: dict[str, bool]) -> float:
    has_resolution = flags["implemented"] or flags["partial"] or flags["rejected"]
    return float(flags["commitment"] and not has_resolution)


def _candidate_components(
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


def _sorted_candidate_claims(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        claims,
        key=lambda item: (
            item["span"]["source_ref"],
            item["span"]["line_start"],
            item["claim_id"],
        ),
    )


def _candidate(intent: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
    claims = _sorted_candidate_claims(claims)
    flags = _candidate_flags(claims)
    status, disposition, rationale = _candidate_state(flags)
    source_refs = sorted({item["span"]["source_ref"] for item in claims})
    source_ids = sorted({item["span"]["source_id"] for item in claims})
    components = _candidate_components(flags, source_refs, claims)
    score = round(
        sum(components[name] * weight for name, weight in RANKING_WEIGHTS.items()),
        6,
    )
    material = {
        "intent_key": intent,
        "claim_ids": [item["claim_id"] for item in claims],
        "disposition": disposition,
    }
    return {
        "candidate_id": _id("candidate", material),
        "intent_key": intent,
        "source_refs": source_refs,
        "source_ids": source_ids,
        "claim_ids": [item["claim_id"] for item in claims],
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


def _known_relationship_intents(
    raw: dict[str, Any], known_intents: set[str], index: int
) -> tuple[str, str]:
    left = raw["left_intent_key"]
    right = raw["right_intent_key"]
    unknown = {left, right} - known_intents
    if unknown:
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
    items = hints or []
    result = [
        _relationship(raw, index, known_intents, known_sources)
        for index, raw in enumerate(items)
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
        target = unkeyed if intent is None else by_intent.setdefault(intent, [])
        target.append(claim["claim_id"] if intent is None else claim)
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


def analyze_corpus(
    corpus: dict[str, Any], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Analyze a prepared corpus without mutating source or external state."""
    if not isinstance(corpus, dict):
        raise CorpusArchaeologyError("corpus input must be an object")
    _validate_input_contract(corpus)
    corpus_id = _string(corpus["corpus_id"], "corpus_id")
    source_inventory_ref = corpus.get("source_inventory_ref")
    if source_inventory_ref is not None:
        source_inventory_ref = _string(source_inventory_ref, "source_inventory_ref")

    sources = _normalized_sources(corpus["sources"])
    claims = _sorted_claims(sources)
    by_intent, unkeyed = _claims_by_intent(claims)
    candidates = [
        _candidate(intent, by_intent[intent]) for intent in sorted(by_intent)
    ]
    refs = {item["source_ref"] for item in sources}
    relationships = _relationships(
        corpus.get("relationship_hints"), set(by_intent), refs
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


def _write_new(path: Path, payload: str) -> None:
    path = path.resolve(strict=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise CorpusArchaeologyError(
            f"output already exists and will not be replaced: {path}"
        ) from exc
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a custody-cleared prepared corpus without mutation"
    )
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--generated-at")
    return parser


def _write_optional_output(
    output: Path | None,
    source: Path,
    payload: str,
    label: str,
) -> None:
    if output is None:
        return
    if output.resolve(strict=False) == source.resolve():
        raise CorpusArchaeologyError(f"{label} path must not replace the source corpus")
    _write_new(output, payload)


def _emit_outputs(args: argparse.Namespace, report: dict[str, Any]) -> None:
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output is None:
        print(payload, end="")
    _write_optional_output(args.output, args.corpus, payload, "output")
    _write_optional_output(
        args.markdown_output,
        args.corpus,
        render_markdown(report),
        "markdown output",
    )


def _execute(args: argparse.Namespace) -> None:
    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    report = analyze_corpus(corpus, generated_at=args.generated_at)
    _emit_outputs(args, report)


def main() -> int:
    args = _build_parser().parse_args()
    try:
        _execute(args)
    except (OSError, json.JSONDecodeError, CorpusArchaeologyError) as exc:
        print(f"INVALID: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())