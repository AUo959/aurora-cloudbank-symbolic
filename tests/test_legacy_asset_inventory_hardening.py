"""Additional denial-of-service and custody hardening tests for legacy inventory."""

from __future__ import annotations

import importlib.util
import os
import warnings
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "salvage" / "inventory_legacy_assets.py"
FIXED_TIME = "2026-07-28T00:00:00Z"


def _load_inventory_module():
    spec = importlib.util.spec_from_file_location("inventory_legacy_assets_hardening", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def inventory_module():
    return _load_inventory_module()


def _artifact(report: dict, relative_path: str, source_kind: str = "filesystem") -> dict:
    return next(
        item
        for item in report["artifacts"]
        if item["relative_path"] == relative_path and item["source_kind"] == source_kind
    )


@pytest.mark.unit
def test_fifo_is_blocked_without_opening(tmp_path: Path, inventory_module) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO creation is unavailable on this platform")

    root = tmp_path / "legacy"
    root.mkdir()
    fifo = root / "input.pipe"
    try:
        os.mkfifo(fifo)
    except OSError:
        pytest.skip("FIFO creation is unavailable on this platform")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    item = _artifact(report, "input.pipe")

    assert item["proposed_disposition"] == "blocked"
    assert "non_regular_file" in item["security_flags"]
    assert item["sha256"] is None


@pytest.mark.unit
def test_archive_entry_limit_blocks_report_amplification(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "many.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("one.txt", "1")
        archive.writestr("two.txt", "2")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME, max_archive_entries=1)
    notice = _artifact(report, "many.zip", "archive_error")

    assert notice["proposed_disposition"] == "blocked"
    assert "archive_entry_count_exceeded" in notice["security_flags"]
    assert not any(item["source_kind"] == "archive_member" for item in report["artifacts"])


@pytest.mark.unit
def test_duplicate_archive_paths_fail_closed(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "duplicate.zip"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("same.txt", "first")
            archive.writestr("same.txt", "second")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    notice = _artifact(report, "duplicate.zip", "archive_error")

    assert notice["proposed_disposition"] == "blocked"
    assert "archive_duplicate_path" in notice["security_flags"]
    assert not any(item["source_kind"] == "archive_member" for item in report["artifacts"])


@pytest.mark.unit
def test_archive_notice_does_not_create_false_duplicate(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    (root / "legacy.tar").write_bytes(b"not-a-real-tar")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)

    assert report["duplicate_groups"] == []


@pytest.mark.unit
def test_limits_must_be_positive(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()

    with pytest.raises(inventory_module.InventoryError, match="must be positive"):
        inventory_module.inventory_tree(root, generated_at=FIXED_TIME, max_archive_entries=0)
