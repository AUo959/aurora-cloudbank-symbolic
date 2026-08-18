"""Semantic orchestration and rendering for deterministic corpus archaeology."""

from __future__ import annotations

import hashlib
from typing import Any

from tools.salvage.corpus_archaeology_candidates import (
    RANKING_WEIGHTS,
    build_candidate,
)
from tools.salvage.corpus_archaeology_claims import claims_by_intent, sorted_claims
from tools.salvage.corpus_archaeology_relationships import build_relationships
from tools.salvage.corpus_archaeology_shared import (
    SCHEMA_VERSION,
    CorpusArchaeologyError,
    canonical_bytes,
    normalize_timestamp,
    semantic_string,
)
from tools.salvage.corpus_archaeology_sources import normalize_sources, public_sources


def _stable_material(
    corpus_id: str,
    source_inventory_ref: str | None,
    sources: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    unkeyed: list[str],
) -> dict[str, Any]:
    return {
        "corpus_id": corpus_id,
        "source_inventory_ref": source_inventory_ref,
        "sources": sources,
        "claims": claims,
        "relationships": relationships,
        "candidates": candidates,
        "unkeyed_claim_ids": sorted(unkeyed),
        "ranking_weights": RANKING_WEIGHTS,
    }


def _report_id(stable: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_bytes(stable)).hexdigest()
    return f"corpus-report:{digest}"


def _build_report(
    *,
    corpus_id: str,
    source_inventory_ref: str | None,
    generated_at: str | None,
    sources: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    unkeyed: list[str],
) -> dict[str, Any]:
    stable = _stable_material(
        corpus_id,
        source_inventory_ref,
        sources,
        claims,
        relationships,
        candidates,
        unkeyed,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "report_id": _report_id(stable),
        "generated_at": normalize_timestamp(generated_at),
        "corpus_id": corpus_id,
        "source_inventory_ref": source_inventory_ref,
        "read_only": True,
        "mutation_performed": False,
        "analysis_profile": "explicit_markers_v1",
        "ranking_model": {
            "name": "explainable_relevance_v1",
            "weights": RANKING_WEIGHTS,
        },
        "sources": sources,
        "claims": claims,
        "relationships": relationships,
        "candidates": candidates,
        "unkeyed_claim_ids": sorted(unkeyed),
    }


def analyze_validated_corpus(
    corpus: dict[str, Any], *, generated_at: str | None = None
) -> dict[str, Any]:
    """Analyze a structurally validated prepared corpus without external mutation."""
    corpus_id = semantic_string(corpus["corpus_id"], "corpus_id")
    source_inventory_ref = corpus.get("source_inventory_ref")
    if source_inventory_ref is not None:
        source_inventory_ref = semantic_string(
            source_inventory_ref, "source_inventory_ref"
        )

    normalized_sources = normalize_sources(corpus["sources"])
    claims = sorted_claims(normalized_sources)
    by_intent, unkeyed = claims_by_intent(claims)
    candidates = [
        build_candidate(intent, by_intent[intent]) for intent in sorted(by_intent)
    ]
    relationships = build_relationships(
        corpus.get("relationship_hints"),
        set(by_intent),
        {item["source_ref"] for item in normalized_sources},
    )
    return _build_report(
        corpus_id=corpus_id,
        source_inventory_ref=source_inventory_ref,
        generated_at=generated_at,
        sources=public_sources(normalized_sources),
        claims=claims,
        relationships=relationships,
        candidates=candidates,
        unkeyed=unkeyed,
    )


def _candidate_lines(item: dict[str, Any]) -> list[str]:
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


def _candidate_section(candidates: list[dict[str, Any]]) -> list[str]:
    if not candidates:
        return ["_No keyed recovery candidates were extracted._"]
    return [line for item in candidates for line in _candidate_lines(item)]


def _unkeyed_section(claim_ids: list[str]) -> list[str]:
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
        *_candidate_section(report["candidates"]),
        *_unkeyed_section(report["unkeyed_claim_ids"]),
    ]
    return "\n".join(lines).rstrip() + "\n"
