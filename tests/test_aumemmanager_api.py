"""
API tests for AuMemManager FastAPI router
"""

import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests._slowapi_stub import install_slowapi_stub

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-aumemmanager-api")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-aumemmanager-api")
install_slowapi_stub()

from modules.aumemmanager.api_integration import router as aumem_router  # noqa: E402
from src.middleware.fastapi_security import generate_csrf_token  # noqa: E402


def _auth_header():
    token = generate_csrf_token("test-session")
    return {"Authorization": f"Bearer {token}"}


def _memory_payload():
    return {
        "content": {"note": "integration-test memory"},
        "memory_type": "agent",
        "owner": "test_agent",
        "importance": 3.5,
        "tags": ["test", "integration"],
        "quantum_properties": {"vector_id": "vec_it_001", "magnitude": 0.9, "phase": 0.1},
        "aurora_anchors": ["T1:1", "SRB:1"],
        "cultural_score": 0.42,
    }


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(aumem_router)
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.mark.api
@pytest.mark.aurora
def test_memory_health_endpoint(client):
    resp = client.get("/memory/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in {"healthy", "unhealthy"}
    assert "timestamp" in data


@pytest.mark.api
@pytest.mark.aurora
def test_memory_metrics_endpoint(client):
    resp = client.get("/memory/metrics")
    assert resp.status_code == 200
    data = resp.json()
    # Basic shape validation
    expected_keys = {
        "total_memories",
        "active_memories",
        "compressed_memories",
        "archived_memories",
        "quantum_vectors",
        "entangled_pairs",
        "aurora_anchor_coverage",
        "average_cultural_score",
        "quantum_network_density",
    }
    assert expected_keys.issubset(set(data.keys()))


@pytest.mark.api
@pytest.mark.aurora
def test_create_and_retrieve_memory_flow(client):
    # Create
    c_resp = client.post("/memory/create", json=_memory_payload(), headers=_auth_header())
    assert c_resp.status_code == 200
    c_data = c_resp.json()
    assert c_data.get("status") == "created"
    assert "memory_id" in c_data

    # Retrieve
    r_payload = {"query": "integration-test", "owner": "test_agent", "top_k": 5}
    r_resp = client.post("/memory/retrieve", json=r_payload)
    assert r_resp.status_code == 200
    items = r_resp.json()
    assert isinstance(items, list)
    # At least one memory should match the flow
    assert any(m.get("owner") == "test_agent" for m in items)


@pytest.mark.api
@pytest.mark.aurora
@pytest.mark.security
def test_sensitive_memory_routes_reject_missing_token(client):
    requests = (
        ("post", "/memory/create", {"json": _memory_payload()}),
        ("post", "/memory/lifecycle/batch_process", {}),
        ("post", "/memory/compress", {}),
        ("get", "/memory/export", {}),
    )

    for method, url, kwargs in requests:
        response = getattr(client, method)(url, **kwargs)
        assert response.status_code in (401, 403)


@pytest.mark.api
@pytest.mark.aurora
@pytest.mark.security
def test_sensitive_memory_routes_accept_valid_token(client):
    headers = _auth_header()

    create_response = client.post("/memory/create", json=_memory_payload(), headers=headers)
    assert create_response.status_code == 200
    assert create_response.json()["status"] == "created"

    lifecycle_response = client.post("/memory/lifecycle/batch_process", headers=headers)
    assert lifecycle_response.status_code == 200
    assert lifecycle_response.json()["status"] == "completed"

    compress_response = client.post("/memory/compress", headers=headers)
    assert compress_response.status_code == 200
    assert compress_response.json()["status"] == "completed"

    export_response = client.get("/memory/export", headers=headers)
    assert export_response.status_code == 200
    assert export_response.json()["status"] == "exported"
