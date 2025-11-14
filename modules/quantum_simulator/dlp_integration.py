"""
Quantum Simulator DLP Integration

Integrates Quantum Simulator with Aurora's native DLP tracking system.

Anchor: T1-QSS-DLP
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from modules.quantum_simulator.schemas import ScenarioRequest, SimulationResult

try:
    from src.core.native_dlp_export import NativeDLPTracker

    DLP_AVAILABLE = True
except ImportError:
    DLP_AVAILABLE = False
    NativeDLPTracker = None


class QuantumSimulatorDLPIntegration:
    """
    Integration layer between Quantum Simulator and DLP tracking.

    Automatically creates DLP records for simulation operations.
    """

    def __init__(self, dlp_tracker: Optional[Any] = None):
        """
        Initialize DLP integration.

        Args:
            dlp_tracker: NativeDLPTracker instance (optional)
        """
        self.dlp_tracker = dlp_tracker
        self.enabled = DLP_AVAILABLE and dlp_tracker is not None

    def track_scenario_created(
        self,
        simulation_id: str,
        request: ScenarioRequest,
        context_tag: Optional[str] = None,
    ) -> Optional[str]:
        """
        Track scenario creation in DLP system.

        Args:
            simulation_id: Simulation identifier
            request: Original scenario request
            context_tag: Optional context tag (defaults to "quantum_simulator")

        Returns:
            DLP record ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            metadata = {
                "simulation_id": simulation_id,
                "scenario_type": request.scenario_type.value,
                "scenario_name": request.name,
                "backend": request.backend.value,
                "optimization_method": request.optimization_method.value,
                "num_shots": request.num_shots,
                "max_iterations": request.max_iterations,
                "timeout_seconds": request.timeout_seconds,
                "has_description": request.description is not None,
                "has_forecast_config": request.forecast_config is not None,
                "parameter_count": len(request.parameters),
                "tag_count": len(request.tags) if request.tags else 0,
            }

            return self.dlp_tracker.track_operation(
                operation_type="scenario_created",
                context_tag=context_tag or "quantum_simulator",
                metadata=metadata,
                symbolic_hash_validation=True,
            )
        except Exception as e:
            print(f"Warning: DLP tracking failed for scenario creation: {e}")
            return None

    def track_simulation_completed(
        self,
        result: SimulationResult,
        execution_time: float,
        context_tag: Optional[str] = None,
    ) -> Optional[str]:
        """
        Track simulation completion in DLP system.

        Args:
            result: Simulation result
            execution_time: Total execution time in seconds
            context_tag: Optional context tag (defaults to "quantum_simulator")

        Returns:
            DLP record ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            metadata = {
                "simulation_id": result.simulation_id,
                "status": result.status.value,
                "scenario_type": result.scenario_type.value,
                "backend": result.backend.value,
                "execution_time_seconds": execution_time,
                "has_quantum_state": result.quantum_state is not None,
                "has_measurement_result": result.measurement_result is not None,
                "has_optimization_result": result.optimization_result is not None,
                "has_forecast_result": result.forecast_result is not None,
                "metadata_keys": list(result.metadata.keys()) if result.metadata else [],
            }

            # Add optimization details if available
            if result.optimization_result:
                metadata.update(
                    {
                        "objective_value": result.optimization_result.objective_value,
                        "num_iterations": result.optimization_result.num_iterations,
                        "converged": result.optimization_result.converged,
                        "has_convergence_history": result.optimization_result.convergence_history is not None,
                    }
                )

            # Add forecast details if available
            if result.forecast_result:
                metadata.update(
                    {
                        "forecast_horizon": result.forecast_result.forecast_horizon,
                        "prediction_count": len(result.forecast_result.predictions),
                        "has_confidence_intervals": result.forecast_result.confidence_intervals is not None,
                    }
                )

            return self.dlp_tracker.track_operation(
                operation_type="simulation_completed",
                context_tag=context_tag or "quantum_simulator",
                metadata=metadata,
                symbolic_hash_validation=True,
            )
        except Exception as e:
            print(f"Warning: DLP tracking failed for simulation completion: {e}")
            return None

    def track_simulation_error(
        self,
        simulation_id: str,
        error_message: str,
        scenario_type: str,
        context_tag: Optional[str] = None,
    ) -> Optional[str]:
        """
        Track simulation error in DLP system.

        Args:
            simulation_id: Simulation identifier
            error_message: Error description
            scenario_type: Type of scenario that failed
            context_tag: Optional context tag (defaults to "quantum_simulator")

        Returns:
            DLP record ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            metadata = {
                "simulation_id": simulation_id,
                "scenario_type": scenario_type,
                "error_message": error_message[:500],  # Truncate for storage
                "status": "failed",
            }

            return self.dlp_tracker.track_operation(
                operation_type="simulation_error",
                context_tag=context_tag or "quantum_simulator",
                metadata=metadata,
                symbolic_hash_validation=True,
            )
        except Exception as e:
            print(f"Warning: DLP tracking failed for simulation error: {e}")
            return None

    def track_cache_hit(
        self,
        simulation_id: str,
        scenario_type: str,
        age_seconds: float,
        context_tag: Optional[str] = None,
    ) -> Optional[str]:
        """
        Track cache hit in DLP system.

        Args:
            simulation_id: Simulation identifier
            scenario_type: Type of cached scenario
            age_seconds: Age of cached result in seconds
            context_tag: Optional context tag (defaults to "quantum_simulator")

        Returns:
            DLP record ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            metadata = {
                "simulation_id": simulation_id,
                "scenario_type": scenario_type,
                "age_seconds": age_seconds,
                "cache_reuse": True,
            }

            return self.dlp_tracker.track_operation(
                operation_type="cache_hit",
                context_tag=context_tag or "quantum_simulator",
                metadata=metadata,
                symbolic_hash_validation=True,
            )
        except Exception as e:
            print(f"Warning: DLP tracking failed for cache hit: {e}")
            return None

    def track_cache_cleared(
        self,
        cleared_count: int,
        context_tag: Optional[str] = None,
    ) -> Optional[str]:
        """
        Track cache clearing in DLP system.

        Args:
            cleared_count: Number of entries cleared
            context_tag: Optional context tag (defaults to "quantum_simulator")

        Returns:
            DLP record ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            metadata = {
                "cleared_count": cleared_count,
                "operation": "cache_clear",
            }

            return self.dlp_tracker.track_operation(
                operation_type="cache_cleared",
                context_tag=context_tag or "quantum_simulator",
                metadata=metadata,
                symbolic_hash_validation=True,
            )
        except Exception as e:
            print(f"Warning: DLP tracking failed for cache clear: {e}")
            return None

    def create_export_manifest(
        self,
        simulation_ids: list[str],
        include_metadata: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Create DLP export manifest for simulations.

        Args:
            simulation_ids: List of simulation IDs to include
            include_metadata: Include detailed metadata in manifest

        Returns:
            Export manifest dictionary if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            manifest = {
                "export_type": "quantum_simulator",
                "simulation_count": len(simulation_ids),
                "simulation_ids": simulation_ids,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "include_metadata": include_metadata,
            }

            if hasattr(self.dlp_tracker, "create_export_manifest"):
                return self.dlp_tracker.create_export_manifest(
                    context_tag="quantum_simulator",
                    metadata=manifest,
                )

            return manifest
        except Exception as e:
            print(f"Warning: DLP manifest creation failed: {e}")
            return None


# Global DLP integration instance
_dlp_integration: Optional[QuantumSimulatorDLPIntegration] = None


def get_dlp_integration() -> QuantumSimulatorDLPIntegration:
    """
    Get the global DLP integration instance.

    Returns:
        QuantumSimulatorDLPIntegration instance
    """
    global _dlp_integration
    if _dlp_integration is None:
        if DLP_AVAILABLE:
            try:
                tracker = NativeDLPTracker()
                _dlp_integration = QuantumSimulatorDLPIntegration(tracker)
            except Exception:
                _dlp_integration = QuantumSimulatorDLPIntegration(None)
        else:
            _dlp_integration = QuantumSimulatorDLPIntegration(None)
    return _dlp_integration


def set_dlp_integration(integration: QuantumSimulatorDLPIntegration) -> None:
    """
    Set the global DLP integration instance.

    Args:
        integration: DLP integration to use
    """
    global _dlp_integration
    _dlp_integration = integration
