"""Log-injection regression tests for the event coordination surface.

CodeQL reported py/log-injection across this module and it was dismissed as
"won't fix" with no recorded rationale. Re-examined during a dismissal audit,
it was a true positive and reachable:

    api/aurora_api.py mounts src.coordination.event_api
      -> SubscribeRequest.agent_id was an unvalidated str
      -> passed verbatim to EventCoordinationRegistry.subscribe()
      -> logged with a raw f-string

A newline in agent_id therefore produced a second, fully-formed log entry
that reads as though the system emitted it.

Note truncation is *not* a defence. Several sites in this codebase apply
[:100] to logged values, which caps length but preserves control characters —
see test_truncation_alone_does_not_neutralise_newlines below.
"""

import asyncio
import io
import logging

import pytest

from src.core.logging_security import safe_str

EVIL_ID = "attacker\nCRITICAL:audit:ADMIN OVERRIDE GRANTED to attacker"


@pytest.mark.unit
@pytest.mark.security
def test_truncation_alone_does_not_neutralise_newlines():
    """[:N] limits length but leaves the injection intact; safe_str removes it."""
    assert "\n" in EVIL_ID[:100], "truncation unexpectedly stripped the newline"
    assert "\n" not in safe_str(EVIL_ID)
    assert "\r" not in safe_str(EVIL_ID)


@pytest.mark.unit
@pytest.mark.security
def test_registry_logging_cannot_forge_a_log_entry():
    """A crafted agent id must not produce an additional log line."""
    from src.coordination.event_registry import EventCoordinationRegistry, EventFilter

    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    previous_level = root.level
    root.setLevel(logging.INFO)
    try:
        async def scenario():
            registry = EventCoordinationRegistry()
            await registry.subscribe(agent_id=EVIL_ID, event_filter=EventFilter())

        asyncio.run(scenario())
    finally:
        root.removeHandler(handler)
        root.setLevel(previous_level)

    output = buffer.getvalue()
    forged = [line for line in output.splitlines() if line.startswith("CRITICAL:audit:")]
    assert not forged, f"crafted agent id forged a log entry: {forged}"

    # The value should still be present, just rendered inert on one line.
    assert "attacker" in output


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize(
    "payload",
    [
        "attacker\nCRITICAL:audit:forged",
        "attacker\r\nWARNING:root:forged",
        "attacker\roverwrite",
    ],
)
def test_identifiers_with_control_characters_are_rejected_at_the_boundary(payload):
    """Control characters must not enter the system through a request identifier."""
    from pydantic import ValidationError

    from src.coordination.event_api import LockRequest, SubscribeRequest

    with pytest.raises(ValidationError):
        SubscribeRequest(agent_id=payload)

    with pytest.raises(ValidationError):
        LockRequest(agent_id="valid-agent", resource_id=payload)


@pytest.mark.unit
@pytest.mark.security
def test_ordinary_identifiers_still_accepted():
    """The constraint must not reject the identifiers the system actually uses."""
    from src.coordination.event_api import LockRequest, SubscribeRequest

    assert SubscribeRequest(agent_id="r2-agent-001").agent_id == "r2-agent-001"
    lock = LockRequest(agent_id="agent.v2:1", resource_id="mem-01")
    assert lock.resource_id == "mem-01"
