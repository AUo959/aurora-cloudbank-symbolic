"""
Tests for src.monitoring.ethics_gate — ethics-gated quantum simulation.

Covers:
- check_ethics passes when engine permits action
- check_ethics raises EthicsViolationError when engine blocks action
- check_ethics fails closed when EthicsEngine is unavailable for high-impact work
- check_ethics fails closed when EthicsEngine raises an unexpected error
- check_ethics can explicitly allow low-risk degraded operation with visible logging
- EthicsViolationError carries the violations list
- Quantum endpoint returns 422 when ethics check fails (mock)
- Quantum endpoint proceeds when ethics check passes (mock)
- EthicsViolationError message includes the action type
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.monitoring.ethics_gate import (
    EthicsViolationError,
    _non_blocking_severity,
    _violations_to_verdict,
    check_ethics,
)
from modules.superposition_gate import VerdictSeverity


# ---------------------------------------------------------------------------
# Unit tests for the collapse()-adapter helpers
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_non_blocking_severity_maps_known_levels():
    for value, expected in (
        ("low", (VerdictSeverity.WARN, 0.7)),
        ("medium", (VerdictSeverity.WARN, 0.5)),
        ("high", (VerdictSeverity.THROTTLE, 0.3)),
        ("critical", (VerdictSeverity.THROTTLE, 0.1)),
    ):
        violation = MagicMock()
        violation.severity.value = value
        assert _non_blocking_severity(violation) == expected


@pytest.mark.unit
def test_non_blocking_severity_falls_back_for_unknown_value():
    violation = MagicMock()
    violation.severity.value = "not_a_real_severity"
    assert _non_blocking_severity(violation) == (VerdictSeverity.WARN, 0.5)


@pytest.mark.unit
def test_non_blocking_severity_falls_back_when_severity_missing():
    # A test double/mock that never sets `.severity` to a real enum must not
    # raise -- this is what lets existing MagicMock()-based tests pass.
    violation = MagicMock(spec=[])
    assert _non_blocking_severity(violation) == (VerdictSeverity.WARN, 0.5)


@pytest.mark.unit
def test_violations_to_verdict_empty_list_is_allow():
    verdict = _violations_to_verdict([], "tag_1")
    assert verdict.severity == VerdictSeverity.ALLOW
    assert verdict.hard_veto is False
    assert verdict.score == 1.0
    assert verdict.context_tag == "tag_1"


@pytest.mark.unit
def test_violations_to_verdict_non_blocking_violation_does_not_hard_veto():
    violation = MagicMock()
    violation.blocked = False
    violation.severity.value = "high"
    violation.rule_name = "some_rule"

    verdict = _violations_to_verdict([violation], None)
    assert verdict.hard_veto is False
    assert verdict.severity == VerdictSeverity.THROTTLE


@pytest.mark.unit
def test_violations_to_verdict_blocked_violation_forces_hard_veto_regardless_of_severity():
    # Even a nominally "low" severity violation must hard-veto if blocked=True --
    # only `blocked` drives the raise decision, never the severity mapping.
    violation = MagicMock()
    violation.blocked = True
    violation.severity.value = "low"
    violation.rule_name = "low_severity_but_blocking_rule"

    verdict = _violations_to_verdict([violation], "tag_2")
    assert verdict.hard_veto is True
    assert verdict.severity == VerdictSeverity.HARD_VETO
    assert verdict.score == 0.0
    assert "low_severity_but_blocking_rule" in verdict.reason


@pytest.mark.unit
def test_violations_to_verdict_hard_veto_audits_blocking_violation():
    blocking = MagicMock()
    blocking.blocked = True
    blocking.severity.value = "low"
    blocking.rule_name = "blocking_rule"

    non_blocking = MagicMock()
    non_blocking.blocked = False
    non_blocking.severity.value = "critical"
    non_blocking.rule_name = "non_blocking_rule"

    verdict = _violations_to_verdict([blocking, non_blocking], None)

    assert verdict.hard_veto is True
    assert verdict.severity == VerdictSeverity.HARD_VETO
    assert verdict.score == 0.0
    assert "worst=blocking_rule" in verdict.reason


@pytest.mark.unit
def test_violations_to_verdict_tie_break_is_order_independent():
    alpha = MagicMock()
    alpha.blocked = False
    alpha.severity.value = "medium"
    alpha.rule_name = "alpha_rule"

    omega = MagicMock()
    omega.blocked = False
    omega.severity.value = "medium"
    omega.rule_name = "omega_rule"

    forward = _violations_to_verdict([omega, alpha], None)
    reverse = _violations_to_verdict([alpha, omega], None)

    assert forward.reason == reverse.reason
    assert "worst=alpha_rule" in forward.reason


@pytest.mark.unit
def test_check_ethics_raises_on_low_severity_blocked_violation():
    # Regression guard for the same invariant as above, at the check_ethics()
    # level: a "low" severity violation that is nonetheless auto_block=True
    # must still raise, matching the pre-collapse() check_should_block() behavior.
    violation = MagicMock()
    violation.blocked = True
    violation.severity.value = "low"
    violation.rule_name = "low_severity_but_blocking_rule"
    violation.to_dict.return_value = {"rule_id": "X", "blocked": True}

    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.return_value = [violation]
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", MagicMock()):
        with pytest.raises(EthicsViolationError):
            check_ethics("quantum_simulate", {"scenario_type": "dangerous"})


# ---------------------------------------------------------------------------
# Unit tests for check_ethics()
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_check_ethics_passes_when_no_violations():
    """check_ethics does not raise when EthicsEngine returns no violations."""
    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.return_value = []
    mock_engine_instance.check_should_block.return_value = False
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    mock_context_cls = MagicMock()

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", mock_context_cls):
        # Should not raise
        check_ethics("quantum_simulate", {"scenario_type": "supply_chain"})


@pytest.mark.unit
def test_check_ethics_raises_when_blocked():
    """check_ethics raises EthicsViolationError when engine signals block."""
    violation = MagicMock()
    violation.blocked = True
    violation.to_dict.return_value = {
        "rule_id": "SAFETY_001",
        "severity": "critical",
        "description": "Life safety violation",
        "blocked": True,
    }

    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.return_value = [violation]
    mock_engine_instance.check_should_block.return_value = True
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", MagicMock()):
        with pytest.raises(EthicsViolationError) as exc_info:
            check_ethics("quantum_simulate", {"scenario_type": "dangerous"})

    assert len(exc_info.value.violations) == 1
    assert exc_info.value.violations[0]["rule_id"] == "SAFETY_001"


@pytest.mark.unit
def test_check_ethics_fails_closed_when_import_fails():
    """High-impact checks fail closed when EthicsEngine cannot be imported."""
    import sys

    original_modules = {}
    modules_to_remove = ["src.monitoring.ethics_engine"]

    for mod in modules_to_remove:
        if mod in sys.modules:
            original_modules[mod] = sys.modules.pop(mod)

    try:
        with patch.dict("sys.modules", {"src.monitoring.ethics_engine": None}):
            with pytest.raises(EthicsViolationError) as exc_info:
                check_ethics("quantum_simulate", {"scenario_type": "supply_chain"})
    finally:
        # Restore original modules
        for mod, val in original_modules.items():
            sys.modules[mod] = val

    assert exc_info.value.violations[0]["rule_id"] == "ETHICS_GATE_UNAVAILABLE"
    assert exc_info.value.violations[0]["blocked"] is True
    assert exc_info.value.violations[0]["impact_level"] == "high"


@pytest.mark.unit
def test_check_ethics_fails_closed_on_unexpected_error():
    """High-impact checks fail closed when EthicsEngine raises an unexpected error."""
    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.side_effect = RuntimeError("db connection lost")
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", MagicMock()):
        with pytest.raises(EthicsViolationError) as exc_info:
            check_ethics("quantum_simulate", {"scenario_type": "energy_grid"})

    assert "failing closed" in str(exc_info.value)
    assert exc_info.value.violations[0]["rule_id"] == "ETHICS_GATE_UNAVAILABLE"
    assert exc_info.value.violations[0]["error_type"] == "RuntimeError"


@pytest.mark.unit
def test_check_ethics_allows_explicit_low_risk_degraded_mode(caplog):
    """Low-risk degraded operation is allowed only when explicitly requested."""
    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.side_effect = RuntimeError("db connection lost")
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", MagicMock()), \
         caplog.at_level("WARNING"):
        check_ethics(
            "read_status",
            {"resource": "health"},
            impact_level="low",
            allow_degraded=True,
        )

    assert "allowing low-risk degraded action 'read_status'" in caplog.text


@pytest.mark.unit
def test_check_ethics_degraded_mode_does_not_allow_high_impact():
    """allow_degraded cannot silently permit high-impact operations."""
    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.side_effect = RuntimeError("db connection lost")
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", MagicMock()):
        with pytest.raises(EthicsViolationError):
            check_ethics(
                "quantum_simulate",
                {"scenario_type": "energy_grid"},
                impact_level="high",
                allow_degraded=True,
            )


@pytest.mark.unit
def test_ethics_violation_error_carries_violations():
    """EthicsViolationError stores and exposes the violations list."""
    violations = [
        {"rule_id": "AI_001", "severity": "critical", "blocked": True},
        {"rule_id": "MISSION_001", "severity": "high", "blocked": True},
    ]
    exc = EthicsViolationError("Two violations", violations)

    assert str(exc) == "Two violations"
    assert exc.violations is violations
    assert len(exc.violations) == 2
    assert exc.violations[0]["rule_id"] == "AI_001"


@pytest.mark.unit
def test_check_ethics_error_message_includes_action_type():
    """EthicsViolationError message contains the action_type string."""
    violation = MagicMock()
    violation.blocked = True
    violation.to_dict.return_value = {"rule_id": "X", "blocked": True}

    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.return_value = [violation]
    mock_engine_instance.check_should_block.return_value = True
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", MagicMock()):
        with pytest.raises(EthicsViolationError) as exc_info:
            check_ethics("quantum_simulate", {})

    assert "quantum_simulate" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Integration tests for the quantum simulator endpoint
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.api
def test_quantum_endpoint_returns_422_when_ethics_blocked():
    """POST /simulate/scenario returns 422 when ethics gate blocks the request."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from modules.quantum_simulator.api import router
    from src.middleware.fastapi_security import require_csrf_token

    app = FastAPI()
    app.include_router(router)

    # Override CSRF dependency so it never blocks
    app.dependency_overrides[require_csrf_token] = lambda: None

    client = TestClient(app, raise_server_exceptions=False)

    violation_dict = {
        "rule_id": "SAFETY_001",
        "rule_name": "Life Safety Priority",
        "severity": "critical",
        "blocked": True,
        "description": "Dangerous scenario",
    }

    with patch(
        "modules.quantum_simulator.api.check_ethics",
        side_effect=EthicsViolationError("Ethics blocked", [violation_dict]),
    ):
        response = client.post(
            "/simulate/scenario",
            json={
                "name": "Dangerous Test",
                "scenario_type": "supply_chain",
                "backend": "mock",
                "parameters": {},
            },
        )

    assert response.status_code == 422
    body = response.json()
    assert body["detail"]["error"] == "ethics_violation"
    assert "violations" in body["detail"]
    assert len(body["detail"]["violations"]) == 1


@pytest.mark.unit
@pytest.mark.api
def test_quantum_endpoint_proceeds_when_ethics_passes():
    """POST /simulate/scenario proceeds to simulation when ethics gate passes."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from modules.quantum_simulator.api import router
    from modules.quantum_simulator.schemas import QuantumBackend, ScenarioType, SimulationResult
    from src.middleware.fastapi_security import require_csrf_token

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[require_csrf_token] = lambda: None

    client = TestClient(app, raise_server_exceptions=False)

    mock_result = SimulationResult(
        simulation_id="sim_test_001",
        scenario_name="Allowed Test",
        scenario_type=ScenarioType.SUPPLY_CHAIN,
        status="completed",
        backend_used=QuantumBackend.MOCK,
        start_time=datetime.now(timezone.utc),
        parameters={},
        metrics={},
    )

    async def fake_execute(req):
        return mock_result

    mock_engine_instance = MagicMock()
    mock_engine_instance.execute_scenario = fake_execute

    mock_cache = MagicMock()
    mock_orch = MagicMock()

    async def fake_get_orchestrator():
        return mock_orch

    with patch("modules.quantum_simulator.api.check_ethics"), \
         patch("modules.quantum_simulator.api.ScenarioEngine", return_value=mock_engine_instance), \
         patch("modules.quantum_simulator.api.get_orchestrator", fake_get_orchestrator), \
         patch("modules.quantum_simulator.api.get_cache", return_value=mock_cache):

        response = client.post(
            "/simulate/scenario",
            json={
                "name": "Allowed Test",
                "scenario_type": "supply_chain",
                "backend": "mock",
                "parameters": {},
            },
        )

    # Ethics passed — simulation ran, not blocked by ethics gate
    assert response.status_code != 422
    assert response.status_code in (200, 202)
