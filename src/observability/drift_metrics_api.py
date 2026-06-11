"""
Drift Metrics API

FastAPI router providing endpoints for drift metrics, Prometheus export,
and drift monitoring health checks.

DLP: drift_metrics_api_v1
Anchors: EOS_SEED_ORION, HALO_CONTINUITY_GRAFT_005
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from src.monitoring.drift_detector import DriftDetector, DriftLevel

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/api/drift", tags=["drift-metrics"])

# Global drift detector and exporter instances (injected at startup)
_drift_detector: Optional[DriftDetector] = None
_drift_exporter = None  # Lazy import to avoid circular deps


def _monitoring_storage_dir() -> Path:
    """Resolve the shared monitoring storage directory."""
    return Path(os.getenv("MONITORING_STORAGE_DIR", "./monitoring_data"))


def _get_exporter():
    """Get or create the drift exporter instance."""
    global _drift_exporter
    if _drift_exporter is None:
        from src.observability.drift_prometheus_exporter import get_drift_exporter
        _drift_exporter = get_drift_exporter(drift_detector=_drift_detector)
    return _drift_exporter


def _get_drift_detector():
    """Get current drift detector instance, creating one if needed."""
    global _drift_detector
    if _drift_detector is None:
        _drift_detector = DriftDetector(
            alerts_path=_monitoring_storage_dir() / "drift_alerts.jsonl"
        )
    return _drift_detector


def set_drift_detector(detector: DriftDetector):
    """
    Set the drift detector instance for the API.

    Args:
        detector: DriftDetector instance to use
    """
    global _drift_detector
    _drift_detector = detector
    if _drift_exporter is not None:
        _drift_exporter.set_drift_detector(detector)


# Request/Response Models

class EstablishBaselineRequest(BaseModel):
    """Request model for establishing a new baseline."""
    agent_id: str = Field(..., description="Agent identifier")
    metric_name: str = Field(..., description="Metric name")
    values: List[float] = Field(..., description="Historical values to establish baseline")


class BaselineResponse(BaseModel):
    """Response model for baseline operations."""
    success: bool
    agent_id: str
    metric_name: str
    mean: float
    std_dev: float
    sample_count: int
    context_tag: str = "drift_metrics_api_v1"


class DriftAlertResponse(BaseModel):
    """Response model for drift alerts."""
    timestamp: str
    agent_id: str
    metric_name: str
    level: str
    method: str
    current_value: float
    baseline_value: float
    deviation: float
    description: str
    context_tag: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check."""
    healthy: bool
    service_name: str
    has_detector: bool
    metrics_count: int
    alerts_count: int
    timestamp: str
    context_tag: str = "drift_metrics_api_v1"


# Endpoints

@router.get(
    "/metrics",
    response_class=PlainTextResponse,
    summary="Prometheus metrics export",
    description="Export drift metrics in Prometheus text format"
)
async def get_prometheus_metrics():
    """
    Export drift metrics in Prometheus text format.

    Returns Prometheus-compatible metrics for:
    - aurora_drift_delta: Current drift from baseline
    - aurora_drift_baseline_mean: Baseline mean value
    - aurora_drift_baseline_stddev: Baseline standard deviation
    - aurora_drift_moving_average: Current moving average
    - aurora_drift_alerts_total: Total alerts generated
    - aurora_drift_detector_info: Detector configuration info

    DLP: drift_metrics_api_v1
    """
    try:
        exporter = _get_exporter()
        metrics = exporter.export_metrics()
        return PlainTextResponse(content=metrics, media_type="text/plain")
    except Exception as e:
        logger.error("Failed to export Prometheus metrics: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/summary",
    summary="Drift metrics summary",
    description="Get JSON summary of current drift state"
)
async def get_drift_summary() -> Dict[str, Any]:
    """
    Get JSON summary of current drift state.

    Returns aggregated metrics including:
    - Total monitored metrics
    - Total alerts
    - Alerts by level and agent
    - Detector configuration
    - Recent measurement count

    DLP: drift_metrics_api_v1
    """
    try:
        exporter = _get_exporter()
        summary = exporter.get_metrics_summary()
        return {
            "success": True,
            **summary
        }
    except Exception as e:
        logger.error("Failed to get drift summary: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/alerts",
    summary="Get drift alerts",
    description="Get recent drift alerts with optional filtering"
)
async def get_drift_alerts(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    level: Optional[str] = Query(None, description="Filter by alert level (info/warning/critical)"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts to return")
) -> Dict[str, Any]:
    """
    Get recent drift alerts with filtering.

    Args:
        agent_id: Optional filter by agent ID
        level: Optional filter by alert level
        limit: Maximum number of alerts to return

    DLP: drift_metrics_api_v1
    """
    try:
        if _drift_detector is None:
            return {
                "success": True,
                "alerts": [],
                "count": 0,
                "drift_detector_configured": False,
                "message": "No drift detector configured - alerts unavailable",
                "context_tag": "drift_metrics_api_v1",
            }

        # Parse level filter
        level_filter = None
        if level:
            try:
                level_filter = DriftLevel(level.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid level: {level}. Must be one of: info, warning, critical"
                )

        # Get alerts from detector
        alerts = _drift_detector.get_alerts(agent_id=agent_id, level=level_filter)

        # Convert to response format and limit
        alert_dicts = [alert.to_dict() for alert in alerts[-limit:]]

        return {
            "success": True,
            "alerts": alert_dicts[::-1],  # Most recent first
            "count": len(alert_dicts),
            "total_available": len(alerts),
            "context_tag": "drift_metrics_api_v1",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get drift alerts: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/baselines",
    summary="Get current baselines",
    description="Get current baseline configurations for all monitored metrics"
)
async def get_baselines() -> Dict[str, Any]:
    """
    Get current baseline configurations.

    Returns all established baselines with their statistical parameters.

    DLP: drift_metrics_api_v1
    """
    try:
        if _drift_detector is None:
            exporter = _get_exporter()
            baselines_data = exporter.get_baselines()
            return {
                "success": True,
                "drift_detector_configured": False,
                **baselines_data
            }

        # Get baselines from detector
        baselines = _drift_detector.export_baselines()

        return {
            "success": True,
            "drift_detector_configured": True,
            "count": len(baselines),
            "baselines": baselines,
            "context_tag": "drift_metrics_api_v1",
        }
    except Exception as e:
        logger.error("Failed to get baselines: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/baseline",
    summary="Establish new baseline",
    description="Establish a new baseline for an agent/metric combination"
)
async def establish_baseline(request: EstablishBaselineRequest) -> Dict[str, Any]:
    """
    Establish a new baseline for drift detection.

    Creates baseline metrics from provided historical values.

    Args:
        request: EstablishBaselineRequest with agent_id, metric_name, and values

    DLP: drift_metrics_api_v1
    """
    try:
        detector = _get_drift_detector()

        if not request.values:
            raise HTTPException(status_code=400, detail="Values list cannot be empty")

        if len(request.values) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 values required to establish baseline"
            )

        baseline = detector.establish_baseline(
            agent_id=request.agent_id,
            metric_name=request.metric_name,
            values=request.values
        )

        # Update exporter
        exporter = _get_exporter()
        exporter.record_drift_measurement(
            agent_id=baseline.agent_id,
            metric_name=baseline.metric_name,
            current_value=baseline.mean,
            baseline_mean=baseline.mean,
            baseline_stddev=baseline.std_dev,
            deviation=0.0,
            moving_average=baseline.moving_average
        )

        return {
            "success": True,
            "agent_id": baseline.agent_id,
            "metric_name": baseline.metric_name,
            "mean": baseline.mean,
            "std_dev": baseline.std_dev,
            "min_value": baseline.min_value,
            "max_value": baseline.max_value,
            "sample_count": baseline.sample_count,
            "last_updated": baseline.last_updated,
            "context_tag": "drift_metrics_api_v1",
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid value: {e}")
    except Exception as e:
        logger.error("Failed to establish baseline: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/health",
    summary="Health check",
    description="Check drift monitoring health status"
)
async def health_check() -> Dict[str, Any]:
    """
    Perform health check on drift monitoring system.

    Returns health status including:
    - Service availability
    - Detector presence
    - Metrics and alert counts

    DLP: drift_metrics_api_v1
    """
    try:
        exporter = _get_exporter()
        health = exporter.health_check()

        # Add detector-specific info
        if _drift_detector:
            health["detector_baselines"] = len(_drift_detector.baselines)
            health["detector_alerts"] = len(_drift_detector.alerts)

        return {
            "success": True,
            **health
        }
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return {
            "success": False,
            "healthy": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_tag": "drift_metrics_api_v1",
        }


def create_drift_metrics_router(detector: Optional[DriftDetector] = None) -> APIRouter:
    """
    Create and configure the drift metrics router.

    Args:
        detector: Optional DriftDetector instance to use

    Returns:
        Configured APIRouter
    """
    if detector:
        set_drift_detector(detector)
    return router


# ---------------------------------------------------------------------------
# WebSocket drift stream (requires starlette WebSocket support)
# ---------------------------------------------------------------------------

import asyncio
import json
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

# Connected WebSocket clients
_ws_clients: Set[WebSocket] = set()

# Async queue used by the broadcast hook to pass events to the WS loop
_ws_event_queue: asyncio.Queue = asyncio.Queue()


def _ws_enqueue_event(payload: Dict[str, Any]) -> None:
    """Synchronous hook registered with DriftResponder to enqueue WS events."""
    try:
        _ws_event_queue.put_nowait(payload)
    except asyncio.QueueFull:
        logger.warning("[DriftStream] WS event queue full — dropping event")


async def _ws_broadcast_loop() -> None:
    """Background task: dequeue events and broadcast to all WS clients."""
    while True:
        payload = await _ws_event_queue.get()
        disconnected: Set[WebSocket] = set()
        for ws in list(_ws_clients):
            try:
                await ws.send_text(json.dumps(payload))
            except Exception:  # noqa: BLE001
                disconnected.add(ws)
        _ws_clients.difference_update(disconnected)
        _ws_event_queue.task_done()


@router.websocket("/stream")
async def drift_stream(websocket: WebSocket) -> None:
    """WebSocket endpoint: stream real-time drift events to connected clients.

    Connect to ws://<host>/api/drift/stream to receive JSON events pushed
    by the DriftResponder whenever a runbook action of type ``notify`` fires.

    Event shape::

        {
          "event_type": "drift_warning",
          "agent_id": "...",
          "metric_name": "...",
          "drift_level": "warning",
          "deviation": 2.7,
          "description": "...",
          "timestamp": "2026-..."
        }

    DLP: drift_stream_v1
    """
    await websocket.accept()
    _ws_clients.add(websocket)
    logger.info("[DriftStream] Client connected (%d total)", len(_ws_clients))
    try:
        # Register the broadcast hook with the responder (idempotent)
        try:
            from src.agents.drift_responder import register_ws_broadcast_hook
            register_ws_broadcast_hook(_ws_enqueue_event)
        except ImportError:
            pass
        # Keep connection alive; receive loop also handles client disconnects
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    finally:
        _ws_clients.discard(websocket)
        logger.info("[DriftStream] Client disconnected (%d remaining)", len(_ws_clients))


async def start_ws_broadcast_loop() -> None:
    """Start the background WS broadcast loop.

    Call this once from the FastAPI lifespan or startup event::

        @app.on_event("startup")
        async def startup():
            asyncio.create_task(start_ws_broadcast_loop())
    """
    asyncio.create_task(_ws_broadcast_loop())
