"""Tests for the ARC import utility."""

import json
from pathlib import Path

import pytest

from src.aurora.utils.arc_importer import ARC_EXPORT_SCHEMA, import_arc_file


def _write_arc_file(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _base_payload() -> dict:
    return {
        "schema": ARC_EXPORT_SCHEMA,
        "validation": {"validation_passed": True},
        "arc_chain": [
            {
                "type": "T1_THREAD_SUMMARY",
                "summary": "Anchor recap",
                "timestamp": 1731615123.321,
                "by": "Aurora-Core",
                "anchor_pair": ["seed-alpha", "seed-beta"],
            }
        ],
    }


def test_import_arc_file_reconstructs_thread_state(tmp_path, capsys):
    payload = _base_payload()
    arc_path = _write_arc_file(tmp_path / "thread.arc.json", payload)

    thread_state = import_arc_file(arc_path)

    assert thread_state == {
        "T1_THREAD_SUMMARY": {
            "summary": "Anchor recap",
            "timestamp": 1731615123.321,
            "by": "Aurora-Core",
            "anchor_pair": ["seed-alpha", "seed-beta"],
        }
    }

    out, err = capsys.readouterr()
    assert "[RECALL_ARC] Loaded ARC recap: 1 entries." in out
    assert err == ""


def test_import_arc_file_rejects_invalid_schema(tmp_path):
    payload = _base_payload()
    payload["schema"] = "OTHER_SCHEMA"
    arc_path = _write_arc_file(tmp_path / "bad_schema.arc.json", payload)

    with pytest.raises(ValueError, match="Unsupported ARC schema"):
        import_arc_file(arc_path)


def test_import_arc_file_rejects_failed_validation(tmp_path):
    payload = _base_payload()
    payload["validation"] = {"validation_passed": False}
    arc_path = _write_arc_file(tmp_path / "invalid_validation.arc.json", payload)

    with pytest.raises(ValueError, match="ARC checksum validation failed"):
        import_arc_file(arc_path)


def test_import_arc_file_requires_arc_chain_list(tmp_path):
    payload = _base_payload()
    payload["arc_chain"] = "not-a-list"
    arc_path = _write_arc_file(tmp_path / "invalid_chain.arc.json", payload)

    with pytest.raises(ValueError, match="ARC chain payload malformed"):
        import_arc_file(arc_path)


def test_import_arc_file_missing_entry_fields(tmp_path):
    payload = _base_payload()
    payload["arc_chain"][0].pop("summary")
    arc_path = _write_arc_file(tmp_path / "missing_fields.arc.json", payload)

    with pytest.raises(ValueError, match="missing required fields"):
        import_arc_file(arc_path)
