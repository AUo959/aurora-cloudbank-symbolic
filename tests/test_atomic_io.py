"""Unit tests for src.utils.atomic_io helpers."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.atomic_io import atomic_write_json, append_jsonl


@pytest.mark.unit
def test_atomic_write_json_creates_file(tmp_path):
    """Write a dict atomically, then read it back and assert correctness."""
    target = tmp_path / "state.json"
    payload = {"key": "value", "number": 42}

    atomic_write_json(target, payload)

    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == payload


@pytest.mark.unit
def test_atomic_write_json_no_partial_on_exception(tmp_path):
    """If os.replace raises, the original file must remain unchanged."""
    target = tmp_path / "state.json"
    original = {"original": True}
    target.write_text(json.dumps(original), encoding="utf-8")

    with patch("os.replace", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            atomic_write_json(target, {"new": "data"})

    # Original file must be intact
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == original

    # Temp file must be cleaned up
    tmp_file = target.with_suffix(target.suffix + ".tmp")
    assert not tmp_file.exists()


@pytest.mark.unit
def test_append_jsonl_creates_valid_lines(tmp_path):
    """Append 3 records, read lines back, assert each parses as JSON."""
    target = tmp_path / "records.jsonl"
    records = [{"id": 1, "msg": "first"}, {"id": 2, "msg": "second"}, {"id": 3, "msg": "third"}]

    for record in records:
        append_jsonl(target, record)

    assert target.exists()
    lines = [line for line in target.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 3

    for i, line in enumerate(lines):
        parsed = json.loads(line)
        assert parsed["id"] == records[i]["id"]
        assert parsed["msg"] == records[i]["msg"]
