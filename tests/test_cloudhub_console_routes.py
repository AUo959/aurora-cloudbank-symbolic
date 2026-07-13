"""Regression tests for CloudHub console entrypoint routing."""

import os
import unittest

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-cloudhub-console")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-cloudhub-console")

from api.aurora_gui_cloudhub_fastapi import app, html_file_response  # noqa: E402

pytestmark = pytest.mark.unit


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


def test_missing_static_asset_returns_404(tmp_path) -> None:
    checks = unittest.TestCase()

    with checks.assertRaises(HTTPException) as exc_info:
        html_file_response(tmp_path / "missing.html")

    checks.assertEqual(exc_info.exception.status_code, 404)


def test_security_session_is_not_cacheable() -> None:
    checks = unittest.TestCase()
    response = _client().get("/api/security/session")

    checks.assertEqual(response.status_code, 200)
    checks.assertEqual(response.headers["cache-control"], "no-store")
    checks.assertEqual(
        set(response.json()),
        {"session_id", "csrf_token", "ws_token"},
    )
