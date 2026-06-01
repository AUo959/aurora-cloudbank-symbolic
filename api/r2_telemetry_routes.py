"""
FastAPI routes for R-2 agent telemetry monitoring

Provides HTTP endpoints for:
- Prometheus metrics export
- Real-time telemetry dashboards
- Anomaly alerts
- Health status checks
"""

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse

from src.middleware.fastapi_security import require_csrf_token

try:
    from src.observability import get_r2_telemetry
except ImportError:
    # Fallback for testing
    from observability import get_r2_telemetry


router = APIRouter(
    prefix="/r2-telemetry",
    tags=["R-2 Agent Telemetry"],
    dependencies=[Depends(require_csrf_token)],
)


@router.get("/metrics", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """
    Export R-2 agent metrics in Prometheus format

    This endpoint is designed to be scraped by Prometheus for monitoring.
    Returns metrics in the Prometheus text exposition format.
    """
    telemetry = get_r2_telemetry()
    return telemetry.export_prometheus_metrics()


@router.get("/summary")
async def get_metrics_summary(
    time_window: Optional[int] = Query(
        default=3600,
        description="Time window in seconds to summarize metrics"
    ),
    context_tag: Optional[str] = Query(
        default=None,
        description="DLP context tag for lineage tracking"
    )
) -> Dict[str, Any]:
    """
    Get comprehensive metrics summary for R-2 agent operations

    Args:
        time_window: Time window in seconds (default: 3600 = 1 hour)
        context_tag: Optional DLP context tag

    Returns:
        Summary with counts, success rates, and performance metrics
    """
    telemetry = get_r2_telemetry()
    summary = telemetry.get_metrics_summary(
        time_window_seconds=time_window,
        context_tag=context_tag
    )
    return summary


@router.get("/operations/recent")
async def get_recent_operations(
    limit: int = Query(default=10, ge=1, le=100, description="Max operations to return"),
    operation_type: Optional[str] = Query(default=None, description="Filter by operation type"),
    failures_only: bool = Query(default=False, description="Only return failed operations")
) -> List[Dict[str, Any]]:
    """
    Get recent R-2 agent operations

    Args:
        limit: Maximum number of operations to return
        operation_type: Filter by specific operation type
        failures_only: Only return failed operations

    Returns:
        List of operation metrics
    """
    telemetry = get_r2_telemetry()
    operations = telemetry.get_recent_operations(
        limit=limit,
        operation_type=operation_type,
        include_failures_only=failures_only
    )

    return [asdict(op) for op in operations]


@router.get("/health")
async def get_telemetry_health() -> Dict[str, Any]:
    """
    Get R-2 agent telemetry system health status

    Returns:
        Health status with system information
    """
    telemetry = get_r2_telemetry()

    # Get recent metrics summary
    summary = telemetry.get_metrics_summary(time_window_seconds=300)  # Last 5 minutes

    # Determine health status
    success_rate = summary.get("success_rate", 0)
    anomaly_count = summary.get("anomaly_count", 0)

    if success_rate >= 0.95 and anomaly_count == 0:
        status = "healthy"
    elif success_rate >= 0.80:
        status = "degraded"
    else:
        status = "unhealthy"

    return {
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "telemetry_enabled": telemetry.enabled,
        "service_name": telemetry.service_name,
        "recent_metrics": {
            "success_rate": success_rate,
            "total_operations": summary.get("total_operations", 0),
            "anomaly_count": anomaly_count,
            "average_duration_ms": summary.get("average_duration_ms", 0)
        }
    }


@router.get("/anomalies")
async def get_detected_anomalies(
    limit: int = Query(default=20, ge=1, le=100, description="Max anomalies to return")
) -> List[Dict[str, Any]]:
    """
    Get recently detected anomalies in R-2 agent operations

    Args:
        limit: Maximum number of anomalies to return

    Returns:
        List of detected anomalies with details
    """
    telemetry = get_r2_telemetry()

    # Use public method to get anomalies
    anomalies = telemetry.get_recent_anomalies(limit=limit)

    return [asdict(anomaly) for anomaly in anomalies]


@router.get("/operations/types")
async def get_operation_types() -> Dict[str, Any]:
    """
    Get list of all tracked operation types with statistics

    Returns:
        Dictionary of operation types with their statistics
    """
    telemetry = get_r2_telemetry()
    summary = telemetry.get_metrics_summary()

    operations_by_type = summary.get("operations_by_type", {})

    return {
        "total_types": len(operations_by_type),
        "operations": operations_by_type
    }


@router.post("/test-operation")
async def test_telemetry_operation(
    operation_type: str = Query(default="test", description="Type of test operation"),
    should_fail: bool = Query(default=False, description="Whether to simulate failure")
) -> Dict[str, Any]:
    """
    Test endpoint to generate sample telemetry data

    Args:
        operation_type: Type of operation to simulate
        should_fail: Whether to simulate a failure

    Returns:
        Test operation result
    """
    import time

    telemetry = get_r2_telemetry()

    with telemetry.trace_agent_operation(
        operation_type=operation_type,
        context_tag=f"test_operation_{int(time.time())}",
        symbolic_anchor="T1:TEST",
        test_mode=True
    ) as metrics:
        # Simulate work
        time.sleep(0.1)

        # Add some metadata
        metrics.decisions_made = 3
        metrics.tools_invoked = ["test_tool_1", "test_tool_2"]

        if should_fail:
            raise ValueError("Simulated test failure")

    return {
        "success": True,
        "message": "Test operation completed successfully",
        "operation_id": metrics.operation_id,
        "correlation_id": metrics.correlation_id
    }
