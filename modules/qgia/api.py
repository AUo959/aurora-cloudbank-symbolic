"""QGIA Forecast API — FastAPI router exposing the QSFE forecast engine.

Provides REST endpoints for running multi-agent belief-propagation forecasts,
browsing the analyst population, and inspecting the trust network.

DLP: qgia_forecast_api_v1
Anchors: T1:QGIA_API, SRB:L1_QGIA
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .forecast_engine import QGIAForecastEngine
from .scenario import EXAMPLE_SCENARIOS, create_scenario
from .schemas import ForecastOutput, ScenarioInput

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/qgia", tags=["qgia-forecast"])

# ---------------------------------------------------------------------------
# Module-level engine singleton — created lazily on first use
# ---------------------------------------------------------------------------
_engine: Optional[QGIAForecastEngine] = None


def _get_engine() -> QGIAForecastEngine:
    """Return (or create) the shared forecast engine instance."""
    global _engine
    if _engine is None:
        _engine = QGIAForecastEngine(seed=42)
        logger.info("QGIA ForecastEngine initialised (seed=42, %d agents)", len(_engine.agents))
    return _engine


# ---------------------------------------------------------------------------
# In-memory forecast result store (keyed by forecast_id)
# ---------------------------------------------------------------------------
_forecast_store: Dict[str, ForecastOutput] = {}


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class RunForecastRequest(BaseModel):
    """Request body for POST /qgia/forecast."""

    scenario_id: str = Field(..., description="Unique identifier for the scenario")
    title: str = Field(..., description="Short descriptive title")
    description: str = Field(..., description="Full scenario narrative")
    region: str = Field(..., description="Geographic region (e.g. 'Middle East')")
    domain: str = Field(
        ...,
        description="Domain tag: military | political | economic | humanitarian | cyber",
    )
    evidence_fragments: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="List of evidence objects with source, content, reliability (0-1), recency",
    )
    requesting_node: str = Field(default="L1_QGIA", description="Requesting node identifier")


class ForecastListItem(BaseModel):
    """Lightweight summary of a stored forecast."""

    forecast_id: str
    scenario_id: str
    scenario_title: Optional[str]
    timestamp: str
    tier_count: int
    processing_ms: int
    context_tag: str = "qgia_forecast_api_v1"


class PopulationSummary(BaseModel):
    """Summary statistics for the analyst population."""

    total_agents: int
    division_counts: Dict[str, int]
    grade_distribution: Dict[str, int]
    archetype_distribution: Dict[str, int]
    context_tag: str = "qgia_forecast_api_v1"


class NetworkSummary(BaseModel):
    """High-level trust network statistics."""

    total_agents: int
    total_edges: int
    edge_type_counts: Dict[str, int]
    avg_out_degree: float
    context_tag: str = "qgia_forecast_api_v1"


class ExampleScenariosResponse(BaseModel):
    """List of built-in example scenarios."""

    scenarios: List[Dict[str, Any]]
    count: int
    context_tag: str = "qgia_forecast_api_v1"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/health")
async def qgia_health() -> Dict[str, Any]:
    """QGIA module health and population statistics."""
    try:
        engine = _get_engine()
        return {
            "status": "healthy",
            "module": "QGIA Forecast Simulation Engine",
            "version": "1.0.0",
            "agent_count": len(engine.agents),
            "edge_count": len(engine.edges),
            "stored_forecasts": len(_forecast_store),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_tag": "qgia_forecast_api_v1",
        }
    except Exception as exc:
        logger.exception("QGIA health check failed")
        raise HTTPException(status_code=503, detail=f"QGIA engine unavailable: {exc}") from exc


@router.post("/forecast", response_model=ForecastOutput, status_code=201)
async def run_forecast(request: RunForecastRequest) -> ForecastOutput:
    """Run a full QSFE five-phase belief-propagation forecast.

    Accepts a scenario description and evidence fragments, returns a structured
    three-tier probabilistic forecast with dissent analysis and provenance data.

    DLP: qgia_run_forecast
    """
    try:
        engine = _get_engine()
        scenario = create_scenario(
            scenario_id=request.scenario_id,
            title=request.title,
            description=request.description,
            region=request.region,
            domain=request.domain,
            evidence_fragments=request.evidence_fragments,
            requesting_node=request.requesting_node,
        )
        result = engine.run_forecast(scenario)
        _forecast_store[result.forecast_id] = result
        logger.info(
            "Forecast complete: id=%s scenario=%s agents_in_cell=%s ms=%s",
            result.forecast_id,
            scenario.scenario_id,
            result.meta.get("cell_size"),
            result.meta.get("processing_ms"),
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Forecast execution failed")
        raise HTTPException(status_code=500, detail=f"Forecast failed: {exc}") from exc


@router.get("/forecast", response_model=List[ForecastListItem])
async def list_forecasts(
    scenario_id: Optional[str] = Query(default=None, description="Filter by scenario_id"),
    limit: int = Query(default=20, ge=1, le=100, description="Max results"),
) -> List[ForecastListItem]:
    """List stored forecast results, optionally filtered by scenario_id."""
    results = list(_forecast_store.values())
    if scenario_id:
        results = [r for r in results if r.scenario_id == scenario_id]
    results = sorted(results, key=lambda r: r.timestamp, reverse=True)[:limit]
    return [
        ForecastListItem(
            forecast_id=r.forecast_id,
            scenario_id=r.scenario_id,
            scenario_title=None,
            timestamp=r.timestamp,
            tier_count=len(r.tier_assessments),
            processing_ms=r.meta.get("processing_ms", 0),
        )
        for r in results
    ]


@router.get("/forecast/{forecast_id}", response_model=ForecastOutput)
async def get_forecast(forecast_id: str) -> ForecastOutput:
    """Retrieve a previously computed forecast by its ID.

    DLP: qgia_get_forecast
    """
    # Validate forecast_id format to prevent injection
    if not forecast_id or len(forecast_id) > 64:
        raise HTTPException(status_code=400, detail="Invalid forecast_id")
    result = _forecast_store.get(forecast_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Forecast '{forecast_id}' not found")
    return result


@router.get("/population", response_model=PopulationSummary)
async def get_population() -> PopulationSummary:
    """Return summary statistics for the 551-analyst population.

    DLP: qgia_population_summary
    """
    try:
        engine = _get_engine()
        division_counts: Dict[str, int] = {}
        grade_dist: Dict[str, int] = {}
        archetype_dist: Dict[str, int] = {}

        for agent in engine.agents:
            div = agent.division.value
            division_counts[div] = division_counts.get(div, 0) + 1
            grade_dist[agent.grade] = grade_dist.get(agent.grade, 0) + 1
            archetype_dist[agent.archetype] = archetype_dist.get(agent.archetype, 0) + 1

        return PopulationSummary(
            total_agents=len(engine.agents),
            division_counts=division_counts,
            grade_distribution=grade_dist,
            archetype_distribution=archetype_dist,
        )
    except Exception as exc:
        logger.exception("Population summary failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/network", response_model=NetworkSummary)
async def get_network_summary() -> NetworkSummary:
    """Return high-level statistics for the analyst trust network.

    DLP: qgia_network_summary
    """
    try:
        engine = _get_engine()
        edge_type_counts: Dict[str, int] = {}
        for edge in engine.edges:
            edge_type_counts[edge.edge_type] = edge_type_counts.get(edge.edge_type, 0) + 1

        avg_out = len(engine.edges) / max(len(engine.agents), 1)

        return NetworkSummary(
            total_agents=len(engine.agents),
            total_edges=len(engine.edges),
            edge_type_counts=edge_type_counts,
            avg_out_degree=round(avg_out, 2),
        )
    except Exception as exc:
        logger.exception("Network summary failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/scenarios/examples", response_model=ExampleScenariosResponse)
async def list_example_scenarios() -> ExampleScenariosResponse:
    """List the built-in example forecast scenarios available for quick testing.

    DLP: qgia_example_scenarios
    """
    scenarios = []
    for scenario in EXAMPLE_SCENARIOS:
        scenarios.append({
            "scenario_id": scenario.scenario_id,
            "title": scenario.title,
            "region": scenario.region,
            "domain": scenario.domain,
            "evidence_fragment_count": len(scenario.evidence_fragments),
            "requesting_node": scenario.requesting_node,
        })
    return ExampleScenariosResponse(scenarios=scenarios, count=len(scenarios))


def _find_example_scenario(name: str) -> Optional[ScenarioInput]:
    """Return an example scenario whose id or title contains `name`."""
    normalized = name.lower().replace("-", "_")
    for s in EXAMPLE_SCENARIOS:
        key = s.title.lower().replace(" ", "_").replace("-", "_")
        if normalized in key or normalized == s.scenario_id.lower():
            return s
    return None


@router.post("/forecast/example/{scenario_name}", response_model=ForecastOutput, status_code=201)
async def run_example_forecast(scenario_name: str) -> ForecastOutput:
    """Run a forecast using one of the built-in example scenarios.

    Available names: iran_nuclear_escalation, south_china_sea_confrontation,
    european_energy_crisis, subsaharan_instability

    DLP: qgia_example_forecast
    """
    matched = _find_example_scenario(scenario_name)
    if matched is None:
        available = [s.scenario_id for s in EXAMPLE_SCENARIOS]
        raise HTTPException(
            status_code=404,
            detail=f"Example scenario '{scenario_name}' not found. Available: {available}",
        )
    try:
        engine = _get_engine()
        result = engine.run_forecast(matched)
        _forecast_store[result.forecast_id] = result
        return result
    except Exception as exc:
        logger.exception("Example forecast failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
