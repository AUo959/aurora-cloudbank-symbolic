"""Tests for the ARC chain import utilities."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

# Ensure the src package is discoverable when tests are executed directly.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aurora.core.arc_importer import ARC_EXPORT_SCHEMA, import_arc_file


@pytest.fixture()
def arc_export_payload() -> Dict[str, Any]:
    """Provide a baseline ARC export payload for mutation in tests."""

    return {
        "schema": ARC_EXPORT_SCHEMA,
        "validation": {"validation_passed": True},
        "arc_chain": [
            {
                "type": "THREAD_SUMMARY",
                "summary": "Consolidated ARC recap",
                "timestamp": "2025-07-11T04:53:00Z",
                "by": "Aurora",
                "anchor_pair": ["T1//070", "SRB//992"],
            },
            {
                "type": "ANCHOR_UPDATE",
                "summary": "Refreshed anchor pair alignment",
                "timestamp": "2025-07-11T04:55:00Z",
                "by": "ARCHY",
                "anchor_pair": ["T1//071", "SRB//993"],
            },
        ],
    }


def write_payload(tmp_path: Path, payload: Dict[str, Any]) -> Path:
    arc_path = tmp_path / "arc_export.json"
    arc_path.write_text(json.dumps(payload), encoding="utf-8")
    return arc_path


def test_import_arc_file_success(tmp_path: Path, capsys, arc_export_payload: Dict[str, Any]) -> None:
    arc_path = write_payload(tmp_path, arc_export_payload)

    thread_state = import_arc_file(arc_path)

    assert set(thread_state) == {"THREAD_SUMMARY", "ANCHOR_UPDATE"}
    assert thread_state["THREAD_SUMMARY"]["anchor_pair"] == ["T1//070", "SRB//992"]

    output = capsys.readouterr().out
    assert "[RECALL_ARC] Loaded ARC recap: 2 entries." in output


def test_import_arc_file_missing_schema(tmp_path: Path, arc_export_payload: Dict[str, Any]) -> None:
    payload = json.loads(json.dumps(arc_export_payload))
    payload["schema"] = "ARC_CHAIN_EXPORT_SCHEMA_v0.9"
    arc_path = write_payload(tmp_path, payload)

    with pytest.raises(ValueError, match="Unsupported ARC export schema"):
        import_arc_file(arc_path)


def test_import_arc_file_invalid_validation(tmp_path: Path, arc_export_payload: Dict[str, Any]) -> None:
    payload = json.loads(json.dumps(arc_export_payload))
    payload["validation"]["validation_passed"] = False
    arc_path = write_payload(tmp_path, payload)

    with pytest.raises(ValueError, match="ARC checksum validation failed"):
        import_arc_file(arc_path)


def test_import_arc_file_missing_source(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"
    with pytest.raises(FileNotFoundError):
        import_arc_file(missing_path)
