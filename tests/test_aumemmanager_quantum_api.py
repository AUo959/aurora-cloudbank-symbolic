"""
Quantum API tests for AuMemManager FastAPI router
"""

import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests._slowapi_stub import install_slowapi_stub

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-aumemmanager-quantum-api")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-aumemmanager-quantum-api")
install_slowapi_stub()

from modules.aumemmanager.api_integration import router as aumem_router  # noqa: E402
from src.middleware.fastapi_security import generate_csrf_token  # noqa: E402


def _auth_header():
    token = generate_csrf_token("test-session")
    return {"Authorization": f"Bearer {token}"}


def _quantum_payload(vector_id):
    return {
        "vector_id": vector_id,
        "magnitude": 0.75,
        "phase": 0.2,
        "aurora_anchors": ["T1:2", "SRB:3"],
        "dlp_classification": "DLP_L1_OK",
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
@pytest.mark.quantum
def test_create_quantum_vector(client):
    resp = client.post("/memory/quantum/create_vector", json=_quantum_payload("vec_qt_001"), headers=_auth_header())
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
            json=_quantum_payload(vid),
            headers=_auth_header(),
        )

    # Entangle using query params (function signature takes plain args)
    resp = client.post(
        "/memory/quantum/entangle",
        params={"vector1_id": "vec_qt_002", "vector2_id": "vec_qt_003"},
        headers=_auth_header(),
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
        json=_quantum_payload("vec_qt_traj"),
        headers=_auth_header(),
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
        headers=_auth_header(),
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


@pytest.mark.api
@pytest.mark.quantum
@pytest.mark.security
def test_quantum_mutation_routes_reject_missing_token(client):
    requests = (
        (
            "/memory/quantum/create_vector",
            {"json": _quantum_payload("vec_blocked")},
        ),
        (
            "/memory/quantum/entangle",
            {"params": {"vector1_id": "vec_blocked_1", "vector2_id": "vec_blocked_2"}},
        ),
        (
            "/memory/quantum/trajectory",
            {
                "json": {
                    "vector_id": "vec_blocked_traj",
                    "target_magnitude": 0.9,
                    "target_phase": 0.8,
                    "trajectory_type": "quantum_optimal",
                }
            },
        ),
    )

    for url, kwargs in requests:
        response = client.post(url, **kwargs)
        assert response.status_code in (401, 403)
