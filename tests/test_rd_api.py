from fastapi.testclient import TestClient

from api.aurora_api import app
from src.middleware.fastapi_security import generate_csrf_token

client = TestClient(app)


def _auth_headers() -> dict:
    # GlobalCsrfMiddleware checks X-CSRF-Token on unsafe methods; the
    # require_csrf_token route dependency reads the bearer credentials.
    token = generate_csrf_token("rd-api-test-session")
    return {"Authorization": f"Bearer {token}", "X-CSRF-Token": token}


def test_rd_health():
    r = client.get("/rd/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert "active_projects" in data


def test_list_seed_projects():
    r = client.get("/rd/projects")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    # Seed should load >= 1 projects
    assert data["count"] >= 1


def test_create_and_advance_project():
    payload = {
        "project_id": "rdp-test-api",
        "name": "API Test Project",
        "project_type": "tool",
        "lead_researcher": "test_lead",
        "team_members": ["alpha", "beta"],
        "key_technologies": ["python"],
    }
    r_create = client.post("/rd/projects", json=payload, headers=_auth_headers())
    assert r_create.status_code == 200, r_create.text
    r_adv = client.post(
        "/rd/projects/rdp-test-api/advance",
        json={"new_stage": "proof_of_concept", "milestone": "Initial POC"},
        headers=_auth_headers(),
    )
    assert r_adv.status_code == 200, r_adv.text
    data = r_adv.json()
    assert data["project"]["stage"] == "proof_of_concept"


def test_update_readiness_and_coherence():
    # Ensure project exists
    client.post(
        "/rd/projects",
        json={
            "project_id": "rdp-readiness",
            "name": "Readiness Project",
            "project_type": "module",
            "lead_researcher": "lead_x",
            "team_members": ["member_a", "member_b"],
            "key_technologies": ["fastapi"],
        },
        headers=_auth_headers(),
    )
    r_ready = client.post(
        "/rd/projects/rdp-readiness/readiness",
        json={
            "code_quality": 0.9,
            "documentation": 0.8,
            "test_coverage": 0.85,
            "performance": 0.75,
            "security": 0.88,
        },
        headers=_auth_headers(),
    )
    assert r_ready.status_code == 200, r_ready.text
    readiness_score = r_ready.json()["production_readiness"]
    assert 0.0 <= readiness_score <= 1.0

    r_coh = client.post(
        "/rd/projects/rdp-readiness/coherence",
        json={
            "team_vectors": {
                "lead_x": [0.2, 0.3, 0.5],
                "member_a": [0.21, 0.29, 0.52],
                "member_b": [0.19, 0.31, 0.49],
            }
        },
        headers=_auth_headers(),
    )
    assert r_coh.status_code == 200, r_coh.text
    coherence = r_coh.json()["team_coherence"]
    assert 0.0 <= coherence <= 1.0


def test_mutating_endpoint_requires_csrf_token():
    r = client.post(
        "/rd/projects",
        json={
            "project_id": "rdp-no-token",
            "name": "No Token Project",
            "project_type": "tool",
            "lead_researcher": "lead_y",
            "team_members": [],
            "key_technologies": [],
        },
    )
    assert r.status_code == 403


def test_pipeline_report():
    r = client.get("/rd/report")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "aggregate_metrics" in data
