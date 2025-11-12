"""
Test suite for Ethics Framework integration in RD API.

Validates that inquiry-first patterns are properly implemented.
"""
from fastapi.testclient import TestClient

from api.aurora_api import app
from modules.hr.rd_api import security, verify_csrf_token


def override_security():
    """Mock security dependency."""
    return {"sub": "test_user"}


def override_csrf():
    """Mock CSRF verification."""
    return True


app.dependency_overrides[security] = override_security
app.dependency_overrides[verify_csrf_token] = override_csrf

client = TestClient(app)


def test_full_coherence_has_ethics_context():
    """Verify /rd/coherence/full includes interpretive guidance."""
    response = client.get("/rd/coherence/full")
    assert response.status_code == 200
    
    data = response.json()
    assert "interpretation" in data
    assert "system_health" in data["interpretation"]
    assert "recommended_action" in data["interpretation"]
    assert "what_this_means" in data["interpretation"]
    assert "next_steps" in data["interpretation"]


def test_mediation_has_inquiry_prompts():
    """Verify /rd/coherence/mediation includes conversation starters."""
    response = client.get("/rd/coherence/mediation?threshold=0.6&limit=5")
    assert response.status_code == 200
    
    data = response.json()
    assert "ethics_context" in data
    assert "what_this_observes" in data["ethics_context"]
    assert "inquiry_first_mandate" in data["ethics_context"]
    assert "escalation_path" in data["ethics_context"]
    
    # Check pairs have inquiry prompts
    if data["pair_count"] > 0:
        first_pair = data["pairs"][0]
        assert "conversation_starters" in first_pair
        assert isinstance(first_pair["conversation_starters"], list)
        assert len(first_pair["conversation_starters"]) > 0
        assert "mediation_recommended" in first_pair


def test_readiness_has_inquiry_prompts():
    """Verify readiness endpoint includes contextual questions."""
    # Create test project first
    client.post("/rd/projects", json={"body": {
        "project_id": "ethics-test-001",
        "name": "Ethics Test Project",
        "project_type": "module",
        "lead_researcher": "test_lead",
        "team_members": [],
        "key_technologies": []
    }})
    
    # Update readiness
    response = client.post("/rd/projects/ethics-test-001/readiness", json={"body": {
        "code_quality": 0.9,
        "documentation": 0.85,
        "test_coverage": 0.88,
        "performance": 0.82,
        "security": 0.91
    }})
    
    assert response.status_code == 200
    data = response.json()
    assert "inquiry_prompts" in data
    assert "status" in data["inquiry_prompts"]
    assert "questions_to_ask" in data["inquiry_prompts"]
    assert isinstance(data["inquiry_prompts"]["questions_to_ask"], list)


def test_coherence_has_ethics_guidance():
    """Verify team coherence includes interpretive guidance."""
    # Create test project first
    client.post("/rd/projects", json={"body": {
        "project_id": "ethics-test-002",
        "name": "Ethics Test Project 2",
        "project_type": "tool",
        "lead_researcher": "test_lead",
        "team_members": ["member_a", "member_b"],
        "key_technologies": []
    }})
    
    # Update coherence
    response = client.post("/rd/projects/ethics-test-002/coherence", json={"body": {
        "team_vectors": {
            "member_a": [0.5, 0.5, 0.5],
            "member_b": [0.52, 0.48, 0.51]
        }
    }})
    
    assert response.status_code == 200
    data = response.json()
    assert "guidance" in data
    assert "interpretation" in data["guidance"]
    assert "inquiry_prompts" in data["guidance"]
    assert "ethics_note" in data


def test_ethics_context_prevents_misuse():
    """Verify ethics context explicitly addresses prohibited uses."""
    response = client.get("/rd/coherence/mediation")
    assert response.status_code == 200
    
    data = response.json()
    ethics = data["ethics_context"]
    
    # Ensure it's clear what NOT to do with this data
    assert "NOT" in ethics["what_this_observes"] or "not" in ethics["what_this_observes"]
    # Verify what_this_cannot_tell exists and has substance
    assert len(ethics["what_this_cannot_tell"]) > 20
    assert "conversation" in ethics["inquiry_first_mandate"].lower()
