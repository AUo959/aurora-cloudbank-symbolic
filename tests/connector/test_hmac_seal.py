"""
Tests for HMAC-SHA256-based Pilot seal validation (issue #822).
"""

import time

import pytest

from connector.auth.token import generate_pilot_seal, is_valid_pilot_seal

_SECRET = "test-secret-do-not-use-in-production"


@pytest.mark.unit
def test_valid_seal_accepted(monkeypatch):
    """A freshly generated seal should pass validation."""
    monkeypatch.setenv("AURORA_PILOT_SEAL_SECRET", _SECRET)

    seal = generate_pilot_seal(operator_id="alice", scope="write", exp_seconds=3600)
    assert is_valid_pilot_seal(seal) is True


@pytest.mark.unit
def test_tampered_seal_rejected(monkeypatch):
    """Altering any part of the payload must invalidate the seal."""
    monkeypatch.setenv("AURORA_PILOT_SEAL_SECRET", _SECRET)

    seal = generate_pilot_seal(operator_id="alice", scope="write", exp_seconds=3600)

    # Tamper with the operator_id field
    parts = seal.split(":")
    parts[0] = "mallory"
    tampered = ":".join(parts)

    assert is_valid_pilot_seal(tampered) is False


@pytest.mark.unit
def test_expired_seal_rejected(monkeypatch):
    """A seal whose expiry timestamp is in the past must be rejected."""
    monkeypatch.setenv("AURORA_PILOT_SEAL_SECRET", _SECRET)

    # Generate a seal that expires immediately (0 seconds into the future).
    seal = generate_pilot_seal(operator_id="bob", scope="read", exp_seconds=0)

    # Wait just long enough for the timestamp to be in the past.
    time.sleep(0.05)

    assert is_valid_pilot_seal(seal) is False


@pytest.mark.unit
def test_no_secret_configured_returns_false(monkeypatch):
    """Without AURORA_PILOT_SEAL_SECRET set, validation must return False."""
    monkeypatch.delenv("AURORA_PILOT_SEAL_SECRET", raising=False)

    # Craft a syntactically valid-looking seal to confirm the secret check
    # is what causes rejection, not a format error.
    fake_seal = "alice:write:9999999999:deadbeefdeadbeef"
    assert is_valid_pilot_seal(fake_seal) is False


@pytest.mark.unit
def test_old_substring_seal_rejected(monkeypatch):
    """Legacy v0.1 substring-style seals must be rejected."""
    monkeypatch.setenv("AURORA_PILOT_SEAL_SECRET", _SECRET)

    old_seal = (
        "Continuity flows through coherence. "
        "The system remembers because we chose to align."
    )
    assert is_valid_pilot_seal(old_seal) is False
