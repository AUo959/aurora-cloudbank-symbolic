"""
Integration tests for telemetry activation in FastAPI application
"""

import hashlib
import hmac
import os
import time

import pytest
from fastapi.testclient import TestClient


def _auth_header():
    session_id = "test-session"
    timestamp = str(int(time.time()))
    message = f"{session_id}.{timestamp}"
    signature = hmac.new(
        os.environ["CSRF_SECRET_KEY"].encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    token = f"{session_id}.{timestamp}.{signature}"
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
@pytest.mark.observability
def test_prometheus_metrics_endpoint():
    """Test Prometheus metrics endpoint is accessible"""
    from api.aurora_api import app

    client = TestClient(app)
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")

    # Verify Prometheus format
    content = response.text
    assert "aurora_operations_total" in content or "# HELP" in content


@pytest.mark.integration
@pytest.mark.observability
def test_telemetry_snapshot_endpoint():
    """Test telemetry snapshot endpoint returns structured data"""
    from api.aurora_api import app

    client = TestClient(app)
    response = client.get("/telemetry/snapshot")

    assert response.status_code == 200
    data = response.json()

    # Verify expected structure
    assert "timestamp" in data
    assert "performance_metrics" in data
    assert "adoption_metrics" in data
    assert "error_metrics" in data


@pytest.mark.integration
@pytest.mark.observability
def test_telemetry_snapshot_with_context_tag():
    """Test telemetry snapshot with DLP context tag"""
    from api.aurora_api import app

    client = TestClient(app)
    response = client.get("/telemetry/snapshot?context_tag=test_context_001")

    assert response.status_code == 200
    data = response.json()
    assert data["context_tag"] == "test_context_001"


@pytest.mark.integration
@pytest.mark.observability
def test_r2_telemetry_routes_available():
    """Test R2 telemetry routes are accessible"""
    from api.aurora_api import app

    client = TestClient(app)

    # Test metrics endpoint
    response = client.get("/r2-telemetry/metrics", headers=_auth_header())
    assert response.status_code == 200
    assert "r2_agent" in response.text or "# HELP" in response.text

    # Test health endpoint
    response = client.get("/r2-telemetry/health", headers=_auth_header())
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "telemetry_enabled" in data


@pytest.mark.integration
@pytest.mark.observability
def test_r2_telemetry_summary():
    """Test R2 telemetry summary endpoint"""
    from api.aurora_api import app

    client = TestClient(app)
    response = client.get("/r2-telemetry/summary", headers=_auth_header())

    assert response.status_code == 200
    data = response.json()

    # Verify expected structure
    assert "total_operations" in data
    assert "success_rate" in data


@pytest.mark.integration
@pytest.mark.observability
def test_telemetry_middleware_traces_requests():
    """Test that telemetry middleware automatically traces requests"""
    from api.aurora_api import app
    from src.observability import get_telemetry, reset_telemetry

    # Reset telemetry to start fresh
    reset_telemetry()

    client = TestClient(app)

    # Make a request to health endpoint
    response = client.get("/health")
    assert response.status_code == 200

    # Check that telemetry recorded the operation
    telemetry = get_telemetry()
    snapshot = telemetry.get_metrics_snapshot()

    # Should have at least one operation recorded
    assert len(snapshot.performance_metrics) > 0


@pytest.mark.integration
@pytest.mark.observability
def test_health_endpoint_still_works():
    """Ensure telemetry doesn't break existing health check"""
    from api.aurora_api import app

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


@pytest.mark.integration
@pytest.mark.observability
def test_telemetry_initialized_in_lifespan():
    """Test that telemetry is initialized during app startup"""
    from src.observability import get_telemetry, get_r2_telemetry

    # Telemetry should be initialized
    aurora_telemetry = get_telemetry()
    r2_telemetry = get_r2_telemetry()

    assert aurora_telemetry is not None
    assert r2_telemetry is not None
    # Service names may vary if initialized before lifespan runs
    assert aurora_telemetry.service_name in ["aurora-cloudbank", "aurora-cloudbank-api"]
    assert r2_telemetry.service_name in ["aurora-r2-agent", "r2-agent"]


@pytest.mark.integration
@pytest.mark.observability
def test_r2_middleware_records_span_per_request():
    """R2AgentTelemetry middleware must produce at least one span per non-skip request.

    This is the acceptance-criteria test for issue #769: removing the middleware
    causes this test to fail because no operations are recorded.
    """
    from api.aurora_api import app
    from src.observability import get_r2_telemetry, reset_r2_telemetry

    reset_r2_telemetry()

    client = TestClient(app)
    # /telemetry/snapshot is a real API path (not in _R2_SKIP_PATHS) so the
    # middleware must wrap it and record an operation.
    response = client.get("/telemetry/snapshot")
    assert response.status_code == 200

    r2 = get_r2_telemetry()
    summary = r2.get_metrics_summary()
    # At least one operation must have been recorded by the middleware.
    assert summary.get("total_operations", 0) >= 1, (
        "R2AgentTelemetry middleware did not record any spans — "
        "check that r2_telemetry_middleware is registered in aurora_api.py"
    )


@pytest.mark.integration
@pytest.mark.observability
def test_metrics_endpoint_includes_r2_counters():
    """The /metrics endpoint must expose R2 Prometheus counters after a traced request."""
    from api.aurora_api import app
    from src.observability import reset_r2_telemetry

    reset_r2_telemetry()

    client = TestClient(app)
    # Trigger a span by hitting a real endpoint first
    client.get("/telemetry/snapshot")

    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.text
    # R2 Prometheus counters should appear after at least one span is recorded
    assert "r2_agent_operations_total" in content, (
        "/metrics is not exporting R2AgentTelemetry counters"
    )
