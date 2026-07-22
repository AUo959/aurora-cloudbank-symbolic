"""Contract and execution tests for the OPAL2 tool foundry."""

import json

import pytest

from modules.opal2.tool_contract import (
    JsonObject,
    Opal2Tool,
    ToolContractError,
    ToolExecutionContext,
    ToolInputError,
    ToolManifest,
    ToolOutputError,
)
from modules.opal2.tool_registry import (
    ToolAlreadyRegisteredError,
    ToolNotFoundError,
    ToolRegistry,
)
from modules.opal2.tools import GLYPH_RENDER_TOOL_ID, GlyphRenderTool


class EchoTool(Opal2Tool):
    manifest = ToolManifest(
        tool_id="test.echo",
        name="Echo",
        version="1.0.0",
        description="Echo a string for registry tests.",
        capabilities=("echo",),
        input_schema={
            "type": "object",
            "required": ["text"],
            "additionalProperties": False,
            "properties": {"text": {"type": "string"}},
        },
        output_schema={
            "type": "object",
            "required": ["echo", "policy_profile"],
            "properties": {"echo": {"type": "string"}, "policy_profile": {}},
        },
        deterministic=True,
        policy_profiles=("aurora",),
    )

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        return {"echo": payload["text"], "policy_profile": context.policy_profile}


class NonPortableOutputTool(EchoTool):
    """Test fixture that violates the foundry's JSON portability guarantee."""

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        return {"echo": payload["text"], "policy_profile": object()}


@pytest.mark.unit
@pytest.mark.opal2
def test_manifest_rejects_nonportable_identifier():
    with pytest.raises(ToolContractError, match="tool_id"):
        ToolManifest(
            tool_id="Aurora Tool",
            name="Invalid",
            version="1.0.0",
            description="Invalid identifier.",
            capabilities=(),
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_registry_executes_with_portable_provenance():
    registry = ToolRegistry((EchoTool(),))
    context = ToolExecutionContext(run_id="opal2-run-test", policy_profile="aurora")

    result = await registry.run("test.echo", {"text": "coherence"}, context)

    assert result.run_id == "opal2-run-test"  # nosec B101 - pytest assertion
    assert result.output == {  # nosec B101 - pytest assertion
        "echo": "coherence",
        "policy_profile": "aurora",
    }
    assert result.provenance["runtime"] == "python"  # nosec B101 - pytest assertion
    assert len(result.provenance["manifest_sha256"]) == 64  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_registry_is_explicit_and_rejects_duplicate_or_missing_tools():
    registry = ToolRegistry((EchoTool(),))
    duplicate_tool = EchoTool()

    with pytest.raises(ToolAlreadyRegisteredError):
        registry.register(duplicate_tool)
    with pytest.raises(ToolNotFoundError):
        registry.get("test.missing")


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_registry_validates_required_input_before_execution():
    registry = ToolRegistry((EchoTool(),))

    with pytest.raises(ToolInputError, match="missing required field: text"):
        await registry.run("test.echo", {})

    unsupported_context = ToolExecutionContext(policy_profile="unknown")
    with pytest.raises(ToolInputError, match="does not support policy profile"):
        await registry.run(
            "test.echo",
            {"text": "coherence"},
            unsupported_context,
        )


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_registry_rejects_non_json_portable_output():
    registry = ToolRegistry((NonPortableOutputTool(),))

    with pytest.raises(ToolOutputError, match="JSON-serializable"):
        await registry.run("test.echo", {"text": "coherence"})


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "dimensions, expected_error",
    [
        ({"width": 320}, "dimensions missing required field: height"),
        (
            {"width": "320", "height": 200},
            "dimensions.width must be an integer",
        ),
        (
            {"width": 99, "height": 200},
            "dimensions.width must be between 100 and 4096",
        ),
    ],
)
async def test_glyph_renderer_rejects_invalid_dimensions(dimensions, expected_error):
    registry = ToolRegistry((GlyphRenderTool(),))

    with pytest.raises(ToolInputError, match=expected_error):
        await registry.run(
            GLYPH_RENDER_TOOL_ID,
            {
                "glyph_data": {"vertices": [], "indices": [], "dimensions": 2},
                "renderer": "svg",
                "dimensions": dimensions,
            },
        )


@pytest.mark.integration
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_glyph_renderer_is_a_json_portable_reference_tool():
    registry = ToolRegistry((GlyphRenderTool(),))

    result = await registry.run(
        GLYPH_RENDER_TOOL_ID,
        {
            "glyph_data": {
                "vertices": [[0, 0], [1, 1]],
                "indices": [0, 1],
                "dimensions": 2,
            },
            "renderer": "webgl",
            "dimensions": {"width": 320, "height": 200},
            "quantum_params": {"coherence_factor": 0.8},
        },
    )

    assert result.output["format"] == "webgl"  # nosec B101 - pytest assertion
    assert result.output["metadata"]["dimensions"] == {  # nosec B101 - pytest assertion
        "width": 320,
        "height": 200,
    }
    assert (  # nosec B101 - pytest assertion
        json.loads(json.dumps(result.to_dict()))["tool_id"] == GLYPH_RENDER_TOOL_ID
    )
