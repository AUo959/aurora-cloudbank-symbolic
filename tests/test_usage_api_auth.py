"""Auth and RBAC tests for token usage API endpoints."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from modules.ai_core.usage_api import router
from src.security.oauth2 import OAuth2Handler


def _auth_headers(username: str, role: str) -> dict[str, str]:
    token = OAuth2Handler.create_access_token({"sub": username, "role": role})
    return {"Authorization": " ".join(["Bearer", token])}


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture(autouse=True)
def _mock_usage_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "modules.ai_core.usage_api.token_budget.get_user_usage",
        lambda _user_id: {"hour_tokens": 11, "day_tokens": 22},
    )
    monkeypatch.setattr(
        "modules.ai_core.usage_api.token_budget.get_global_usage",
        lambda: {
            "hour_tokens": 33,
            "limits": {
                "max_per_request": 1000,
                "max_per_user_hour": 5000,
                "max_per_user_day": 10000,
                "max_global_hour": 50000,
            },
        },
    )
    monkeypatch.setattr("modules.ai_core.usage_api.token_budget.max_per_request", 1000)
    monkeypatch.setattr("modules.ai_core.usage_api.token_budget.max_per_user_hour", 5000)
    monkeypatch.setattr("modules.ai_core.usage_api.token_budget.max_per_user_day", 10000)


@pytest.mark.api
@pytest.mark.unit
def test_usage_me_authenticated_user_can_query_self(client: TestClient) -> None:
    response = client.get("/api/usage/me", headers=_auth_headers("alice", "observer"))
    assert response.status_code == 200
    assert response.json()["user_id"] == "alice"


@pytest.mark.api
@pytest.mark.unit
def test_usage_me_unauthenticated_returns_401(client: TestClient) -> None:
    response = client.get("/api/usage/me")
    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.unit
def test_usage_global_non_admin_returns_403(client: TestClient) -> None:
    response = client.get("/api/usage/global", headers=_auth_headers("operator", "relay_operator"))
    assert response.status_code == 403


@pytest.mark.api
@pytest.mark.unit
def test_usage_global_admin_returns_200(client: TestClient) -> None:
    response = client.get("/api/usage/global", headers=_auth_headers("admin", "admin"))
    assert response.status_code == 200
