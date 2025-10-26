"""
Quantum State Synthesizer

Hybrid quantum-classical scenario simulator and forecasting engine.

Anchor: T1-QSS-001, T1-QSS-002
"""

from .orchestrator import (
    MockQuantumProvider,
    QuantumOrchestrator,
    QuantumProvider,
    SimulatorQuantumProvider,
    get_orchestrator,
    initialize_orchestrator,
)
from .quantum_state import QuantumState, StateVector, create_ghz_state, create_w_state
from .scenario_cache import ScenarioCache, get_cache, initialize_cache
from .scenario_engine import ScenarioEngine
from .schemas import (
    ForecastConfig,
    ForecastResult,
    MeasurementResult,
    OptimizationMethod,
    OptimizationResult,
    QuantumBackend,
    ScenarioListItem,
    ScenarioRequest,
    ScenarioType,
    SimulationResult,
    SimulationStatus,
    StateVector as StateVectorModel,
)

__version__ = "0.1.0"
__anchor__ = "T1-QSS-001, T1-QSS-002"

__all__ = [
    # Orchestration
    "QuantumOrchestrator",
    "QuantumProvider",
    "MockQuantumProvider",
    "SimulatorQuantumProvider",
    "get_orchestrator",
    "initialize_orchestrator",
    # Quantum State
    "QuantumState",
    "StateVector",
    "create_ghz_state",
    "create_w_state",
    # Scenario Engine
    "ScenarioEngine",
    # Caching
    "ScenarioCache",
    "get_cache",
    "initialize_cache",
    # Schemas
    "ScenarioType",
    "QuantumBackend",
    "OptimizationMethod",
    "ForecastConfig",
    "ScenarioRequest",
    "StateVectorModel",
    "MeasurementResult",
    "OptimizationResult",
    "ForecastResult",
    "SimulationResult",
    "SimulationStatus",
    "ScenarioListItem",
]
