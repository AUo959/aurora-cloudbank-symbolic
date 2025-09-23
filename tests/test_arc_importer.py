"""Tests for the ARC chain import utility."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.aurora.core.arc_importer import ArcImportError, import_arc_file


def _write_arc_file(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _base_payload() -> dict:
    return {
        "schema": "ARC_CHAIN_EXPORT_SCHEMA_v1.0",
        "validation": {"validation_passed": True},
        "arc_chain": [],
    }


def test_import_arc_file_success(tmp_path, capsys):
    payload = _base_payload()
    payload["arc_chain"] = [
        {
            "type": "T1-SEED",
            "summary": "Initialized anchor threads",
            "timestamp": "2025-07-20T18:26:00Z",
            "by": "Aurora-Core",
            "anchor_pair": ["seed://T1", "anchor://root"],
        },
        {
            "type": "T2-RECALL",
            "summary": "Recalled symbolic overlays",
            "timestamp": "2025-07-20T18:27:00Z",
            "by": "Aurora-Core",
            "anchor_pair": ["recall://T2", "anchor://overlay"],
        },
    ]

    arc_file = _write_arc_file(tmp_path / "arc.json", payload)

    thread_state = import_arc_file(arc_file)

    assert thread_state == {
        "T1-SEED": {
            "summary": "Initialized anchor threads",
            "timestamp": "2025-07-20T18:26:00Z",
            "by": "Aurora-Core",
            "anchor_pair": ["seed://T1", "anchor://root"],
        },
        "T2-RECALL": {
            "summary": "Recalled symbolic overlays",
            "timestamp": "2025-07-20T18:27:00Z",
            "by": "Aurora-Core",
            "anchor_pair": ["recall://T2", "anchor://overlay"],
        },
    }

    captured = capsys.readouterr()
    assert "[RECALL_ARC] Loaded ARC recap: 2 entries." in captured.out


def test_import_arc_file_schema_validation(tmp_path):
    payload = _base_payload()
    payload["schema"] = "ARC_CHAIN_EXPORT_SCHEMA_v0.9"

    arc_file = _write_arc_file(tmp_path / "arc-invalid-schema.json", payload)

    with pytest.raises(ArcImportError):
        import_arc_file(arc_file)


def test_import_arc_file_missing_required_fields(tmp_path):
    payload = _base_payload()
    payload["arc_chain"] = [
        {
            "type": "T3-SUMMARY",
            "summary": "Missing anchor pair",
            "timestamp": "2025-07-20T18:28:00Z",
            "by": "Aurora-Core",
            # anchor_pair intentionally omitted
        }
    ]

    arc_file = _write_arc_file(tmp_path / "arc-missing-fields.json", payload)

    with pytest.raises(ArcImportError) as exc_info:
        import_arc_file(arc_file)

    assert "missing required fields" in str(exc_info.value)


def test_import_arc_file_failed_checksum(tmp_path):
    payload = _base_payload()
    payload["validation"] = {"validation_passed": False}

    arc_file = _write_arc_file(tmp_path / "arc-failed-checksum.json", payload)

    with pytest.raises(ArcImportError):
        import_arc_file(arc_file)
