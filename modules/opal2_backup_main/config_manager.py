"""Compatibility shim for legacy ConfigurationManager imports."""

from modules.opal2.config_manager import (  # noqa: F401
    ConfigChangeEvent,
    ConfigFileHandler,
    ConfigFormat,
    ConfigValidationRule,
    ConfigurationManager,
)

__all__ = [
    "ConfigChangeEvent",
    "ConfigFileHandler",
    "ConfigFormat",
    "ConfigValidationRule",
    "ConfigurationManager",
]
