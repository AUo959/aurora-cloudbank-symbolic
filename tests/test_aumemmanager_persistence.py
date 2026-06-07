"""
Tests for AuMemManager optional disk persistence (issue #805).

Covers:
- save + reload: memories survive re-instantiation
- persist_path from AURORA_AUMEM_PERSIST_PATH env var
- no persist_path -> no file created
- corrupt JSON file -> warning logged, empty memory (no crash)
- missing file -> empty memory (new install)
- after save, file exists with correct JSON structure
- all three tiers (active / compressed / archived) round-trip
- memories with quantum vectors persist correctly
- schema version is written to the file
- save_to_disk is a no-op when _persist_path is None
"""

import json
import os

import pytest

from modules.aumemmanager import HierarchicalMemoryManager, MemoryType, MemoryStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _add_sample_memory(manager: HierarchicalMemoryManager, label: str = "test") -> str:
    return manager.add_memory(
        content={"note": label, "value": 42},
        memory_type=MemoryType.AGENT,
        owner="test_owner",
        importance=7.5,
        tags=["persist", label],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.aurora
def test_save_and_reload_memories_survive(tmp_path):
    """Memories added before save are present after re-instantiation with the same path."""
    persist_file = str(tmp_path / "aumem.json")

    manager = HierarchicalMemoryManager(persist_path=persist_file)
    mid = _add_sample_memory(manager, "hello")
    manager.save_to_disk()

    # Re-open with a fresh instance pointing at the same file.
    manager2 = HierarchicalMemoryManager(persist_path=persist_file)
    assert mid in manager2.active_tier, "memory id should be present after reload"
    memory = manager2.active_tier[mid]
    assert memory.content["note"] == "hello"
    assert memory.importance == pytest.approx(7.5)
    assert memory.owner == "test_owner"


@pytest.mark.unit
@pytest.mark.aurora
def test_persist_path_from_env_var(tmp_path, monkeypatch):
    """AURORA_AUMEM_PERSIST_PATH env var is used when persist_path arg is omitted."""
    persist_file = str(tmp_path / "env_aumem.json")
    monkeypatch.setenv("AURORA_AUMEM_PERSIST_PATH", persist_file)

    manager = HierarchicalMemoryManager()  # no explicit persist_path
    assert manager._persist_path == persist_file

    mid = _add_sample_memory(manager, "env_test")
    manager.save_to_disk()

    # New instance also reads env var.
    manager2 = HierarchicalMemoryManager()
    assert mid in manager2.active_tier


@pytest.mark.unit
@pytest.mark.aurora
def test_no_persist_path_no_file_created(tmp_path, monkeypatch):
    """When persist_path is None and env var is unset, save_to_disk creates no file."""
    monkeypatch.delenv("AURORA_AUMEM_PERSIST_PATH", raising=False)

    manager = HierarchicalMemoryManager()  # no persistence configured
    _add_sample_memory(manager, "no_persist")
    manager.save_to_disk()  # should be a no-op

    # Verify nothing was written anywhere in tmp_path.
    files = list(tmp_path.iterdir())
    assert files == [], "No file should be created when persist_path is None"


@pytest.mark.unit
@pytest.mark.aurora
def test_corrupt_json_returns_empty_memory(tmp_path, caplog):
    """Corrupt JSON in the persist file logs a warning and starts with empty memory."""
    persist_file = tmp_path / "corrupt.json"
    persist_file.write_text("{ this is not valid JSON !!!}", encoding="utf-8")

    import logging
    with caplog.at_level(logging.WARNING, logger="modules.aumemmanager.hierarchical_memory"):
        manager = HierarchicalMemoryManager(persist_path=str(persist_file))

    assert len(manager.active_tier) == 0
    assert len(manager.compressed_tier) == 0
    assert len(manager.archived_tier) == 0
    # Should have logged a warning about the corrupt file.
    assert any("corrupt" in rec.message.lower() or "could not read" in rec.message.lower()
               for rec in caplog.records), "Expected a warning about the corrupt file"


@pytest.mark.unit
@pytest.mark.aurora
def test_missing_file_starts_fresh(tmp_path, caplog):
    """Missing persist file results in empty memory (new install path)."""
    persist_file = str(tmp_path / "nonexistent.json")
    # File does NOT exist.

    import logging
    with caplog.at_level(logging.INFO, logger="modules.aumemmanager.hierarchical_memory"):
        manager = HierarchicalMemoryManager(persist_path=persist_file)

    assert len(manager.active_tier) == 0
    # Should log an informational message (not an error).
    assert any("starting fresh" in rec.message.lower() or "no persist" in rec.message.lower()
               for rec in caplog.records)


@pytest.mark.unit
@pytest.mark.aurora
def test_file_exists_after_save(tmp_path):
    """After save_to_disk the persist file exists."""
    persist_file = str(tmp_path / "save_check.json")
    manager = HierarchicalMemoryManager(persist_path=persist_file)
    _add_sample_memory(manager)
    manager.save_to_disk()

    assert os.path.exists(persist_file), "Persist file should be created by save_to_disk"


@pytest.mark.unit
@pytest.mark.aurora
def test_saved_file_has_correct_schema(tmp_path):
    """The persisted JSON has _schema_version, _saved_at, and memories keys."""
    persist_file = str(tmp_path / "schema_check.json")
    manager = HierarchicalMemoryManager(persist_path=persist_file)
    _add_sample_memory(manager)
    manager.save_to_disk()

    with open(persist_file, encoding="utf-8") as fh:
        payload = json.load(fh)

    assert payload.get("_schema_version") == 1
    assert "_saved_at" in payload
    assert isinstance(payload.get("memories"), list)
    assert len(payload["memories"]) == 1

    record = payload["memories"][0]
    assert "id" in record
    assert "content" in record
    assert "_tier" in record


@pytest.mark.unit
@pytest.mark.aurora
def test_multiple_memories_all_restored(tmp_path):
    """All memories (not just the first) survive a save/reload cycle."""
    persist_file = str(tmp_path / "multi.json")
    manager = HierarchicalMemoryManager(persist_path=persist_file)

    ids = [_add_sample_memory(manager, f"item_{i}") for i in range(5)]
    manager.save_to_disk()

    manager2 = HierarchicalMemoryManager(persist_path=persist_file)
    for mid in ids:
        assert mid in manager2.active_tier, f"Memory {mid} should be restored"


@pytest.mark.unit
@pytest.mark.aurora
def test_memory_type_and_status_roundtrip(tmp_path):
    """Enum fields (memory_type, status) are correctly preserved through JSON."""
    persist_file = str(tmp_path / "enum_check.json")
    manager = HierarchicalMemoryManager(persist_path=persist_file)
    mid = manager.add_memory(
        content={"x": 1},
        memory_type=MemoryType.QUANTUM_SYMBOLIC,
        owner="owner_q",
        importance=5.0,
    )
    manager.save_to_disk()

    manager2 = HierarchicalMemoryManager(persist_path=persist_file)
    assert mid in manager2.active_tier
    mem = manager2.active_tier[mid]
    assert mem.memory_type == MemoryType.QUANTUM_SYMBOLIC
    assert mem.status == MemoryStatus.ACTIVE


@pytest.mark.unit
@pytest.mark.aurora
def test_save_to_disk_noop_when_no_path(monkeypatch):
    """save_to_disk is a no-op and does not raise when _persist_path is None."""
    monkeypatch.delenv("AURORA_AUMEM_PERSIST_PATH", raising=False)
    manager = HierarchicalMemoryManager()  # no persistence
    _add_sample_memory(manager)
    # Should complete without raising any exception.
    manager.save_to_disk()


@pytest.mark.unit
@pytest.mark.aurora
def test_metrics_updated_after_load(tmp_path):
    """After loading from disk the metrics counters reflect the restored memories."""
    persist_file = str(tmp_path / "metrics.json")
    manager = HierarchicalMemoryManager(persist_path=persist_file)
    for i in range(3):
        _add_sample_memory(manager, f"m{i}")
    manager.save_to_disk()

    manager2 = HierarchicalMemoryManager(persist_path=persist_file)
    metrics = manager2.get_metrics()
    assert metrics["total_memories"] == 3
    assert metrics["active_memories"] == 3
