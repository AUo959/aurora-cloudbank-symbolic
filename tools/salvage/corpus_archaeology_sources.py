"""Prepared-source normalization for deterministic corpus archaeology."""

from __future__ import annotations

from typing import Any

from tools.salvage.corpus_archaeology_shared import (
    CorpusArchaeologyError,
    make_id,
    semantic_string,
    sha256_text,
)


def _validate_optional_strings(source_ref: str, raw: dict[str, Any]) -> None:
    for name in ("artifact_id", "inventory_report_id", "platform"):
        value = raw.get(name)
        if value is not None:
            semantic_string(value, f"{source_ref}.{name}")


def _released_content(raw: dict[str, Any], source_ref: str) -> tuple[str, str]:
    content = raw["content"]
    digest = sha256_text(content)
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


def normalize_source(raw: dict[str, Any]) -> dict[str, Any]:
    source_ref = semantic_string(raw["source_ref"], "source_ref")
    _validate_optional_strings(source_ref, raw)
    content, digest = _prepared_content(raw, source_ref)
    artifact_id = raw.get("artifact_id")
    inventory_ref = raw.get("inventory_report_id")
    identity = {
        "source_ref": source_ref,
        "sha256": digest,
        "artifact_id": artifact_id,
        "inventory_report_id": inventory_ref,
    }
    return {
        "source_ref": source_ref,
        "source_id": make_id("source", identity),
        "title": semantic_string(raw["title"], f"{source_ref}.title"),
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


def normalize_sources(raw_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sources = [normalize_source(raw) for raw in raw_sources]
    refs = [item["source_ref"] for item in sources]
    if len(refs) != len(set(refs)):
        raise CorpusArchaeologyError("source_ref values must be unique")
    return sorted(sources, key=lambda item: (item["source_ref"], item["source_id"]))


def public_sources(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {key: value for key, value in item.items() if key != "_content"}
        for item in sources
    ]
