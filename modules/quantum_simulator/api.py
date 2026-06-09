"""
Quantum Simulator API

FastAPI router for quantum-classical hybrid simulations.

Anchor: T1-QSS-003
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from src.middleware.fastapi_security import require_csrf_token
from src.monitoring.ethics_gate import EthicsViolationError, check_ethics

from .orchestrator import get_orchestrator
from .scenario_cache import get_cache
from .scenario_engine import ScenarioEngine
from .schemas import ScenarioListItem, ScenarioRequest, ScenarioType, SimulationResult, SimulationStatus

logger = logging.getLogger(__name__)

# Action Guard: fire-and-forget ethics/compliance evaluation
try:
    from src.monitoring.action_guard import evaluate_response as _evaluate_response
    _ACTION_GUARD_AVAILABLE = True
except Exception as _ag_exc:  # pragma: no cover - graceful degradation
    logger.warning("ActionGuard not available in quantum_simulator.api: %s", _ag_exc)
    _ACTION_GUARD_AVAILABLE = False

    def _evaluate_response(*_args, **_kwargs) -> None:  # type: ignore[misc]
        """No-op fallback when action_guard cannot be imported."""

# Create router
router = APIRouter(prefix="/simulate", tags=["quantum-simulator"])
MUTATION_DEPENDENCIES = [Depends(require_csrf_token)]

# WebSocket connections for progress tracking
active_connections: Dict[str, List[WebSocket]] = {}
active_simulations: Dict[str, SimulationStatus] = {}


def _completed_status_from_result(
    simulation_id: str,
    result: SimulationResult,
) -> SimulationStatus:
    return SimulationStatus(
        simulation_id=simulation_id,
        status=result.status,
        progress=1.0 if result.status == "completed" else 0.0,
        elapsed_time_seconds=result.execution_time_seconds or 0.0,
        estimated_time_remaining=None,
        message=f"Simulation {result.status}",
    )


def _not_found_status(simulation_id: str) -> SimulationStatus:
    return SimulationStatus(
        simulation_id=simulation_id,
        status="not_found",
        progress=0.0,
        elapsed_time_seconds=0.0,
        estimated_time_remaining=None,
        message=f"Simulation {simulation_id} not found or not active",
    )


@router.post(
    "/scenario",
    status_code=202,
    dependencies=MUTATION_DEPENDENCIES,
)
async def run_simulation(request: ScenarioRequest) -> SimulationResult:
    """
    Run quantum-classical hybrid simulation scenario.

    Executes simulation asynchronously and returns result. For long-running
    simulations, use the progress WebSocket endpoint to track status.

    Args:
        request: Scenario configuration and parameters

    Returns:
        SimulationResult with measurement, optimization, and/or forecast results

    Example:
        ```json
        {
            "name": "Q1 Supply Chain Optimization",
            "scenario_type": "supply_chain",
            "backend": "mock",
            "optimization_method": "qaoa",
            "parameters": {"max_iterations": 100},
            "forecast_config": {
                "time_steps": 30,
                "variables": ["inventory", "demand", "cost"]
            },
            "seed": 42,
            "tags": ["supply-chain", "q1-2025"]
        }
        ```
    """
    # Ethics gate: block scenarios that fail the ethics check
    try:
        check_ethics(
            "quantum_simulate",
            {"scenario_type": str(request.scenario_type), **dict(request.parameters or {})},
            context_tag=request.tags[0] if request.tags else "",
        )
    except EthicsViolationError as exc:
        raise HTTPException(
            status_code=422,
            detail={"error": "ethics_violation", "message": str(exc), "violations": exc.violations},
        )

    try:
        # Get orchestrator and cache
        orchestrator = await get_orchestrator()
        cache = get_cache()

        # Create scenario engine
        engine = ScenarioEngine(orchestrator, status_store=active_simulations)

        # Execute scenario
        result = await engine.execute_scenario(request)

        # Cache result
        cache.set(result, ttl_hours=24)
        active_simulations.pop(result.simulation_id, None)

        # Ethics/compliance evaluation — fire-and-forget, never blocks response
        _evaluate_response(
            "quantum_simulate",
            result.model_dump(mode="json") if hasattr(result, "model_dump") else {},
            metadata={
                "endpoint": "/simulate/scenario",
                "scenario_type": request.scenario_type.value if hasattr(request.scenario_type, "value") else str(request.scenario_type),
                "simulation_id": result.simulation_id,
            },
            context_tag=f"quantum_simulate_{result.simulation_id}",
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/results/{simulation_id}", response_model=SimulationResult)
async def get_simulation_result(simulation_id: str) -> SimulationResult:
    """
    Retrieve simulation result by ID.

    Checks cache first, returns cached result if available and not expired.

    Args:
        simulation_id: Unique simulation identifier

    Returns:
        SimulationResult if found

    Raises:
        HTTPException: 404 if simulation not found or expired
    """
    cache = get_cache()
    result = cache.get(simulation_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation {simulation_id} not found or expired"
        )

    return result


@router.get("/scenarios", response_model=List[ScenarioListItem])
async def list_scenarios(
    scenario_type: Optional[ScenarioType] = Query(None, description="Filter by scenario type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
) -> List[ScenarioListItem]:
    """
    List cached simulation scenarios with optional filtering.

    Args:
        scenario_type: Filter by scenario type (supply_chain, energy_grid, etc.)
        status: Filter by status (completed, running, failed)
        limit: Maximum number of results (1-1000)

    Returns:
        List of scenario summaries, sorted by start time (most recent first)

    Example:
        GET /simulate/scenarios?scenario_type=supply_chain&status=completed&limit=50
    """
    cache = get_cache()

    # Convert scenario_type to string if provided
    type_filter = scenario_type.value if scenario_type else None

    scenarios = cache.list_scenarios(
        scenario_type=type_filter,
        status=status,
        limit=limit
    )

    return scenarios


@router.get("/status/{simulation_id}", response_model=SimulationStatus)
async def get_simulation_status(simulation_id: str) -> SimulationStatus:
    """
    Get current status of running simulation.

    Args:
        simulation_id: Simulation identifier

    Returns:
        SimulationStatus with progress and estimated time remaining

    Raises:
        HTTPException: 404 if simulation not found
    """
    # Check if result is cached
    cache = get_cache()
    result = cache.get(simulation_id)

    if result:
        # Return completed status
        return _completed_status_from_result(simulation_id, result)

    status = active_simulations.get(simulation_id)
    if status:
        return status

    raise HTTPException(
        status_code=404,
        detail=f"Simulation {simulation_id} not found"
    )


@router.delete(
    "/results/{simulation_id}",
    status_code=204,
    dependencies=MUTATION_DEPENDENCIES,
)
async def delete_simulation_result(simulation_id: str) -> None:
    """
    Delete cached simulation result.

    Args:
        simulation_id: Simulation identifier

    Raises:
        HTTPException: 404 if simulation not found
    """
    cache = get_cache()
    deleted = cache.delete(simulation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Simulation {simulation_id} not found"
        )


@router.post(
    "/forecast",
    status_code=202,
    dependencies=MUTATION_DEPENDENCIES,
)
async def run_forecast(request: ScenarioRequest) -> SimulationResult:
    """
    Run quantum-enhanced forecasting simulation.

    Specialized endpoint for supply chain and energy grid forecasting scenarios.
    Validates that forecast_config is provided.

    Args:
        request: Scenario configuration with forecast parameters

    Returns:
        SimulationResult with forecast time series

    Raises:
        HTTPException: 400 if forecast_config is missing
    """
    # Validate forecast config
    if not request.forecast_config:
        raise HTTPException(
            status_code=400,
            detail="forecast_config is required for forecasting simulations"
        )

    # Validate scenario type
    if request.scenario_type not in [
        ScenarioType.SUPPLY_CHAIN,
        ScenarioType.ENERGY_GRID,
        ScenarioType.RISK_ANALYSIS
    ]:
        raise HTTPException(
            status_code=400,
            detail=f"Scenario type {request.scenario_type.value} does not support forecasting"
        )

    # Run simulation using main endpoint
    return await run_simulation(request)


@router.get("/cache/stats")
async def get_cache_stats() -> Dict:
    """
    Get cache statistics and metrics.

    Returns:
        Dict with cache performance metrics:
        - total_entries: Total cached simulations
        - active_entries: Non-expired entries
        - expired_entries: Expired entries pending cleanup
        - cache_utilization: Percentage of cache capacity used
        - symbolic_nodes: Number of scenario genealogy relationships

    Example Response:
        ```json
        {
            "total_entries": 156,
            "active_entries": 142,
            "expired_entries": 14,
            "total_accesses": 1847,
            "avg_access_count": 13.0,
            "cache_utilization": 0.156,
            "symbolic_nodes": 23
        }
        ```
    """
    cache = get_cache()
    return cache.get_cache_stats()


@router.post(
    "/cache/clear",
    status_code=204,
    dependencies=MUTATION_DEPENDENCIES,
)
async def clear_cache(
    expired_only: bool = Query(False, description="Clear only expired entries")
) -> None:
    """
    Clear simulation cache.

    Args:
        expired_only: If True, only remove expired entries. If False, clear all.

    Returns:
        204 No Content on success
    """
    cache = get_cache()

    if expired_only:
        cache.clear_expired()
    else:
        cache.clear_all()


@router.get("/genealogy/{simulation_id}")
async def get_scenario_genealogy(simulation_id: str) -> Dict[str, Any]:
    """
    Get scenario genealogy (parent chain).

    Returns the chain of parent simulations that led to this scenario,
    useful for tracking scenario evolution and parameter optimization.

    Args:
        simulation_id: Simulation identifier

    Returns:
        Dict with genealogy information:
        - simulation_id: Current simulation ID
        - parents: List of parent simulation IDs (oldest first)

    Example Response:
        ```json
        {
            "simulation_id": "sim_20251026_120000_abc123",
            "parents": ["sim_20251025_100000_xyz789", "sim_20251024_140000_def456"]
        }
        ```
    """
    cache = get_cache()
    parents = cache.get_scenario_genealogy(simulation_id)

    return {
        "simulation_id": simulation_id,
        "parents": parents
    }


@router.websocket("/progress/{simulation_id}")
async def simulation_progress_websocket(websocket: WebSocket, simulation_id: str):
    """
    WebSocket endpoint for real-time simulation progress tracking.

    Establishes WebSocket connection and sends periodic status updates
    for the specified simulation.

    Args:
        websocket: WebSocket connection
        simulation_id: Simulation identifier to track

    Message Format:
        ```json
        {
            "simulation_id": "sim_20251026_120000_abc123",
            "status": "running",
            "progress": 0.67,
            "elapsed_time_seconds": 45.2,
            "estimated_time_remaining": 22.1,
            "message": "Iteration 67 of 100"
        }
        ```

    Example Usage (JavaScript):
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/simulate/progress/sim_123');
        ws.onmessage = (event) => {
            const status = JSON.parse(event.data);
            console.log(`Progress: ${status.progress * 100}%`);
        };
        ```
    """
    await websocket.accept()

    # Register connection
    if simulation_id not in active_connections:
        active_connections[simulation_id] = []
    active_connections[simulation_id].append(websocket)

    try:
        cache = get_cache()

        # Send updates every second
        while True:
            # Check if simulation is completed (in cache)
            result = cache.get(simulation_id)
            if result:
                await websocket.send_json(
                    _completed_status_from_result(simulation_id, result).model_dump(mode="json")
                )
                break

            status = active_simulations.get(simulation_id)
            if not status:
                await websocket.send_json(_not_found_status(simulation_id).model_dump(mode="json"))
                break

            await websocket.send_json(status.model_dump(mode="json"))
            if status.status in {"completed", "failed", "timeout"}:
                break

            await asyncio.sleep(1.0)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "error": str(e),
            "simulation_id": simulation_id
        })
    finally:
        # Cleanup connection
        if simulation_id in active_connections:
            if websocket in active_connections[simulation_id]:
                active_connections[simulation_id].remove(websocket)
            if not active_connections[simulation_id]:
                del active_connections[simulation_id]


@router.get("/backends")
async def list_available_backends() -> Dict[str, Any]:
    """
    List available quantum backends.

    Returns:
        Dict with list of available backend names

    Example Response:
        ```json
        {
            "available_backends": ["mock", "simulator"],
            "total_count": 2
        }
        ```
    """
    orchestrator = await get_orchestrator()
    backends = orchestrator.list_available_backends()

    return {
        "available_backends": [backend.value for backend in backends],
        "total_count": len(backends)
    }


@router.get("/health")
async def quantum_simulator_health():
    """
    Health check for quantum simulator service.

    Returns:
        Dict with service health status

    Example Response:
        ```json
        {
            "status": "healthy",
            "orchestrator_initialized": true,
            "available_backends": 2,
            "cache_active_entries": 142,
            "message": "Quantum simulator operational"
        }
        ```
    """
    try:
        orchestrator = await get_orchestrator()
        cache = get_cache()
        stats = cache.get_cache_stats()

        return {
            "status": "healthy",
            "orchestrator_initialized": True,
            "available_backends": len(orchestrator.list_available_backends()),
            "cache_active_entries": stats["active_entries"],
            "message": "Quantum simulator operational"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "message": "Quantum simulator unavailable"
            }
        )
