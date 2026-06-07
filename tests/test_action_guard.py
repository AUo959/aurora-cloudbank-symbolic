"""Tests for src.monitoring.action_guard.

Verifies that evaluate_response correctly calls MonitoringSystem.evaluate_action,
dispatches violations to registered enforcement handlers, and never raises
regardless of downstream failures.
"""
from __future__ import annotations

import pytest

import src.monitoring.action_guard as _guard_module
from src.monitoring.action_guard import (
    clear_enforcement_handlers,
    evaluate_response,
    register_enforcement_handler,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_module_state():
    """Reset singleton and enforcement-handler list between tests."""
    # Clear enforcement handlers
    clear_enforcement_handlers()
    # Reset cached MonitoringSystem singleton so each test starts clean
    _guard_module._monitoring = None
    yield
    # Cleanup after test as well
    clear_enforcement_handlers()
    _guard_module._monitoring = None


def _make_monitoring_stub(violations=None, raise_on_evaluate=False):
    """Return a simple object that mimics MonitoringSystem.evaluate_action."""

    class _Stub:
        def evaluate_action(self, agent_id, action_type, parameters, context_tag=None):
            if raise_on_evaluate:
                raise RuntimeError("synthetic evaluate_action error")
            return {
                "violations": violations or [],
                "blocked": bool(violations),
                "violation_count": len(violations or []),
                "agent_id": agent_id,
                "timestamp": "2026-01-01T00:00:00Z",
            }

    return _Stub()


# ---------------------------------------------------------------------------
# Tests — evaluate_response calls monitoring
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_evaluate_response_calls_monitoring_evaluate_action():
    """evaluate_response should delegate to monitoring.evaluate_action."""
    calls = []

    class _Stub:
        def evaluate_action(self, **kwargs):
            calls.append(kwargs)
            return {"violations": [], "blocked": False, "violation_count": 0}

    _guard_module._monitoring = _Stub()
    evaluate_response("chat_response", {"status": "ok"})
    assert len(calls) == 1
    assert calls[0]["action_type"] == "chat_response"


@pytest.mark.unit
def test_evaluate_response_passes_agent_id():
    """The agent_id keyword arg must be forwarded to evaluate_action."""
    calls = []

    class _Stub:
        def evaluate_action(self, **kwargs):
            calls.append(kwargs)
            return {"violations": [], "blocked": False, "violation_count": 0}

    _guard_module._monitoring = _Stub()
    evaluate_response("agent_execute", {}, agent_id="crew-thorne")
    assert calls[0]["agent_id"] == "crew-thorne"


@pytest.mark.unit
def test_evaluate_response_includes_metadata_in_parameters():
    """Metadata dict should be forwarded inside parameters."""
    calls = []

    class _Stub:
        def evaluate_action(self, **kwargs):
            calls.append(kwargs)
            return {"violations": [], "blocked": False, "violation_count": 0}

    _guard_module._monitoring = _Stub()
    evaluate_response(
        "quantum_simulate",
        {"simulation_id": "sim-001"},
        metadata={"endpoint": "/simulate/scenario", "scenario_type": "supply_chain"},
    )
    params = calls[0]["parameters"]
    assert params["endpoint"] == "/simulate/scenario"
    assert params["scenario_type"] == "supply_chain"


# ---------------------------------------------------------------------------
# Tests — graceful degradation when monitoring is unavailable
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_evaluate_response_does_not_raise_when_monitoring_unavailable():
    """evaluate_response must not raise if MonitoringSystem cannot be initialised."""
    # Ensure _monitoring remains None (no real singleton)
    _guard_module._monitoring = None

    # Patch _get_monitoring to return None (simulates import failure)
    original = _guard_module._get_monitoring

    def _no_monitoring():
        return None

    _guard_module._get_monitoring = _no_monitoring
    try:
        # Must not raise
        evaluate_response("chat_response", {"status": "ok"})
    finally:
        _guard_module._get_monitoring = original


@pytest.mark.unit
def test_evaluate_response_does_not_raise_when_evaluate_action_raises():
    """If evaluate_action raises, evaluate_response must swallow and log only."""
    _guard_module._monitoring = _make_monitoring_stub(raise_on_evaluate=True)
    # Must not propagate the RuntimeError
    evaluate_response("agent_execute", {"tool": "symbolic_processing"})


# ---------------------------------------------------------------------------
# Tests — enforcement handler dispatch
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_enforcement_handler_called_on_violation():
    """A registered enforcement handler must be called when there are violations."""
    violation = {"rule_id": "R-001", "severity": "high", "blocked": False}
    _guard_module._monitoring = _make_monitoring_stub(violations=[violation])

    received = []
    register_enforcement_handler(received.append)

    evaluate_response("agent_execute", {})
    # Handlers are called once per violation (individual violation dict passed)
    assert len(received) == 1
    assert received[0]["rule_id"] == "R-001"


@pytest.mark.unit
def test_enforcement_handler_not_called_when_no_violations():
    """Enforcement handlers must NOT fire when evaluate_action returns no violations."""
    _guard_module._monitoring = _make_monitoring_stub(violations=[])

    received = []
    register_enforcement_handler(received.append)

    evaluate_response("chat_response", {"status": "ok"})
    assert received == []


@pytest.mark.unit
def test_multiple_enforcement_handlers_called_in_order():
    """All registered handlers must be called in registration order."""
    violation = {"rule_id": "R-002", "severity": "critical", "blocked": True}
    _guard_module._monitoring = _make_monitoring_stub(violations=[violation])

    call_order = []
    register_enforcement_handler(lambda v: call_order.append("first"))
    register_enforcement_handler(lambda v: call_order.append("second"))
    register_enforcement_handler(lambda v: call_order.append("third"))

    evaluate_response("quantum_simulate", {})
    assert call_order == ["first", "second", "third"]


@pytest.mark.unit
def test_enforcement_handler_exception_does_not_prevent_other_handlers():
    """A failing enforcement handler must not prevent subsequent handlers from running."""
    violation = {"rule_id": "R-003", "severity": "medium", "blocked": False}
    _guard_module._monitoring = _make_monitoring_stub(violations=[violation])

    received = []

    def _bad_handler(v):
        raise ValueError("handler exploded")

    register_enforcement_handler(_bad_handler)
    register_enforcement_handler(received.append)

    # Must not raise; second handler must still run for the one violation
    evaluate_response("agent_execute", {})
    assert len(received) >= 1


@pytest.mark.unit
def test_clear_enforcement_handlers_removes_all():
    """clear_enforcement_handlers must empty the handler list."""
    violation = {"rule_id": "R-004", "severity": "low", "blocked": False}
    _guard_module._monitoring = _make_monitoring_stub(violations=[violation])

    received = []
    register_enforcement_handler(received.append)
    clear_enforcement_handlers()

    evaluate_response("agent_execute", {})
    assert received == [], "Handlers were not cleared"
