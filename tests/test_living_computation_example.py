"""Tests for the living computation example API."""

import pytest
from fastapi import HTTPException

from src.api.living_computation_example import (
    AnalysisRequest,
    analyze_with_living_computation,
)
from src.core.event_system import get_event_system


@pytest.fixture
def anyio_backend():
    """Limit AnyIO to the asyncio backend for deterministic testing."""

    return "asyncio"


@pytest.mark.anyio
async def test_high_risk_request_aborts_event(monkeypatch):
    """Ensure high-risk requests leave no active events and record denial."""

    event_system = get_event_system()
    event_system.timeline.clear()
    event_system.active_events.clear()

    original_create_event = event_system.create_event

    def _high_risk_event(*args, **kwargs):
        event = original_create_event(*args, **kwargs)
        event.risk_score = 0.95
        return event

    monkeypatch.setattr(event_system, "create_event", _high_risk_event)

    request = AnalysisRequest(data={"payload": "sensitive"}, user_context="QA")

    with pytest.raises(HTTPException) as exc_info:
        await analyze_with_living_computation(request)

    assert exc_info.value.status_code == 403
    assert event_system.active_events == {}
    assert event_system.timeline, "Denied event should be recorded in the timeline"
    denied_event = event_system.timeline[-1]
    assert denied_event.result["status"] == "denied"
    assert denied_event.result["audit"]["risk_score"] == pytest.approx(0.95)

    event_system.timeline.clear()

