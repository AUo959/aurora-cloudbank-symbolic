"""
Quantum Simulator Schemas

Pydantic models for scenario requests, simulation results, and forecast configurations.

Anchor: T1-QSS-001
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ScenarioType(str, Enum):
    """Types of simulation scenarios."""

    SUPPLY_CHAIN = "supply_chain"  # Supply chain optimization
    ENERGY_GRID = "energy_grid"  # Energy grid forecasting
    RISK_ANALYSIS = "risk_analysis"  # Risk/uncertainty analysis
    OPTIMIZATION = "optimization"  # General optimization
    MONTE_CARLO = "monte_carlo"  # Monte Carlo simulation
    QUANTUM_ANNEALING = "quantum_annealing"  # Quantum annealing
    VARIATIONAL = "variational"  # Variational quantum algorithms


class QuantumBackend(str, Enum):
    """Available quantum backends."""

    MOCK = "mock"  # Mock quantum provider (for testing)
    SIMULATOR = "simulator"  # Classical quantum simulator
    IBMQ = "ibmq"  # IBM Quantum (if available)
    AZURE_QUANTUM = "azure_quantum"  # Azure Quantum (if available)
    AWS_BRAKET = "aws_braket"  # AWS Braket (if available)


class OptimizationMethod(str, Enum):
    """Optimization methods for scenarios."""

    QAOA = "qaoa"  # Quantum Approximate Optimization Algorithm
    VQE = "vqe"  # Variational Quantum Eigensolver
    ANNEALING = "annealing"  # Quantum Annealing
    CLASSICAL = "classical"  # Classical optimization fallback


class ForecastConfig(BaseModel):
    """Configuration for forecasting scenarios."""

    time_steps: int = Field(..., ge=1, le=1000, description="Number of time steps to forecast")
    variables: List[str] = Field(..., min_length=1, max_length=50, description="Variables to forecast")
    initial_conditions: Dict[str, float] = Field(
        default_factory=dict, description="Initial conditions for variables"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default=None, description="Constraints for optimization"
    )
    uncertainty_level: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Uncertainty level (0.0-1.0)"
    )

    @field_validator("variables")
    @classmethod
    def validate_variables(cls, v: List[str]) -> List[str]:
        """Ensure variables are unique and non-empty."""
        if not v:
            raise ValueError("At least one variable required")
        return list(set(var.strip() for var in v if var.strip()))

    class Config:
        json_schema_extra = {
            "example": {
                "time_steps": 24,
                "variables": ["demand", "supply", "cost"],
                "initial_conditions": {"demand": 100.0, "supply": 120.0, "cost": 50.0},
                "constraints": {"max_cost": 1000.0},
                "uncertainty_level": 0.15,
            }
        }


class ScenarioRequest(BaseModel):
    """Request to simulate a scenario."""

    scenario_type: ScenarioType = Field(..., description="Type of scenario to simulate")
    name: str = Field(..., min_length=1, max_length=256, description="Scenario name")
    description: Optional[str] = Field(None, max_length=2000, description="Scenario description")
    backend: QuantumBackend = Field(
        default=QuantumBackend.MOCK, description="Quantum backend to use"
    )
    optimization_method: OptimizationMethod = Field(
        default=OptimizationMethod.CLASSICAL, description="Optimization method"
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Scenario parameters")
    forecast_config: Optional[ForecastConfig] = Field(
        None, description="Forecast configuration (if applicable)"
    )
    num_shots: int = Field(default=1000, ge=1, le=100000, description="Number of quantum shots")
    seed: Optional[int] = Field(None, ge=0, description="Random seed for reproducibility")
    max_iterations: int = Field(default=100, ge=1, le=10000, description="Max optimization iterations")
    timeout_seconds: int = Field(default=300, ge=1, le=3600, description="Timeout in seconds")
    tags: Optional[List[str]] = Field(default=None, max_items=20, description="Classification tags")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Ensure tags are unique and trimmed."""
        if v is None:
            return None
        return list(set(tag.strip() for tag in v if tag.strip()))

    class Config:
        json_schema_extra = {
            "example": {
                "scenario_type": "supply_chain",
                "name": "Q1 Supply Chain Optimization",
                "description": "Optimize inventory levels for Q1 demand forecast",
                "backend": "mock",
                "optimization_method": "qaoa",
                "parameters": {"num_warehouses": 5, "num_products": 10},
                "num_shots": 5000,
                "seed": 42,
                "tags": ["supply-chain", "q1-2025"],
            }
        }


class StateVector(BaseModel):
    """Quantum state vector representation."""

    model_config = {
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "example": {
                "amplitudes": [0.707 + 0j, 0.707 + 0j],
                "num_qubits": 1,
                "basis_labels": ["|0⟩", "|1⟩"],
            }
        }
    }

    amplitudes: List[complex] = Field(..., description="Complex amplitudes")
    num_qubits: int = Field(..., ge=1, le=50, description="Number of qubits")
    basis_labels: Optional[List[str]] = Field(None, description="Basis state labels")

    @field_validator("amplitudes")
    @classmethod
    def validate_amplitudes(cls, v: List[complex]) -> List[complex]:
        """Validate state vector normalization."""
        if not v:
            raise ValueError("Amplitudes cannot be empty")
        # Check normalization (sum of squared magnitudes should be ~1)
        norm_sq = sum(abs(amp) ** 2 for amp in v)
        if not (0.99 <= norm_sq <= 1.01):  # Allow small numerical errors
            raise ValueError(f"State vector not normalized: norm² = {norm_sq}")
        return v


class MeasurementResult(BaseModel):
    """Result from quantum measurement."""

    counts: Dict[str, int] = Field(..., description="Measurement counts per basis state")
    probabilities: Dict[str, float] = Field(..., description="Measurement probabilities")
    total_shots: int = Field(..., ge=1, description="Total number of shots")
    execution_time_ms: float = Field(..., ge=0, description="Execution time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "counts": {"00": 487, "01": 23, "10": 31, "11": 459},
                "probabilities": {"00": 0.487, "01": 0.023, "10": 0.031, "11": 0.459},
                "total_shots": 1000,
                "execution_time_ms": 125.4,
            }
        }


class OptimizationResult(BaseModel):
    """Result from optimization procedure."""

    optimal_solution: Dict[str, Any] = Field(..., description="Optimal solution found")
    objective_value: float = Field(..., description="Objective function value at optimum")
    iterations: int = Field(..., ge=0, description="Number of iterations performed")
    converged: bool = Field(..., description="Whether optimization converged")
    convergence_history: Optional[List[float]] = Field(
        None, description="Objective value history"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "optimal_solution": {"x1": 5.0, "x2": 3.0, "x3": 2.0},
                "objective_value": 42.5,
                "iterations": 87,
                "converged": True,
                "convergence_history": [100.0, 75.3, 52.1, 45.8, 42.5],
            }
        }


class ForecastResult(BaseModel):
    """Forecasting result with time series predictions."""

    forecast_values: Dict[str, List[float]] = Field(
        ..., description="Forecasted values per variable"
    )
    confidence_intervals: Optional[Dict[str, List[tuple]]] = Field(
        None, description="Confidence intervals (lower, upper) per variable"
    )
    time_labels: List[str] = Field(..., description="Time step labels")
    forecast_accuracy: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Accuracy score (if validation data available)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "forecast_values": {
                    "demand": [100.0, 105.2, 103.8, 108.5],
                    "supply": [120.0, 118.3, 122.1, 119.7],
                },
                "confidence_intervals": {
                    "demand": [(95.0, 105.0), (100.2, 110.2), (98.8, 108.8), (103.5, 113.5)]
                },
                "time_labels": ["T0", "T1", "T2", "T3"],
                "forecast_accuracy": 0.92,
            }
        }


class SimulationResult(BaseModel):
    """Complete simulation result."""

    simulation_id: str = Field(..., description="Unique simulation identifier")
    scenario_name: str = Field(..., description="Scenario name")
    scenario_type: ScenarioType = Field(..., description="Scenario type")
    status: str = Field(..., pattern="^(running|completed|failed|timeout)$", description="Status")
    backend_used: QuantumBackend = Field(..., description="Quantum backend used")
    start_time: datetime = Field(..., description="Simulation start time")
    end_time: Optional[datetime] = Field(None, description="Simulation end time")
    execution_time_seconds: Optional[float] = Field(
        None, ge=0, description="Total execution time"
    )

    # Results (depending on scenario type)
    measurement_result: Optional[MeasurementResult] = Field(None, description="Measurement results")
    optimization_result: Optional[OptimizationResult] = Field(
        None, description="Optimization results"
    )
    forecast_result: Optional[ForecastResult] = Field(None, description="Forecast results")

    # Metadata
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Scenario parameters")
    metrics: Dict[str, float] = Field(
        default_factory=dict, description="Performance metrics (fidelity, etc.)"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    tags: Optional[List[str]] = Field(None, description="Classification tags")

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "sim_20250126_120000_abc123",
                "scenario_name": "Q1 Supply Chain Optimization",
                "scenario_type": "supply_chain",
                "status": "completed",
                "backend_used": "mock",
                "start_time": "2025-01-26T12:00:00Z",
                "end_time": "2025-01-26T12:02:15Z",
                "execution_time_seconds": 135.4,
                "optimization_result": {
                    "optimal_solution": {"inventory_w1": 100, "inventory_w2": 150},
                    "objective_value": 45000.0,
                    "iterations": 75,
                    "converged": True,
                },
                "metrics": {"solution_quality": 0.95, "resource_usage": 0.68},
                "tags": ["supply-chain", "q1-2025"],
            }
        }


class SimulationStatus(BaseModel):
    """Status check for running simulation."""

    simulation_id: str = Field(..., description="Simulation identifier")
    status: str = Field(..., description="Current status")
    progress: float = Field(..., ge=0.0, le=1.0, description="Progress (0.0-1.0)")
    elapsed_time_seconds: float = Field(..., ge=0, description="Time elapsed")
    estimated_time_remaining: Optional[float] = Field(
        None, ge=0, description="Estimated time remaining (seconds)"
    )
    message: Optional[str] = Field(None, description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "sim_20250126_120000_abc123",
                "status": "running",
                "progress": 0.67,
                "elapsed_time_seconds": 45.2,
                "estimated_time_remaining": 22.1,
                "message": "Iteration 67 of 100",
            }
        }


class ScenarioListItem(BaseModel):
    """Summary item for scenario list."""

    simulation_id: str
    scenario_name: str
    scenario_type: ScenarioType
    status: str
    start_time: datetime
    execution_time_seconds: Optional[float] = None
    tags: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "simulation_id": "sim_20250126_120000_abc123",
                "scenario_name": "Q1 Supply Chain",
                "scenario_type": "supply_chain",
                "status": "completed",
                "start_time": "2025-01-26T12:00:00Z",
                "execution_time_seconds": 135.4,
                "tags": ["supply-chain"],
            }
        }
