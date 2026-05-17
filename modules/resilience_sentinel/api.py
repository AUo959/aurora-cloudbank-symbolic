"""
Resilience Sentinel Dashboard API

FastAPI endpoints for monitoring, metrics, alerts, and health status.
Provides REST API and WebSocket streaming for real-time dashboard updates.

Anchor: T1-RSD-002
"""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from src.middleware.fastapi_security import require_csrf_token, verify_ws_token

from .alert_manager import AlertSeverity
from .monitoring_engine import MonitoringEngine

# Pydantic models for API requests/responses


class MetricResponse(BaseModel):
    """Single metric response."""
    name: str
    type: str
    value: float
    timestamp: float
    datetime: str
    unit: str
    tags: Dict[str, str]


class MetricStatsResponse(BaseModel):
    """Metric statistics response."""
    metric_name: str
    count: int
    latest: Optional[float]
    average: Optional[float]
    min: Optional[float]
    max: Optional[float]
    trend: str
    timestamp: Optional[float]


class HealthCheckResponse(BaseModel):
    """Individual health check response."""
    name: str
    status: str
    value: float
    threshold: float
    message: str
    timestamp: float


class HealthResponse(BaseModel):
    """Overall health report response."""
    status: str
    timestamp: float
    checks: List[HealthCheckResponse]
    alerts: Dict[str, int]


class AlertResponse(BaseModel):
    """Alert response model."""
    id: str
    severity: str
    title: str
    message: str
    metric_name: str
    metric_value: float
    threshold: float
    timestamp: float
    datetime: str
    tags: Dict[str, str]
    acknowledged: bool
    resolved: bool
    acknowledged_at: Optional[float]
    resolved_at: Optional[float]


class AlertRuleRequest(BaseModel):
    """Request to create/update alert rule."""
    name: str
    metric_name: str
    condition: str = Field(..., pattern="^(>|<|>=|<=|==|!=)$")
    threshold: float
    severity: str
    message_template: str
    cooldown_seconds: int = 300
    enabled: bool = True
    tags: Dict[str, str] = {}


class AlertAckRequest(BaseModel):
    """Request to acknowledge/resolve alert."""
    alert_id: str


class DashboardResponse(BaseModel):
    """Comprehensive dashboard data."""
    health: HealthResponse
    metrics: Dict[str, Any]
    alerts: Dict[str, Any]
    recent_alerts: List[AlertResponse]
    system: Dict[str, Any]


# Global monitoring engine instance
_monitoring_engine: Optional[MonitoringEngine] = None


def get_monitoring_engine() -> MonitoringEngine:
    """Get or create monitoring engine singleton."""
    global _monitoring_engine
    if _monitoring_engine is None:
        _monitoring_engine = MonitoringEngine(
            collection_interval=60,
            history_size=1000,
            enable_default_rules=True,
        )
    return _monitoring_engine


# Create API router
router = APIRouter(prefix="/sentinel", tags=["monitoring", "resilience"])
SENTINEL_MUTATION_DEPENDENCIES = [Depends(require_csrf_token)]


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Get comprehensive health report.

    Returns overall system health status with individual checks for CPU,
    memory, and disk usage, plus active alert counts.
    """
    engine = get_monitoring_engine()
    report = engine.get_health_report()

    return HealthResponse(
        status=report["status"],
        timestamp=report["timestamp"],
        checks=[HealthCheckResponse(**check) for check in report["checks"]],
        alerts=report["alerts"],
    )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics_summary():
    """
    Get summary of all collected metrics.

    Returns metric names, data point counts, collection info, and stats
    for key system metrics (CPU, memory, disk).
    """
    engine = get_monitoring_engine()
    return engine.get_metrics_summary()


@router.get("/metrics/{metric_name}", response_model=MetricStatsResponse)
async def get_metric_stats(metric_name: str):
    """
    Get detailed statistics for a specific metric.

    Args:
        metric_name: Name of metric to query

    Returns:
        Statistics including avg, min, max, trend, latest value
    """
    engine = get_monitoring_engine()
    stats = engine.history.get_stats(metric_name)

    if "error" in stats:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")

    return MetricStatsResponse(**stats)


@router.get("/metrics/{metric_name}/history", response_model=List[MetricResponse])
async def get_metric_history(
    metric_name: str,
    count: int = Query(100, ge=1, le=1000, description="Number of recent values"),
):
    """
    Get historical values for a metric.

    Args:
        metric_name: Name of metric to query
        count: Number of recent values to return (1-1000)

    Returns:
        List of recent metric values
    """
    engine = get_monitoring_engine()
    history = engine.history.get_recent(metric_name, count)

    if not history:
        raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")

    return [MetricResponse(**metric.to_dict()) for metric in history]


@router.post("/metrics/collect")
async def trigger_collection():
    """
    Manually trigger metric collection.

    Useful for testing or forcing immediate data refresh.

    Returns:
        Collection results with metrics collected and alerts triggered
    """
    engine = get_monitoring_engine()

    # Collect metrics
    metrics = engine.collect_metrics()

    # Evaluate alerts
    alerts = engine.evaluate_alerts(metrics)

    return {
        "success": True,
        "metrics_collected": len(metrics),
        "alerts_triggered": len(alerts),
        "metrics": [m.to_dict() for m in metrics],
        "alerts": [a.to_dict() for a in alerts],
    }


@router.get("/alerts", response_model=Dict[str, Any])
async def get_alerts(
    active_only: bool = Query(True, description="Filter to active alerts only"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
):
    """
    Get alerts with optional filtering.

    Args:
        active_only: Only return unresolved alerts
        severity: Filter by severity (info/warning/error/critical)

    Returns:
        Alert list and statistics
    """
    engine = get_monitoring_engine()

    if severity:
        try:
            sev = AlertSeverity(severity.lower())
            alerts = engine.alert_manager.get_active_alerts(sev)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
    elif active_only:
        alerts = engine.alert_manager.get_active_alerts()
    else:
        alerts = engine.alert_manager.alerts

    return {
        "alerts": [AlertResponse(**a.to_dict()) for a in alerts],
        "count": len(alerts),
        "stats": engine.alert_manager.get_alert_stats(),
    }


@router.post("/alerts/acknowledge", dependencies=SENTINEL_MUTATION_DEPENDENCIES)
async def acknowledge_alert(request: AlertAckRequest):
    """
    Acknowledge an alert.

    Args:
        request: Alert acknowledgment request with alert_id

    Returns:
        Success status
    """
    engine = get_monitoring_engine()
    success = engine.alert_manager.acknowledge_alert(request.alert_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Alert '{request.alert_id}' not found")

    return {"success": True, "message": f"Alert {request.alert_id} acknowledged"}


@router.post("/alerts/resolve", dependencies=SENTINEL_MUTATION_DEPENDENCIES)
async def resolve_alert(request: AlertAckRequest):
    """
    Resolve an alert.

    Args:
        request: Alert resolution request with alert_id

    Returns:
        Success status
    """
    engine = get_monitoring_engine()
    success = engine.alert_manager.resolve_alert(request.alert_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Alert '{request.alert_id}' not found")

    return {"success": True, "message": f"Alert {request.alert_id} resolved"}


@router.get("/alerts/rules", response_model=List[Dict[str, Any]])
async def get_alert_rules():
    """Get all configured alert rules."""
    engine = get_monitoring_engine()
    rules = engine.alert_manager.get_all_rules()
    return [rule.to_dict() for rule in rules]


@router.post("/alerts/rules", dependencies=SENTINEL_MUTATION_DEPENDENCIES)
async def create_alert_rule(rule_request: AlertRuleRequest):
    """
    Create a new alert rule.

    Args:
        rule_request: Alert rule configuration

    Returns:
        Created rule details
    """
    from .alert_manager import AlertRule, AlertSeverity

    engine = get_monitoring_engine()

    # Convert severity string to enum
    try:
        severity = AlertSeverity(rule_request.severity.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid severity: {rule_request.severity}")

    # Create rule
    rule = AlertRule(
        name=rule_request.name,
        metric_name=rule_request.metric_name,
        condition=rule_request.condition,
        threshold=rule_request.threshold,
        severity=severity,
        message_template=rule_request.message_template,
        cooldown_seconds=rule_request.cooldown_seconds,
        enabled=rule_request.enabled,
        tags=rule_request.tags,
    )

    engine.add_alert_rule(rule)

    return {"success": True, "rule": rule.to_dict()}


@router.delete("/alerts/rules/{rule_name}", dependencies=SENTINEL_MUTATION_DEPENDENCIES)
async def delete_alert_rule(rule_name: str):
    """Delete an alert rule."""
    engine = get_monitoring_engine()
    success = engine.alert_manager.remove_rule(rule_name)

    if not success:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found")

    return {"success": True, "message": f"Rule '{rule_name}' deleted"}


@router.get("/notifications/status")
async def get_notification_status():
    """
    Get notification system status.

    Returns enabled channels, configuration, and recent notification history.
    """
    engine = get_monitoring_engine()
    return engine.get_notification_status()


@router.get("/notifications/channels")
async def list_notification_channels():
    """
    List all registered notification channels.

    Returns channel names, types, and status.
    """
    engine = get_monitoring_engine()
    router_inst = engine.get_notification_router()

    if not router_inst:
        return {"enabled": False, "channels": []}

    return {
        "enabled": True,
        "channels": router_inst.list_channels(),
        "status": router_inst.get_channel_status(),
    }


@router.get("/notifications/history")
async def get_notification_history(
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
):
    """
    Get notification history.

    Args:
        limit: Number of recent notifications to return (1-1000)

    Returns:
        List of notification records with alert ID, channel, success status
    """
    engine = get_monitoring_engine()
    router_inst = engine.get_notification_router()

    if not router_inst:
        return {"enabled": False, "history": []}

    return {
        "enabled": True,
        "history": router_inst.get_notification_history(limit=limit),
    }


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    """
    Get comprehensive dashboard data.

    Returns health, metrics, alerts, and system info in single response.
    Ideal for dashboard UI that needs all data at once.
    """
    engine = get_monitoring_engine()
    data = engine.get_dashboard_data()

    return DashboardResponse(
        health=HealthResponse(
            status=data["health"]["status"],
            timestamp=data["health"]["timestamp"],
            checks=[HealthCheckResponse(**c) for c in data["health"]["checks"]],
            alerts=data["health"]["alerts"],
        ),
        metrics=data["metrics"],
        alerts=data["alerts"],
        recent_alerts=[AlertResponse(**a) for a in data["recent_alerts"]],
        system=data["system"],
    )


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for live metric streaming."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove connection."""
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Connection likely closed, will be cleaned up
                pass


manager = ConnectionManager()


def _extract_websocket_token(websocket: WebSocket) -> Optional[str]:
    token = websocket.query_params.get("token")
    if token:
        return token

    authorization = websocket.headers.get("authorization")
    if authorization and authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1].strip()
    return None


async def _authorize_metrics_websocket(websocket: WebSocket) -> Optional[str]:
    token = _extract_websocket_token(websocket)
    client_id = verify_ws_token(token) if token else None
    if not client_id:
        await websocket.close(code=1008, reason="Unauthorized: Invalid or missing token")
        return None
    return client_id


@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """
    WebSocket endpoint for real-time metric streaming.

    Connects clients to receive live metric updates every collection interval.
    Sends dashboard data snapshot periodically.

    Protocol:
        - On connect: Sends current dashboard state
        - Every 60s: Sends updated dashboard data
        - On new alert: Sends alert notification
    """
    client_id = await _authorize_metrics_websocket(websocket)
    if not client_id:
        return

    engine = get_monitoring_engine()
    await manager.connect(websocket)

    try:
        while True:
            # Send current dashboard state
            data = engine.get_dashboard_data()
            await websocket.send_json({
                "type": "dashboard_update",
                "data": data,
                "timestamp": data["health"]["timestamp"],
            })

            # Wait for collection interval
            await asyncio.sleep(engine.collection_interval)

            # Trigger collection and get updates
            metrics = engine.collect_metrics()
            alerts = engine.evaluate_alerts(metrics)

            # Send updates
            if alerts:
                await websocket.send_json({
                    "type": "new_alerts",
                    "alerts": [a.to_dict() for a in alerts],
                    "count": len(alerts),
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
        print(f"WebSocket error: {e}")


# Startup handler to initialize monitoring
async def start_monitoring():
    """Initialize monitoring engine on startup."""
    engine = get_monitoring_engine()
    # Perform initial collection
    engine.collect_metrics()
    return engine


# Optional: Background task for continuous collection
async def background_collection():
    """Background task for continuous metric collection."""
    engine = get_monitoring_engine()

    while True:
        await asyncio.sleep(engine.collection_interval)
        metrics = engine.collect_metrics()
        alerts = engine.evaluate_alerts(metrics)

        # Broadcast to WebSocket clients
        if alerts:
            await manager.broadcast({
                "type": "new_alerts",
                "alerts": [a.to_dict() for a in alerts],
                "count": len(alerts),
            })
