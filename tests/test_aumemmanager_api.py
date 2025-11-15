"""
API tests for AuMemManager FastAPI router
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.aumemmanager.api_integration import router as aumem_router


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
    create_payload = {
        "content": {"note": "integration-test memory"},
        "memory_type": "agent",
        "owner": "test_agent",
        "importance": 3.5,
        "tags": ["test", "integration"],
        "quantum_properties": {"vector_id": "vec_it_001", "magnitude": 0.9, "phase": 0.1},
        "aurora_anchors": ["T1:1", "SRB:1"],
        "cultural_score": 0.42,
    }
    c_resp = client.post("/memory/create", json=create_payload)
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
