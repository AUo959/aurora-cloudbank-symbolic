"""Centralized application settings validated at startup."""
from __future__ import annotations

import logging
import sys
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Env vars that MUST be non-empty for the app to boot correctly.
_CRITICAL_VARS = ("CSRF_SECRET_KEY", "AURORA_SECRET_KEY")

# Env vars that are used but for which a warning (not a hard failure) is sufficient.
_IMPORTANT_VARS = ("JWT_SECRET_KEY", "WS_AUTH_SECRET", "AES_KEY_256_HEX")


class AuroraSettings(BaseSettings):
    """Validated environment configuration for Aurora CloudBank API.

    Critical vars raise ValueError on validation if empty; important vars
    emit warnings. Instantiate once at startup; do not re-instantiate.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # --- Critical (fail-closed) ---
    csrf_secret_key: str = ""
    aurora_secret_key: str = ""

    # --- Important (warn-only) ---
    jwt_secret_key: str = ""
    ws_auth_secret: str = ""
    aes_key_256_hex: str = ""

    # --- Optional / operational ---
    aurora_build_phase: str = "0"
    monitoring_storage_dir: Optional[str] = None
    aurora_state_root: Optional[str] = None
    aurora_monitoring_path: Optional[str] = None
    aurora_ledger_path: Optional[str] = None
    openai_api_key: str = ""
    mesh_openai_model: str = "gpt-4.1-mini"

    @model_validator(mode="after")
    def check_critical_vars(self) -> "AuroraSettings":
        build_phase = self.aurora_build_phase.strip() == "1"
        if build_phase:
            return self
        missing = [v for v in _CRITICAL_VARS if not getattr(self, v.lower(), "")]
        if missing:
            raise ValueError(
                f"Critical env var(s) missing or empty at startup: {', '.join(missing)}. "
                "Set them before starting the API."
            )
        for v in _IMPORTANT_VARS:
            if not getattr(self, v.lower(), ""):
                logger.warning(
                    "Important env var %s is not set — related features may be degraded.", v
                )
        return self


def load_settings(exit_on_error: bool = True) -> Optional[AuroraSettings]:
    """Load and validate application settings.

    Args:
        exit_on_error: When True (default), call sys.exit(1) on validation failure
                       so container orchestrators detect a bad boot.

    Returns:
        AuroraSettings on success; None if exit_on_error=False and validation fails.
    """
    try:
        return AuroraSettings()
    except Exception as exc:
        logger.critical("Aurora startup failed — invalid configuration: %s", exc)
        if exit_on_error:
            sys.exit(1)
        return None
