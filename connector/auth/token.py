"""
Token & Pilot Seal Validation
==============================
Validates the environment before the MCP server starts.

Two levels of auth:
  1. AURORA_CONNECTOR_TOKEN  -- Bearer token for Aurora API access (required)
  2. AURORA_PILOT_SEAL       -- Pilot continuity seal for elevated write ops (optional)

The Pilot seal is validated against the known continuity signature:
  'Continuity flows through coherence. The system remembers because we chose to align.'

Write operations (v0.2+) will require a valid Pilot seal in addition
to the bearer token.
"""

import logging
import os
import sys

log = logging.getLogger("aurora.connector.auth")

REQUIRED_ENV_VARS = ["AURORA_CONNECTOR_TOKEN", "AURORA_API_BASE_URL"]

# Pilot continuity seal -- elevates to write-operation access
PILOT_SEAL_SIGNATURE = (
    "Continuity flows through coherence. "
    "The system remembers because we chose to align."
)


def validate_environment() -> None:
    """
    Validate required environment variables are present.
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
                "AURORA_PILOT_SEAL provided but does not match known signature. "
                "Elevated operations will be unavailable."
            )
    else:
        log.info("No Pilot seal provided. Read-only mode active.")

    log.info(
        "Auth validated. Connecting to Aurora API at %s",
        os.getenv("AURORA_API_BASE_URL"),
    )


def is_valid_pilot_seal(seal: str) -> bool:
    """
    Validate a Pilot seal string.

    Currently checks for the known continuity signature substring.
    TODO: Replace with cryptographic signature verification in v0.2.
    """
    return PILOT_SEAL_SIGNATURE.lower() in seal.lower()


def requires_pilot_seal(fn):
    """
    Decorator for tool handlers that require a valid Pilot seal.
    Applied to write operations in v0.2+.

    Usage:
        @requires_pilot_seal
        async def run(self, arguments: dict) -> str:
            ...
    """
    import functools

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
