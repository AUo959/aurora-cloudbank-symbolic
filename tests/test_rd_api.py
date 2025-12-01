import pytest
from fastapi.testclient import TestClient

from api.aurora_api import app

# Mock security dependencies for testing
from src.middleware.fastapi_security import security, verify_csrf_token


def override_security():
    """Mock security dependency - always allow access in tests."""
    return {"sub": "test_user"}


def override_csrf():
    """Mock CSRF verification - always pass in tests."""
    return True


@pytest.fixture(autouse=True)
def setup_security_overrides():
    """Set up security overrides for each test and clean up after."""
    # Set overrides before each test
    app.dependency_overrides[security] = override_security
    app.dependency_overrides[verify_csrf_token] = override_csrf
    yield
    # Clean up after each test (though they need to stay for this module)


# Create client after overrides are set
@pytest.fixture
def rd_client():
    """Provide a test client with security overrides."""
    app.dependency_overrides[security] = override_security
    app.dependency_overrides[verify_csrf_token] = override_csrf
    return TestClient(app)


# For backward compatibility with existing tests
client = TestClient(app)
app.dependency_overrides[security] = override_security
app.dependency_overrides[verify_csrf_token] = override_csrf


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
    # Creation - FastAPI embeds body when Request parameter present
    r_create = client.post("/rd/projects", json={"body": payload})
    assert r_create.status_code == 200, r_create.text
    r_adv = client.post(
        "/rd/projects/rdp-test-api/advance",
        json={"body": {"new_stage": "proof_of_concept", "milestone": "Initial POC"}},
    )
    assert r_adv.status_code == 200, r_adv.text
    data = r_adv.json()
    assert data["project"]["stage"] == "proof_of_concept"


def test_update_readiness_and_coherence():
    # Ensure project exists - embedded body format
    client.post(
        "/rd/projects",
        json={"body": {
            "project_id": "rdp-readiness",
            "name": "Readiness Project",
            "project_type": "module",
            "lead_researcher": "lead_x",
            "team_members": ["member_a", "member_b"],
            "key_technologies": ["fastapi"],
        }},
    )
    r_ready = client.post(
        "/rd/projects/rdp-readiness/readiness",
        json={"body": {
            "code_quality": 0.9,
            "documentation": 0.8,
            "test_coverage": 0.85,
            "performance": 0.75,
            "security": 0.88,
        }},
    )
    assert r_ready.status_code == 200
    readiness_score = r_ready.json()["production_readiness"]
    assert 0.0 <= readiness_score <= 1.0

    r_coh = client.post(
        "/rd/projects/rdp-readiness/coherence",
        json={"body": {
            "team_vectors": {
                "lead_x": [0.2, 0.3, 0.5],
                "member_a": [0.21, 0.29, 0.52],
                "member_b": [0.19, 0.31, 0.49],
            }
        }},
    )
    assert r_coh.status_code == 200
    coherence = r_coh.json()["team_coherence"]
    assert 0.0 <= coherence <= 1.0


def test_pipeline_report():
    r = client.get("/rd/report")
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert "aggregate_metrics" in data
