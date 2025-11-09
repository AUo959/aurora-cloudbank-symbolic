"""Quantum simulation models."""

from typing import Any, Literal, Optional

from pydantic import Field

from aurora_sdk.models.base import AuroraBaseModel

# Scenario types
ScenarioType = Literal[
    "supply_chain_optimization",
    "energy_grid_balancing",
    "risk_assessment",
    "portfolio_optimization",
    "network_routing",
    "resource_allocation",
    "scheduling",
]

# Scenario status
ScenarioStatus = Literal["pending", "running", "completed", "failed"]

# Circuit types
CircuitType = Literal["bell", "ghz", "custom"]


class QuantumScenarioResult(AuroraBaseModel):
    """Result from quantum scenario execution.

    Attributes:
        scenario_id: Unique scenario identifier
        scenario_type: Type of scenario executed
        status: Execution status
        optimal_state: Optimal quantum state found
        metrics: Performance metrics
        execution_time: Execution time in seconds
        circuit_depth: Quantum circuit depth
        qubit_count: Number of qubits used
    """

    scenario_id: str = Field(..., description="Unique scenario identifier")
    scenario_type: str = Field(..., description="Type of scenario")
    status: ScenarioStatus = Field(..., description="Execution status")
    optimal_state: list[int] = Field(..., description="Optimal quantum state")
    metrics: dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    execution_time: float = Field(..., description="Execution time in seconds")
    circuit_depth: Optional[int] = Field(None, description="Quantum circuit depth")
    qubit_count: Optional[int] = Field(None, description="Number of qubits")


class QuantumCircuit(AuroraBaseModel):
    """Quantum circuit representation.

    Attributes:
        circuit_id: Unique circuit identifier
        circuit_type: Type of circuit
        num_qubits: Number of qubits
        depth: Circuit depth
        gates: Gate operations
        measurements: Measurement results
        statevector: Final statevector (if available)
    """

    circuit_id: str = Field(..., description="Unique circuit identifier")
    circuit_type: CircuitType = Field(..., description="Type of circuit")
    num_qubits: int = Field(..., description="Number of qubits")
    depth: int = Field(..., description="Circuit depth")
    gates: list[dict[str, Any]] = Field(default_factory=list, description="Gate operations")
    measurements: Optional[dict[str, int]] = Field(None, description="Measurement results")
    statevector: Optional[list[complex]] = Field(None, description="Final statevector")


class QuantumBackend(AuroraBaseModel):
    """Quantum backend configuration.

    Attributes:
        backend_id: Backend identifier
        backend_type: Type of backend (simulator, hardware, cloud)
        available: Whether backend is available
        queue_length: Number of jobs in queue
        max_qubits: Maximum number of qubits supported
    """

    backend_id: str = Field(..., description="Backend identifier")
    backend_type: Literal["simulator", "hardware", "cloud"] = Field(
        ..., description="Backend type"
    )
    available: bool = Field(..., description="Whether backend is available")
    queue_length: int = Field(0, description="Jobs in queue")
    max_qubits: int = Field(..., description="Maximum qubits supported")
