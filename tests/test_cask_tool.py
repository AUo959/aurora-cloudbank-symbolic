import os

from modules.cask_tool import (
    generate_architecture_chart,
    load_risk_assessment,
    load_specifications,
    load_vs_sota,
)


def test_load_specifications():
    df = load_specifications()
    assert not df.empty
    assert "Component" in df.columns


def test_load_risk_assessment():
    df = load_risk_assessment()
    assert not df.empty
    assert "Risk_Category" in df.columns


def test_load_vs_sota():
    df = load_vs_sota()
    assert not df.empty
    assert "Technical_Domain" in df.columns


def test_generate_architecture_chart(tmp_path):
    out = tmp_path / "chart.png"
    path = generate_architecture_chart(str(out))
    assert os.path.exists(path)
