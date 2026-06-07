"""
Action Guard — lightweight bridge between API response paths and MonitoringSystem.

Calls MonitoringSystem.evaluate_action in a fire-and-forget manner so that
ethics/compliance checks never block a response. Violations are passed to any
registered enforcement handlers after evaluation.

Usage::

    from src.monitoring.action_guard import evaluate_response, register_enforcement_handler

    # In an API endpoint, after building the result:
    evaluate_response("agent_execute", result, metadata={"endpoint": "/agent/execute"})

    # To register a handler that is called on violations:
    def my_handler(violation: dict) -> None:
        ...
    register_enforcement_handler(my_handler)
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singleton MonitoringSystem cache
# ---------------------------------------------------------------------------

_monitoring = None


def _get_monitoring():
    """Return a shared MonitoringSystem instance, creating it on first call."""
    global _monitoring
    if _monitoring is None:
        try:
            from src.monitoring.monitoring_system import MonitoringSystem
            _monitoring = MonitoringSystem()
        except Exception as exc:
            logger.warning("MonitoringSystem unavailable: %s", exc)
    return _monitoring


# ---------------------------------------------------------------------------
# Enforcement handlers registry
# ---------------------------------------------------------------------------

_enforcement_handlers: List[Callable[[dict], None]] = []


def register_enforcement_handler(handler_fn: Callable[[dict], None]) -> None:
    """Register a callable that is invoked for every violation detected.

    The callable receives a single *violation* dict (as returned by
    ``MonitoringSystem.evaluate_action`` inside the ``violations`` list).
    Handlers are called in registration order.  Any exception raised by a
    handler is caught and logged so that remaining handlers still run.

    Args:
        handler_fn: Callable accepting a violation dict, returning None.
    """
    _enforcement_handlers.append(handler_fn)
    logger.debug("Registered enforcement handler: %s", getattr(handler_fn, "__name__", repr(handler_fn)))


def _dispatch_violations(violations: List[dict]) -> None:
    """Call all registered enforcement handlers for each violation."""
    if not _enforcement_handlers or not violations:
        return
    for violation in violations:
        for handler in _enforcement_handlers:
            try:
                handler(violation)
            except Exception as exc:
                logger.warning(
                    "Enforcement handler %s raised for violation %s: %s",
                    getattr(handler, "__name__", repr(handler)),
                    violation.get("rule_id", "?"),
                    exc,
                )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_response(
    action_type: str,
    response_data: Any,
    metadata: Optional[Dict[str, Any]] = None,
    *,
    agent_id: str = "aurora-api",
    context_tag: Optional[str] = None,
) -> None:
    """Evaluate an API response against ethics/compliance rules.

    Calls ``MonitoringSystem.evaluate_action`` and dispatches any violations
    to registered enforcement handlers.  This function **never raises** —
    any error is logged as a warning so that the caller's response path is
    not affected.

    Args:
        action_type: Semantic label for the action (e.g. ``"agent_execute"``).
        response_data: The response payload; included in *parameters* so that
            the ethics engine can inspect its content.
        metadata: Optional extra key/value pairs forwarded as evaluation
            parameters (e.g. ``{"endpoint": "/agent/execute"}``).
        agent_id: Identifier for the acting agent.  Defaults to
            ``"aurora-api"``.
        context_tag: DLP context tag forwarded to the monitoring system.
    """
    monitoring = _get_monitoring()
    if monitoring is None:
        return

    parameters: Dict[str, Any] = dict(metadata or {})
    # Include a lightweight representation of the response so the ethics
    # engine can reason about content without needing to serialise large
    # payloads.  We only store type and, for dicts, the top-level keys.
    if isinstance(response_data, dict):
        parameters["response_type"] = "dict"
        parameters["response_keys"] = list(response_data.keys())
    else:
        parameters["response_type"] = type(response_data).__name__

    try:
        evaluation = monitoring.evaluate_action(
            agent_id=agent_id,
            action_type=action_type,
            parameters=parameters,
            context_tag=context_tag,
        )
    except Exception as exc:
        logger.warning("Monitoring evaluation failed for %s: %s", action_type, exc)
        return

    # Dispatch violations to registered enforcement handlers.
    violations = evaluation.get("violations", [])
    if violations:
        logger.info(
            "MonitoringSystem flagged %d violation(s) for action=%s agent=%s",
            len(violations),
            action_type,
            agent_id,
        )
        _dispatch_violations(violations)


def clear_enforcement_handlers() -> None:
    """Remove all registered enforcement handlers.

    Primarily intended for use in tests to avoid cross-test pollution.
    """
    _enforcement_handlers.clear()
