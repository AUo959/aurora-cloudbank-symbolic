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
    case.assertIn("timestamp", data)
    # The canonical state file ships with this PR, so it must load and the
    # layer must report operational — a broken state-file path is a regression.
    case.assertEqual(data["state_file"], "loaded")
    case.assertEqual(data["status"], "operational")
    case.assertIsNotNone(data["simulation_status"])
    case.assertIsNotNone(data["station_name"])


@pytest.mark.unit
@pytest.mark.api
def test_l1_simulation_state_endpoint():
    resp = client.get("/api/aurora/simulation/state")
    case.assertEqual(resp.status_code, 200)
    data = resp.json()
    # The canonical state file ships with this PR, so it must load.
    case.assertEqual(data["state_file"], "loaded")
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


@pytest.mark.unit
@pytest.mark.api
def test_l1_health_degrades_on_corrupt_state(tmp_path, monkeypatch):
    """A non-UTF8/corrupt state file degrades to invalid, never 5xx."""
    bad = tmp_path / "SIMULATION_STATE.json"
    bad.write_bytes(b"\xff\xfe\x00 not-valid-utf8")
    monkeypatch.setattr("src.api.l1_station_api._STATE_FILE", bad)

    resp = client.get("/api/aurora/health/l1")
    case.assertEqual(resp.status_code, 200)
    data = resp.json()
    case.assertEqual(data["state_file"], "invalid")
    case.assertEqual(data["status"], "degraded")
