"""Regression tests for auth on event coordination mutation routes."""

import os
import unittest

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-coordination-api")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-coordination-api")

from src.coordination import event_api  # noqa: E402
from src.coordination.event_registry import EventCoordinationRegistry  # noqa: E402
from src.middleware.fastapi_security import generate_csrf_token  # noqa: E402


def _auth_header() -> dict[str, str]:
    token = generate_csrf_token("coordination-test-session")
    return {"Authorization": f"Bearer {token}"}


def _event_payload(source_agent_id: str = "agent-a") -> dict:
    return {
        "event_type": "task.created",
        "priority": "normal",
        "source_agent_id": source_agent_id,
        "payload": {"task_id": "task-1"},
    }


def _subscribe_payload(agent_id: str = "agent-a") -> dict:
    return {
        "agent_id": agent_id,
        "event_types": ["task.created"],
        "priorities": ["normal"],
    }


def _lock_payload(agent_id: str = "agent-a", resource_id: str = "dataset-1") -> dict:
    return {
        "agent_id": agent_id,
        "resource_id": resource_id,
        "resource_type": "dataset",
        "ttl_seconds": 300,
    }


def _conflict_payload(agent_id: str = "agent-b", resource_id: str = "dataset-1") -> dict:
    return {
        "agent_id": agent_id,
        "resource_id": resource_id,
        "resource_type": "dataset",
        "operation": "write",
    }


def _workflow_payload() -> dict:
    return {
        "name": "Coordination Test Workflow",
        "description": "Auth regression workflow",
        "steps": [{"step_id": "step-1", "action": "fetch"}],
        "agent_assignments": {"step-1": "agent-a"},
        "created_by": "agent-a",
    }


@pytest.fixture
def registry(monkeypatch) -> EventCoordinationRegistry:
    registry = EventCoordinationRegistry()
    monkeypatch.setattr(event_api, "get_event_registry", lambda: registry)
    return registry


@pytest.fixture
def client(registry) -> TestClient:
    app = FastAPI()
    app.include_router(event_api.router)
    return TestClient(app)


@pytest.mark.parametrize(
    ("method", "path", "kwargs"),
    [
        ("post", "/api/coordination/events/publish", {"json": _event_payload()}),
        ("post", "/api/coordination/subscriptions/subscribe", {"json": _subscribe_payload()}),
        ("delete", "/api/coordination/subscriptions/sub-1", {}),
        ("post", "/api/coordination/conflicts/detect", {"json": _conflict_payload()}),
        (
            "post",
            "/api/coordination/conflicts/resolve",
            {"json": {"conflict_id": "conflict-1", "strategy": "manual", "resolved_by": "agent-a"}},
        ),
        ("post", "/api/coordination/locks/acquire", {"json": _lock_payload()}),
        ("delete", "/api/coordination/locks/dataset-1", {"params": {"agent_id": "agent-a"}}),
        ("post", "/api/coordination/workflows/create", {"json": _workflow_payload()}),
    ],
)
def test_coordination_mutations_reject_missing_auth_before_state_change(
    client: TestClient,
    registry: EventCoordinationRegistry,
    method: str,
    path: str,
    kwargs: dict,
) -> None:
    checks = unittest.TestCase()

    response = getattr(client, method)(path, **kwargs)

    checks.assertIn(response.status_code, (401, 403))
    checks.assertEqual(registry._event_history, [])
    checks.assertEqual(registry._subscriptions, {})
    checks.assertEqual(registry._resource_locks, {})
    checks.assertEqual(registry._workflows, {})


def test_coordination_event_publish_accepts_valid_auth(client: TestClient) -> None:
    response = client.post(
        "/api/coordination/events/publish",
        json=_event_payload(),
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_coordination_subscribe_and_unsubscribe_accept_valid_auth(client: TestClient) -> None:
    subscribe_response = client.post(
        "/api/coordination/subscriptions/subscribe",
        json=_subscribe_payload(),
        headers=_auth_header(),
    )

    assert subscribe_response.status_code == 200
    subscription_id = subscribe_response.json()["subscription_id"]

    unsubscribe_response = client.delete(
        f"/api/coordination/subscriptions/{subscription_id}",
        headers=_auth_header(),
    )

    assert unsubscribe_response.status_code == 200
    assert unsubscribe_response.json()["success"] is True


def test_coordination_lock_conflict_and_release_accept_valid_auth(client: TestClient) -> None:
    acquire_response = client.post(
        "/api/coordination/locks/acquire",
        json=_lock_payload(),
        headers=_auth_header(),
    )

    assert acquire_response.status_code == 200

    conflict_response = client.post(
        "/api/coordination/conflicts/detect",
        json=_conflict_payload(),
        headers=_auth_header(),
    )

    assert conflict_response.status_code == 200
    conflict = conflict_response.json()["conflict"]

    resolve_response = client.post(
        "/api/coordination/conflicts/resolve",
        json={
            "conflict_id": conflict["conflict_id"],
            "strategy": "manual",
            "resolved_by": "agent-a",
        },
        headers=_auth_header(),
    )

    assert resolve_response.status_code == 200

    release_response = client.delete(
        "/api/coordination/locks/dataset-1",
        params={"agent_id": "agent-a"},
        headers=_auth_header(),
    )

    assert release_response.status_code == 200
    assert release_response.json()["success"] is True


def test_coordination_workflow_create_accepts_valid_auth(client: TestClient) -> None:
    response = client.post(
        "/api/coordination/workflows/create",
        json=_workflow_payload(),
        headers=_auth_header(),
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
