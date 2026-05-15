"""Regression tests for Playground session auth and ownership gates."""

import os
import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from tests._slowapi_stub import install_slowapi_stub


os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-playground-auth")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-playground-auth")
install_slowapi_stub()

from src.middleware.fastapi_security import generate_csrf_token  # noqa: E402
from src.playground import api as playground_api  # noqa: E402
from src.playground.limiter import get_rate_limiter  # noqa: E402
from src.playground.models import ExecutionStatusResponse  # noqa: E402
from src.playground.storage import SessionStore  # noqa: E402


class _QueueStub:
    queue = None
    runner = object()

    async def enqueue(self, session_id, code, language, stdin, background_tasks):
        return "task-test"

    def get_status(self, session_id, task_id):
        return ExecutionStatusResponse(
            task_id=task_id,
            session_id=session_id,
            status="pending",
        )


@pytest.fixture(autouse=True)
def isolate_playground_state(monkeypatch):
    test_store = SessionStore()
    monkeypatch.setattr(playground_api, "store", test_store)
    monkeypatch.setattr(playground_api, "rate_limiter", get_rate_limiter(test_store))
    monkeypatch.setattr(playground_api, "queue", _QueueStub())


@pytest.fixture(name="client")
def client_fixture():
    app = FastAPI()
    app.include_router(playground_api.router)
    return TestClient(app)


def _auth_header(session_id="owner-session"):
    token = generate_csrf_token(session_id)
    return {"Authorization": f"Bearer {token}"}


def _session_payload():
    return {
        "language": "python",
        "metadata": {"purpose": "auth-test"},
        "seed_code": "print('ready')",
    }


def _execute_payload(session_id):
    return {
        "session_id": session_id,
        "code": "print('hello')",
        "language": "python",
    }


def _share_payload(session_id):
    return {
        "session_id": session_id,
        "code": "print('shared')",
        "language": "python",
    }


@pytest.mark.api
@pytest.mark.security
def test_playground_sensitive_http_routes_reject_missing_token(client):
    checks = unittest.TestCase()

    requests = (
        ("post", "/playground/session", {"json": _session_payload()}),
        ("post", "/playground/execute", {"json": _execute_payload("session-a")}),
        ("post", "/playground/share", {"json": _share_payload("session-a")}),
        ("get", "/playground/results/session-a", {"params": {"task_id": "task-test"}}),
    )

    for method, url, kwargs in requests:
        response = getattr(client, method)(url, **kwargs)
        checks.assertIn(response.status_code, (401, 403))


@pytest.mark.api
@pytest.mark.security
def test_playground_sensitive_http_routes_accept_owner_token(client):
    checks = unittest.TestCase()
    headers = _auth_header("owner-a")

    session_response = client.post("/playground/session", json=_session_payload(), headers=headers)
    checks.assertEqual(session_response.status_code, 200)
    session_id = session_response.json()["session_id"]

    execute_response = client.post(
        "/playground/execute",
        json=_execute_payload(session_id),
        headers=headers,
    )
    checks.assertEqual(execute_response.status_code, 200)
    checks.assertEqual(execute_response.json()["session_id"], session_id)

    results_response = client.get(
        f"/playground/results/{session_id}",
        params={"task_id": "task-test"},
        headers=headers,
    )
    checks.assertEqual(results_response.status_code, 200)

    share_response = client.post(
        "/playground/share",
        json=_share_payload(session_id),
        headers=headers,
    )
    checks.assertEqual(share_response.status_code, 200)
    checks.assertEqual(share_response.json()["session_id"], session_id)


@pytest.mark.api
@pytest.mark.security
def test_playground_session_owner_is_enforced(client):
    checks = unittest.TestCase()
    owner_headers = _auth_header("owner-a")
    other_headers = _auth_header("owner-b")

    session_response = client.post("/playground/session", json=_session_payload(), headers=owner_headers)
    checks.assertEqual(session_response.status_code, 200)
    session_id = session_response.json()["session_id"]

    blocked_requests = (
        ("post", "/playground/execute", {"json": _execute_payload(session_id), "headers": other_headers}),
        ("post", "/playground/share", {"json": _share_payload(session_id), "headers": other_headers}),
        (
            "get",
            f"/playground/results/{session_id}",
            {"params": {"task_id": "task-test"}, "headers": other_headers},
        ),
    )

    for method, url, kwargs in blocked_requests:
        response = getattr(client, method)(url, **kwargs)
        checks.assertEqual(response.status_code, 403)


@pytest.mark.api
@pytest.mark.security
def test_playground_websocket_requires_owner_token(client, monkeypatch):
    checks = unittest.TestCase()
    owner_headers = _auth_header("owner-a")
    other_headers = _auth_header("owner-b")

    session_response = client.post("/playground/session", json=_session_payload(), headers=owner_headers)
    checks.assertEqual(session_response.status_code, 200)
    session_id = session_response.json()["session_id"]

    with checks.assertRaises(WebSocketDisconnect):
        with client.websocket_connect(f"/playground/ws/{session_id}"):
            pass

    with checks.assertRaises(WebSocketDisconnect):
        with client.websocket_connect(f"/playground/ws/{session_id}", headers=other_headers):
            pass

    async def _stream_events(requested_session_id):
        yield {
            "event": "authorized",
            "session_id": requested_session_id,
            "payload": {},
        }

    monkeypatch.setattr(playground_api.store, "stream_events", _stream_events)

    with client.websocket_connect(f"/playground/ws/{session_id}", headers=owner_headers) as websocket:
        message = websocket.receive_json()

    checks.assertEqual(message["event"], "authorized")
    checks.assertEqual(message["session_id"], session_id)
