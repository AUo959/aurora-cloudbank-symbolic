"""
QGIA Knowledge Bridge

Loads a knowledge index (produced by ``knowledge_indexer``) and provides
lookup / enrichment functions for the QSFE forecast engine.

Ref: Aurora Constellation Architecture Proposal v1.0.0 — Gap 5

This module is designed to work alongside the QSFE module on the
``feat/qgia-forecast-engine`` branch.  It reads a knowledge-index.json and
can enrich forecast results with cross-referenced knowledge documents.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Data holder
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeBridge:
    """In-memory searchable knowledge index."""

    documents: list[dict[str, Any]] = field(default_factory=list)
    _by_id: dict[str, dict[str, Any]] = field(default_factory=dict, repr=False)
    _by_domain: dict[str, list[dict[str, Any]]] = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    @classmethod
    def from_file(cls, path: str | Path) -> "KnowledgeBridge":
        """Load a knowledge-index.json file."""
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KnowledgeBridge":
        """Build the bridge from an already-parsed index dict."""
        docs = data.get("documents", [])
        bridge = cls(documents=docs)
        for doc in docs:
            bridge._by_id[doc["id"]] = doc
            domain = doc.get("domain", "hybrid")
            bridge._by_domain.setdefault(domain, []).append(doc)
        return bridge

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def search_by_domain(self, domain: str) -> list[dict[str, Any]]:
        """Return all documents matching the given domain."""
        return list(self._by_domain.get(domain, []))

    def search_by_keyword(self, keyword: str) -> list[dict[str, Any]]:
        """Return documents whose title, summary, or tags contain *keyword*."""
        keyword_lower = keyword.lower()
        results: list[dict[str, Any]] = []
        for doc in self.documents:
            searchable = " ".join([
                doc.get("title", ""),
                doc.get("summary", ""),
                " ".join(doc.get("tags", [])),
            ]).lower()
            if keyword_lower in searchable:
                results.append(doc)
        return results

    def get_document(self, doc_id: str) -> dict[str, Any] | None:
        """Return a single document by its ID, or None if not found."""
        return self._by_id.get(doc_id)

    # ------------------------------------------------------------------
    # QSFE integration
    # ------------------------------------------------------------------

    def enrich_forecast_with_knowledge(
        self,
        forecast_result: dict[str, Any],
        knowledge_index: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Cross-reference forecast evidence with knowledge documents.

        For each evidence fragment in every tier, if its ``knowledge_ref``
        matches a document ID in the index, the fragment is annotated with
        the document title, domain, and path.

        Args:
            forecast_result: A dict conforming to ``forecast-result.schema.json``.
            knowledge_index: Optional override index dict.  If ``None``, uses
                the documents already loaded into this bridge.

        Returns:
            The enriched forecast result (mutated in-place and returned).
        """
        if knowledge_index is not None:
            bridge = KnowledgeBridge.from_dict(knowledge_index)
        else:
            bridge = self

        for tier in forecast_result.get("tiers", []):
            for fragment in tier.get("evidence_fragments", []):
                ref = fragment.get("knowledge_ref")
                if ref is None:
                    continue
                doc = bridge.get_document(ref)
                if doc is not None:
                    fragment["knowledge_title"] = doc.get("title")
                    fragment["knowledge_domain"] = doc.get("domain")
                    fragment["knowledge_path"] = doc.get("path")

        return forecast_result
