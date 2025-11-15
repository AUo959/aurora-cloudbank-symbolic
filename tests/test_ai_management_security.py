"""Regression tests for AI management CSRF enforcement."""

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import ai_management_routes
from src.middleware.fastapi_security import generate_csrf_token


@pytest.fixture(autouse=True)
def stub_ai_core(monkeypatch):
    """Provide deterministic AI core stubs for route handlers."""

    class _DummyHub:
        def get_global_status(self):
            return {"online": True}

    class _DummyUnifiedAI:
        def get_available_models(self):
            return [SimpleNamespace(value="test-model")]

        def get_model_capabilities(self, model):
            return SimpleNamespace(
                provider=SimpleNamespace(value="aurora"),
                context_window=8192,
                max_output_tokens=4096,
                supports_function_calling=True,
                supports_vision=False,
                supports_code_execution=False,
                reasoning_strength=9.0,
                code_generation_strength=8.5,
                mathematical_strength=8.0,
                latency_avg_ms=120,
                cost_per_1k_tokens=0.02,
                available=True,
            )

    monkeypatch.setattr(ai_management_routes, "claude_hub", _DummyHub())
    monkeypatch.setattr(ai_management_routes, "gpt5_hub", _DummyHub())
    monkeypatch.setattr(ai_management_routes, "unified_ai", _DummyUnifiedAI())


@pytest.fixture(name="client")
def client_fixture():
    """Return a FastAPI test client wired with the AI router."""

    app = FastAPI()
    app.include_router(ai_management_routes.router)
    return TestClient(app)


def test_ai_routes_reject_invalid_token(client):
    """Ensure AI routes deny requests with malformed bearer tokens."""

    response = client.get(
        "/ai/status",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 403


def test_ai_routes_accept_valid_token(client):
    """Ensure valid CSRF tokens allow handlers to execute."""

    token = generate_csrf_token("test-session")

    response = client.get(
        "/ai/status",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_models"] == 1
