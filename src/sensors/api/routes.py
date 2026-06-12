"""
Sensor array API router — spec §API Structure.

GET-only by design: the API is an observation surface. There are no POST/PUT
endpoints because sensors cannot be commanded to act (one-way observation).

Usage:
    from src.sensors.api.routes import build_router
    app.include_router(build_router(array), prefix="/api/sensors")
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from src.sensors.array import SensorArrayFacade

try:
    from fastapi import APIRouter, HTTPException
    _FASTAPI = True
except ImportError:  # pragma: no cover — headless/test contexts
    APIRouter = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    _FASTAPI = False


def _dump(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, list):
        return [_dump(o) for o in obj]
    return obj


def build_router(array: "SensorArrayFacade"):
    """Build the /api/sensors router against a SensorArrayFacade."""
    if not _FASTAPI:
        raise RuntimeError("fastapi is not installed; sensor API unavailable")

    router = APIRouter(tags=["sensors"])

    # -- internal / external (generic category reads) -------------------------
    for group, cats in (
        ("internal", ["environmental", "structural", "biometrics", "operational"]),
        ("external", ["proximity", "deep-space", "astronomical",
                      "communications", "salvage"]),
        ("observatory/physical",
         ["containment", "fidelity", "boundary", "reality-anchor", "earth-relay"]),
    ):
        for cat in cats:
            def make(group=group, cat=cat):
                async def endpoint():
                    reading = array.read_category(group, cat.replace("-", "_"))
                    if reading is None:
                        raise HTTPException(404, f"no sensor for {group}/{cat}")
                    return _dump(reading)
                return endpoint
            router.add_api_route(f"/{group}/{cat}", make(), methods=["GET"])

    # -- observatory symbolic --------------------------------------------------
    router.add_api_route(
        "/observatory/symbolic/concept-resonance",
        lambda: _dump(array.concept_resonance_reading()), methods=["GET"])
    router.add_api_route(
        "/observatory/symbolic/ethical-signal",
        lambda: _dump(array.ethical_signal_reading()), methods=["GET"])
    router.add_api_route(
        "/observatory/symbolic/ethical-signal/{entity_id}",
        lambda entity_id: _dump(array.ethical_signal_reading(entity_id)),
        methods=["GET"])
    router.add_api_route(
        "/observatory/symbolic/drift-presignature",
        lambda: _dump(array.drift_presignature()), methods=["GET"])
    # NEW in v0.3.0:
    router.add_api_route(
        "/observatory/symbolic/integration-depth",
        lambda: _dump(array.integration_depth()), methods=["GET"])

    # -- fusion ------------------------------------------------------------------
    router.add_api_route("/fusion/resonance",
                         lambda: _dump(array.fusion_resonance()), methods=["GET"])
    router.add_api_route("/fusion/oscillation-health",
                         lambda: _dump(array.oscillation_health()), methods=["GET"])
    router.add_api_route("/fusion/forecasts",
                         lambda: _dump(array.forecasts()), methods=["GET"])
    router.add_api_route(
        "/fusion/forecasts/{anomaly_type}",
        lambda anomaly_type: _dump(array.forecasts(anomaly_type)), methods=["GET"])
    router.add_api_route("/fusion/certification",
                         lambda: _dump(array.certification()), methods=["GET"])

    # -- health -------------------------------------------------------------------
    router.add_api_route("/health/status",
                         lambda: array.health_status(), methods=["GET"])
    router.add_api_route("/health/performance",
                         lambda: array.performance(), methods=["GET"])

    return router
