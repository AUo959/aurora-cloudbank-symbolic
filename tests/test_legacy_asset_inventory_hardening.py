"""Additional denial-of-service and custody hardening tests for legacy inventory."""

from __future__ import annotations

import importlib.util
import os
import stat
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
def test_archive_entry_limit_is_enforced_before_zipfile_construction(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "many.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("one.txt", "1")
        archive.writestr("two.txt", "2")

    def fail_if_constructed(*args, **kwargs):
        raise AssertionError("ZipFile must not be constructed after preflight rejects entry count")

    monkeypatch.setattr(inventory_module.zipfile, "ZipFile", fail_if_constructed)
    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME, max_archive_entries=1)
    notice = _artifact(report, "many.zip", "archive_error")

    assert notice["proposed_disposition"] == "blocked"
    assert "archive_entry_count_exceeded" in notice["security_flags"]
    assert not any(item["source_kind"] == "archive_member" for item in report["artifacts"])


@pytest.mark.unit
def test_central_directory_limit_is_enforced_before_zipfile_construction(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "directory-heavy.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("long-member-name.txt", "content")

    def fail_if_constructed(*args, **kwargs):
        raise AssertionError("ZipFile must not be constructed after central-directory preflight rejects input")

    monkeypatch.setattr(inventory_module.zipfile, "ZipFile", fail_if_constructed)
    report = inventory_module.inventory_tree(
        root,
        generated_at=FIXED_TIME,
        max_central_directory_bytes=1,
    )
    notice = _artifact(report, "directory-heavy.zip", "archive_error")

    assert notice["proposed_disposition"] == "blocked"
    assert "archive_central_directory_too_large" in notice["security_flags"]


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
def test_archive_parent_is_part_of_member_identity(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    for archive_name in ("first.zip", "second.zip"):
        with zipfile.ZipFile(root / archive_name, "w") as archive:
            archive.writestr("same.txt", "identical")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    members = [
        item
        for item in report["artifacts"]
        if item["source_kind"] == "archive_member" and item["relative_path"] == "same.txt"
    ]

    assert len(members) == 2
    assert {item["archive_parent"] for item in members} == {"first.zip", "second.zip"}
    assert len({item["artifact_id"] for item in members}) == 2
    duplicate_group = next(group for group in report["duplicate_groups"] if group["sha256"] == members[0]["sha256"])
    assert len(duplicate_group["artifact_ids"]) == 2
    assert len(set(duplicate_group["artifact_ids"])) == 2


@pytest.mark.unit
def test_zip_member_executable_bits_trigger_quarantine(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "executable.zip"
    executable = zipfile.ZipInfo("run.sh")
    executable.create_system = 3
    executable.external_attr = (stat.S_IFREG | 0o755) << 16
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(executable, "#!/bin/sh\necho blocked\n")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    member = _artifact(report, "run.sh", "archive_member")

    assert member["category"] == "executable"
    assert member["proposed_disposition"] == "quarantine"
    assert "archive_executable" in member["security_flags"]


@pytest.mark.unit
def test_zip_special_file_is_blocked(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "special.zip"
    special = zipfile.ZipInfo("pipe")
    special.create_system = 3
    special.external_attr = (stat.S_IFIFO | 0o600) << 16
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(special, b"")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    member = _artifact(report, "pipe", "archive_member")

    assert member["proposed_disposition"] == "blocked"
    assert "archive_special_file" in member["security_flags"]
    assert member["sha256"] is None


@pytest.mark.unit
def test_walk_errors_are_recorded_as_blocked_artifacts(
    tmp_path: Path,
    inventory_module,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    unreadable = root / "restricted"

    def fake_walk(path, *, followlinks, onerror):
        assert Path(path) == root
        assert followlinks is False
        error = PermissionError("denied")
        error.filename = str(unreadable)
        onerror(error)
        yield str(root), [], []

    monkeypatch.setattr(inventory_module.os, "walk", fake_walk)
    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    item = _artifact(report, "restricted")

    assert item["proposed_disposition"] == "blocked"
    assert "walk_error" in item["security_flags"]


@pytest.mark.unit
def test_archive_notice_does_not_create_false_duplicate(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    (root / "legacy.tar").write_bytes(b"not-a-real-tar")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)

    assert report["duplicate_groups"] == []


@pytest.mark.unit
def test_limits_must_be_finite_and_positive(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()

    with pytest.raises(inventory_module.InventoryError, match="finite and positive"):
        inventory_module.inventory_tree(root, generated_at=FIXED_TIME, max_archive_entries=0)

    with pytest.raises(inventory_module.InventoryError, match="finite and positive"):
        inventory_module.inventory_tree(root, generated_at=FIXED_TIME, max_compression_ratio=float("nan"))
