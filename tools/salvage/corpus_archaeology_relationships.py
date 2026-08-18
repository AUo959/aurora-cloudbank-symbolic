"""Explicit relationship validation for Phase-1 corpus archaeology."""

from __future__ import annotations

from typing import Any

from tools.salvage.corpus_archaeology_shared import CorpusArchaeologyError, make_id


def _known_intents(
    raw: dict[str, Any], known_intents: set[str], index: int
) -> tuple[str, str]:
    left = raw["left_intent_key"]
    right = raw["right_intent_key"]
    if {left, right} - known_intents:
        raise CorpusArchaeologyError(
            f"relationship_hints[{index}] references an unknown intent key"
        )
    return left, right


def _known_sources(
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


def build_relationship(
    raw: dict[str, Any],
    index: int,
    known_intents: set[str],
    known_sources: set[str],
) -> dict[str, Any]:
    left, right = _known_intents(raw, known_intents, index)
    refs = _known_sources(raw, known_sources, index)
    material = {
        "left_intent_key": left,
        "right_intent_key": right,
        "relationship": raw["relationship"],
        "rationale": raw["rationale"],
        "evidence_source_refs": refs,
    }
    return {"relationship_id": make_id("relationship", material), **material}


def build_relationships(
    hints: list[dict[str, Any]] | None,
    known_intents: set[str],
    known_sources: set[str],
) -> list[dict[str, Any]]:
    result = [
        build_relationship(raw, index, known_intents, known_sources)
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
