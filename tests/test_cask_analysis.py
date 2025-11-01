from modules.cask import (
    generate_risk_assessment,
    generate_technical_specifications,
    generate_vs_sota_comparison,
)


@pytest.mark.unit
def test_specifications_columns():
    df = generate_technical_specifications()
    assert set(df.columns) == {
        "Component",
        "Technical_Specification",
        "Key_Innovation",
        "Integration_Challenge",
    }


@pytest.mark.unit
def test_comparison_rows():
    df = generate_vs_sota_comparison()
    assert len(df) == 10


@pytest.mark.unit
def test_risk_assessment_priority():
    df = generate_risk_assessment()
    assert "Priority" in df.columns
    assert set(df["Priority"]) >= {"Critical", "High", "Medium"}
