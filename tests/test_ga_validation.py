import pytest

from src.integrations._ga_validation import validate_ga_expression


@pytest.mark.parametrize("expr", ["e1 + e2", "3.5 * e12"])
def test_validate_ga_expression_accepts_valid_input(expr):
    validate_ga_expression("expression_a", expr)


@pytest.mark.parametrize("expr", ["e1; rm -rf /"])
def test_validate_ga_expression_rejects_whitelist_failures(expr):
    with pytest.raises(ValueError, match="contains characters not permitted"):
        validate_ga_expression("expression_a", expr)


@pytest.mark.parametrize("expr", ["__import__('os')", "eval(x)", "import sys"])
def test_validate_ga_expression_rejects_blacklist_failures(expr):
    with pytest.raises(ValueError, match="contains a disallowed token"):
        validate_ga_expression("expression_a", expr)


def test_validate_ga_expression_rejects_empty_string():
    with pytest.raises(ValueError, match="must not be empty"):
        validate_ga_expression("expression_a", "")
