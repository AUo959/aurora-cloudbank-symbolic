"""Regression tests for CloudHub WebSocket authentication."""

import os
import unittest

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-cloudhub-ws")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-cloudhub-ws")

from api.aurora_gui_cloudhub_fastapi import app, connections  # noqa: E402
from src.middleware.fastapi_security import generate_ws_token  # noqa: E402


def _client() -> TestClient:
    connections.clear()
    return TestClient(app)


def test_broadcast_websocket_rejects_missing_token() -> None:
    checks = unittest.TestCase()
    client = _client()

    with checks.assertRaises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/ws"):
            pass

    checks.assertEqual(disconnect.exception.code, 1008)
    checks.assertEqual(connections, [])


def test_broadcast_websocket_rejects_invalid_token() -> None:
    checks = unittest.TestCase()
    client = _client()

    with checks.assertRaises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/ws?token=invalid"):
            pass

    checks.assertEqual(disconnect.exception.code, 1008)
    checks.assertEqual(connections, [])


def test_broadcast_websocket_accepts_valid_query_token() -> None:
    client = _client()
    token = generate_ws_token("cloudhub-client")

    with client.websocket_connect(f"/ws?token={token}"):
        assert len(connections) == 1

    assert connections == []


def test_collaboration_websocket_rejects_missing_token() -> None:
    checks = unittest.TestCase()
    client = _client()

    with checks.assertRaises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/api/ws/collaboration"):
            pass

    checks.assertEqual(disconnect.exception.code, 1008)
    checks.assertEqual(connections, [])


def test_collaboration_websocket_rejects_invalid_token() -> None:
    checks = unittest.TestCase()
    client = _client()

    with checks.assertRaises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect("/api/ws/collaboration?token=invalid"):
            pass

    checks.assertEqual(disconnect.exception.code, 1008)
    checks.assertEqual(connections, [])


def test_collaboration_websocket_accepts_valid_authorization_header() -> None:
    client = _client()
    token = generate_ws_token("cloudhub-collaboration-client")

    with client.websocket_connect(
        "/api/ws/collaboration",
        headers={"Authorization": f"Bearer {token}"},
    ) as websocket:
        message = websocket.receive_json()

    assert message["type"] == "welcome"
    assert message["client_id"] == "cloudhub-collaboration-client"
    assert connections == []
