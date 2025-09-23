"""Tests for the ARC recap import helper."""

import json
from pathlib import Path

import pytest

from src.core.arc_importer import ARCImportError, import_arc_file


@pytest.fixture()
def sample_arc_payload() -> dict:
    """Provide a reusable valid ARC payload for tests."""

    return {
        "schema": "ARC_CHAIN_EXPORT_SCHEMA_v1.0",
        "validation": {"validation_passed": True, "checksum": "abc123"},
        "arc_chain": [
            {
                "type": "T1_SYNTH",
                "summary": "Synthesized thread recap for T1 anchor.",
                "timestamp": "2025-07-20T10:00:00Z",
                "by": "ARCHY",
                "anchor_pair": ["T1_CORE", "ARC_SYNTH"],
                "t1_markers": ["T1_ALPHA"],
                "anchor_seeds": ["SEED_SYNTH_ALPHA"],
            },
            {
                "type": "RECALL_VECTOR",
                "summary": "Recalled sequence for analyst liora@aurora.ai",
                "timestamp": "2025-07-20T10:05:00Z",
                "by": "liora@aurora.ai",
                "anchor_pair": ["T1_CORE", "ARC_VECTOR"],
                "symbolic_tags": ["RECALL", "VECTOR_STATE"],
            },
        ],
    }


def test_import_arc_file_success(tmp_path: Path, sample_arc_payload: dict, capsys: pytest.CaptureFixture[str]):
    """Valid ARC recap bundles are loaded into overlay blocks."""

    arc_path = tmp_path / "recap.json"
    arc_path.write_text(json.dumps(sample_arc_payload), encoding="utf-8")

    thread_state = import_arc_file(arc_path)

    assert "T1_SYNTH" in thread_state
    synth_overlay = thread_state["T1_SYNTH"]
    assert synth_overlay["summary"] == "Synthesized thread recap for T1 anchor."
    assert synth_overlay["anchor_pair"] == ["T1_CORE", "ARC_SYNTH"]
    assert synth_overlay["metadata"]["t1_markers"] == ["T1_ALPHA"]

    vector_overlay = thread_state["RECALL_VECTOR"]
    assert vector_overlay["by"] == "[REDACTED_EMAIL]"
    assert vector_overlay["metadata"]["symbolic_tags"] == ["RECALL", "VECTOR_STATE"]

    captured = capsys.readouterr()
    assert "[RECALL_ARC] Loaded ARC recap: 2 entries." in captured.out


def test_import_arc_file_schema_validation(tmp_path: Path, sample_arc_payload: dict):
    """Unsupported schemas trigger an ARCImportError."""

    payload = dict(sample_arc_payload)
    payload["schema"] = "ARC_CHAIN_EXPORT_SCHEMA_v0.9"

    arc_path = tmp_path / "invalid_schema.json"
    arc_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ARCImportError):
        import_arc_file(arc_path)


def test_import_arc_file_checksum_failure(tmp_path: Path, sample_arc_payload: dict):
    """Checksum failures are surfaced as ARCImportError."""

    payload = dict(sample_arc_payload)
    payload["validation"] = {"validation_passed": False, "checksum": "abc123"}

    arc_path = tmp_path / "invalid_checksum.json"
    arc_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ARCImportError) as exc_info:
        import_arc_file(arc_path)

    assert "checksum" in str(exc_info.value).lower()


def test_import_arc_file_missing_file(tmp_path: Path):
    """Missing files raise a FileNotFoundError."""

    nonexistent_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        import_arc_file(nonexistent_path)
