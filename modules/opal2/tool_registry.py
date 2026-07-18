"""Explicit registry and execution boundary for OPAL2 tools."""

from __future__ import annotations

import hashlib
import json
from time import perf_counter
from typing import Dict, Iterable

from .tool_contract import (
    JsonObject,
    Opal2Tool,
    ToolExecutionContext,
    ToolInputError,
    ToolManifest,
    ToolRunResult,
)


class ToolRegistryError(RuntimeError):
    """Base registry error."""


class ToolAlreadyRegisteredError(ToolRegistryError):
    """Raised when a duplicate tool ID is registered without replacement."""


class ToolNotFoundError(ToolRegistryError):
    """Raised when a requested tool is not registered."""


class ToolRegistry:
    """Registry for explicitly trusted OPAL2 tool instances.

    Phase 1 intentionally does not discover or import arbitrary code. Package
    verification, signatures, and sandboxed workers must exist before remote
    or user-supplied tools can enter this registry.
    """

    def __init__(self, tools: Iterable[Opal2Tool] = ()) -> None:
        self._tools: Dict[str, Opal2Tool] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: Opal2Tool, *, replace: bool = False) -> None:
        if not isinstance(tool, Opal2Tool):
            raise ToolRegistryError("registered tools must implement Opal2Tool")
        tool_id = tool.manifest.tool_id
        if tool_id in self._tools and not replace:
            raise ToolAlreadyRegisteredError(f"tool already registered: {tool_id}")
        self._tools[tool_id] = tool

    def get(self, tool_id: str) -> Opal2Tool:
        try:
            return self._tools[tool_id]
        except KeyError as exc:
            raise ToolNotFoundError(f"tool not found: {tool_id}") from exc

    def get_manifest(self, tool_id: str) -> ToolManifest:
        return self.get(tool_id).manifest

    def list_manifests(self) -> list[JsonObject]:
        return [
            self._tools[tool_id].manifest.to_dict() for tool_id in sorted(self._tools)
        ]

    async def run(
        self,
        tool_id: str,
        payload: JsonObject,
        context: ToolExecutionContext | None = None,
    ) -> ToolRunResult:
        tool = self.get(tool_id)
        execution_context = context or ToolExecutionContext()
        if (
            execution_context.policy_profile
            and execution_context.policy_profile not in tool.manifest.policy_profiles
        ):
            raise ToolInputError(
                f"tool '{tool_id}' does not support policy profile: {execution_context.policy_profile}"
            )
        tool.validate_input(payload)

        start = perf_counter()
        output = await tool.run(dict(payload), execution_context)
        duration_ms = (perf_counter() - start) * 1000
        tool.validate_output(output)

        manifest = tool.manifest.to_dict()
        manifest_digest = hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return ToolRunResult(
            run_id=execution_context.run_id,
            tool_id=tool.manifest.tool_id,
            tool_version=tool.manifest.version,
            output=dict(output),
            duration_ms=duration_ms,
            provenance={
                "manifest_sha256": manifest_digest,
                "runtime": tool.manifest.runtime,
                "policy_profile": execution_context.policy_profile,
            },
        )
