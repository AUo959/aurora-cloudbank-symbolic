"""Conformance tests for the neutral OPAL2 regex workshop tool."""

import pytest
from jsonschema import Draft7Validator, ValidationError

from modules.opal2.tool_contract import ToolExecutionContext, ToolInputError
from modules.opal2.tool_registry import ToolRegistry
from modules.opal2.tools.regex_workshop import (
    MAX_SAMPLE_LENGTH,
    REGEX_WORKSHOP_TOOL_ID,
    RegexWorkshopTool,
)


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_regex_workshop_builds_escaped_literal_pattern():
    tool = RegexWorkshopTool()
    registry = ToolRegistry((tool,))
    payload = {
        "template": "exact",
        "value": "station[808]",
        "flags": ["ignore_case"],
        "samples": [
            {"text": "STATION[808]", "expected_match": True},
            {"text": "station808", "expected_match": False},
        ],
    }

    result = await registry.run(
        REGEX_WORKSHOP_TOOL_ID,
        payload,
    )

    Draft7Validator(tool.manifest.input_schema).validate(payload)
    Draft7Validator(tool.manifest.output_schema).validate(result.output)

    assert result.output["pattern"] == r"\Astation\[808\]\Z"  # nosec B101 - pytest assertion
    assert result.output["all_expectations_met"] is True  # nosec B101 - pytest assertion
    assert result.output["expectations_evaluated"] == 2  # nosec B101 - pytest assertion
    assert result.provenance["runtime"] == "python"  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_regex_workshop_manifest_rejects_malformed_collection_items():
    manifest = RegexWorkshopTool.manifest
    Draft7Validator.check_schema(manifest.input_schema)
    Draft7Validator.check_schema(manifest.output_schema)
    validator = Draft7Validator(manifest.input_schema)

    with pytest.raises(ValidationError):
        validator.validate({"template": "integer", "flags": [1]})
    with pytest.raises(ValidationError):
        validator.validate({"template": "integer", "flags": ["dotall", "dotall"]})
    with pytest.raises(ValidationError):
        validator.validate({"template": "integer", "samples": [{"text": 42}]})
    with pytest.raises(ValidationError):
        validator.validate(
            {"template": "integer", "samples": [{"text": "42", "extra": True}]}
        )


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "template, matching, rejected",
    [
        ("integer", "+42", "4.2"),
        ("decimal", "-4.2", "4.2.1"),
        ("email", "crew@example.org", "crew@example"),
        ("uuid", "123e4567-e89b-12d3-a456-426614174000", "not-a-uuid"),
        ("iso_date", "2026-07-18", "07/18/2026"),
    ],
)
async def test_regex_workshop_fixed_templates(template, matching, rejected):
    registry = ToolRegistry((RegexWorkshopTool(),))

    result = await registry.run(
        REGEX_WORKSHOP_TOOL_ID,
        {
            "template": template,
            "samples": [
                {"text": matching, "expected_match": True},
                {"text": rejected, "expected_match": False},
            ],
        },
    )

    assert result.output["all_expectations_met"] is True  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload, expected_error",
    [
        ({"template": "exact"}, "requires a string value"),
        ({"template": "integer", "value": "42"}, "does not accept value"),
        (
            {"template": "contains", "value": "x", "flags": ["ascii"]},
            "unsupported flag",
        ),
        (
            {"template": "contains", "value": "x", "flags": [{}]},
            "only strings",
        ),
        (
            {
                "template": "contains",
                "value": "x",
                "samples": [{"text": "x" * (MAX_SAMPLE_LENGTH + 1)}],
            },
            "exceeds",
        ),
    ],
)
async def test_regex_workshop_rejects_unbounded_or_ambiguous_input(
    payload, expected_error
):
    registry = ToolRegistry((RegexWorkshopTool(),))

    with pytest.raises(ToolInputError, match=expected_error):
        await registry.run(REGEX_WORKSHOP_TOOL_ID, payload)


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_regex_workshop_supports_aurora_as_optional_profile():
    registry = ToolRegistry((RegexWorkshopTool(),))

    result = await registry.run(
        REGEX_WORKSHOP_TOOL_ID,
        {"template": "word", "value": "anchor"},
        ToolExecutionContext(policy_profile="aurora"),
    )

    assert result.output["pattern"] == r"\banchor\b"  # nosec B101 - pytest assertion
    assert result.provenance["policy_profile"] == "aurora"  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_regex_workshop_multiline_cannot_weaken_document_anchors():
    registry = ToolRegistry((RegexWorkshopTool(),))

    result = await registry.run(
        REGEX_WORKSHOP_TOOL_ID,
        {
            "template": "integer",
            "flags": ["multiline"],
            "samples": [{"text": "prefix\n42", "expected_match": False}],
        },
    )

    assert result.output["all_expectations_met"] is True  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_regex_workshop_accepts_contract_compatible_tuple_arrays():
    registry = ToolRegistry((RegexWorkshopTool(),))

    result = await registry.run(
        REGEX_WORKSHOP_TOOL_ID,
        {
            "template": "exact",
            "value": "anchor",
            "flags": ("ignore_case",),
            "samples": ({"text": "ANCHOR", "expected_match": True},),
        },
    )

    assert result.output["all_expectations_met"] is True  # nosec B101 - pytest assertion
