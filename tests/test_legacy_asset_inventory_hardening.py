"""Additional denial-of-service and custody hardening tests for legacy inventory."""

from __future__ import annotations

import importlib.util
import os
import stat
import struct
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


# ---------------------------------------------------------------------------
# Bounding regressions
#
# The two tests below cover bypasses that the pre-existing "before ZipFile
# construction" and member-size tests did not catch, because both trusted
# central-directory metadata rather than what the reader actually does.
# ---------------------------------------------------------------------------


def _write_zip64_locator_archive(path: Path, declared_entries: int) -> None:
    """Build an archive whose 32-bit EOCD is small but which carries a ZIP64 EOCD.

    zipfile._EndRecData64 honours the ZIP64 record whenever the locator is
    present and overrides the entry count and central-directory size from it.
    An archive can therefore declare harmless non-sentinel 32-bit values while
    zipfile materializes the far larger ZIP64 counts.
    """
    with zipfile.ZipFile(path, "w") as archive:
        for index in range(5):
            archive.writestr(f"f{index}.txt", "x")

    raw = bytearray(path.read_bytes())
    eocd_offset = raw.rfind(b"PK\x05\x06")
    eocd = bytes(raw[eocd_offset:])
    cd_size, cd_offset = struct.unpack_from("<LL", raw, eocd_offset + 12)

    zip64_eocd = struct.pack(
        "<4sQ2H2L4Q",
        b"PK\x06\x06", 44, 45, 45, 0, 0,
        declared_entries, declared_entries, cd_size, cd_offset,
    )
    locator = struct.pack("<4sLQL", b"PK\x06\x07", 0, eocd_offset, 1)
    path.write_bytes(bytes(raw[:eocd_offset]) + zip64_eocd + locator + eocd)


def test_zip64_locator_is_rejected_even_with_small_32bit_counts(inventory_module, tmp_path: Path) -> None:
    """A ZIP64 locator must be rejected regardless of the 32-bit EOCD values.

    Checking only for 0xFFFF/0xFFFFFFFF sentinels misses this: the crafted
    archive declares 5 entries in the 32-bit record while the ZIP64 record
    declares 60,000, and zipfile uses the latter.
    """
    archive_path = tmp_path / "zip64_locator.zip"
    _write_zip64_locator_archive(archive_path, declared_entries=60_000)

    with archive_path.open("rb") as handle:
        verdict = inventory_module._zip_preflight(
            handle,
            archive_path.stat().st_size,
            max_archive_entries=10_000,
            max_central_directory_bytes=8 * 1024 * 1024,
        )

    assert verdict == "archive_zip64_unsupported"


def test_unboundable_compression_is_not_materialized(inventory_module, tmp_path: Path) -> None:
    """Members whose expansion cannot be bounded are inventoried, not read.

    ZipExtFile only forwards max_length into decompress() for ZIP_DEFLATED, and
    _read2 reads at least MIN_READ_SIZE of compressed input per call, so no read
    chunk size bounds an LZMA member. The central directory here also lies about
    file_size, so size-based guards alone would let the read proceed.
    """
    archive_path = tmp_path / "unboundable.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            zipfile.ZipInfo("lie.bin"),
            b"\0" * 20_000_000,
            compress_type=zipfile.ZIP_LZMA,
        )

    raw = bytearray(archive_path.read_bytes())
    struct.pack_into("<L", raw, raw.find(b"PK\x01\x02") + 24, 1000)
    struct.pack_into("<L", raw, raw.find(b"PK\x03\x04") + 22, 1000)
    archive_path.write_bytes(bytes(raw))

    artifacts = inventory_module.inspect_zip(archive_path, "unboundable.zip")

    assert len(artifacts) == 1
    member = artifacts[0]
    assert "archive_unboundable_compression" in member["security_flags"]
    assert member["sha256"] is None


def test_deflated_members_are_still_read_and_hashed(inventory_module, tmp_path: Path) -> None:
    """The bounding guard must not stop ordinary DEFLATE members being hashed."""
    archive_path = tmp_path / "ordinary.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("a.txt", "hello world")

    artifacts = inventory_module.inspect_zip(archive_path, "ordinary.zip")

    assert len(artifacts) == 1
    assert artifacts[0]["sha256"] is not None
    assert artifacts[0]["security_flags"] == []
