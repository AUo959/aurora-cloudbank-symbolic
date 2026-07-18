"""Portable contracts for tools hosted by the OPAL2 foundry.

The contract deliberately contains no Aurora-specific policy or continuity
types. Platform policy is selected through ``policy_profile`` at execution
time so the same tool can run in Aurora and in a neutral OPAL2 runtime.
"""

from __future__ import annotations

import json
import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Tuple


JsonObject = Dict[str, Any]
_TOOL_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class ToolContractError(ValueError):
    """Base error for invalid manifests and payloads."""


class ToolInputError(ToolContractError):
    """Raised when a tool payload violates its declared input contract."""


class ToolOutputError(ToolContractError):
    """Raised when a tool returns data that violates its output contract."""


@dataclass(frozen=True)
class ToolManifest:
    """Machine-readable identity and execution contract for an OPAL2 tool."""

    tool_id: str
    name: str
    version: str
    description: str
    capabilities: Tuple[str, ...]
    input_schema: Mapping[str, Any]
    output_schema: Mapping[str, Any]
    runtime: str = "python"
    deterministic: bool = False
    side_effects: Tuple[str, ...] = ()
    policy_profiles: Tuple[str, ...] = ()
    export_targets: Tuple[str, ...] = ("python",)

    def __post_init__(self) -> None:
        if not _TOOL_ID_PATTERN.fullmatch(self.tool_id):
            raise ToolContractError(
                "tool_id must start with a lowercase letter or digit and contain only lowercase letters, "
                "digits, dots, underscores, or hyphens"
            )
        if not self.name.strip():
            raise ToolContractError("tool name must not be empty")
        if not self.version.strip():
            raise ToolContractError("tool version must not be empty")
        for schema_name, schema in (
            ("input_schema", self.input_schema),
            ("output_schema", self.output_schema),
        ):
            if schema.get("type", "object") != "object":
                raise ToolContractError(
                    f"{schema_name} must describe a top-level object"
                )

    def to_dict(self) -> JsonObject:
        """Return a JSON-serializable manifest representation."""

        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "capabilities": list(self.capabilities),
            "input_schema": dict(self.input_schema),
            "output_schema": dict(self.output_schema),
            "runtime": self.runtime,
            "deterministic": self.deterministic,
            "side_effects": list(self.side_effects),
            "policy_profiles": list(self.policy_profiles),
            "export_targets": list(self.export_targets),
        }


@dataclass(frozen=True)
class ToolExecutionContext:
    """Portable context supplied to every tool execution."""

    run_id: str = field(default_factory=lambda: f"opal2-run-{uuid.uuid4().hex}")
    policy_profile: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ToolRunResult:
    """Standard execution envelope returned by the foundry registry."""

    run_id: str
    tool_id: str
    tool_version: str
    output: JsonObject
    duration_ms: float
    provenance: Mapping[str, Any]

    def to_dict(self) -> JsonObject:
        return {
            "run_id": self.run_id,
            "tool_id": self.tool_id,
            "tool_version": self.tool_version,
            "output": self.output,
            "duration_ms": self.duration_ms,
            "provenance": dict(self.provenance),
        }


class Opal2Tool(ABC):
    """Base interface implemented by tools hosted by OPAL2."""

    manifest: ToolManifest

    def validate_input(self, payload: Mapping[str, Any]) -> None:
        _validate_object(payload, self.manifest.input_schema, ToolInputError)

    def validate_output(self, output: Mapping[str, Any]) -> None:
        _validate_object(output, self.manifest.output_schema, ToolOutputError)

    @abstractmethod
    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        """Execute the tool for a validated payload."""


def _validate_object(
    value: Mapping[str, Any],
    schema: Mapping[str, Any],
    error_type: type[ToolContractError],
) -> None:
    """Validate the small JSON-Schema subset required by Phase 1.

    Full JSON-Schema conformance belongs in the packaging/conformance phase.
    This runtime check intentionally covers top-level required fields, types,
    and enums without adding another dependency to the portable core.
    """

    if not isinstance(value, Mapping):
        raise error_type("payload must be an object")

    _validate_required_fields(value, schema, error_type)

    properties = schema.get("properties", {})
    for field_name, field_value in value.items():
        _validate_field(
            field_name,
            field_value,
            properties.get(field_name),
            schema.get("additionalProperties", True),
            error_type,
        )


def _validate_required_fields(
    value: Mapping[str, Any],
    schema: Mapping[str, Any],
    error_type: type[ToolContractError],
) -> None:
    missing_fields = [
        field_name
        for field_name in schema.get("required", ())
        if field_name not in value
    ]
    if missing_fields:
        raise error_type(f"missing required field: {missing_fields[0]}")


def _validate_field(
    field_name: str,
    field_value: Any,
    field_schema: Mapping[str, Any] | None,
    additional_properties: bool,
    error_type: type[ToolContractError],
) -> None:
    if field_schema is None:
        if additional_properties is False:
            raise error_type(f"unexpected field: {field_name}")
        return

    expected_type = field_schema.get("type")
    if expected_type and not _matches_json_type(field_value, expected_type):
        raise error_type(f"field '{field_name}' must be of type {expected_type}")

    allowed_values = field_schema.get("enum")
    if allowed_values is not None and field_value not in allowed_values:
        raise error_type(f"field '{field_name}' must be one of {allowed_values}")


def _matches_json_type(value: Any, expected_type: str) -> bool:
    type_checks = {
        "object": lambda item: isinstance(item, Mapping),
        "array": lambda item: isinstance(item, (list, tuple)),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: (
            isinstance(item, (int, float)) and not isinstance(item, bool)
        ),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    checker = type_checks.get(expected_type)
    return checker(value) if checker else True


def json_ready(value: Any) -> Any:
    """Normalize common scientific Python values for API and package output."""

    return json.loads(json.dumps(value, default=_json_default))


def _json_default(value: Any) -> Any:
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item"):
        return value.item()
    return str(value)
