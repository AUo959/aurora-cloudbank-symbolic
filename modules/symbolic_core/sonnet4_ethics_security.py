"""Sonnet compatibility adapter for model-agnostic ethics/security validation.

The model name is metadata, not a trust boundary. This module remains as a
compatibility surface for existing Sonnet imports while delegating enforcement
to the shared model-agnostic validation contract.
"""
from __future__ import annotations

from typing import Any, Dict

from modules.symbolic_core.model_validation import ModelAgnosticValidator, ModelValidationVerdict

SONNET_MODEL_ALIAS = "sonnet-4"


class EthicsValidator:
    """Ethics validation adapter for Sonnet-family operations."""

    def __init__(self, model_alias: str = SONNET_MODEL_ALIAS):
        self._validator = ModelAgnosticValidator(model_alias)

    def validate_request(self, request: Dict[str, Any]) -> ModelValidationVerdict:
        """Validate request through the shared ethics gate."""
        return self._validator.validate_ethics(request, direction="request")

    def validate_response(self, response: Dict[str, Any]) -> ModelValidationVerdict:
        """Validate response through the shared ethics gate."""
        return self._validator.validate_ethics(response, direction="response")


class SecurityValidator:
    """Security validation adapter for Sonnet-family operations."""

    def __init__(self, model_alias: str = SONNET_MODEL_ALIAS):
        self._validator = ModelAgnosticValidator(model_alias)

    def validate_input(self, input_data: Dict[str, Any]) -> ModelValidationVerdict:
        """Validate input through the shared model-agnostic security screen."""
        return self._validator.validate_security(input_data, direction="input")

    def validate_output(self, output_data: Dict[str, Any]) -> ModelValidationVerdict:
        """Validate output through the shared model-agnostic security screen."""
        return self._validator.validate_security(output_data, direction="output")
