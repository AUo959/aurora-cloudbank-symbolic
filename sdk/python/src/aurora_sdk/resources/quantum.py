"""Quantum simulation operations."""

from typing import Any, Optional

from aurora_sdk.models.quantum import (
    CircuitType,
    QuantumBackend,
    QuantumCircuit,
    QuantumScenarioResult,
    ScenarioType,
)
from aurora_sdk.transport.http import HTTPTransport


class QuantumResource:
    """Quantum simulation operations.

    This resource provides access to quantum scenario simulations,
    circuit creation, and backend management.

    Example:
        >>> quantum = client.quantum
        >>> result = await quantum.run_scenario("supply_chain", num_suppliers=5)
        >>> print(result.optimal_state)
    """

    def __init__(self, transport: HTTPTransport) -> None:
        """Initialize quantum resource.

        Args:
            transport: HTTP transport layer
        """
        self._transport = transport

    async def run_scenario(
        self,
        scenario: ScenarioType,
        **params: Any
    ) -> QuantumScenarioResult:
        """Run a quantum scenario simulation.

        Args:
            scenario: Scenario type to execute
            **params: Scenario-specific parameters

        Returns:
            Scenario execution result

        Raises:
            ValidationError: Invalid parameters
            ResourceNotFoundError: Invalid scenario type

        Example:
            >>> result = await client.quantum.run_scenario(
            ...     "supply_chain_optimization",
            ...     num_suppliers=5,
            ...     demand_variance=0.2,
            ...     cost_weights=[0.3, 0.4, 0.2, 0.5, 0.3]
            ... )
            >>> print(f"Optimal state: {result.optimal_state}")
            >>> print(f"Cost reduction: {result.metrics['cost_reduction']:.1f}%")
        """
        response = await self._transport.post(
            f"/quantum/scenario/{scenario}",
            json=params
        )
        return QuantumScenarioResult.from_dict(response)

    async def create_circuit(
        self,
        circuit_type: CircuitType,
        num_qubits: Optional[int] = None,
        gates: Optional[list[dict[str, Any]]] = None,
        **params: Any
    ) -> QuantumCircuit:
        """Create and simulate a quantum circuit.

        Args:
            circuit_type: Type of circuit (bell, ghz, custom)
            num_qubits: Number of qubits (for custom circuits)
            gates: Gate operations (for custom circuits)
            **params: Additional parameters

        Returns:
            Circuit execution result

        Example:
            >>> circuit = await client.quantum.create_circuit(
            ...     "bell",
            ...     num_qubits=2
            ... )
            >>> print(f"Circuit depth: {circuit.depth}")
        """
        payload: dict[str, Any] = {
            "circuit_type": circuit_type,
            **params
        }

        if num_qubits is not None:
            payload["num_qubits"] = num_qubits

        if gates is not None:
            payload["gates"] = gates

        response = await self._transport.post("/quantum/circuit", json=payload)
        return QuantumCircuit.from_dict(response)

    async def list_scenarios(self) -> list[str]:
        """List available quantum scenarios.

        Returns:
            List of scenario names

        Example:
            >>> scenarios = await client.quantum.list_scenarios()
            >>> for scenario in scenarios:
            ...     print(scenario)
        """
        response = await self._transport.get("/quantum/scenarios")
        return response.get("scenarios", [])

    async def list_backends(self) -> list[QuantumBackend]:
        """List available quantum backends.

        Returns:
            List of backend configurations

        Example:
            >>> backends = await client.quantum.list_backends()
            >>> for backend in backends:
            ...     print(f"{backend.backend_id}: {backend.max_qubits} qubits")
        """
        response = await self._transport.get("/quantum/backends")
        backends_data = response.get("backends", [])
        return [QuantumBackend.from_dict(b) for b in backends_data]
