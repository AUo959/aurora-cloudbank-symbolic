"""Security and determinism tests for the read-only salvage inventory."""

from __future__ import annotations

import importlib.util
import json
import stat
import zipfile
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "salvage" / "inventory_legacy_assets.py"
SCHEMA_PATH = REPO_ROOT / "schemas" / "salvage" / "legacy_asset_inventory.schema.json"
FIXED_TIME = "2026-07-28T00:00:00Z"


def _load_inventory_module():
    spec = importlib.util.spec_from_file_location("inventory_legacy_assets", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def inventory_module():
    return _load_inventory_module()


@pytest.fixture(scope="module")
def report_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _artifact(report: dict, relative_path: str, source_kind: str = "filesystem") -> dict:
    return next(
        item
        for item in report["artifacts"]
        if item["relative_path"] == relative_path and item["source_kind"] == source_kind
    )


@pytest.mark.unit
def test_inventory_is_deterministic_read_only_and_schema_valid(
    tmp_path: Path,
    inventory_module,
    report_schema: dict,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    first = root / "first.py"
    second = root / "second.py"
    first.write_text("print('same')\n", encoding="utf-8")
    second.write_bytes(first.read_bytes())
    before = {path.name: path.read_bytes() for path in root.iterdir()}

    report_one = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    report_two = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    after = {path.name: path.read_bytes() for path in root.iterdir()}

    assert report_one == report_two
    assert before == after
    assert report_one["read_only"] is True
    assert report_one["migration_applied"] is False
    assert len(report_one["duplicate_groups"]) == 1
    jsonschema.Draft202012Validator.check_schema(report_schema)
    jsonschema.Draft202012Validator(
        report_schema,
        format_checker=jsonschema.FormatChecker(),
    ).validate(report_one)


@pytest.mark.unit
def test_zip_traversal_absolute_symlink_and_nested_entries_are_blocked(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "bundle.zip"

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("safe/readme.md", "safe")
        archive.writestr("../escape.txt", "blocked")
        archive.writestr("/absolute.txt", "blocked")
        archive.writestr("nested.zip", b"PK\x03\x04")
        symlink = zipfile.ZipInfo("link")
        symlink.create_system = 3
        symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(symlink, "target")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)

    traversal = _artifact(report, "../escape.txt", "archive_member")
    absolute = _artifact(report, "/absolute.txt", "archive_member")
    nested = _artifact(report, "nested.zip", "archive_member")
    link = _artifact(report, "link", "archive_member")
    safe = _artifact(report, "safe/readme.md", "archive_member")

    assert traversal["proposed_disposition"] == "blocked"
    assert "archive_path_traversal" in traversal["security_flags"]
    assert traversal["sha256"] is None

    assert absolute["proposed_disposition"] == "blocked"
    assert "archive_absolute_path" in absolute["security_flags"]
    assert absolute["sha256"] is None

    assert nested["proposed_disposition"] == "blocked"
    assert "nested_archive" in nested["security_flags"]

    assert link["proposed_disposition"] == "blocked"
    assert "archive_symlink" in link["security_flags"]
    assert link["sha256"] is None

    assert safe["proposed_disposition"] == "archive"
    assert safe["sha256"] is not None


@pytest.mark.unit
def test_zip_bomb_limits_block_reading(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "compressed.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("zeros.txt", b"\x00" * 100_000)

    report = inventory_module.inventory_tree(
        root,
        generated_at=FIXED_TIME,
        max_compression_ratio=2.0,
    )
    member = _artifact(report, "zeros.txt", "archive_member")

    assert member["proposed_disposition"] == "blocked"
    assert "archive_compression_ratio" in member["security_flags"]
    assert member["sha256"] is None


@pytest.mark.unit
def test_member_and_total_size_limits_block_reading(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "sized.zip"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("one.txt", b"a" * 64)
        archive.writestr("two.txt", b"b" * 64)

    report = inventory_module.inventory_tree(
        root,
        generated_at=FIXED_TIME,
        max_member_bytes=32,
        max_archive_bytes=100,
        max_compression_ratio=1000.0,
    )

    for name in ("one.txt", "two.txt"):
        member = _artifact(report, name, "archive_member")
        assert "archive_member_too_large" in member["security_flags"]
        assert "archive_total_too_large" in member["security_flags"]
        assert member["sha256"] is None


@pytest.mark.unit
def test_potential_secret_is_quarantined_without_value_disclosure(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    secret_value = "DO_NOT_LOG_1234567890"
    (root / "private_token.env").write_text(
        f"token={secret_value}\n",
        encoding="utf-8",
    )

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    artifact = _artifact(report, "private_token.env")
    serialized = json.dumps(report, sort_keys=True)

    assert artifact["proposed_disposition"] == "quarantine"
    assert "potential_secret" in artifact["security_flags"]
    assert secret_value not in serialized


@pytest.mark.unit
def test_unsupported_archive_is_blocked_without_extraction(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    archive_path = root / "legacy.tar"
    archive_bytes = b"not-a-real-tar"
    archive_path.write_bytes(archive_bytes)

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    notice = _artifact(report, "legacy.tar", "archive_notice")

    assert notice["proposed_disposition"] == "blocked"
    assert "unsupported_archive" in notice["security_flags"]
    assert archive_path.read_bytes() == archive_bytes


@pytest.mark.unit
def test_filesystem_symlink_is_reported_without_following(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = root / "outside-link.txt"
    try:
        link.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation is unavailable on this platform")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    artifact = _artifact(report, "outside-link.txt")

    assert artifact["proposed_disposition"] == "blocked"
    assert "filesystem_symlink" in artifact["security_flags"]
    assert artifact["sha256"] is None
    assert outside.read_text(encoding="utf-8") == "outside"


@pytest.mark.unit
def test_directory_symlink_is_reported_without_traversal(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    outside = tmp_path / "outside-directory"
    outside.mkdir()
    (outside / "hidden.txt").write_text("outside", encoding="utf-8")
    link = root / "outside-directory-link"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Directory symlink creation is unavailable on this platform")

    report = inventory_module.inventory_tree(root, generated_at=FIXED_TIME)
    artifact = _artifact(report, "outside-directory-link")

    assert artifact["proposed_disposition"] == "blocked"
    assert "filesystem_symlink" in artifact["security_flags"]
    assert not any(item["relative_path"] == "outside-directory-link/hidden.txt" for item in report["artifacts"])
    assert (outside / "hidden.txt").read_text(encoding="utf-8") == "outside"


@pytest.mark.unit
def test_output_path_must_remain_outside_source_tree(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()

    with pytest.raises(inventory_module.InventoryError, match="outside the inventory source tree"):
        inventory_module.validate_output_path(root, root / "generated" / "inventory.json")

    external_output = tmp_path / "reports" / "inventory.json"
    assert inventory_module.validate_output_path(root, external_output) == external_output.resolve(strict=False)


@pytest.mark.unit
def test_report_identifier_ignores_generation_timestamp(
    tmp_path: Path,
    inventory_module,
) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    (root / "artifact.json").write_text('{"value": 1}\n', encoding="utf-8")

    first = inventory_module.inventory_tree(root, generated_at="2026-07-28T00:00:00Z")
    second = inventory_module.inventory_tree(root, generated_at="2026-07-29T00:00:00Z")

    assert first["report_id"] == second["report_id"]
    assert first["generated_at"] != second["generated_at"]
