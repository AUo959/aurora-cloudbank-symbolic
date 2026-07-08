"""Regression tests for CloudHub console entrypoint routing."""

import os

from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-cloudhub-console")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-cloudhub-console")

from api.aurora_gui_cloudhub_fastapi import app  # noqa: E402


def _client() -> TestClient:
    return TestClient(app)


def test_root_route_serves_simulation_console() -> None:
    response = _client().get("/")

    assert response.status_code == 200
    assert "Aurora Simulation Console" in response.text
    assert 'role="tab"' in response.text
    assert 'id="tab-simulation"' in response.text
    assert 'id="tab-deployment"' in response.text
    assert "Aurora Quantum VSA Playground" not in response.text


def test_simulation_console_alias_serves_same_surface() -> None:
    response = _client().get("/simulation-console")

    assert response.status_code == 200
    assert "Aurora Simulation Console" in response.text


def test_synergy_dashboard_route_serves_dashboard_ui() -> None:
    response = _client().get("/synergy-dashboard")

    assert response.status_code == 200
    assert "Aurora Component Synergy Dashboard" in response.text
    assert "/static/js/synergy-dashboard.js" in response.text


def test_synergy_dashboard_api_is_mounted() -> None:
    response = _client().get("/api/synergy/health")

    assert response.status_code == 200
    assert response.json()["service"] == "synergy_dashboard_api"


def test_legacy_vsa_route_is_retired() -> None:
    response = _client().get("/legacy/vsa")

    assert response.status_code == 410
    assert "Quantum VSA Playground Retired" in response.text
    assert "/simulation-console" in response.text
