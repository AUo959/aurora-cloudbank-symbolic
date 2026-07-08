"""Regression tests for CloudHub console entrypoint routing."""

import os
import unittest

from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-cloudhub-console")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-cloudhub-console")

from api.aurora_gui_cloudhub_fastapi import app  # noqa: E402


def _client() -> TestClient:
    return TestClient(app)


def test_root_route_serves_simulation_console() -> None:
    checks = unittest.TestCase()
    response = _client().get("/")

    checks.assertEqual(response.status_code, 200)
    checks.assertIn("Aurora Simulation Console", response.text)
    checks.assertIn('role="tab"', response.text)
    checks.assertIn('id="tab-simulation"', response.text)
    checks.assertIn('id="tab-deployment"', response.text)
    checks.assertNotIn("Aurora Quantum VSA Playground", response.text)


def test_simulation_console_alias_serves_same_surface() -> None:
    checks = unittest.TestCase()
    response = _client().get("/simulation-console")

    checks.assertEqual(response.status_code, 200)
    checks.assertIn("Aurora Simulation Console", response.text)


def test_synergy_dashboard_route_serves_dashboard_ui() -> None:
    checks = unittest.TestCase()
    response = _client().get("/synergy-dashboard")

    checks.assertEqual(response.status_code, 200)
    checks.assertIn("Aurora Component Synergy Dashboard", response.text)
    checks.assertIn("/static/js/synergy-dashboard.js", response.text)


def test_synergy_dashboard_api_is_mounted() -> None:
    checks = unittest.TestCase()
    response = _client().get("/api/synergy/health")

    checks.assertEqual(response.status_code, 200)
    checks.assertEqual(response.json()["service"], "synergy_dashboard_api")


def test_legacy_vsa_route_is_retired() -> None:
    checks = unittest.TestCase()
    response = _client().get("/legacy/vsa")

    checks.assertEqual(response.status_code, 410)
    checks.assertIn("Quantum VSA Playground Retired", response.text)
    checks.assertIn("/simulation-console", response.text)
