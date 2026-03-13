#!/usr/bin/env python3
"""
Constellation Knowledge Index Aggregator

Fetches knowledge-index.json from QGIA-CORPUS and QGIA-SPINE,
merges them into a single aggregated index, validates against
the constellation schema, and detects content drift.

Usage:
  python scripts/aggregate-knowledge-indexes.py [--local]

With --local, reads from knowledge-indexes/corpus-knowledge-index.json
and knowledge-indexes/spine-knowledge-index.json instead of fetching
from GitHub. This is used by the GitHub Actions workflow after caching.
"""
import json
import os
import sys
import hashlib
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError

REMOTE_INDEXES = {
    "qgia-knowledge-library": "https://raw.githubusercontent.com/AUo959/qgia-knowledge-library/main/.aurora/knowledge-index.json",
    "qgia-knowledge-spine": "https://raw.githubusercontent.com/AUo959/qgia-knowledge-spine/main/.aurora/knowledge-index.json",
}

LOCAL_INDEXES = {
    "qgia-knowledge-library": "knowledge-indexes/corpus-knowledge-index.json",
    "qgia-knowledge-spine": "knowledge-indexes/spine-knowledge-index.json",
}

OUTPUT_DIR = "knowledge-indexes"
AGGREGATED_FILE = os.path.join(OUTPUT_DIR, "aggregated-knowledge-index.json")
SCHEMA_FILE = "constellation-contracts/schemas/knowledge-index.schema.json"


def fetch_index(url: str) -> dict | None:
    """Fetch a knowledge index from a URL."""
    try:
        req = Request(url, headers={"User-Agent": "Aurora-Constellation-Aggregator/1.0"})
        with urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  WARNING: Failed to fetch {url}: {e}")
        return None


def load_local_index(path: str) -> dict | None:
    """Load a knowledge index from a local file."""
    if not os.path.exists(path):
        print(f"  WARNING: Local index not found: {path}")
        return None
    with open(path, "r") as f:
        return json.load(f)


def validate_index(index: dict, schema: dict) -> list[str]:
    """Basic validation against the schema. Returns list of issues."""
    issues = []
    for required_field in schema.get("required", []):
        if required_field not in index:
            issues.append(f"Missing required field: {required_field}")
    if "documents" in index:
        doc_schema = schema.get("properties", {}).get("documents", {}).get("items", {})
        required_doc_fields = doc_schema.get("required", [])
        for i, doc in enumerate(index["documents"]):
            for field in required_doc_fields:
                if field not in doc:
                    issues.append(f"Document {i} missing required field: {field}")
    return issues


def detect_drift(old_index: dict | None, new_index: dict) -> list[str]:
    """Detect content drift between old and new indexes."""
    if old_index is None:
        return ["First aggregation — no previous index to compare"]

    drift_notes = []
    old_ids = {d["id"] for d in old_index.get("documents", [])}
    new_ids = {d["id"] for d in new_index.get("documents", [])}

    added = new_ids - old_ids
    removed = old_ids - new_ids

    if added:
        drift_notes.append(f"Added {len(added)} documents: {', '.join(sorted(added))}")
    if removed:
        drift_notes.append(f"Removed {len(removed)} documents: {', '.join(sorted(removed))}")

    # Check for checksum changes (content edits)
    old_checksums = {d["id"]: d.get("checksum") for d in old_index.get("documents", [])}
    new_checksums = {d["id"]: d.get("checksum") for d in new_index.get("documents", [])}

    modified = []
    for doc_id in old_ids & new_ids:
        if old_checksums.get(doc_id) != new_checksums.get(doc_id):
            modified.append(doc_id)

    if modified:
        drift_notes.append(f"Modified {len(modified)} documents: {', '.join(sorted(modified))}")

    if not drift_notes:
        drift_notes.append("No content drift detected")

    return drift_notes


def aggregate(use_local: bool = False) -> dict:
    """Main aggregation logic."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("Constellation Knowledge Index Aggregator")
    print("=" * 60)

    # Load existing aggregated index for drift detection
    old_aggregated = None
    if os.path.exists(AGGREGATED_FILE):
        with open(AGGREGATED_FILE, "r") as f:
            old_aggregated = json.load(f)
        print(f"Loaded previous aggregated index ({len(old_aggregated.get('documents', []))} docs)")

    # Load schema for validation
    schema = None
    if os.path.exists(SCHEMA_FILE):
        with open(SCHEMA_FILE, "r") as f:
            schema = json.load(f)
        print(f"Loaded schema: {SCHEMA_FILE}")
    else:
        print(f"WARNING: Schema not found at {SCHEMA_FILE}, skipping validation")

    # Fetch indexes from spoke repos
    all_documents = []
    seen_ids = set()
    source_metadata = {}

    sources = LOCAL_INDEXES if use_local else REMOTE_INDEXES

    for repo_name, source in sources.items():
        print(f"\nFetching index from {repo_name}...")
        index = load_local_index(source) if use_local else fetch_index(source)

        if index is None:
            print(f"  SKIPPED: Could not load index for {repo_name}")
            source_metadata[repo_name] = {"status": "unreachable", "document_count": 0}
            continue

        # Validate
        if schema:
            issues = validate_index(index, schema)
            if issues:
                print(f"  VALIDATION ISSUES:")
                for issue in issues:
                    print(f"    - {issue}")
            else:
                print(f"  Validation passed")

        # Cache locally
        cache_file = LOCAL_INDEXES[repo_name]
        with open(cache_file, "w") as f:
            json.dump(index, f, indent=2)
        print(f"  Cached to {cache_file}")

        # Merge documents (deduplicate by ID)
        doc_count = 0
        for doc in index.get("documents", []):
            if doc["id"] not in seen_ids:
                seen_ids.add(doc["id"])
                all_documents.append(doc)
                doc_count += 1

        source_metadata[repo_name] = {
            "status": "synced",
            "document_count": doc_count,
            "index_version": index.get("version"),
            "generated_at": index.get("generated_at"),
        }
        print(f"  Merged {doc_count} documents")

    # Sort by domain then ID
    all_documents.sort(key=lambda d: (d.get("domain", ""), d.get("id", "")))

    # Build aggregated index
    aggregated = {
        "version": "1.0.0",
        "source_repo": "aggregated",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aggregation_metadata": {
            "sources": source_metadata,
            "total_documents": len(all_documents),
            "aggregated_by": "constellation-knowledge-aggregator",
        },
        "documents": all_documents,
    }

    # Detect drift
    print(f"\nDrift detection:")
    drift_notes = detect_drift(old_aggregated, aggregated)
    for note in drift_notes:
        print(f"  - {note}")
    aggregated["aggregation_metadata"]["drift_notes"] = drift_notes

    # Write aggregated index
    with open(AGGREGATED_FILE, "w") as f:
        json.dump(aggregated, f, indent=2)
    print(f"\nWrote aggregated index: {AGGREGATED_FILE}")
    print(f"Total documents: {len(all_documents)}")

    return aggregated


if __name__ == "__main__":
    use_local = "--local" in sys.argv
    aggregate(use_local=use_local)
