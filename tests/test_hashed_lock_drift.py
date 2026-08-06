"""Tests for the hashed-lock drift checker (#1366).

The checker gates CI, so a bug in it either blocks every PR or — worse — passes
silently while the lock is stale. Both directions are covered here.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_hashed_lock_drift.py"

sys.path.insert(0, str(SCRIPT.parent))
from check_hashed_lock_drift import locked_names, normalize, requirement_name  # noqa: E402


@pytest.mark.parametrize(
    "line,expected",
    [
        ("pytest==9.0.3", "pytest"),
        ("pytest==9.0.3 \\", "pytest"),
        ("fastapi>=0.140.1", "fastapi"),
        ("uvicorn[standard]>=0.51.0", "uvicorn"),
        ("mcp>=1.28.1,<2.0.0", "mcp"),
        ("foo ; python_version < '3.13'", "foo"),
        ("  # a comment", None),
        ("", None),
        ("-r requirements.txt", None),
        ("--hash=sha256:abc", None),
    ],
)
def test_requirement_name_parsing(line: str, expected: str | None) -> None:
    assert requirement_name(line) == expected


def test_normalize_follows_pep503() -> None:
    """typing_extensions, typing-extensions and Typing.Extensions are one name."""
    assert normalize("typing_extensions") == "typing-extensions"
    assert normalize("Typing.Extensions") == "typing-extensions"
    assert normalize("ruamel--yaml") == "ruamel-yaml"


def test_locked_names_ignores_indented_hash_lines(tmp_path: Path) -> None:
    """Hash continuation lines are indented and must not be read as packages."""
    lock = tmp_path / "lock.txt"
    lock.write_text(
        "# generated\n"
        "pytest==9.0.3 \\\n"
        "    --hash=sha256:aaa \\\n"
        "    --hash=sha256:bbb\n"
        "    # via -r requirements-test.txt\n"
        "fastapi==0.136.3 \\\n"
        "    --hash=sha256:ccc\n"
    )
    assert locked_names(lock) == {"pytest", "fastapi"}


def test_real_lock_has_no_drift() -> None:
    """The committed lock must cover everything currently declared."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_detects_a_missing_requirement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A package declared but absent from the lock must fail, and be named."""
    import check_hashed_lock_drift as mod

    (tmp_path / "requirements.txt").write_text("fastapi==0.136.3\nbrand-new-pkg==1.0\n")
    (tmp_path / "requirements-test.txt").write_text("pytest==9.0.3\n")
    (tmp_path / "requirements-ci-hashed.txt").write_text(
        "fastapi==0.136.3 \\\n    --hash=sha256:a\npytest==9.0.3 \\\n    --hash=sha256:b\n"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    assert mod.main() == 1


def test_passes_when_lock_is_complete(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The inverse: a complete lock must not report drift."""
    import check_hashed_lock_drift as mod

    (tmp_path / "requirements.txt").write_text("fastapi==0.136.3\n")
    (tmp_path / "requirements-test.txt").write_text("pytest==9.0.3\n")
    (tmp_path / "requirements-ci-hashed.txt").write_text(
        "fastapi==0.136.3 \\\n    --hash=sha256:a\npytest==9.0.3 \\\n    --hash=sha256:b\n"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    assert mod.main() == 0


def test_name_normalisation_prevents_false_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """typing_extensions in one file and typing-extensions in the other must match."""
    import check_hashed_lock_drift as mod

    (tmp_path / "requirements.txt").write_text("typing_extensions>=4.0\n")
    (tmp_path / "requirements-test.txt").write_text("")
    (tmp_path / "requirements-ci-hashed.txt").write_text(
        "typing-extensions==4.15.0 \\\n    --hash=sha256:a\n"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)

    assert mod.main() == 0
