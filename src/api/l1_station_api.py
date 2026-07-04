"""
L1 Station API
Aurora CloudBank Symbolic

FastAPI router exposing the read-only L1 (Station / Simulation) layer surface
described in ``config/l1_endpoints.yaml``. This is the first implemented slice
of that contract; it is backed by the canonical simulation state in
``.aurora/SIMULATION_STATE.json``.

API Routes:
- GET /api/aurora/health/l1        - L1 Station layer health status
- GET /api/aurora/simulation/state - Current canonical simulation state

Read-only by design: these endpoints observe the simulation state and never
mutate it. Mutating operations (crew activate/deactivate, dispatch) are
intentionally out of scope for this slice.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/api/aurora", tags=["L1 Station"])

# Repo root: src/api/l1_station_api.py -> parents[2] == repository root
_STATE_FILE = Path(__file__).resolve().parents[2] / ".aurora" / "SIMULATION_STATE.json"


def _load_state() -> tuple[Optional[Dict[str, Any]], str]:
    """Load the canonical simulation state.

    Returns a ``(state, status)`` tuple where ``status`` is one of
    ``"loaded"``, ``"missing"`` or ``"invalid"``. The endpoints degrade
    gracefully rather than raising so the health surface stays observable
    even when the state file is absent or corrupt.
    """
    if not _STATE_FILE.exists():
        return None, "missing"
    try:
        with _STATE_FILE.open("r", encoding="utf-8") as fh:
            return json.load(fh), "loaded"
    except (json.JSONDecodeError, OSError):
        return None, "invalid"


class L1HealthResponse(BaseModel):
    """L1 Station layer health summary."""

    model_config = ConfigDict(use_enum_values=True)

    layer: str = "L1"
    status: str = Field(
        description="operational when the state file loads, else degraded"
    )
    state_file: str = Field(description="loaded | missing | invalid")
    simulation_status: Optional[str] = None
    station_name: Optional[str] = None
    station_operational_status: Optional[str] = None
    current_crew: Optional[int] = None
    crew_capacity: Optional[int] = None
    quantum_cycle: Optional[Any] = None
    timestamp: str


class SimulationStateResponse(BaseModel):
    """Wrapper around the canonical simulation state."""

    status: str
    state_file: str
    state: Optional[Dict[str, Any]] = None


@router.get("/health/l1", response_model=L1HealthResponse)
async def get_l1_health() -> L1HealthResponse:
    """Return L1 Station layer health derived from the canonical state."""
    state, file_status = _load_state()
    now = datetime.now(timezone.utc).isoformat()

    if state is None:
        return L1HealthResponse(
            status="degraded",
            state_file=file_status,
            timestamp=now,
        )

    simulation = state.get("simulation", {}) or {}
    station = state.get("station_infrastructure", {}) or {}

    return L1HealthResponse(
        status="operational",
        state_file=file_status,
        simulation_status=simulation.get("status"),
        station_name=station.get("name"),
        station_operational_status=station.get("operational_status"),
        current_crew=station.get("current_crew"),
        crew_capacity=station.get("crew_capacity"),
        quantum_cycle=state.get("quantum_cycle", {}).get("current_cycle")
        if isinstance(state.get("quantum_cycle"), dict)
        else state.get("quantum_cycle"),
        timestamp=now,
    )


@router.get("/simulation/state", response_model=SimulationStateResponse)
async def get_simulation_state() -> SimulationStateResponse:
    """Return the current canonical simulation state (read-only)."""
    state, file_status = _load_state()
    return SimulationStateResponse(
        status="success" if state is not None else "unavailable",
        state_file=file_status,
        state=state,
    )
