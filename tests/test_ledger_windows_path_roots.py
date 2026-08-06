"""Regression tests for ledger path-root hardening (#1337).

Both cases here are Windows-shaped, but every assertion runs on every platform.
No CI job runs the Python suite on Windows, so a test guarded by
``sys.platform == "win32"`` would never execute and would prove nothing.
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath

import pytest

from modules.insight_ledger.ledger_core import resolve_export_root, validate_safe_path


# --------------------------------------------------------------------------
# Drive-relative input must fail closed
# --------------------------------------------------------------------------

DRIVE_RELATIVE = [
    "C:foo",             # drive, no root -- is_absolute() is False on Windows
    "C:ledger.json",
    "D:nested/export.json",
    "c:lowercase.json",
]


def test_drive_relative_is_not_absolute_on_windows() -> None:
    """The premise: these carry a drive but are not absolute.

    If this ever stops holding, the guard below is testing nothing.
    """
    for raw in DRIVE_RELATIVE:
        candidate = PureWindowsPath(raw)
        assert candidate.drive, f"{raw} should carry a drive"
        assert not candidate.is_absolute(), f"{raw} should not be absolute"


def test_joining_drive_relative_discards_the_root() -> None:
    """Why this matters: an anchored right operand drops the containment root."""
    joined = PureWindowsPath("D:/ledger/exports") / "C:foo"
    assert joined == PureWindowsPath("C:foo")
    assert "ledger" not in str(joined)


@pytest.mark.security
@pytest.mark.parametrize("raw", DRIVE_RELATIVE)
def test_drive_relative_paths_are_rejected(tmp_path: Path, raw: str) -> None:
    """Drive-bearing input must be refused rather than joined and resolved."""
    with pytest.raises(ValueError, match="outside allowed directory"):
        validate_safe_path(raw, tmp_path, allow_create=True)


@pytest.mark.security
def test_windows_root_relative_is_rejected(tmp_path: Path) -> None:
    r"""``\foo`` is root-relative on Windows: root but no drive."""
    with pytest.raises(ValueError, match="outside allowed directory"):
        validate_safe_path(r"\ledger.json", tmp_path, allow_create=True)


def test_ordinary_relative_paths_still_work(tmp_path: Path) -> None:
    """The guard must not reject legitimate relative export names."""
    result = validate_safe_path("export.json", tmp_path, allow_create=True)
    assert result == (tmp_path.resolve() / "export.json")

    nested = validate_safe_path("sub/export.json", tmp_path, allow_create=True)
    assert nested == (tmp_path.resolve() / "sub" / "export.json")


def test_traversal_still_rejected(tmp_path: Path) -> None:
    """Pre-existing containment behaviour is unchanged."""
    with pytest.raises(ValueError, match="Parent directory references not allowed"):
        validate_safe_path("../escape.json", tmp_path, allow_create=True)


# --------------------------------------------------------------------------
# Export-root misconfiguration must fail loudly
# --------------------------------------------------------------------------

@pytest.mark.security
def test_export_root_rejects_filesystem_root() -> None:
    """A root of "/" would make containment vacuous."""
    anchor = Path(Path.cwd().anchor)
    with pytest.raises(ValueError, match="must not be the filesystem root"):
        resolve_export_root(str(anchor))


@pytest.mark.security
def test_export_root_rejects_non_directory(tmp_path: Path) -> None:
    """Pointing the root at a file should fail with a message naming the var."""
    target = tmp_path / "not-a-dir"
    target.write_text("x")
    with pytest.raises(ValueError, match="AURORA_LEDGER_EXPORT_PATH must be a directory"):
        resolve_export_root(str(target))


def test_export_root_creates_and_returns_directory(tmp_path: Path) -> None:
    """A valid configured root is created if absent and returned resolved."""
    target = tmp_path / "exports" / "nested"
    result = resolve_export_root(str(target))
    assert result == target.resolve()
    assert result.is_dir()


def test_export_root_default_when_unset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty value falls back to <cwd>/data/exports."""
    monkeypatch.chdir(tmp_path)
    result = resolve_export_root("")
    assert result == (tmp_path / "data" / "exports").resolve()
    assert result.is_dir()
