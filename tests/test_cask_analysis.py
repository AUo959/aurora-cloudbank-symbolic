from modules.cask import (
    generate_risk_assessment,
    generate_technical_specifications,
    generate_vs_sota_comparison,
)


def test_specifications_columns():
    pass
    df = generate_technical_specifications()
    assert set(df.columns) == {
        "Component",
        "Technical_Specification",
        "Key_Innovation",
        "Integration_Challenge",
    }


def test_comparison_rows():
    pass
    df = generate_vs_sota_comparison()
    assert len(df) == 10


def test_risk_assessment_priority():
    pass
    df = generate_risk_assessment()
    assert "Priority" in df.columns
    assert set(df["Priority"]) >= {"Critical", "High", "Medium"}
