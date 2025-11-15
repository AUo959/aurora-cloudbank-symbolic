"""Tests for living computation API security and redaction."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.living_computation_example import router
from src.core.event_system import (
    EventType,
    StationLocation,
    get_event_system,
)
from src.entities.aurora_agent import get_aurora
from src.middleware.fastapi_security import generate_csrf_token


@pytest.fixture
def client():
    """Create a FastAPI test client with the living computation router."""

    app = FastAPI()
    app.include_router(router)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def event_system_state():
    """Reset the global event system state for isolated testing."""

    event_system = get_event_system()
    original_timeline = list(event_system.timeline)
    original_active = dict(event_system.active_events)
    original_t1 = event_system.t1_state
    original_srb = event_system.srb_state

    event_system.timeline = []
    event_system.active_events = {}
    event_system.t1_state = 0
    event_system.srb_state = 0

    try:
        yield event_system
    finally:
        event_system.timeline = original_timeline
        event_system.active_events = original_active
        event_system.t1_state = original_t1
        event_system.srb_state = original_srb


@pytest.fixture
def auth_header():
    """Generate a valid CSRF bearer token header."""

    token = generate_csrf_token("test-session")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize(
    "path",
    [
        "/api/living/aurora/state",
        "/api/living/events/history",
        "/api/living/system/manifest",
    ],
)
def test_endpoints_require_authorization(client, path):
    """Endpoints reject requests without CSRF bearer token."""

    response = client.get(path)
    assert response.status_code == 403


def test_event_history_redacts_sensitive_fields(client, auth_header, event_system_state):
    """Authorized event history response redacts sensitive content."""

    event_system = event_system_state
    aurora_id = get_aurora().entity_id

    event = event_system.create_event(
        event_type=EventType.DATA_ANALYSIS_REQUEST,
        location=StationLocation.RESEARCH_LAB_GAMMA,
        primary_entity=aurora_id,
        payload={"secret": "value"},
        human_context="Commander Vega",
        chain_notation="test-chain",
        context_tag="test-tag",
    )

    event_system.complete_event(
        event_id=event.event_id,
        result={"status": "ok", "analysis": {"score": 0.9}},
        memory_references=["mem-001"],
        pattern_connections=["pattern-alpha"],
        collaboration_network={"HALO": 0.87},
    )

    response = client.get("/api/living/events/history", headers=auth_header)
    assert response.status_code == 200

    payload = response.json()
    assert payload["total_events"] == 1

    record = payload["events"][0]
    assert record["payload"] == {"redacted": True, "entries": 1}
    assert record["entity_context"]["human"] == "[REDACTED]"
    assert record["result"]["redacted"] is True
    assert record["result"]["status"] == "ok"
    assert record["result"]["keys"] == ["analysis", "status"]
    assert record["memory_context"]["network"]["connections"] == 1
    assert record["memory_context"]["references"]["count"] == 1
    assert record["memory_context"]["patterns"]["count"] == 1


def test_manifest_redacts_sensitive_fields(client, auth_header, event_system_state):
    """Authorized manifest response redacts sensitive event content."""

    event_system = event_system_state
    aurora_id = get_aurora().entity_id

    event = event_system.create_event(
        event_type=EventType.DATA_ANALYSIS_REQUEST,
        location=StationLocation.RESEARCH_LAB_GAMMA,
        primary_entity=aurora_id,
        payload={"internal": "data"},
        human_context="Commander Vega",
        chain_notation="test-chain",
        context_tag="test-tag",
    )

    event_system.complete_event(
        event_id=event.event_id,
        result={"status": "ok", "analysis": {"score": 0.95}},
        memory_references=["mem-002"],
        pattern_connections=["pattern-beta"],
        collaboration_network={"HALO": 0.91},
    )

    response = client.get("/api/living/system/manifest", headers=auth_header)
    assert response.status_code == 200

    manifest = response.json()
    assert manifest["event_statistics"]["total_events"] == 1

    timeline_entry = manifest["timeline"][0]
    assert timeline_entry["payload"]["redacted"] is True
    assert timeline_entry["entity_context"]["human"] == "[REDACTED]"
    assert timeline_entry["memory_context"]["network"]["redacted"] is True
    assert timeline_entry["result"]["keys"] == ["analysis", "status"]

    assert "Aurora" in manifest["entities"]
    assert manifest["entities"]["Aurora"]["entity_id"] == aurora_id
