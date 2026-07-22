"""Glyph renderer adapter implementing the portable OPAL2 tool contract."""

from __future__ import annotations

from collections.abc import Mapping

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
MIN_RENDER_DIMENSION = 100
MAX_RENDER_DIMENSION = 4096


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
                "dimensions": {
                    "type": "object",
                    "required": ["width", "height"],
                    "additionalProperties": False,
                    "properties": {
                        "width": {
                            "type": "integer",
                            "minimum": MIN_RENDER_DIMENSION,
                            "maximum": MAX_RENDER_DIMENSION,
                        },
                        "height": {
                            "type": "integer",
                            "minimum": MIN_RENDER_DIMENSION,
                            "maximum": MAX_RENDER_DIMENSION,
                        },
                    },
                },
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

    @staticmethod
    def _dimension_mapping(value: object) -> Mapping[str, object]:
        """Validate the dimension object's required and allowed fields."""

        if not isinstance(value, Mapping):
            raise ToolInputError("dimensions must be an object")

        expected_fields = {"width", "height"}
        missing_fields = expected_fields - value.keys()
        if missing_fields:
            missing = sorted(missing_fields)[0]
            raise ToolInputError(f"dimensions missing required field: {missing}")

        unexpected_fields = value.keys() - expected_fields
        if unexpected_fields:
            unexpected = sorted(unexpected_fields)[0]
            raise ToolInputError(f"dimensions contains unexpected field: {unexpected}")
        return value

    @staticmethod
    def _validated_dimension(field_name: str, value: object) -> int:
        """Validate one dimension against the established OPAL2 graphics bounds."""

        if type(value) is not int:
            raise ToolInputError(f"dimensions.{field_name} must be an integer")
        if not MIN_RENDER_DIMENSION <= value <= MAX_RENDER_DIMENSION:
            raise ToolInputError(
                f"dimensions.{field_name} must be between "
                f"{MIN_RENDER_DIMENSION} and {MAX_RENDER_DIMENSION}"
            )
        return value

    @classmethod
    def _validated_dimensions(cls, value: object) -> dict[str, int] | None:
        """Validate renderer dimensions beyond the Phase 1 top-level schema subset."""

        if value is None:
            return None
        dimensions = cls._dimension_mapping(value)
        return {
            field_name: cls._validated_dimension(field_name, dimensions[field_name])
            for field_name in ("width", "height")
        }

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        renderer_name = payload.get("renderer", "webgl")
        if renderer_name not in self.renderer.list_renderers():
            raise ToolInputError(f"renderer is not available: {renderer_name}")
        dimensions = self._validated_dimensions(payload.get("dimensions"))

        result = await self.renderer.render_async(
            glyph_data=payload["glyph_data"],
            renderer=renderer_name,
            dimensions=dimensions,
            quantum_params=payload.get("quantum_params"),
            metadata={
                **dict(context.metadata),
                "opal2_run_id": context.run_id,
                "policy_profile": context.policy_profile,
            },
        )
        return json_ready(result.to_dict())
