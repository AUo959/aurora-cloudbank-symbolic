"""Autonomous Drift Responder Agent.

Subscribes to drift alerts emitted by the DriftDetector, looks up the
appropriate runbook from drift_runbooks.yaml, and executes each action in
order.  Designed to run as a background task inside the FastAPI lifespan or
as a standalone asyncio loop.

DLP: drift_responder_v1
Anchors: T1:DRIFT_RESPONDER_INIT, SRB:ORION_SENTINEL
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from src.monitoring.drift_detector import DriftAlert

logger = logging.getLogger(__name__)

_RUNBOOKS_PATH = Path(__file__).parent / "drift_runbooks.yaml"


# ---------------------------------------------------------------------------
# Response event (emitted after each runbook execution)
# ---------------------------------------------------------------------------

class ResponseStatus(Enum):
    EXECUTED = "executed"
    PARTIAL = "partial"    # Some actions failed but others succeeded
    FAILED = "failed"


@dataclass
class DriftResponseEvent:
    """Record of a completed runbook execution."""

    timestamp: str
    alert_agent_id: str
    alert_metric: str
    drift_level: str
    runbook_name: str
    actions_attempted: int
    actions_succeeded: int
    status: ResponseStatus
    errors: List[str] = field(default_factory=list)
    context_tag: str = "drift_responder_v1"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "alert_agent_id": self.alert_agent_id,
            "alert_metric": self.alert_metric,
            "drift_level": self.drift_level,
            "runbook_name": self.runbook_name,
            "actions_attempted": self.actions_attempted,
            "actions_succeeded": self.actions_succeeded,
            "status": self.status.value,
            "errors": self.errors,
            "context_tag": self.context_tag,
        }


# ---------------------------------------------------------------------------
# WS broadcast hook — populated by the drift_metrics_api at startup
# ---------------------------------------------------------------------------
_ws_broadcast_hook: Optional[Callable[[Dict[str, Any]], None]] = None


def register_ws_broadcast_hook(fn: Callable[[Dict[str, Any]], None]) -> None:
    """Register a callable that forwards events to WebSocket consumers."""
    global _ws_broadcast_hook
    _ws_broadcast_hook = fn


# ---------------------------------------------------------------------------
# Runbook loader
# ---------------------------------------------------------------------------

def _load_runbooks(path: Path = _RUNBOOKS_PATH) -> Dict[str, Dict[str, Any]]:
    """Load runbooks from YAML, keyed by DriftLevel value string."""
    if not path.exists():
        logger.error("Runbooks file not found: %s", path)
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    result: Dict[str, Dict[str, Any]] = {}
    for entry in data.get("runbooks", []):
        level_key = entry.get("level", "").lower()
        result[level_key] = entry
    logger.info("Loaded %d drift runbooks from %s", len(result), path)
    return result


# ---------------------------------------------------------------------------
# Individual action handlers
# ---------------------------------------------------------------------------

def _action_log(params: Dict[str, Any], alert: DriftAlert, _detector: Any) -> None:
    sev = params.get("severity", "info")
    msg = params.get("message", "Drift action triggered")
    log_fn = getattr(logger, sev, logger.info)
    log_fn(
        "[DriftResponder] %s | agent=%s metric=%s deviation=%.3f",
        msg, alert.agent_id, alert.metric_name, alert.deviation,
    )


def _action_notify(params: Dict[str, Any], alert: DriftAlert, detector: Any) -> None:
    if not _ws_broadcast_hook:
        return
    payload: Dict[str, Any] = {
        "event_type": params.get("event_type", "drift_event"),
        "agent_id": alert.agent_id,
        "metric_name": alert.metric_name,
        "drift_level": alert.level.value,
        "deviation": alert.deviation,
        "description": alert.description,
        "timestamp": alert.timestamp,
    }
    if params.get("include_metrics") and hasattr(detector, "get_metrics"):
        payload["metrics"] = detector.get_metrics(alert.agent_id)
    _ws_broadcast_hook(payload)


def _action_alert(params: Dict[str, Any], alert: DriftAlert, _detector: Any) -> None:
    logger.warning(
        "[DriftResponder] ALERT (priority=%s route=%s) agent=%s metric=%s",
        params.get("priority", "medium"),
        params.get("route_to", "sentinel_bus"),
        alert.agent_id,
        alert.metric_name,
    )


def _action_throttle(params: Dict[str, Any], alert: DriftAlert, _detector: Any) -> None:
    logger.warning(
        "[DriftResponder] THROTTLE agent=%s by %s%% for %ss",
        alert.agent_id, params.get("percent", 50), params.get("duration_s", 300),
    )
    # Future: integrate with rate-limiter API


def _action_suspend(params: Dict[str, Any], alert: DriftAlert, _detector: Any) -> None:
    logger.critical(
        "[DriftResponder] SUSPEND agent=%s for %ss",
        alert.agent_id, params.get("duration_s", 600),
    )
    # Future: integrate with agent lifecycle manager


def _action_rebaseline(params: Dict[str, Any], alert: DriftAlert, detector: Any) -> None:
    hard = params.get("hard", False)
    window = params.get("window_size", 60)
    if hard and hasattr(detector, "clear_baseline"):
        detector.clear_baseline(alert.agent_id, alert.metric_name)
    elif hasattr(detector, "update_baseline_window"):
        detector.update_baseline_window(alert.agent_id, alert.metric_name, window)
    logger.info(
        "[DriftResponder] REBASELINE agent=%s metric=%s window=%ss hard=%s",
        alert.agent_id, alert.metric_name, window, hard,
    )


def _action_escalate(params: Dict[str, Any], _alert: DriftAlert, _detector: Any) -> None:
    logger.critical(
        "[DriftResponder] ESCALATE target=%s channel=%s | %s",
        params.get("target", "unknown"),
        params.get("channel", "unknown"),
        params.get("message", "Drift escalation"),
    )
    # Future: publish to crew notification bus


_ACTION_HANDLERS: Dict[str, Any] = {
    "log": _action_log,
    "notify": _action_notify,
    "alert": _action_alert,
    "throttle": _action_throttle,
    "suspend": _action_suspend,
    "rebaseline": _action_rebaseline,
    "escalate": _action_escalate,
}


def _execute_action(
    action: Dict[str, Any],
    alert: DriftAlert,
    detector: Any,
) -> bool:
    """Dispatch a single runbook action to its handler.  Returns True on success."""
    atype = action.get("type", "")
    handler = _ACTION_HANDLERS.get(atype)
    if handler is None:
        logger.warning("[DriftResponder] Unknown action type '%s' — skipping", atype)
        return False
    try:
        handler(action.get("params", {}), alert, detector)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.exception("[DriftResponder] Action '%s' failed: %s", atype, exc)
        return False


# ---------------------------------------------------------------------------
# DriftResponder class
# ---------------------------------------------------------------------------

class DriftResponder:
    """Autonomous agent that executes runbooks in response to drift alerts.

    Usage (standalone asyncio task)::

        from src.monitoring.drift_detector import DriftDetector
        from src.agents.drift_responder import DriftResponder

        detector = DriftDetector()
        responder = DriftResponder(detector=detector)
        asyncio.create_task(responder.run())

    Usage (callback-based when drift is detected)::

        detector.on_alert = responder.handle_alert
    """

    def __init__(
        self,
        detector: Optional[Any] = None,
        poll_interval_s: float = 5.0,
    ) -> None:
        self._detector = detector
        self._poll_interval = poll_interval_s
        self._runbooks: Dict[str, Dict[str, Any]] = _load_runbooks()
        self._history: List[DriftResponseEvent] = []
        self._running = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def handle_alert(self, alert: DriftAlert) -> DriftResponseEvent:
        """Synchronously handle a single DriftAlert by running its runbook."""
        level_key = alert.level.value.lower()
        runbook = self._runbooks.get(level_key)
        if not runbook:
            return self._no_runbook_event(alert, level_key)
        return self._run_runbook(alert, level_key, runbook)

    def _no_runbook_event(self, alert: DriftAlert, level_key: str) -> DriftResponseEvent:
        logger.warning("[DriftResponder] No runbook for level '%s' — alert ignored", level_key)
        event = DriftResponseEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            alert_agent_id=alert.agent_id,
            alert_metric=alert.metric_name,
            drift_level=level_key,
            runbook_name="<none>",
            actions_attempted=0,
            actions_succeeded=0,
            status=ResponseStatus.FAILED,
            errors=[f"No runbook defined for drift level '{level_key}'"],
        )
        self._history.append(event)
        return event

    def _run_runbook(self, alert: DriftAlert, level_key: str, runbook: Dict[str, Any]) -> DriftResponseEvent:
        actions = runbook.get("actions", [])
        succeeded = 0
        errors: List[str] = []
        logger.info(
            "[DriftResponder] Executing runbook '%s' (%d actions) for agent=%s metric=%s",
            runbook.get("name", level_key), len(actions), alert.agent_id, alert.metric_name,
        )
        for action in actions:
            if _execute_action(action, alert, self._detector):
                succeeded += 1
            else:
                errors.append(f"Action '{action.get('type')}' failed")
        if succeeded == len(actions):
            status = ResponseStatus.EXECUTED
        elif succeeded > 0:
            status = ResponseStatus.PARTIAL
        else:
            status = ResponseStatus.FAILED
        event = DriftResponseEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            alert_agent_id=alert.agent_id,
            alert_metric=alert.metric_name,
            drift_level=level_key,
            runbook_name=runbook.get("name", level_key),
            actions_attempted=len(actions),
            actions_succeeded=succeeded,
            status=status,
            errors=errors,
        )
        self._history.append(event)
        return event

    async def handle_alert_async(self, alert: DriftAlert) -> DriftResponseEvent:
        """Async wrapper around handle_alert (runs in thread executor)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.handle_alert, alert)

    async def run(self) -> None:
        """Poll the detector's alert queue and process new alerts continuously."""
        if not self._detector:
            logger.error("[DriftResponder] No detector configured — run() aborted")
            return
        self._running = True
        logger.info("[DriftResponder] Starting poll loop (interval=%.1fs)", self._poll_interval)
        processed_ids: set = set()
        try:
            while self._running:
                alerts: List[DriftAlert] = getattr(self._detector, "alerts", [])
                for alert in alerts:
                    alert_key = f"{alert.timestamp}:{alert.agent_id}:{alert.metric_name}"
                    if alert_key not in processed_ids:
                        processed_ids.add(alert_key)
                        await self.handle_alert_async(alert)
                await asyncio.sleep(self._poll_interval)
        except asyncio.CancelledError:
            logger.info("[DriftResponder] Poll loop cancelled — shutting down")
        finally:
            self._running = False

    def stop(self) -> None:
        """Signal the run() loop to exit."""
        self._running = False

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return the most recent response events as dicts."""
        return [e.to_dict() for e in self._history[-limit:]]

    def get_runbook_names(self) -> Dict[str, str]:
        """Return mapping of drift level → runbook name."""
        return {k: v.get("name", k) for k, v in self._runbooks.items()}
