"""
Tests for connector/auth/token.py
Covers: is_valid_pilot_seal, validate_environment (missing vars, all vars present).
"""

import os
import sys

import pytest

from connector.auth.token import (
    PILOT_SEAL_SIGNATURE,
    REQUIRED_ENV_VARS,
    is_valid_pilot_seal,
    validate_environment,
)


# ---------------------------------------------------------------------------
# is_valid_pilot_seal
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.security
def test_valid_pilot_seal_exact_match():
    """Exact PILOT_SEAL_SIGNATURE string must return True."""
    assert is_valid_pilot_seal(PILOT_SEAL_SIGNATURE) is True


@pytest.mark.unit
@pytest.mark.security
def test_valid_pilot_seal_case_insensitive():
    """Seal validation is case-insensitive; uppercased seal must still pass."""
    assert is_valid_pilot_seal(PILOT_SEAL_SIGNATURE.upper()) is True


@pytest.mark.unit
@pytest.mark.security
def test_valid_pilot_seal_embedded_in_longer_string():
    """Seal signature embedded inside a longer string must still validate."""
    wrapped = f"PREFIX {PILOT_SEAL_SIGNATURE} SUFFIX"
    assert is_valid_pilot_seal(wrapped) is True


@pytest.mark.unit
@pytest.mark.security
def test_invalid_pilot_seal_wrong_string():
    """A completely wrong seal string must return False."""
    assert is_valid_pilot_seal("wrong-seal-value") is False


@pytest.mark.unit
@pytest.mark.security
def test_invalid_pilot_seal_empty_string():
    """An empty seal must return False."""
    assert is_valid_pilot_seal("") is False


@pytest.mark.unit
@pytest.mark.security
def test_invalid_pilot_seal_partial_match():
    """A partial / truncated seal must return False."""
    partial = PILOT_SEAL_SIGNATURE[:10]
    assert is_valid_pilot_seal(partial) is False


# ---------------------------------------------------------------------------
# validate_environment
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_exits_on_missing_token(monkeypatch):
    """validate_environment() must call sys.exit(1) when AURORA_CONNECTOR_TOKEN is absent."""
    # Remove all required env vars
    for var in REQUIRED_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(SystemExit) as exc_info:
        validate_environment()

    assert exc_info.value.code == 1


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_exits_on_missing_base_url(monkeypatch):
    """validate_environment() must call sys.exit(1) when AURORA_API_BASE_URL is absent."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-123")
    monkeypatch.delenv("AURORA_API_BASE_URL", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        validate_environment()

    assert exc_info.value.code == 1


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_passes_with_required_vars(monkeypatch):
    """validate_environment() must not raise or exit when all required vars are set."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-abc")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    # Remove optional pilot seal so we don't accidentally trigger its branch
    monkeypatch.delenv("AURORA_PILOT_SEAL", raising=False)

    # Must not raise SystemExit
    validate_environment()


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_accepts_valid_pilot_seal(monkeypatch):
    """validate_environment() must accept a valid pilot seal without exiting."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-abc")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("AURORA_PILOT_SEAL", PILOT_SEAL_SIGNATURE)

    # Must not raise
    validate_environment()


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_accepts_invalid_pilot_seal_with_warning(monkeypatch):
    """
    validate_environment() must not exit for an invalid pilot seal —
    it only logs a warning. Exit is reserved for missing required vars.
    """
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-abc")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("AURORA_PILOT_SEAL", "bad-seal-value")

    # Must not raise
    validate_environment()
