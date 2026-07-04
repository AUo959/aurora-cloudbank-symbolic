"""Tests for the read-only L1 Station API (src/api/l1_station_api.py).

Covers the first implemented slice of the config/l1_endpoints.yaml contract:
- GET /api/aurora/health/l1
- GET /api/aurora/simulation/state

The router is mounted on a dedicated app instance here so the unit tests do
not depend on the full aurora_api app assembly. Both endpoints are GET
(CSRF-exempt) and back onto .aurora/SIMULATION_STATE.json.
"""

import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.l1_station_api import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)
case = unittest.TestCase()


@pytest.mark.unit
@pytest.mark.api
def test_l1_health_endpoint():
    resp = client.get("/api/aurora/health/l1")
    case.assertEqual(resp.status_code, 200)
    data = resp.json()
    case.assertEqual(data["layer"], "L1")
    case.assertIn(data["status"], ("operational", "degraded"))
    case.assertIn(data["state_file"], ("loaded", "missing", "invalid"))
    case.assertIn("timestamp", data)
    # With the canonical state present, the layer should be operational.
    if data["state_file"] == "loaded":
        case.assertEqual(data["status"], "operational")
        case.assertIsNotNone(data["simulation_status"])
        case.assertIsNotNone(data["station_name"])


@pytest.mark.unit
@pytest.mark.api
def test_l1_simulation_state_endpoint():
    resp = client.get("/api/aurora/simulation/state")
    case.assertEqual(resp.status_code, 200)
    data = resp.json()
    case.assertIn(data["state_file"], ("loaded", "missing", "invalid"))
    if data["state_file"] == "loaded":
        case.assertEqual(data["status"], "success")
        case.assertIsInstance(data["state"], dict)
        case.assertIn("simulation", data["state"])


@pytest.mark.unit
@pytest.mark.api
def test_l1_state_is_read_only():
    """Two reads return the same state — the endpoint never mutates it."""
    first = client.get("/api/aurora/simulation/state").json()
    second = client.get("/api/aurora/simulation/state").json()
    case.assertEqual(first, second)
