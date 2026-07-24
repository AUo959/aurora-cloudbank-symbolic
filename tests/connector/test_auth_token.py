"""
Tests for connector/auth/token.py

Covers the v0.2+ HMAC Pilot seal (generate_pilot_seal / is_valid_pilot_seal)
and validate_environment.

These tests previously asserted the v0.1 substring-matching seal, which the
#822 hardening pass deliberately removed. Seals are now
``{operator_id}:{scope}:{exp_unix}:{hmac_hex}``, signed with
AURORA_PILOT_SEAL_SECRET and rejected once expired.
"""

import time

import pytest

from connector.auth.token import (
    REQUIRED_ENV_VARS,
    generate_pilot_seal,
    is_valid_pilot_seal,
    validate_environment,
)

SECRET = "test-pilot-seal-secret-not-for-production"


@pytest.fixture
def seal_secret(monkeypatch):
    """Configure the signing secret for seal generation and validation."""
    monkeypatch.setenv("AURORA_PILOT_SEAL_SECRET", SECRET)
    return SECRET


# ---------------------------------------------------------------------------
# generate_pilot_seal
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.security
def test_generated_seal_has_four_colon_separated_fields(seal_secret):
    seal = generate_pilot_seal("operator-1", scope="read")
    assert len(seal.split(":")) == 4  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_generate_requires_configured_secret(monkeypatch):
    monkeypatch.delenv("AURORA_PILOT_SEAL_SECRET", raising=False)
    with pytest.raises(RuntimeError):
        generate_pilot_seal("operator-1")


# ---------------------------------------------------------------------------
# is_valid_pilot_seal — acceptance
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.security
def test_freshly_generated_seal_validates(seal_secret):
    assert is_valid_pilot_seal(generate_pilot_seal("operator-1")) is True  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_seal_expiring_in_the_future_is_accepted(seal_secret):
    seal = generate_pilot_seal("operator-1", exp_seconds=60)
    assert int(seal.split(":")[2]) > time.time()  # nosec B101 - pytest assertion
    assert is_valid_pilot_seal(seal) is True  # nosec B101 - pytest assertion


# ---------------------------------------------------------------------------
# is_valid_pilot_seal — rejection
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.security
def test_seal_is_rejected_without_configured_secret(seal_secret, monkeypatch):
    seal = generate_pilot_seal("operator-1")
    monkeypatch.delenv("AURORA_PILOT_SEAL_SECRET", raising=False)
    assert is_valid_pilot_seal(seal) is False  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_seal_signed_with_a_different_secret_is_rejected(seal_secret, monkeypatch):
    seal = generate_pilot_seal("operator-1")
    monkeypatch.setenv("AURORA_PILOT_SEAL_SECRET", "a-different-secret")
    assert is_valid_pilot_seal(seal) is False  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_tampered_scope_is_rejected(seal_secret):
    """Escalating scope in a validly-signed seal must break the HMAC."""
    operator_id, _scope, exp, mac = generate_pilot_seal(
        "operator-1", scope="read"
    ).split(":")
    assert is_valid_pilot_seal(f"{operator_id}:write:{exp}:{mac}") is False  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_extended_expiry_is_rejected(seal_secret):
    """Pushing out the expiry must break the HMAC."""
    operator_id, scope, exp, mac = generate_pilot_seal("operator-1").split(":")
    forged_exp = int(exp) + 86_400
    assert is_valid_pilot_seal(f"{operator_id}:{scope}:{forged_exp}:{mac}") is False  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_expired_seal_is_rejected(seal_secret):
    seal = generate_pilot_seal("operator-1", exp_seconds=-1)
    assert is_valid_pilot_seal(seal) is False  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_non_integer_expiry_is_rejected(seal_secret):
    assert is_valid_pilot_seal("operator-1:read:not-a-number:deadbeef") is False  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.parametrize(
    "seal",
    [
        "",
        "wrong-seal-value",
        "operator-1:read",
        "operator-1:read:123",
        "operator-1:read:123:mac:extra",
    ],
)
def test_malformed_seals_are_rejected(seal_secret, seal):
    assert is_valid_pilot_seal(seal) is False  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_v0_1_substring_seal_is_rejected(seal_secret):
    """The pre-#822 substring seal must no longer validate."""
    assert is_valid_pilot_seal("AURORA-PILOT-SEAL-VERIFIED") is False  # nosec B101 - pytest assertion


# ---------------------------------------------------------------------------
# validate_environment
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_exits_on_missing_token(monkeypatch):
    for var in REQUIRED_ENV_VARS:
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(SystemExit) as exc_info:
        validate_environment()

    assert exc_info.value.code == 1  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_exits_on_missing_base_url(monkeypatch):
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-123")
    monkeypatch.delenv("AURORA_API_BASE_URL", raising=False)

    with pytest.raises(SystemExit) as exc_info:
        validate_environment()

    assert exc_info.value.code == 1  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_passes_with_required_vars(monkeypatch):
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-abc")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    monkeypatch.delenv("AURORA_PILOT_SEAL", raising=False)

    validate_environment()


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_accepts_valid_pilot_seal(seal_secret, monkeypatch):
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-abc")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("AURORA_PILOT_SEAL", generate_pilot_seal("operator-1"))

    validate_environment()


@pytest.mark.unit
@pytest.mark.security
def test_validate_environment_tolerates_invalid_pilot_seal(seal_secret, monkeypatch):
    """An invalid seal degrades to read-only rather than exiting."""
    monkeypatch.setenv("AURORA_CONNECTOR_TOKEN", "test-token-abc")
    monkeypatch.setenv("AURORA_API_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("AURORA_PILOT_SEAL", "not-a-valid-seal")

    validate_environment()
