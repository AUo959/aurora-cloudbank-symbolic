"""Glyph renderer adapter implementing the portable OPAL2 tool contract."""

from __future__ import annotations

from ..quantum_renderer import QuantumRenderer
from ..tool_contract import (
    JsonObject,
    Opal2Tool,
    ToolExecutionContext,
    ToolInputError,
    ToolManifest,
    json_ready,
)


GLYPH_RENDER_TOOL_ID = "opal2.glyph.render"


class GlyphRenderTool(Opal2Tool):
    """Expose the surviving OPAL2 renderer as the first foundry tool."""

    manifest = ToolManifest(
        tool_id=GLYPH_RENDER_TOOL_ID,
        name="OPAL2 Glyph Renderer",
        version="2.1.0",
        description="Render symbolic glyph data through an OPAL2 rendering backend.",
        capabilities=("symbolic-rendering", "glyph-rendering", "quantum-visualization"),
        input_schema={
            "type": "object",
            "required": ["glyph_data"],
            "additionalProperties": False,
            "properties": {
                "glyph_data": {"type": "object"},
                "renderer": {
                    "type": "string",
                    "enum": [
                        "webgl",
                        "canvas",
                        "svg",
                        "quantum_field",
                        "holographic",
                        "geometric_algebra",
                    ],
                },
                "dimensions": {"type": "object"},
                "quantum_params": {"type": "object"},
            },
        },
        output_schema={
            "type": "object",
            "required": [
                "output",
                "format",
                "metadata",
                "render_time",
                "quantum_metrics",
            ],
            "properties": {
                "output": {},
                "format": {"type": "string"},
                "metadata": {"type": "object"},
                "render_time": {"type": "number"},
                "quantum_metrics": {"type": "object"},
                "cache_key": {},
            },
        },
        runtime="python",
        deterministic=False,
        side_effects=(),
        policy_profiles=("aurora",),
        export_targets=("python", "oci"),
    )

    def __init__(self, renderer: QuantumRenderer | None = None) -> None:
        self.renderer = renderer or QuantumRenderer()

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        renderer_name = payload.get("renderer", "webgl")
        if renderer_name not in self.renderer.list_renderers():
            raise ToolInputError(f"renderer is not available: {renderer_name}")

        result = await self.renderer.render_async(
            glyph_data=payload["glyph_data"],
            renderer=renderer_name,
            dimensions=payload.get("dimensions"),
            quantum_params=payload.get("quantum_params"),
            metadata={
                **dict(context.metadata),
                "opal2_run_id": context.run_id,
                "policy_profile": context.policy_profile,
            },
        )
        return json_ready(result.to_dict())
