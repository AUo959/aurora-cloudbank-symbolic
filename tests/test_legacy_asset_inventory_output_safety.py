"""Regression tests for fail-closed legacy-inventory report creation."""

from __future__ import annotations

import importlib.util
import os
import stat
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "salvage" / "inventory_legacy_assets.py"
SECURE_OUTPUT_SUPPORTED = os.open in os.supports_dir_fd and hasattr(os, "O_DIRECTORY")

pytestmark = pytest.mark.skipif(
    not SECURE_OUTPUT_SUPPORTED,
    reason="secure directory-relative output creation is unavailable on this platform",
)


def _load_inventory_module():
    spec = importlib.util.spec_from_file_location("inventory_legacy_assets_output_safety", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def inventory_module():
    return _load_inventory_module()


@pytest.mark.unit
def test_report_is_created_as_new_single_link_regular_file(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    output = tmp_path / "reports" / "inventory.json"
    payload = '{"read_only": true}\n'

    created = inventory_module.write_report_exclusive(root, output, payload)

    assert created == output.resolve()
    assert output.read_text(encoding="utf-8") == payload
    metadata = output.stat()
    assert stat.S_ISREG(metadata.st_mode)
    assert metadata.st_nlink == 1
    assert stat.S_IMODE(metadata.st_mode) == 0o600


@pytest.mark.unit
def test_existing_output_file_is_rejected_without_replacement(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    output = tmp_path / "reports" / "inventory.json"
    output.parent.mkdir()
    output.write_text("preserve-existing\n", encoding="utf-8")

    with pytest.raises(inventory_module.InventoryError, match="already exists"):
        inventory_module.write_report_exclusive(root, output, "replacement\n")

    assert output.read_text(encoding="utf-8") == "preserve-existing\n"


@pytest.mark.unit
def test_existing_hard_link_cannot_modify_inventoried_source(tmp_path: Path, inventory_module) -> None:
    if not hasattr(os, "link"):
        pytest.skip("hard-link creation is unavailable on this platform")

    root = tmp_path / "legacy"
    root.mkdir()
    source = root / "source.txt"
    source.write_text("source-custody\n", encoding="utf-8")

    output = tmp_path / "reports" / "inventory.json"
    output.parent.mkdir()
    try:
        os.link(source, output)
    except OSError:
        pytest.skip("hard-link creation is unavailable for this filesystem")

    with pytest.raises(inventory_module.InventoryError, match="already exists"):
        inventory_module.write_report_exclusive(root, output, "replacement\n")

    assert source.read_text(encoding="utf-8") == "source-custody\n"
    assert output.read_text(encoding="utf-8") == "source-custody\n"
    assert source.stat().st_ino == output.stat().st_ino


@pytest.mark.unit
def test_existing_symlink_output_is_rejected_without_touching_target(tmp_path: Path, inventory_module) -> None:
    root = tmp_path / "legacy"
    root.mkdir()
    target = root / "source.txt"
    target.write_text("source-custody\n", encoding="utf-8")

    output = tmp_path / "reports" / "inventory.json"
    output.parent.mkdir()
    try:
        output.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")

    with pytest.raises(
        inventory_module.InventoryError,
        match="outside the inventory source tree|already exists",
    ):
        inventory_module.write_report_exclusive(root, output, "replacement\n")

    assert target.read_text(encoding="utf-8") == "source-custody\n"
    assert output.is_symlink()
