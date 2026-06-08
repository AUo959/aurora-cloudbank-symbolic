"""Per-endpoint performance budgets and SLO tracking.

Budgets are intentionally conservative for a first pass.
Tighten them as baseline data is collected.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class EndpointBudget:
    """Performance budget for a single endpoint."""
    p95_ms: float          # p95 response time target
    p99_ms: float          # p99 response time target
    error_rate_pct: float  # max acceptable error rate (%)
    notes: str = ""


# Per-endpoint performance budgets
# Key format: "METHOD /path" (uppercase method, exact path)
ENDPOINT_BUDGETS: Dict[str, EndpointBudget] = {
    "GET /health":                                  EndpointBudget(p95_ms=50,   p99_ms=100,  error_rate_pct=0.1),
    "GET /api/health":                              EndpointBudget(p95_ms=50,   p99_ms=100,  error_rate_pct=0.1),
    "GET /live":                                    EndpointBudget(p95_ms=30,   p99_ms=80,   error_rate_pct=0.1),
    "GET /ready":                                   EndpointBudget(p95_ms=30,   p99_ms=80,   error_rate_pct=0.1),
    "GET /metrics":                                 EndpointBudget(p95_ms=100,  p99_ms=200,  error_rate_pct=0.1),
    "GET /telemetry/snapshot":                      EndpointBudget(p95_ms=200,  p99_ms=400,  error_rate_pct=0.5),
    "POST /api/memory-retrieval/retrieve":          EndpointBudget(p95_ms=500,  p99_ms=1000, error_rate_pct=1.0),
    "POST /api/memory-retrieval/memories":          EndpointBudget(p95_ms=300,  p99_ms=600,  error_rate_pct=1.0),
    "GET /api/memory-retrieval/cache-stats":        EndpointBudget(p95_ms=100,  p99_ms=200,  error_rate_pct=0.5),
    "POST /api/chat/rag":                           EndpointBudget(p95_ms=3000, p99_ms=5000, error_rate_pct=1.0,  notes="LLM call included"),
    "POST /agent/execute":                          EndpointBudget(p95_ms=5000, p99_ms=8000, error_rate_pct=2.0,  notes="LLM call included"),
    "POST /agent/gemini/execute":                   EndpointBudget(p95_ms=5000, p99_ms=8000, error_rate_pct=2.0,  notes="LLM call included"),
    "POST /agent/session":                          EndpointBudget(p95_ms=2000, p99_ms=4000, error_rate_pct=1.0),
    "GET /agent/status":                            EndpointBudget(p95_ms=100,  p99_ms=200,  error_rate_pct=0.5),
    "GET /agent/tools":                             EndpointBudget(p95_ms=100,  p99_ms=200,  error_rate_pct=0.5),
    "POST /simulate/scenario":                      EndpointBudget(p95_ms=5000, p99_ms=10000, error_rate_pct=2.0, notes="Quantum simulation"),
    "GET /aumem/metrics":                           EndpointBudget(p95_ms=100,  p99_ms=200,  error_rate_pct=0.5),
    "POST /aumem/retrieve":                         EndpointBudget(p95_ms=500,  p99_ms=1000, error_rate_pct=1.0),
    "GET /api/thread-bridge/status":                EndpointBudget(p95_ms=200,  p99_ms=500,  error_rate_pct=0.5),
    "POST /api/thread-bridge/handshake":            EndpointBudget(p95_ms=1000, p99_ms=2000, error_rate_pct=1.0),
    "POST /api/thread-bridge/transfer":             EndpointBudget(p95_ms=2000, p99_ms=4000, error_rate_pct=1.0),
    "GET /api/v2/nodes":                            EndpointBudget(p95_ms=200,  p99_ms=400,  error_rate_pct=0.5),
    "GET /api/v2/cluster/health":                   EndpointBudget(p95_ms=200,  p99_ms=400,  error_rate_pct=0.5),
    "GET /api/v2/drift/patterns":                   EndpointBudget(p95_ms=300,  p99_ms=600,  error_rate_pct=0.5),
    "GET /api/v2/drift/accuracy":                   EndpointBudget(p95_ms=200,  p99_ms=400,  error_rate_pct=0.5),
    "POST /api/v2/drift/predict":                   EndpointBudget(p95_ms=1000, p99_ms=2000, error_rate_pct=1.0),
    "GET /sonnet4/status":                          EndpointBudget(p95_ms=100,  p99_ms=200,  error_rate_pct=0.5),
    "POST /geometric/vector":                       EndpointBudget(p95_ms=300,  p99_ms=600,  error_rate_pct=1.0),
    "POST /geometric/mult":                         EndpointBudget(p95_ms=500,  p99_ms=1000, error_rate_pct=1.0),
    "GET /api/performance-budgets":                 EndpointBudget(p95_ms=50,   p99_ms=100,  error_rate_pct=0.1),
}


def get_budget(method: str, path: str) -> Optional[EndpointBudget]:
    """Look up budget for method+path. Returns None if no budget defined."""
    key = f"{method.upper()} {path}"
    return ENDPOINT_BUDGETS.get(key)


def check_budget_violation(method: str, path: str, duration_ms: float, is_error: bool) -> Optional[str]:
    """Check if a request violates its performance budget.

    Returns a violation message string if violated, None if OK or no budget.
    """
    budget = get_budget(method, path)
    if budget is None:
        return None
    if duration_ms > budget.p99_ms:
        return (
            f"p99 budget exceeded: {duration_ms:.0f}ms > {budget.p99_ms:.0f}ms "
            f"for {method.upper()} {path}"
        )
    if duration_ms > budget.p95_ms:
        logger.debug(
            "p95 budget soft breach: %.0fms > %.0fms for %s %s",
            duration_ms, budget.p95_ms, method.upper(), path,
        )
    return None


def list_budgets() -> Dict[str, dict]:
    """Return all budgets as a plain dict for serialization."""
    return {
        k: {
            "p95_ms": v.p95_ms,
            "p99_ms": v.p99_ms,
            "error_rate_pct": v.error_rate_pct,
            "notes": v.notes,
        }
        for k, v in ENDPOINT_BUDGETS.items()
    }
