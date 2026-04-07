"""Tests for the autonomous DriftResponder agent and runbook loader.

DLP: test_drift_responder_v1
Anchors: T1:TEST_DRIFT_RESPONDER, SRB:ORION_SENTINEL
"""

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.agents.drift_responder import (
    DriftResponder,
    DriftResponseEvent,
    ResponseStatus,
    _load_runbooks,
    register_ws_broadcast_hook,
)
from src.monitoring.drift_detector import DriftAlert, DriftLevel, DriftMethod


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_alert(
    level: DriftLevel = DriftLevel.WARNING,
    agent_id: str = "agent-test",
    metric_name: str = "response_time",
    deviation: float = 2.5,
) -> DriftAlert:
    return DriftAlert(
        timestamp=datetime.now(timezone.utc).isoformat(),
        agent_id=agent_id,
        metric_name=metric_name,
        deviation=deviation,
        level=level,
        method=DriftMethod.Z_SCORE,
        current_value=5.0,
        baseline_value=2.0,
        description=f"Test drift at {level.value}",
    )


# ---------------------------------------------------------------------------
# Runbook loader
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_load_runbooks_returns_dict():
    runbooks = _load_runbooks()
    assert isinstance(runbooks, dict)
    assert len(runbooks) > 0


@pytest.mark.unit
@pytest.mark.aurora
def test_load_runbooks_has_expected_levels():
    runbooks = _load_runbooks()
    # All three DriftLevel values must have a runbook
    for level_key in ("info", "warning", "critical"):
        assert level_key in runbooks, f"Missing runbook for level '{level_key}'"


@pytest.mark.unit
@pytest.mark.aurora
def test_load_runbooks_missing_file():
    runbooks = _load_runbooks(path=Path("/nonexistent/runbooks.yaml"))
    assert runbooks == {}


@pytest.mark.unit
@pytest.mark.aurora
def test_load_runbooks_runbook_has_actions():
    runbooks = _load_runbooks()
    for level_key, entry in runbooks.items():
        actions = entry.get("actions", [])
        assert len(actions) > 0, f"Runbook '{level_key}' has no actions"


# ---------------------------------------------------------------------------
# DriftResponder initialisation
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_responder_initialises_without_detector():
    responder = DriftResponder()
    assert responder._detector is None
    assert responder._running is False
    assert isinstance(responder._history, list)


@pytest.mark.unit
@pytest.mark.aurora
def test_responder_initialises_with_detector():
    mock_detector = MagicMock()
    responder = DriftResponder(detector=mock_detector)
    assert responder._detector is mock_detector


@pytest.mark.unit
@pytest.mark.aurora
def test_responder_loads_runbooks_on_init():
    responder = DriftResponder()
    assert len(responder._runbooks) > 0


@pytest.mark.unit
@pytest.mark.aurora
def test_get_runbook_names_returns_mapping():
    responder = DriftResponder()
    names = responder.get_runbook_names()
    assert isinstance(names, dict)
    assert len(names) > 0
    for key, name in names.items():
        assert isinstance(key, str)
        assert isinstance(name, str)


# ---------------------------------------------------------------------------
# handle_alert — synchronous path
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_handle_alert_warning_returns_event():
    responder = DriftResponder()
    alert = _make_alert(level=DriftLevel.WARNING)
    event = responder.handle_alert(alert)
    assert isinstance(event, DriftResponseEvent)
    assert event.drift_level == "warning"
    assert event.alert_agent_id == "agent-test"
    assert event.alert_metric == "response_time"


@pytest.mark.unit
@pytest.mark.aurora
def test_handle_alert_info_returns_executed():
    responder = DriftResponder()
    alert = _make_alert(level=DriftLevel.INFO)
    event = responder.handle_alert(alert)
    assert event.status in (ResponseStatus.EXECUTED, ResponseStatus.PARTIAL)
    assert event.actions_attempted > 0


@pytest.mark.unit
@pytest.mark.aurora
def test_handle_alert_critical_returns_event():
    responder = DriftResponder()
    alert = _make_alert(level=DriftLevel.CRITICAL)
    event = responder.handle_alert(alert)
    assert isinstance(event, DriftResponseEvent)
    assert event.drift_level == "critical"


@pytest.mark.unit
@pytest.mark.aurora
def test_handle_alert_unknown_level_returns_failed():
    """A custom/unknown level with no runbook must return FAILED status."""
    responder = DriftResponder()
    alert = _make_alert()
    # Temporarily inject an unknown level string
    alert.level = MagicMock()
    alert.level.value = "unknown_level"
    event = responder.handle_alert(alert)
    assert event.status == ResponseStatus.FAILED
    assert event.actions_attempted == 0


@pytest.mark.unit
@pytest.mark.aurora
def test_handle_alert_appends_to_history():
    responder = DriftResponder()
    alert = _make_alert(level=DriftLevel.INFO)
    responder.handle_alert(alert)
    assert len(responder._history) == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_handle_multiple_alerts_appended():
    responder = DriftResponder()
    for level in (DriftLevel.INFO, DriftLevel.WARNING, DriftLevel.CRITICAL):
        responder.handle_alert(_make_alert(level=level))
    assert len(responder._history) == 3


# ---------------------------------------------------------------------------
# DriftResponseEvent
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_response_event_to_dict():
    responder = DriftResponder()
    alert = _make_alert(level=DriftLevel.WARNING)
    event = responder.handle_alert(alert)
    d = event.to_dict()
    assert isinstance(d, dict)
    required_keys = {
        "timestamp", "alert_agent_id", "alert_metric", "drift_level",
        "runbook_name", "actions_attempted", "actions_succeeded", "status", "errors",
    }
    assert required_keys.issubset(d.keys())
    assert d["status"] in ("executed", "partial", "failed")


@pytest.mark.unit
@pytest.mark.aurora
def test_response_event_context_tag():
    responder = DriftResponder()
    alert = _make_alert()
    event = responder.handle_alert(alert)
    assert event.context_tag == "drift_responder_v1"


# ---------------------------------------------------------------------------
# get_history
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_get_history_returns_list():
    responder = DriftResponder()
    responder.handle_alert(_make_alert())
    history = responder.get_history()
    assert isinstance(history, list)
    assert len(history) == 1
    assert isinstance(history[0], dict)


@pytest.mark.unit
@pytest.mark.aurora
def test_get_history_respects_limit():
    responder = DriftResponder()
    for _ in range(10):
        responder.handle_alert(_make_alert())
    history = responder.get_history(limit=5)
    assert len(history) == 5


@pytest.mark.unit
@pytest.mark.aurora
def test_get_history_empty_when_no_alerts():
    responder = DriftResponder()
    assert responder.get_history() == []


# ---------------------------------------------------------------------------
# WebSocket broadcast hook
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_register_ws_broadcast_hook():
    captured = []

    def hook(payload):
        captured.append(payload)

    register_ws_broadcast_hook(hook)
    # Trigger an INFO alert which fires the notify action
    responder = DriftResponder()
    alert = _make_alert(level=DriftLevel.INFO)
    responder.handle_alert(alert)
    # At least one broadcast should have occurred
    assert len(captured) >= 1
    # Clean up — reset the global hook
    register_ws_broadcast_hook(None)


# ---------------------------------------------------------------------------
# stop()
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.aurora
def test_stop_sets_running_false():
    responder = DriftResponder()
    responder._running = True
    responder.stop()
    assert responder._running is False


# ---------------------------------------------------------------------------
# async handle_alert_async
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.aurora
async def test_handle_alert_async_returns_event():
    responder = DriftResponder()
    alert = _make_alert(level=DriftLevel.WARNING)
    event = await responder.handle_alert_async(alert)
    assert isinstance(event, DriftResponseEvent)
    assert event.drift_level == "warning"


# ---------------------------------------------------------------------------
# run() — poll loop with cancellation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.aurora
async def test_run_loop_processes_alerts():
    mock_detector = MagicMock()
    alert = _make_alert(level=DriftLevel.WARNING)
    mock_detector.alerts = [alert]

    responder = DriftResponder(detector=mock_detector, poll_interval_s=0.05)
    task = asyncio.create_task(responder.run())
    await asyncio.sleep(0.15)
    task.cancel()
    # run() catches CancelledError internally and returns normally
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert len(responder._history) >= 1


@pytest.mark.asyncio
@pytest.mark.unit
@pytest.mark.aurora
async def test_run_loop_no_detector_returns_immediately():
    responder = DriftResponder(detector=None)
    await responder.run()  # Should return without hanging
    assert responder._running is False
