"""
QGIA Knowledge Indexer

Walks a QGIA knowledge repository (markdown files), extracts metadata, and
produces a ``knowledge-index.json`` conforming to the constellation contract
schema ``knowledge-index.schema.json``.

Ref: Aurora Constellation Architecture Proposal v1.0.0 — Gap 5

Usage (CLI):
    python -m modules.qgia.knowledge_indexer \
        --repo-path /path/to/qgia-knowledge-library \
        --output knowledge-index.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Domain detection heuristics
# ---------------------------------------------------------------------------

_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "nuclear": ["nuclear", "fission", "fusion", "reactor", "uranium", "plutonium", "nonproliferation"],
    "cyber": ["cyber", "malware", "ransomware", "phishing", "zero-day", "exploit", "vulnerability", "infosec"],
    "economic": ["economic", "trade", "gdp", "inflation", "sanctions", "tariff", "fiscal", "monetary"],
    "military": ["military", "defense", "weapon", "army", "navy", "air force", "missile", "combat"],
    "political": ["political", "election", "diplomacy", "geopolitical", "governance", "legislature", "treaty"],
    "environmental": ["environmental", "climate", "carbon", "pollution", "biodiversity", "sustainability"],
    "social": ["social", "demographic", "migration", "inequality", "education", "health", "cultural"],
    "technological": ["technological", "ai", "quantum", "blockchain", "semiconductor", "innovation", "biotech"],
}


def _detect_domain(text: str) -> str:
    """Return the best-matching domain based on keyword frequency, or 'hybrid'."""
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for domain, keywords in _DOMAIN_KEYWORDS.items():
        scores[domain] = sum(text_lower.count(kw) for kw in keywords)

    if not scores or max(scores.values()) == 0:
        return "hybrid"
    return max(scores, key=lambda d: scores[d])


def _extract_title(content: str, fallback: str) -> str:
    """Extract the first markdown heading, or use the fallback filename."""
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def _extract_tags(content: str) -> list[str]:
    """Extract tags from YAML front-matter or inline markers."""
    tags: list[str] = []

    # YAML front-matter tags: field
    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if line.strip().startswith("- ") and "tags" in content[:content.index(line)].split("\n")[-2:]:
                tags.append(line.strip().lstrip("- ").strip())
            tag_match = re.match(r"tags:\s*\[(.+)]", line.strip())
            if tag_match:
                tags.extend(t.strip().strip("'\"") for t in tag_match.group(1).split(","))

    return tags


def _compute_checksum(content: str) -> str:
    """SHA-256 hex digest of the file content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Indexer
# ---------------------------------------------------------------------------

def index_repository(repo_path: str | Path, source_repo: str | None = None) -> dict[str, Any]:
    """Walk *repo_path* and build a knowledge index dict.

    Args:
        repo_path: Root of the cloned QGIA knowledge repository.
        source_repo: Repo name for the index (auto-detected from path if omitted).

    Returns:
        A dict conforming to ``knowledge-index.schema.json``.
    """
    repo_path = Path(repo_path).resolve()
    if not repo_path.is_dir():
        raise FileNotFoundError(f"Repository path not found: {repo_path}")

    if source_repo is None:
        name = repo_path.name.lower()
        if "spine" in name:
            source_repo = "qgia-knowledge-spine"
        else:
            source_repo = "qgia-knowledge-library"

    documents: list[dict[str, Any]] = []
    doc_counter = 0

    for md_file in sorted(repo_path.rglob("*.md")):
        # Skip hidden dirs and common non-content files
        rel = md_file.relative_to(repo_path)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if rel.name.upper() in {"README.MD", "CONTRIBUTING.MD", "LICENSE.MD"}:
            continue

        content = md_file.read_text(encoding="utf-8", errors="replace")
        if not content.strip():
            continue

        doc_counter += 1
        stat = md_file.stat()

        documents.append({
            "id": f"QGIA-DOC-{doc_counter:04d}",
            "title": _extract_title(content, rel.stem),
            "domain": _detect_domain(content),
            "path": str(rel),
            "checksum": _compute_checksum(content),
            "word_count": len(content.split()),
            "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "tags": _extract_tags(content),
            "summary": content[:300].replace("\n", " ").strip(),
        })

    return {
        "version": "1.0.0-alpha",
        "source_repo": source_repo,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documents": documents,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate a QGIA knowledge index from a knowledge repository."
    )
    parser.add_argument(
        "--repo-path",
        required=True,
        help="Path to the cloned QGIA knowledge repository.",
    )
    parser.add_argument(
        "--output",
        default="knowledge-index.json",
        help="Output JSON file path (default: knowledge-index.json).",
    )
    parser.add_argument(
        "--source-repo",
        default=None,
        help="Override source_repo name (auto-detected from path otherwise).",
    )
    args = parser.parse_args(argv)

    index = index_repository(args.repo_path, args.source_repo)

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=2)

    print(f"Indexed {len(index['documents'])} documents → {args.output}")


if __name__ == "__main__":
    main()
