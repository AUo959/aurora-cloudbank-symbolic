import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from modules.resilience_sentinel import api as sentinel_api
from src.middleware.fastapi_security import generate_ws_token


class _FakeSentinelEngine:
    collection_interval = 60

    def get_dashboard_data(self):
        return {
            "health": {"timestamp": 123.0},
            "metrics": {},
            "alerts": {},
            "recent_alerts": [],
            "system": {},
        }

    def collect_metrics(self):
        return []

    def evaluate_alerts(self, metrics):
        return []


def _build_client(monkeypatch):
    monkeypatch.setattr(sentinel_api, "get_monitoring_engine", lambda: _FakeSentinelEngine())
    app = FastAPI()
    app.include_router(sentinel_api.router)
    return TestClient(app)


def test_metrics_websocket_rejects_missing_token(monkeypatch):
    checks = unittest.TestCase()
    client = _build_client(monkeypatch)

    with checks.assertRaises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/sentinel/ws/metrics"):
            pass

    checks.assertEqual(disconnect.exception.code, 1008)


def test_metrics_websocket_rejects_invalid_token(monkeypatch):
    checks = unittest.TestCase()
    client = _build_client(monkeypatch)

    with checks.assertRaises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/sentinel/ws/metrics?token=invalid"):
            pass

    checks.assertEqual(disconnect.exception.code, 1008)


def test_metrics_websocket_accepts_valid_query_token(monkeypatch):
    checks = unittest.TestCase()
    client = _build_client(monkeypatch)
    token = generate_ws_token("sentinel-client")

    with client.websocket_connect(f"/sentinel/ws/metrics?token={token}") as websocket:
        message = websocket.receive_json()

    checks.assertEqual(message["type"], "dashboard_update")
    checks.assertEqual(message["timestamp"], 123.0)


def test_metrics_websocket_accepts_authorization_header(monkeypatch):
    checks = unittest.TestCase()
    client = _build_client(monkeypatch)
    token = generate_ws_token("sentinel-client")

    with client.websocket_connect(
        "/sentinel/ws/metrics",
        headers={"Authorization": f"Bearer {token}"},
    ) as websocket:
        message = websocket.receive_json()

    checks.assertEqual(message["type"], "dashboard_update")
    checks.assertEqual(message["timestamp"], 123.0)
