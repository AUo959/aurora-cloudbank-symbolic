"""Tests for the read-only L1 Station API (src/api/l1_station_api.py).

Covers the first implemented slice of the config/l1_endpoints.yaml contract:
- GET /api/aurora/health/l1
- GET /api/aurora/simulation/state

The router is mounted on a dedicated app instance here so the unit tests do
not depend on the full aurora_api app assembly. Both endpoints are GET
(CSRF-exempt) and back onto .aurora/SIMULATION_STATE.json.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.l1_station_api import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.mark.unit
@pytest.mark.api
def test_l1_health_endpoint():
    resp = client.get("/api/aurora/health/l1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["layer"] == "L1"
    assert data["status"] in ("operational", "degraded")
    assert data["state_file"] in ("loaded", "missing", "invalid")
    assert "timestamp" in data
    # With the canonical state present, the layer should be operational.
    if data["state_file"] == "loaded":
        assert data["status"] == "operational"
        assert data["simulation_status"] is not None
        assert data["station_name"] is not None


@pytest.mark.unit
@pytest.mark.api
def test_l1_simulation_state_endpoint():
    resp = client.get("/api/aurora/simulation/state")
    assert resp.status_code == 200
    data = resp.json()
    assert data["state_file"] in ("loaded", "missing", "invalid")
    if data["state_file"] == "loaded":
        assert data["status"] == "success"
        assert isinstance(data["state"], dict)
        assert "simulation" in data["state"]


@pytest.mark.unit
@pytest.mark.api
def test_l1_state_is_read_only():
    """Two reads return the same state — the endpoint never mutates it."""
    first = client.get("/api/aurora/simulation/state").json()
    second = client.get("/api/aurora/simulation/state").json()
    assert first == second
