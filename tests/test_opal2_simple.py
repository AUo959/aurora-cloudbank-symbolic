"""Small fail-closed smoke tests for the OPAL2 module surface."""

from pathlib import Path

import pytest
from fastapi import FastAPI


REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.smoke
def test_api_imports():
    """FastAPI must be importable and able to construct an application."""

    app = FastAPI(title="OPAL2 smoke test")

    assert app.title == "OPAL2 smoke test"


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.smoke
def test_opal2_structure():
    """Required OPAL2 runtime files must exist in the repository."""

    opal2_path = REPO_ROOT / "modules" / "opal2"
    expected_paths = {
        opal2_path / "__init__.py",
        opal2_path / "api" / "opal2_api.py",
        opal2_path / "glyph_cache.py",
        opal2_path / "glyph_core.py",
        opal2_path / "tool_contract.py",
        opal2_path / "tool_package.py",
        opal2_path / "tool_registry.py",
    }

    missing_paths = sorted(
        str(path.relative_to(REPO_ROOT)) for path in expected_paths if not path.is_file()
    )
    assert not missing_paths, f"missing OPAL2 runtime files: {missing_paths}"
