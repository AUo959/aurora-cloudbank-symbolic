"""
Tests for src.monitoring.ethics_gate — ethics-gated quantum simulation.

Covers:
- check_ethics passes when engine permits action
- check_ethics raises EthicsViolationError when engine blocks action
- check_ethics is a no-op when EthicsEngine is unavailable (ImportError)
- EthicsViolationError carries the violations list
- Quantum endpoint returns 422 when ethics check fails (mock)
- Quantum endpoint proceeds when ethics check passes (mock)
- check_ethics is a no-op when EthicsEngine raises an unexpected error
- EthicsViolationError message includes the action type
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, AsyncMock

from src.monitoring.ethics_gate import EthicsViolationError, check_ethics


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
def test_check_ethics_noop_when_import_fails():
    """check_ethics silently passes when EthicsEngine cannot be imported."""
    import sys
    original_modules = {}
    modules_to_remove = ["src.monitoring.ethics_engine"]

    for mod in modules_to_remove:
        if mod in sys.modules:
            original_modules[mod] = sys.modules.pop(mod)

    try:
        with patch.dict("sys.modules", {"src.monitoring.ethics_engine": None}):
            # Should not raise — graceful degradation
            check_ethics("quantum_simulate", {"scenario_type": "supply_chain"})
    finally:
        # Restore original modules
        for mod, val in original_modules.items():
            sys.modules[mod] = val


@pytest.mark.unit
def test_check_ethics_noop_on_unexpected_error():
    """check_ethics silently passes when EthicsEngine raises an unexpected error."""
    mock_engine_instance = MagicMock()
    mock_engine_instance.evaluate_action.side_effect = RuntimeError("db connection lost")
    mock_engine_cls = MagicMock(return_value=mock_engine_instance)

    with patch("src.monitoring.ethics_engine.EthicsEngine", mock_engine_cls), \
         patch("src.monitoring.ethics_engine.ActionContext", MagicMock()):
        # Should not raise — graceful degradation
        check_ethics("quantum_simulate", {"scenario_type": "energy_grid"})


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
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
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
    from fastapi.testclient import TestClient
    from fastapi import FastAPI
    from modules.quantum_simulator.api import router
    from modules.quantum_simulator.schemas import SimulationResult, ScenarioType, QuantumBackend
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
