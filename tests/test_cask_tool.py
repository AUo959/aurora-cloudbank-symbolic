import os
import zipfile

import pytest

from modules.cask_tool import generate_architecture_chart, load_risk_assessment, load_specifications, load_vs_sota


# Check if CASK assets are available (not just LFS pointer)
def cask_assets_available():
    """Check if CASK_Assets.zip is actually available (not LFS pointer)."""
    paths = ["CASK_Assets.zip", "archives/CASK_Assets.zip"]
    for path in paths:
        if os.path.exists(path):
            try:
                with zipfile.ZipFile(path) as zf:
                    return True
            except zipfile.BadZipFile:
                continue
    return False


requires_cask_assets = pytest.mark.skipif(
    not cask_assets_available(),
    reason="CASK_Assets.zip not available (may be Git LFS pointer)"
)


@requires_cask_assets
def test_load_specifications():
    df = load_specifications()
    assert not df.empty
    assert "Component" in df.columns


@requires_cask_assets
def test_load_risk_assessment():
    df = load_risk_assessment()
    assert not df.empty
    assert "Risk_Category" in df.columns


@requires_cask_assets
def test_load_vs_sota():
    df = load_vs_sota()
    assert not df.empty
    assert "Technical_Domain" in df.columns


def test_generate_architecture_chart(tmp_path):
    out = tmp_path / "chart.png"
    path = generate_architecture_chart(str(out))
    assert out.exists()
    assert path == str(out)
