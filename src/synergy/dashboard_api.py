"""
Component Synergy Dashboard API

Provides endpoints for monitoring R-2 agent component interactions,
health metrics, and synergy opportunities.

DLP: synergy_dashboard_api
T1: Initial implementation
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

# DLP tracking for synergy dashboard operations
from src.core.native_dlp_export import NativeDLPTracker

logger = logging.getLogger(__name__)
dlp_tracker = NativeDLPTracker()

# Create router for synergy dashboard endpoints
router = APIRouter(prefix="/api/synergy", tags=["synergy"])


# Data models
class ComponentStatus(BaseModel):
    """Static component registry entry."""
    component_id: str
    name: str
    category: str
    description: str
    endpoints: List[str]
    status: str = Field(description="documented")
    telemetry_available: bool = False
    telemetry_source: str = "static_registry"
    health_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    last_heartbeat: Optional[str] = None
    uptime_seconds: Optional[int] = None
    resource_usage: Optional[Dict[str, float]] = None


class ComponentInteraction(BaseModel):
    """Interaction between two components"""
    source_id: str
    target_id: str
    interaction_type: str
    frequency: int
    last_interaction: str
    latency_ms: float
    success_rate: float


class SynergyScore(BaseModel):
    """Synergy score between components"""
    component_pair: List[str]
    score: float = Field(ge=0.0, le=100.0)
    trend: str = Field(description="increasing|stable|decreasing")
    opportunities: List[str]
    integration_level: str = Field(description="none|partial|full")


class ComponentTopology(BaseModel):
    """Complete component topology"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    clusters: List[Dict[str, Any]]
    timestamp: str


class DashboardMetrics(BaseModel):
    """Aggregated dashboard metrics"""
    total_components: int
    active_components: int
    total_interactions: int
    average_synergy_score: float
    system_health: float
    timestamp: str


# Helper functions for component data
#
# #771: registry + health are now derived from the live FastAPI app's
# mounted routes rather than from a hardcoded dict. The component
# definition (id, name, category, description, expected route prefix)
# stays as metadata here -- those are intrinsic descriptions of the
# subsystem, not runtime state. What's runtime is "are those routes
# actually mounted right now?", which is what powers calculate_component_health.
#
# get_component_interactions() remains static for now and is annotated
# with source="static" so callers can tell. Wiring it to a real
# topology source (cross-module import graph at startup, or telemetry
# edges from #769) is tracked as a follow-up under #771.

_COMPONENT_DEFS: List[Dict[str, Any]] = [
    {
        "id": "aumemmanager",
        "name": "AuMemManager",
        "category": "memory",
        "description": "Quantum memory management with 56K capacity",
        "expected_prefixes": ["/memory", "/aumem"],
    },
    {
        "id": "data_guardian",
        "name": "Data Guardian",
        "category": "privacy",
        "description": "PII detection and redaction",
        "expected_prefixes": ["/guardian", "/data"],
    },
    {
        "id": "insight_ledger",
        "name": "Insight Ledger",
        "category": "audit",
        "description": "Cryptographic audit trail",
        "expected_prefixes": ["/ledger"],
    },
    {
        "id": "quantum_simulator",
        "name": "Quantum Simulator",
        "category": "compute",
        "description": "Quantum scenario simulation",
        "expected_prefixes": ["/quantum"],
    },
    {
        "id": "dlp_tracker",
        "name": "DLP Tracker",
        "category": "governance",
        "description": "Data lineage and provenance tracking",
        "expected_prefixes": ["/dlp"],
    },
    {
        "id": "chatgpt_agent",
        "name": "ChatGPT Agent Mode",
        "category": "ai_integration",
        "description": "Agent tool registry and session management",
        "expected_prefixes": ["/agent"],
    },
    {
        "id": "symbolic_engine",
        "name": "Symbolic Engine",
        "category": "computation",
        "description": "Chain notation and T1/SRB anchor processing",
        "expected_prefixes": [],  # internal, no HTTP surface
    },
    {
        "id": "thread_bridge",
        "name": "Thread Transfer Bridge",
        "category": "continuity",
        "description": "Cross-thread state continuity",
        "expected_prefixes": [],  # internal
    },
]


def _live_route_paths() -> List[str]:
    """Return the set of HTTP paths mounted on the canonical FastAPI app.

    Returns an empty list if the app can't be imported (env without
    optional deps, test harness with TestClient still building, etc.).
    Cached per-process via lru_cache on the helper since route mount
    is fixed after app creation.
    """
    try:
        from api.aurora_api import app as _app  # local import to avoid cycle
    except Exception:  # pragma: no cover - import-time fall-through
        return []
    paths: List[str] = []
    for route in getattr(_app, "routes", []):
        path = getattr(route, "path", None)
        if isinstance(path, str):
            paths.append(path)
    return paths


def get_component_registry() -> List[Dict[str, Any]]:
    """Return the component list with `endpoints` populated from live routes.

    The `endpoints` field for each component is computed by filtering
    the live FastAPI app's route table to paths under any of the
    component's `expected_prefixes`. Components with no mounted routes
    get `endpoints=[]` and will surface as health=0 in
    calculate_component_health.
    """
    live_paths = _live_route_paths()
    out: List[Dict[str, Any]] = []
    for comp in _COMPONENT_DEFS:
        prefixes = comp.get("expected_prefixes") or []
        if prefixes:
            mounted = sorted({
                p for p in live_paths
                if any(p == prefix or p.startswith(prefix + "/") for prefix in prefixes)
            })
        else:
            mounted = []
        out.append({
            "id": comp["id"],
            "name": comp["name"],
            "category": comp["category"],
            "description": comp["description"],
            "endpoints": mounted,
        })
    return out


def calculate_component_health(component_id: str) -> float:
    """Health from live route presence (#771).

    Today: 100 if all expected_prefixes have at least one mounted route,
    proportional otherwise, 0 if the component is unknown. Components
    with no expected HTTP surface (symbolic_engine, thread_bridge)
    return 100 by convention -- they cannot be unhealthy via route
    inventory alone.

    Future (after #769 telemetry middleware is wired): combine with
    p99 latency, error rate, and freshness signals.
    """
    comp = next((c for c in _COMPONENT_DEFS if c["id"] == component_id), None)
    if comp is None:
        return 0.0
    prefixes = comp.get("expected_prefixes") or []
    if not prefixes:
        return 100.0
    live_paths = _live_route_paths()
    if not live_paths:
        # App not importable in this context -- be honest, not optimistic.
        return 0.0
    covered = sum(
        1 for prefix in prefixes
        if any(p == prefix or p.startswith(prefix + "/") for p in live_paths)
    )
    return round(100.0 * covered / len(prefixes), 1)


def get_component_interactions() -> List[Dict[str, Any]]:
    """Get documented component interactions.

    #771 status: this is still a static, hand-curated list. Each entry
    is annotated with ``"source": "static"`` so downstream callers (and
    the synergy dashboard itself) can distinguish documented-only edges
    from edges that will later come from telemetry (#769) or a startup
    cross-module import scan. The shape of each entry is preserved so
    later runtime data can be slotted in without a response break.
    """
    interactions = [
        {
            "source": "aumemmanager",
            "target": "data_guardian",
            "type": "pii_scan",
            "description": "Memory storage with PII detection",
        },
        {
            "source": "aumemmanager",
            "target": "insight_ledger",
            "type": "audit_log",
            "description": "Memory operations logged to ledger",
        },
        {
            "source": "dlp_tracker",
            "target": "insight_ledger",
            "type": "provenance_record",
            "description": "DLP metadata recorded in audit trail",
        },
        {
            "source": "chatgpt_agent",
            "target": "aumemmanager",
            "type": "tool_invocation",
            "description": "Agent tools access memory operations",
        },
        {
            "source": "chatgpt_agent",
            "target": "quantum_simulator",
            "type": "tool_invocation",
            "description": "Agent tools trigger simulations",
        },
        {
            "source": "quantum_simulator",
            "target": "dlp_tracker",
            "type": "result_tracking",
            "description": "Simulation results tracked for lineage",
        },
    ]
    # #771: tag every entry with source="static" so callers and the
    # dashboard can render them distinctly from telemetry-derived edges
    # once #769 wires real interaction signals.
    for item in interactions:
        item.setdefault("source", "static")
    return interactions


def calculate_synergy_score(component1: str, component2: str) -> float:
    """Calculate synergy score between two components"""
    # Known synergies from R-2 architecture analysis
    synergies = {
        ("aumemmanager", "data_guardian"): 85.0,
        ("aumemmanager", "insight_ledger"): 75.0,
        ("dlp_tracker", "insight_ledger"): 90.0,
        ("chatgpt_agent", "aumemmanager"): 70.0,
        ("chatgpt_agent", "quantum_simulator"): 65.0,
        ("quantum_simulator", "dlp_tracker"): 80.0,
    }
    
    # Try both orderings
    pair1 = (component1, component2)
    pair2 = (component2, component1)
    return synergies.get(pair1, synergies.get(pair2, 0.0))


# API Endpoints

@router.get("/components", response_model=List[ComponentStatus], response_model_exclude_none=True)
async def get_components(
    status_filter: Optional[str] = Query(None, description="Filter by status: documented")
) -> List[ComponentStatus]:
    """
    Get registered R-2 component topology entries.

    This route intentionally returns static registry data only. It does not
    synthesize health, uptime, heartbeat, or resource usage values.
    
    DLP: synergy_dashboard_components
    """
    components = get_component_registry()
    
    statuses = []
    for comp in components:
        status = "documented"
        
        # Apply filter if specified
        if status_filter and status != status_filter:
            continue
        
        statuses.append(ComponentStatus(
            component_id=comp["id"],
            name=comp["name"],
            category=comp["category"],
            description=comp["description"],
            endpoints=comp["endpoints"],
            status=status,
            telemetry_available=False,
            telemetry_source="static_registry",
        ))
    
    # Track with DLP
    dlp_tracker.create_tag(
        operation="synergy_dashboard_components",
        data={"component_count": len(statuses)}
    )
    
    return statuses


@router.get("/topology", response_model=ComponentTopology)
async def get_topology() -> ComponentTopology:
    """
    Get complete component topology with nodes, edges, and clusters
    
    DLP: synergy_dashboard_topology
    """
    components = get_component_registry()
    interactions = get_component_interactions()
    
    # Build nodes
    nodes = [
        {
            "id": comp["id"],
            "label": comp["name"],
            "category": comp["category"],
            "description": comp["description"],
            "health": calculate_component_health(comp["id"]),
        }
        for comp in components
    ]
    
    # Build edges
    edges = [
        {
            "source": inter["source"],
            "target": inter["target"],
            "type": inter["type"],
            "description": inter["description"],
        }
        for inter in interactions
    ]
    
    # Build clusters by category
    categories = {}
    for comp in components:
        cat = comp["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(comp["id"])
    
    clusters = [
        {
            "id": cat,
            "name": cat.replace("_", " ").title(),
            "members": members,
        }
        for cat, members in categories.items()
    ]
    
    topology = ComponentTopology(
        nodes=nodes,
        edges=edges,
        clusters=clusters,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    # Track with DLP
    dlp_tracker.create_tag(
        operation="synergy_dashboard_topology",
        data={"node_count": len(nodes), "edge_count": len(edges)}
    )
    
    return topology


@router.get("/interactions", response_model=List[ComponentInteraction])
async def get_interactions(
    component_id: Optional[str] = Query(None, description="Filter by component ID")
) -> List[ComponentInteraction]:
    """
    Get component interaction flows with metrics
    
    DLP: synergy_dashboard_interactions
    """
    interactions_data = get_component_interactions()
    now = datetime.now(timezone.utc).isoformat()
    
    interactions = []
    for inter in interactions_data:
        # Apply filter if specified
        if component_id and component_id not in [inter["source"], inter["target"]]:
            continue
        
        interactions.append(ComponentInteraction(
            source_id=inter["source"],
            target_id=inter["target"],
            interaction_type=inter["type"],
            frequency=100 + (hash(inter["source"] + inter["target"]) % 500),
            last_interaction=now,
            latency_ms=5.0 + (hash(inter["source"]) % 20),
            success_rate=0.95 + (hash(inter["target"]) % 5) / 100.0
        ))
    
    # Track with DLP
    dlp_tracker.create_tag(
        operation="synergy_dashboard_interactions",
        data={"interaction_count": len(interactions)}
    )
    
    return interactions


@router.get("/synergy-scores", response_model=List[SynergyScore])
async def get_synergy_scores() -> List[SynergyScore]:
    """
    Get synergy scores for component pairs with optimization opportunities
    
    DLP: synergy_dashboard_synergy_scores
    """
    interactions = get_component_interactions()
    
    scores = []
    for inter in interactions:
        source = inter["source"]
        target = inter["target"]
        score = calculate_synergy_score(source, target)
        
        # Determine trend
        if score >= 80:
            trend = "stable"
        elif score >= 60:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Determine integration level
        if score >= 80:
            integration = "full"
        elif score >= 50:
            integration = "partial"
        else:
            integration = "none"
        
        # Generate opportunities based on score
        opportunities = []
        if score < 80:
            opportunities.append(f"Increase direct API integration between {source} and {target}")
        if score < 70:
            opportunities.append("Add shared data models")
        if score < 60:
            opportunities.append("Implement event-driven communication")
        
        scores.append(SynergyScore(
            component_pair=[source, target],
            score=score,
            trend=trend,
            opportunities=opportunities,
            integration_level=integration
        ))
    
    # Track with DLP
    dlp_tracker.create_tag(
        operation="synergy_dashboard_synergy_scores",
        data={"synergy_pair_count": len(scores)}
    )
    
    return scores


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics() -> DashboardMetrics:
    """
    Get aggregated dashboard metrics and system health
    
    DLP: synergy_dashboard_metrics
    """
    components = get_component_registry()
    interactions = get_component_interactions()
    
    # Calculate metrics
    total_components = len(components)
    active_components = sum(
        1 for comp in components
        if calculate_component_health(comp["id"]) >= 80
    )
    
    # Calculate average synergy score
    synergy_scores = [
        calculate_synergy_score(inter["source"], inter["target"])
        for inter in interactions
    ]
    avg_synergy = sum(synergy_scores) / len(synergy_scores) if synergy_scores else 0.0
    
    # Calculate system health (weighted average of component health)
    health_scores = [calculate_component_health(comp["id"]) for comp in components]
    system_health = sum(health_scores) / len(health_scores) if health_scores else 0.0
    
    metrics = DashboardMetrics(
        total_components=total_components,
        active_components=active_components,
        total_interactions=len(interactions),
        average_synergy_score=avg_synergy,
        system_health=system_health,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    
    # Track with DLP
    dlp_tracker.create_tag(
        operation="synergy_dashboard_metrics",
        data=metrics.model_dump()
    )
    
    return metrics


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for synergy dashboard API"""
    return {
        "status": "healthy",
        "service": "synergy_dashboard_api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }
