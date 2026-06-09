import importlib.util
import json
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "aggregate-knowledge-indexes.py"


def load_aggregator_module():
    spec = importlib.util.spec_from_file_location("aggregate_knowledge_indexes", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_aggregate_preserves_existing_file_for_timestamp_only_changes(tmp_path, monkeypatch):
    module = load_aggregator_module()

    output_dir = tmp_path / "knowledge-indexes"
    output_dir.mkdir()
    aggregated_file = output_dir / "aggregated-knowledge-index.json"
    corpus_index = output_dir / "corpus-knowledge-index.json"
    spine_index = output_dir / "spine-knowledge-index.json"

    corpus_payload = {
        "version": "1.0.0",
        "source_repo": "qgia-knowledge-library",
        "generated_at": "2026-06-08T10:00:00+00:00",
        "documents": [
            {
                "id": "qgia-library:alpha",
                "title": "Alpha",
                "domain": "framework",
                "path": "alpha.md",
                "checksum": "abc123",
            }
        ],
    }
    spine_payload = {
        "version": "1.0.0",
        "source_repo": "qgia-knowledge-spine",
        "generated_at": "2026-06-08T11:00:00+00:00",
        "documents": [
            {
                "id": "qgia-spine:beta",
                "title": "Beta",
                "domain": "runtime",
                "path": "beta.md",
                "checksum": "def456",
            }
        ],
    }
    old_aggregate = {
        "version": "1.0.0",
        "source_repo": "aggregated",
        "generated_at": "2026-06-08T12:00:00+00:00",
        "aggregation_metadata": {
            "sources": {
                "qgia-knowledge-library": {
                    "status": "synced",
                    "document_count": 1,
                    "index_version": "1.0.0",
                    "generated_at": "2026-06-08T09:00:00+00:00",
                },
                "qgia-knowledge-spine": {
                    "status": "synced",
                    "document_count": 1,
                    "index_version": "1.0.0",
                    "generated_at": "2026-06-08T09:30:00+00:00",
                },
            },
            "total_documents": 2,
            "aggregated_by": "constellation-knowledge-aggregator",
            "drift_notes": ["No content drift detected"],
        },
        "documents": [
            corpus_payload["documents"][0],
            spine_payload["documents"][0],
        ],
    }

    corpus_index.write_text(json.dumps(corpus_payload), encoding="utf-8")
    spine_index.write_text(json.dumps(spine_payload), encoding="utf-8")
    aggregated_file.write_text(json.dumps(old_aggregate, indent=2), encoding="utf-8")

    monkeypatch.setattr(module, "OUTPUT_DIR", str(output_dir))
    monkeypatch.setattr(module, "AGGREGATED_FILE", str(aggregated_file))
    monkeypatch.setattr(module, "SCHEMA_FILE", str(tmp_path / "missing-schema.json"))
    monkeypatch.setattr(
        module,
        "LOCAL_INDEXES",
        {
            "qgia-knowledge-library": str(corpus_index),
            "qgia-knowledge-spine": str(spine_index),
        },
    )

    result = module.aggregate(use_local=True)
    written = json.loads(aggregated_file.read_text(encoding="utf-8"))

    assert result == old_aggregate
    assert written == old_aggregate


def test_spoke_cache_preserves_existing_file_for_timestamp_only_changes(tmp_path):
    module = load_aggregator_module()
    cache_file = tmp_path / "spoke-index.json"
    old_index = {
        "version": "1.0.0",
        "source_repo": "qgia-knowledge-spine",
        "generated_at": "2026-06-08T10:00:00+00:00",
        "documents": [
            {
                "id": "qgia-spine:beta",
                "title": "Beta",
                "domain": "runtime",
                "path": "beta.md",
                "checksum": "def456",
            }
        ],
    }
    new_index = {
        **old_index,
        "generated_at": "2026-06-08T11:00:00+00:00",
    }
    cache_file.write_text(json.dumps(old_index, indent=2), encoding="utf-8")

    assert module.preserve_existing_noop_cache(str(cache_file), new_index) == old_index
