"""Tests for the QGIA Forecast API endpoints.

DLP: qgia_api_tests_v1
Anchors: T1:TEST_QGIA, SRB:L1_QGIA
"""

import pytest
from fastapi.testclient import TestClient

import os

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-qgia-api")


def _auth_headers() -> dict[str, str]:
    from src.middleware.fastapi_security import generate_csrf_token

    token = generate_csrf_token("qgia-api-test-session")
    return {"Authorization": f"Bearer {token}", "X-CSRF-Token": token}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """Import the FastAPI app and return a test client.

    Importing inside the fixture avoids side-effects at collection time.
    """
    try:
        from api.aurora_api import app
        return TestClient(app, raise_server_exceptions=True)
    except ImportError:
        pytest.skip("aurora_api not importable — skipping QGIA API tests")


@pytest.fixture(scope="module")
def forecast_payload():
    """Minimal valid POST /qgia/forecast payload."""
    return {
        "scenario_id": "TEST-001",
        "title": "Test Scenario",
        "description": "A minimal test scenario for unit-level API validation.",
        "region": "Test Region",
        "domain": "political",
        "evidence_fragments": [
            {
                "source": "Unit Test Source",
                "content": "Placeholder evidence fragment for testing.",
                "reliability": 0.7,
                "recency": 0.8,
            }
        ],
        "requesting_node": "L1_QGIA_TEST",
    }


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_qgia_health(client):
    """GET /qgia/health should return 200 with status=healthy."""
    resp = client.get("/qgia/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "agent_count" in data
    assert data["agent_count"] > 0
    assert "edge_count" in data
    assert "context_tag" in data


# ---------------------------------------------------------------------------
# POST /qgia/forecast
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_run_forecast_returns_201(client, forecast_payload):
    """POST /qgia/forecast should return 201 and a valid ForecastOutput."""
    resp = client.post("/qgia/forecast", json=forecast_payload, headers=_auth_headers())
    assert resp.status_code == 201
    data = resp.json()
    assert "forecast_id" in data
    assert data["forecast_id"].startswith("QSFE-")
    assert data["scenario_id"] == "TEST-001"
    assert "tier_assessments" in data
    assert isinstance(data["tier_assessments"], list)
    assert len(data["tier_assessments"]) > 0


@pytest.mark.api
@pytest.mark.unit
def test_run_forecast_missing_evidence_rejected(client):
    """POST /qgia/forecast with empty evidence_fragments should return 422."""
    payload = {
        "scenario_id": "TEST-BAD",
        "title": "Invalid",
        "description": "No evidence.",
        "region": "Nowhere",
        "domain": "military",
        "evidence_fragments": [],
    }
    resp = client.post("/qgia/forecast", json=payload, headers=_auth_headers())
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /qgia/forecast (list)
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_list_forecasts(client, forecast_payload):
    """GET /qgia/forecast should return a list."""
    # Ensure at least one forecast exists
    client.post("/qgia/forecast", json=forecast_payload, headers=_auth_headers())
    resp = client.get("/qgia/forecast")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.api
@pytest.mark.unit
def test_list_forecasts_filter_by_scenario_id(client, forecast_payload):
    """GET /qgia/forecast?scenario_id=X should filter results."""
    resp = client.get("/qgia/forecast?scenario_id=TEST-001")
    assert resp.status_code == 200
    data = resp.json()
    for item in data:
        assert item["scenario_id"] == "TEST-001"


# ---------------------------------------------------------------------------
# GET /qgia/forecast/{forecast_id}
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_get_forecast_by_id(client, forecast_payload):
    """GET /qgia/forecast/{id} should return the stored forecast."""
    post_resp = client.post("/qgia/forecast", json=forecast_payload, headers=_auth_headers())
    assert post_resp.status_code == 201
    forecast_id = post_resp.json()["forecast_id"]

    get_resp = client.get(f"/qgia/forecast/{forecast_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["forecast_id"] == forecast_id


@pytest.mark.api
@pytest.mark.unit
def test_get_forecast_not_found(client):
    """GET /qgia/forecast/NONEXISTENT should return 404."""
    resp = client.get("/qgia/forecast/QSFE-NONEXISTENT123")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /qgia/population
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_population_summary(client):
    """GET /qgia/population should return agent counts > 0."""
    resp = client.get("/qgia/population")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_agents"] > 0
    assert "division_counts" in data
    assert "grade_distribution" in data
    assert "archetype_distribution" in data


# ---------------------------------------------------------------------------
# GET /qgia/network
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_network_summary(client):
    """GET /qgia/network should return edge stats."""
    resp = client.get("/qgia/network")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_edges"] > 0
    assert "avg_out_degree" in data
    assert "edge_type_counts" in data


# ---------------------------------------------------------------------------
# GET /qgia/scenarios/examples
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.unit
def test_example_scenarios_list(client):
    """GET /qgia/scenarios/examples should return at least 4 templates."""
    resp = client.get("/qgia/scenarios/examples")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 4
    assert len(data["scenarios"]) == data["count"]
    for s in data["scenarios"]:
        assert "scenario_id" in s
        assert "title" in s
        assert "evidence_fragment_count" in s


# ---------------------------------------------------------------------------
# POST /qgia/forecast/example/{scenario_name}
# ---------------------------------------------------------------------------

@pytest.mark.api
@pytest.mark.integration
def test_run_example_forecast(client):
    """POST /qgia/forecast/example/iran should return 201."""
    resp = client.post("/qgia/forecast/example/iran", headers=_auth_headers())
    assert resp.status_code == 201
    data = resp.json()
    assert data["forecast_id"].startswith("QSFE-")


@pytest.mark.api
@pytest.mark.unit
def test_run_example_forecast_not_found(client):
    """POST /qgia/forecast/example/nonexistent should return 404."""
    resp = client.post("/qgia/forecast/example/nonexistent_scenario_xyz", headers=_auth_headers())
    assert resp.status_code == 404
