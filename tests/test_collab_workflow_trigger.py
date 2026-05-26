"""Regression tests for collaboration workflow trigger dispatch semantics."""

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-collab-workflow")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-collab-workflow")

from src.collab.api_routes import router  # noqa: E402
from src.middleware.fastapi_security import generate_csrf_token  # noqa: E402


def _auth_headers() -> dict[str, str]:
    token = generate_csrf_token("collab-workflow-session")
    return {"Authorization": f"Bearer {token}"}


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _workflow_payload() -> dict:
    return {
        "target_repo": "AUo959/aurora-cloudbank-symbolic",
        "workflow_name": "ci.yml",
        "event_type": "workflow_dispatch",
        "payload": {"reason": "regression-test"},
    }


def test_workflow_trigger_rejects_missing_auth_before_dispatch() -> None:
    client = _client()

    response = client.post("/collab/workflow/trigger", json=_workflow_payload())

    assert response.status_code in (401, 403)


def test_workflow_trigger_fails_closed_without_dispatch_provider() -> None:
    client = _client()

    response = client.post(
        "/collab/workflow/trigger",
        json=_workflow_payload(),
        headers=_auth_headers(),
    )

    assert response.status_code == 501
    detail = response.json()["detail"]
    assert detail["error"] == "workflow_dispatch_not_configured"
    assert detail["target_repo"] == "AUo959/aurora-cloudbank-symbolic"
    assert detail["workflow_name"] == "ci.yml"
    assert "success" not in detail
