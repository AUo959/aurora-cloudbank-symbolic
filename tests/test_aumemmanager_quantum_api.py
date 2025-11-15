"""
Quantum API tests for AuMemManager FastAPI router
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
@pytest.mark.quantum
def test_create_quantum_vector(client):
    payload = {
        "vector_id": "vec_qt_001",
        "magnitude": 0.75,
        "phase": 0.2,
        "aurora_anchors": ["T1:2", "SRB:3"],
        "dlp_classification": "DLP_L1_OK",
    }
    resp = client.post("/memory/quantum/create_vector", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "created"
    assert data["vector_id"] == "vec_qt_001"


@pytest.mark.api
@pytest.mark.quantum
def test_entangle_vectors(client):
    # Ensure two vectors exist
    for vid in ("vec_qt_002", "vec_qt_003"):
        client.post(
            "/memory/quantum/create_vector",
            json={
                "vector_id": vid,
                "magnitude": 0.6,
                "phase": 0.1,
                "aurora_anchors": ["T1:3"],
                "dlp_classification": "DLP_L1_OK",
            },
        )

    # Entangle using query params (function signature takes plain args)
    resp = client.post(
        "/memory/quantum/entangle", params={"vector1_id": "vec_qt_002", "vector2_id": "vec_qt_003"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "entangled"
    assert {data["vector1_id"], data["vector2_id"]} == {"vec_qt_002", "vec_qt_003"}


@pytest.mark.api
@pytest.mark.quantum
def test_compute_trajectory(client):
    # Create a vector first
    client.post(
        "/memory/quantum/create_vector",
        json={
            "vector_id": "vec_qt_traj",
            "magnitude": 0.5,
            "phase": 0.0,
            "aurora_anchors": ["T1:4"],
            "dlp_classification": "DLP_L1_OK",
        },
    )

    # Compute a trajectory
    resp = client.post(
        "/memory/quantum/trajectory",
        json={
            "vector_id": "vec_qt_traj",
            "target_magnitude": 0.9,
            "target_phase": 0.8,
            "trajectory_type": "quantum_optimal",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "computed"
    assert data["vector_id"] == "vec_qt_traj"
    assert data["waypoints"] >= 1
    assert isinstance(data["trajectory"], list)


@pytest.mark.api
@pytest.mark.quantum
def test_quantum_network_analysis(client):
    # Request analysis
    resp = client.get("/memory/quantum/network_analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "analyzed"
    assert "network_analysis" in data
