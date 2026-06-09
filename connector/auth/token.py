"""
Token & Pilot Seal Validation
==============================
Validates the environment before the MCP server starts.

Two levels of auth:
  1. AURORA_CONNECTOR_TOKEN  -- Bearer token for Aurora API access (required)
  2. AURORA_PILOT_SEAL       -- Pilot continuity seal for elevated write ops (optional)

The Pilot seal is validated using HMAC-SHA256.  Seals are generated with
``generate_pilot_seal()`` and consist of a structured payload plus an HMAC
tag:

    {operator_id}:{scope}:{exp_unix}:{hmac_hex}

The HMAC is computed over ``{operator_id}:{scope}:{exp_unix}`` using the
secret stored in ``AURORA_PILOT_SEAL_SECRET``.

Write operations (v0.2+) require a valid Pilot seal in addition to the
bearer token.
"""

import functools
import hashlib
import hmac
import logging
import os
import sys
import time

log = logging.getLogger("aurora.connector.auth")

REQUIRED_ENV_VARS = ["AURORA_CONNECTOR_TOKEN", "AURORA_API_BASE_URL"]


# ---------------------------------------------------------------------------
# Seal generation
# ---------------------------------------------------------------------------


def generate_pilot_seal(
    operator_id: str,
    scope: str = "read",
    exp_seconds: int = 3600,
) -> str:
    """Generate a time-limited, HMAC-SHA256-signed Pilot seal.

    The returned seal has the form::

        {operator_id}:{scope}:{exp_unix}:{hmac_hex}

    where ``hmac_hex`` is the HMAC-SHA256 of the string
    ``{operator_id}:{scope}:{exp_unix}`` keyed with the value of the
    ``AURORA_PILOT_SEAL_SECRET`` environment variable.

    Args:
        operator_id: Identifier for the operator requesting elevated access.
        scope: Access scope, e.g. ``"read"`` or ``"write"``.
        exp_seconds: Lifetime of the seal in seconds (default 3600).

    Returns:
        A signed seal string.

    Raises:
        RuntimeError: If ``AURORA_PILOT_SEAL_SECRET`` is not set.
    """
    secret = os.getenv("AURORA_PILOT_SEAL_SECRET", "")
    if not secret:
        raise RuntimeError(
            "AURORA_PILOT_SEAL_SECRET must be set to generate a Pilot seal."
        )

    exp_unix = int(time.time()) + exp_seconds
    payload = f"{operator_id}:{scope}:{exp_unix}"
    mac = _compute_hmac(secret, payload)
    return f"{payload}:{mac}"


# ---------------------------------------------------------------------------
# Seal validation
# ---------------------------------------------------------------------------


def is_valid_pilot_seal(seal: str) -> bool:
    """Validate a Pilot seal using HMAC-SHA256 and expiry check.

    Expects the seal in the format produced by :func:`generate_pilot_seal`::

        {operator_id}:{scope}:{exp_unix}:{hmac_hex}

    Validation steps:

    1. ``AURORA_PILOT_SEAL_SECRET`` must be configured; if it is not, the
       function logs a warning and returns ``False``.
    2. The seal must contain exactly four colon-separated fields.
    3. The HMAC tag must match the recomputed tag (constant-time comparison).
    4. The ``exp_unix`` timestamp must be in the future.

    Old substring-style seals (v0.1) do not match this format and are
    therefore rejected.

    Args:
        seal: The seal string to validate.

    Returns:
        ``True`` if the seal is cryptographically valid and unexpired,
        ``False`` otherwise.
    """
    secret = os.getenv("AURORA_PILOT_SEAL_SECRET", "")
    if not secret:
        log.warning(
            "AURORA_PILOT_SEAL_SECRET is not configured; "
            "no Pilot seal can be validated."
        )
        return False

    parts = seal.split(":")
    if len(parts) != 4:
        return False

    operator_id, scope, exp_unix_str, provided_mac = parts

    # Verify HMAC first (timing-safe), then check expiry so we don't leak
    # timing information about which check failed.
    payload = f"{operator_id}:{scope}:{exp_unix_str}"
    expected_mac = _compute_hmac(secret, payload)

    if not hmac.compare_digest(expected_mac, provided_mac):
        return False

    try:
        exp_unix = int(exp_unix_str)
    except ValueError:
        return False

    if time.time() > exp_unix:
        return False

    return True


# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------


def validate_environment() -> None:
    """Validate required environment variables are present.

    Logs warnings for missing optional vars.
    Exits with code 1 if required vars are absent.
    """
    missing_required = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]

    if missing_required:
        log.error(
            "Missing required environment variables: %s\n"
            "Set them before starting the connector:",
            ", ".join(missing_required),
        )
        for var in missing_required:
            log.error("  export %s=<value>", var)
        sys.exit(1)

    pilot_seal = os.getenv("AURORA_PILOT_SEAL", "")
    if pilot_seal:
        if is_valid_pilot_seal(pilot_seal):
            log.info("Pilot seal validated. Elevated operations available (v0.2+).")
        else:
            log.warning(
                "AURORA_PILOT_SEAL provided but failed HMAC validation. "
                "Elevated operations will be unavailable."
            )
    else:
        log.info("No Pilot seal provided. Read-only mode active.")

    log.info(
        "Auth validated. Connecting to Aurora API at %s",
        os.getenv("AURORA_API_BASE_URL"),
    )


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def requires_pilot_seal(fn):
    """Decorator for tool handlers that require a valid Pilot seal.

    Applied to write operations in v0.2+.

    Usage::

        @requires_pilot_seal
        async def run(self, arguments: dict) -> str:
            ...
    """

    @functools.wraps(fn)
    async def wrapper(self, arguments: dict) -> str:
        pilot_seal = os.getenv("AURORA_PILOT_SEAL", "")
        if not is_valid_pilot_seal(pilot_seal):
            return (
                '{"error": "Pilot seal required for this operation. '
                'Set AURORA_PILOT_SEAL environment variable.", '
                '"operation": "write", "status": "denied"}'
            )
        return await fn(self, arguments)

    return wrapper


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _compute_hmac(secret: str, message: str) -> str:
    """Return the lowercase hex HMAC-SHA256 of *message* keyed with *secret*."""
    return hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
