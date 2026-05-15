"""
Comprehensive test suite for Quantum State Synthesizer

Tests quantum state representation, orchestration, scenario execution,
caching, and API endpoints.

Anchor: T1-QSS-TEST
"""

import hashlib
import hmac
import importlib.util
import os
import sys
import time
import types
import unittest
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

if "slowapi" not in sys.modules and importlib.util.find_spec("slowapi") is None:
    slowapi_module = types.ModuleType("slowapi")
    slowapi_util_module = types.ModuleType("slowapi.util")

    class _Limiter:
        def __init__(self, *args, **kwargs):
            # Test stub: the limiter has no runtime state in local dependency-light runs.
            pass

        def limit(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    slowapi_module.Limiter = _Limiter
    slowapi_util_module.get_remote_address = lambda request: "test-client"
    sys.modules["slowapi"] = slowapi_module
    sys.modules["slowapi.util"] = slowapi_util_module

from modules.quantum_simulator import (
    MockQuantumProvider,
    OptimizationMethod,
    QuantumBackend,
    QuantumOrchestrator,
    QuantumState,
    ScenarioCache,
    ScenarioEngine,
    ScenarioRequest,
    ScenarioType,
    SimulatorQuantumProvider,
    StateVector,
    create_ghz_state,
    create_w_state,
)
from modules.quantum_simulator.api import router as quantum_simulator_router


def _auth_header():
    session_id = "test-session"
    timestamp = str(int(time.time()))
    message = f"{session_id}.{timestamp}"
    signature = hmac.new(
        os.environ["CSRF_SECRET_KEY"].encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    token = f"{session_id}.{timestamp}.{signature}"
    return {"Authorization": f"Bearer {token}"}


def _simulation_payload(name="API Test Simulation"):
    return {
        "scenario_type": "optimization",
        "name": name,
        "description": "Test simulation via API",
        "backend": "mock",
        "optimization_method": "qaoa",
        "parameters": {"num_variables": 3, "max_iterations": 10},
        "seed": 42,
    }


# ============================================================================
# Quantum State Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.quantum
def test_state_vector_initialization():
    """Test StateVector initialization and normalization."""
    # Valid normalized state
    amplitudes = [1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]
    state = StateVector(amplitudes=amplitudes)
    assert state.num_qubits == 1
    assert len(state.amplitudes) == 2

    # Test normalization check
    with pytest.raises(ValueError, match="not normalized"):
        StateVector(amplitudes=[1.0, 1.0])


@pytest.mark.unit
@pytest.mark.quantum
def test_state_vector_probabilities():
    """Test probability calculation from state vector."""
    amplitudes = [1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]
    state = StateVector(amplitudes=amplitudes)
    probs = state.probabilities()

    assert "|0⟩" in probs
    assert "|1⟩" in probs
    assert abs(probs["|0⟩"] - 0.5) < 1e-6
    assert abs(probs["|1⟩"] - 0.5) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_state_vector_measurement():
    """Test measurement with shots."""
    amplitudes = [1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]
    state = StateVector(amplitudes=amplitudes)

    result = state.measure(num_shots=1000, seed=42)

    assert "|0⟩" in result
    assert "|1⟩" in result
    total_shots = sum(result.values())
    assert total_shots == 1000
    # Check probabilities are reasonable
    assert 0.4 < result["|0⟩"] / 1000 < 0.6


@pytest.mark.unit
@pytest.mark.quantum
def test_state_vector_entropy():
    """Test Von Neumann entropy calculation."""
    # Maximally mixed state (high entropy)
    amplitudes = [1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]
    state = StateVector(amplitudes=amplitudes)
    entropy = state.entropy()
    assert entropy > 0.5  # High entropy for mixed state

    # Pure state (low entropy)
    pure_amplitudes = [1.0, 0.0]
    pure_state = StateVector(amplitudes=pure_amplitudes)
    pure_entropy = pure_state.entropy()
    assert pure_entropy < 0.01  # Near zero for pure state


@pytest.mark.unit
@pytest.mark.quantum
def test_state_vector_fidelity():
    """Test fidelity between two states."""
    state1 = StateVector(amplitudes=[1.0, 0.0])
    state2 = StateVector(amplitudes=[1.0, 0.0])
    state3 = StateVector(amplitudes=[0.0, 1.0])

    # Identical states have fidelity 1
    assert abs(state1.fidelity(state2) - 1.0) < 1e-6

    # Orthogonal states have fidelity 0
    assert abs(state1.fidelity(state3)) < 1e-6


@pytest.mark.unit
@pytest.mark.quantum
def test_quantum_state_factory_methods():
    """Test factory methods for common quantum states."""
    # Computational basis
    state = QuantumState.from_computational_basis("101")
    assert state.num_qubits == 3

    # Hadamard state (uniform superposition)
    hadamard = QuantumState.hadamard_state(2)
    assert hadamard.num_qubits == 2

    # Bell states
    bell_phi_plus = QuantumState.bell_state("phi_plus")
    assert bell_phi_plus.num_qubits == 2


@pytest.mark.unit
@pytest.mark.quantum
def test_ghz_state_creation():
    """Test GHZ state creation."""
    ghz = create_ghz_state(3)
    assert ghz.num_qubits == 3
    # GHZ state should have high entanglement


@pytest.mark.unit
@pytest.mark.quantum
def test_w_state_creation():
    """Test W state creation."""
    w = create_w_state(3)
    assert w.num_qubits == 3


# ============================================================================
# Quantum Provider Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_mock_provider_execution():
    """Test mock quantum provider circuit execution."""
    provider = MockQuantumProvider()
    assert provider.is_available

    result = await provider.execute_circuit(num_qubits=2, num_shots=100, seed=42)

    assert result.total_shots == 100
    assert len(result.counts) > 0
    assert sum(result.counts.values()) == 100
    assert result.execution_time_ms > 0


@pytest.mark.unit
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_mock_provider_optimization():
    """Test mock provider optimization."""
    provider = MockQuantumProvider()

    def objective(x):
        return float(np.sum(x**2))

    result = await provider.optimize(
        objective_function=objective,
        num_variables=3,
        method=OptimizationMethod.QAOA,
        max_iterations=50,
        seed=42,
    )

    assert result.iterations <= 50
    assert len(result.optimal_solution) == 3
    assert result.objective_value >= 0
    if result.convergence_history:
        assert len(result.convergence_history) > 0


@pytest.mark.unit
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_simulator_provider_execution():
    """Test simulator provider circuit execution."""
    provider = SimulatorQuantumProvider()
    assert provider.is_available

    result = await provider.execute_circuit(num_qubits=3, num_shots=500, seed=42)

    assert result.total_shots == 500
    assert len(result.counts) > 0
    assert result.execution_time_ms > 0


# ============================================================================
# Quantum Orchestrator Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initialization and backend listing."""
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()

    backends = orchestrator.list_available_backends()
    assert QuantumBackend.MOCK in backends
    assert QuantumBackend.SIMULATOR in backends


@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_orchestrator_circuit_execution():
    """Test orchestrator circuit execution with backend selection."""
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()

    result = await orchestrator.execute_quantum_circuit(
        backend=QuantumBackend.MOCK, num_qubits=2, num_shots=100, seed=42
    )

    assert result.total_shots == 100
    assert len(result.counts) > 0


@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_orchestrator_optimization():
    """Test orchestrator optimization."""
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()

    def objective(x):
        return float(np.sum((x - 0.5) ** 2))

    result = await orchestrator.run_optimization(
        backend=QuantumBackend.MOCK,
        objective_function=objective,
        num_variables=4,
        method=OptimizationMethod.VQE,
        max_iterations=30,
        seed=42,
    )

    assert len(result.optimal_solution) == 4
    assert result.iterations <= 30
    assert result.objective_value >= 0


# ============================================================================
# Scenario Engine Tests
# ============================================================================


@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_scenario_engine_supply_chain():
    """Test supply chain optimization scenario."""
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()
    engine = ScenarioEngine(orchestrator)

    request = ScenarioRequest(
        scenario_type=ScenarioType.SUPPLY_CHAIN,
        name="Test Supply Chain",
        description="Test supply chain optimization",
        backend=QuantumBackend.MOCK,
        optimization_method=OptimizationMethod.QAOA,
        parameters={"max_iterations": 20},
        seed=42,
    )

    result = await engine.execute_scenario(request)

    assert result.status == "completed"
    assert result.optimization_result is not None
    assert result.forecast_result is not None
    assert result.execution_time_seconds and result.execution_time_seconds > 0


@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_scenario_engine_energy_grid():
    """Test energy grid forecasting scenario."""
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()
    engine = ScenarioEngine(orchestrator)

    request = ScenarioRequest(
        scenario_type=ScenarioType.ENERGY_GRID,
        name="Test Energy Grid",
        description="Test energy grid forecasting",
        backend=QuantumBackend.MOCK,
        optimization_method=OptimizationMethod.VQE,
        parameters={"max_iterations": 20, "num_qubits": 3, "num_shots": 500},
        seed=42,
    )

    result = await engine.execute_scenario(request)

    assert result.status == "completed"
    assert result.optimization_result is not None
    assert result.measurement_result is not None
    assert result.forecast_result is not None


@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_scenario_engine_risk_analysis():
    """Test risk analysis scenario."""
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()
    engine = ScenarioEngine(orchestrator)

    request = ScenarioRequest(
        scenario_type=ScenarioType.RISK_ANALYSIS,
        name="Test Risk Analysis",
        description="Test risk analysis",
        backend=QuantumBackend.MOCK,
        parameters={"num_qubits": 4, "num_shots": 1000},
        seed=42,
    )

    result = await engine.execute_scenario(request)

    assert result.status == "completed"
    assert result.measurement_result is not None
    assert result.forecast_result is not None


@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_scenario_engine_optimization():
    """Test generic optimization scenario."""
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()
    engine = ScenarioEngine(orchestrator)

    request = ScenarioRequest(
        scenario_type=ScenarioType.OPTIMIZATION,
        name="Test Optimization",
        description="Test optimization",
        backend=QuantumBackend.MOCK,
        optimization_method=OptimizationMethod.QAOA,
        parameters={"num_variables": 5, "max_iterations": 30},
        seed=42,
    )

    result = await engine.execute_scenario(request)

    assert result.status == "completed"
    assert result.optimization_result is not None
    assert len(result.optimization_result.optimal_solution) == 5


# ============================================================================
# Scenario Cache Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_cache_set_and_get(tmp_path):
    """Test cache set and get operations."""
    cache = ScenarioCache(cache_dir=None, max_cache_size=10)

    # Create mock result
    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()
    engine = ScenarioEngine(orchestrator)

    request = ScenarioRequest(
        name="Test Cache",
        scenario_type=ScenarioType.OPTIMIZATION,
        backend=QuantumBackend.MOCK,
        parameters={"num_variables": 3, "max_iterations": 10},
        seed=42,
    )

    result = await engine.execute_scenario(request)

    # Cache result
    cache.set(result, ttl_hours=1)

    # Retrieve result
    cached_result = cache.get(result.simulation_id)
    assert cached_result is not None
    assert cached_result.simulation_id == result.simulation_id


@pytest.mark.unit
@pytest.mark.quantum
def test_cache_expiration():
    """Test cache expiration."""
    cache = ScenarioCache(cache_dir=None, max_cache_size=10)

    # Manually create expired entry
    from modules.quantum_simulator.scenario_cache import CacheEntry
    from modules.quantum_simulator.schemas import SimulationResult

    result = SimulationResult(
        simulation_id="test_expired",
        scenario_name="Test",
        scenario_type=ScenarioType.OPTIMIZATION,
        status="completed",
        backend_used=QuantumBackend.MOCK,
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        execution_time_seconds=1.0,
        parameters={},
        metrics={},
        error_message=None,
        tags=None,
    )

    # Create entry that expired 1 hour ago
    entry = CacheEntry(
        result=result,
        created_at=datetime.now(timezone.utc) - timedelta(hours=2),
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        access_count=0,
        last_accessed=datetime.now(timezone.utc) - timedelta(hours=2),
    )

    cache._cache[result.simulation_id] = entry

    # Should return None for expired entry
    cached_result = cache.get(result.simulation_id)
    assert cached_result is None


@pytest.mark.unit
@pytest.mark.quantum
@pytest.mark.asyncio
async def test_cache_list_scenarios():
    """Test listing cached scenarios with filtering."""
    cache = ScenarioCache(cache_dir=None, max_cache_size=100)

    orchestrator = QuantumOrchestrator()
    await orchestrator.initialize()
    engine = ScenarioEngine(orchestrator)

    # Create multiple scenarios
    for i in range(5):
        request = ScenarioRequest(
            scenario_type=ScenarioType.SUPPLY_CHAIN if i % 2 == 0 else ScenarioType.ENERGY_GRID,
            name=f"Test {i}",
            description=f"Test scenario {i}",
            backend=QuantumBackend.MOCK,
            parameters={"max_iterations": 10},
            seed=42,
        )
        result = await engine.execute_scenario(request)
        cache.set(result)

    # List all scenarios
    all_scenarios = cache.list_scenarios(limit=10)
    assert len(all_scenarios) == 5

    # Filter by type
    supply_chain = cache.list_scenarios(scenario_type="supply_chain", limit=10)
    assert len(supply_chain) == 3


@pytest.mark.unit
@pytest.mark.quantum
def test_cache_stats():
    """Test cache statistics."""
    cache = ScenarioCache(cache_dir=None, max_cache_size=100)

    stats = cache.get_cache_stats()
    assert stats["total_entries"] == 0
    assert stats["max_cache_size"] == 100
    assert stats["cache_utilization"] == 0.0


@pytest.mark.unit
@pytest.mark.quantum
def test_cache_clear():
    """Test cache clearing."""
    cache = ScenarioCache(cache_dir=None, max_cache_size=100)

    # Would add entries here, then clear
    count = cache.clear_all()
    assert count >= 0
    assert len(cache._cache) == 0


# ============================================================================
# API Endpoint Tests
# ============================================================================


@pytest.fixture
def test_client():
    """Create test client for API endpoints."""
    app = FastAPI()
    app.include_router(quantum_simulator_router)
    return TestClient(app)


@pytest.mark.api
@pytest.mark.quantum
def test_health_endpoint(test_client):
    """Test health check endpoint."""
    response = test_client.get("/simulate/health")
    assert response.status_code in [200, 503]


@pytest.mark.api
@pytest.mark.quantum
def test_list_backends_endpoint(test_client):
    """Test list backends endpoint."""
    response = test_client.get("/simulate/backends")
    assert response.status_code == 200
    data = response.json()
    assert "available_backends" in data
    assert isinstance(data["available_backends"], list)


@pytest.mark.api
@pytest.mark.quantum
def test_run_simulation_endpoint(test_client):
    """Test run simulation endpoint."""
    payload = _simulation_payload()

    response = test_client.post(
        "/simulate/scenario",
        json=payload,
        headers=_auth_header(),
    )
    assert response.status_code == 202
    data = response.json()
    assert "simulation_id" in data
    assert data["status"] == "completed"


@pytest.mark.api
@pytest.mark.quantum
def test_get_simulation_result_endpoint(test_client):
    """Test get simulation result endpoint."""
    # First create a simulation
    payload = _simulation_payload("Test for Retrieval")
    payload["parameters"] = {"num_variables": 2, "max_iterations": 5}

    create_response = test_client.post(
        "/simulate/scenario",
        json=payload,
        headers=_auth_header(),
    )
    simulation_id = create_response.json()["simulation_id"]

    # Retrieve it
    response = test_client.get(f"/simulate/results/{simulation_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["simulation_id"] == simulation_id


@pytest.mark.api
@pytest.mark.quantum
def test_list_scenarios_endpoint(test_client):
    """Test list scenarios endpoint."""
    response = test_client.get("/simulate/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.api
@pytest.mark.quantum
def test_cache_stats_endpoint(test_client):
    """Test cache stats endpoint."""
    response = test_client.get("/simulate/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_entries" in data
    assert "cache_utilization" in data


@pytest.mark.api
@pytest.mark.quantum
def test_forecast_endpoint_validation(test_client):
    """Test forecast endpoint with validation."""
    # Missing forecast_config should fail
    payload = {
        "scenario_type": "supply_chain",
        "name": "Invalid Forecast",
        "description": "Test invalid forecast",
        "backend": "mock",
    }

    response = test_client.post(
        "/simulate/forecast",
        json=payload,
        headers=_auth_header(),
    )
    assert response.status_code == 400


class TestQuantumSimulatorAPISecurity(unittest.TestCase):
    """Mutation routes require CSRF bearer auth before simulator state changes."""

    def setUp(self) -> None:
        app = FastAPI()
        app.include_router(quantum_simulator_router)
        self.client = TestClient(app)

    def test_mutation_routes_reject_missing_token(self) -> None:
        unauthorized_requests = [
            self.client.post("/simulate/scenario", json=_simulation_payload()),
            self.client.post("/simulate/forecast", json=_simulation_payload()),
            self.client.delete("/simulate/results/sim-missing"),
            self.client.post("/simulate/cache/clear"),
        ]

        for response in unauthorized_requests:
            self.assertIn(response.status_code, (401, 403))

    def test_cache_clear_accepts_valid_token(self) -> None:
        response = self.client.post(
            "/simulate/cache/clear",
            headers=_auth_header(),
        )

        self.assertEqual(response.status_code, 204)


# ============================================================================
# Markers and Summary
# ============================================================================

# Test markers:
# - unit: Fast unit tests (< 1 second)
# - integration: Integration tests (1-10 seconds)
# - api: API endpoint tests
# - quantum: Quantum simulator tests

# Run specific test groups:
# pytest tests/test_quantum_simulator.py -m unit
# pytest tests/test_quantum_simulator.py -m integration
# pytest tests/test_quantum_simulator.py -m api
# pytest tests/test_quantum_simulator.py -m quantum
