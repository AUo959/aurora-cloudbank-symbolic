"""Tests for per-endpoint performance budgets (issue #839)."""
import pytest

from src.observability.performance_budgets import (
    EndpointBudget,
    ENDPOINT_BUDGETS,
    check_budget_violation,
    get_budget,
    list_budgets,
)


# ---------------------------------------------------------------------------
# get_budget
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.observability
def test_get_budget_known_endpoint():
    """get_budget returns an EndpointBudget for a registered endpoint."""
    budget = get_budget("GET", "/health")
    assert budget is not None
    assert isinstance(budget, EndpointBudget)
    assert budget.p95_ms > 0
    assert budget.p99_ms >= budget.p95_ms


@pytest.mark.unit
@pytest.mark.observability
def test_get_budget_method_case_insensitive():
    """get_budget normalises the HTTP method to uppercase."""
    assert get_budget("get", "/health") == get_budget("GET", "/health")


@pytest.mark.unit
@pytest.mark.observability
def test_get_budget_unknown_endpoint_returns_none():
    """get_budget returns None for an endpoint with no budget defined."""
    assert get_budget("GET", "/nonexistent/path/xyz") is None


@pytest.mark.unit
@pytest.mark.observability
def test_get_budget_unknown_method_returns_none():
    """get_budget returns None when method+path combo has no budget."""
    assert get_budget("DELETE", "/health") is None


# ---------------------------------------------------------------------------
# check_budget_violation
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.observability
def test_check_budget_violation_under_budget_returns_none():
    """No violation when duration is well within both p95 and p99."""
    result = check_budget_violation("GET", "/health", duration_ms=10.0, is_error=False)
    assert result is None


@pytest.mark.unit
@pytest.mark.observability
def test_check_budget_violation_p99_exceeded_returns_message():
    """Violation message is returned when duration exceeds p99."""
    budget = get_budget("GET", "/health")
    assert budget is not None, "Need a known budget for this test"

    over_p99 = budget.p99_ms + 1
    result = check_budget_violation("GET", "/health", duration_ms=over_p99, is_error=False)
    assert result is not None
    assert "p99 budget exceeded" in result
    assert "/health" in result


@pytest.mark.unit
@pytest.mark.observability
def test_check_budget_violation_between_p95_and_p99_returns_none():
    """Between p95 and p99 is a soft breach (logged at DEBUG) but not a violation."""
    budget = get_budget("GET", "/health")
    assert budget is not None

    midpoint = (budget.p95_ms + budget.p99_ms) / 2
    result = check_budget_violation("GET", "/health", duration_ms=midpoint, is_error=False)
    # Soft breaches do NOT return a violation string
    assert result is None


@pytest.mark.unit
@pytest.mark.observability
def test_check_budget_violation_no_budget_returns_none():
    """Returns None gracefully when no budget is defined for the endpoint."""
    result = check_budget_violation(
        "PATCH", "/no/budget/here", duration_ms=99999.0, is_error=False
    )
    assert result is None


# ---------------------------------------------------------------------------
# list_budgets
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.observability
def test_list_budgets_returns_all_entries():
    """list_budgets returns a dict with the same number of entries as ENDPOINT_BUDGETS."""
    budgets = list_budgets()
    assert isinstance(budgets, dict)
    assert len(budgets) == len(ENDPOINT_BUDGETS)


@pytest.mark.unit
@pytest.mark.observability
def test_list_budgets_entries_have_required_fields():
    """Every entry in list_budgets has p95_ms, p99_ms, error_rate_pct, and notes."""
    budgets = list_budgets()
    required_keys = {"p95_ms", "p99_ms", "error_rate_pct", "notes"}
    for key, value in budgets.items():
        assert required_keys <= value.keys(), f"Missing keys in budget for {key!r}"
        assert value["p95_ms"] > 0, f"p95_ms must be positive for {key!r}"
        assert value["p99_ms"] >= value["p95_ms"], f"p99_ms must be >= p95_ms for {key!r}"
        assert 0 <= value["error_rate_pct"] <= 100, f"error_rate_pct out of range for {key!r}"
