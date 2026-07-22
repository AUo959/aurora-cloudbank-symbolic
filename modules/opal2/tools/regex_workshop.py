"""Deterministic regex composition and sample-testing reference tool."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ..tool_contract import (
    JsonObject,
    Opal2Tool,
    ToolExecutionContext,
    ToolInputError,
    ToolManifest,
)

REGEX_WORKSHOP_TOOL_ID = "opal2.regex.workshop"
MAX_LITERAL_LENGTH = 1_024
MAX_SAMPLES = 100
MAX_SAMPLE_LENGTH = 10_000

_FLAG_VALUES: dict[str, re.RegexFlag] = {
    "ignore_case": re.IGNORECASE,
    "multiline": re.MULTILINE,
    "dotall": re.DOTALL,
}
_FIXED_PATTERNS = {
    "integer": r"\A[+-]?\d+\Z",
    "decimal": r"\A[+-]?(?:\d+(?:\.\d*)?|\.\d+)\Z",
    "email": (
        r"\A[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
        r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+\Z"
    ),
    "uuid": (
        r"\A[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\Z"
    ),
    "iso_date": r"\A\d{4}-\d{2}-\d{2}\Z",
}
_LITERAL_TEMPLATES = {"exact", "contains", "starts_with", "ends_with", "word"}
_TEMPLATES = sorted(_FIXED_PATTERNS.keys() | _LITERAL_TEMPLATES)


class RegexWorkshopTool(Opal2Tool):
    """Build safe regex templates and evaluate bounded conformance samples."""

    manifest = ToolManifest(
        tool_id=REGEX_WORKSHOP_TOOL_ID,
        name="OPAL2 Regex Workshop",
        version="1.0.0",
        description=(
            "Compose deterministic regular expressions from curated templates "
            "and evaluate bounded sample expectations."
        ),
        capabilities=("regex-generation", "pattern-testing", "input-validation"),
        input_schema={
            "type": "object",
            "required": ["template"],
            "additionalProperties": False,
            "properties": {
                "template": {"type": "string", "enum": _TEMPLATES},
                "value": {"type": "string", "maxLength": MAX_LITERAL_LENGTH},
                "flags": {
                    "type": "array",
                    "items": {"type": "string", "enum": sorted(_FLAG_VALUES)},
                    "maxItems": len(_FLAG_VALUES),
                    "uniqueItems": True,
                },
                "samples": {
                    "type": "array",
                    "maxItems": MAX_SAMPLES,
                    "items": {
                        "type": "object",
                        "required": ["text"],
                        "additionalProperties": False,
                        "properties": {
                            "text": {
                                "type": "string",
                                "maxLength": MAX_SAMPLE_LENGTH,
                            },
                            "expected_match": {"type": ["boolean", "null"]},
                        },
                    },
                },
            },
        },
        output_schema={
            "type": "object",
            "required": [
                "pattern",
                "template",
                "flags",
                "samples",
                "expectations_evaluated",
                "all_expectations_met",
                "warnings",
            ],
            "additionalProperties": False,
            "properties": {
                "pattern": {"type": "string"},
                "template": {"type": "string"},
                "flags": {
                    "type": "array",
                    "items": {"type": "string", "enum": sorted(_FLAG_VALUES)},
                    "maxItems": len(_FLAG_VALUES),
                    "uniqueItems": True,
                },
                "samples": {
                    "type": "array",
                    "maxItems": MAX_SAMPLES,
                    "items": {
                        "type": "object",
                        "required": [
                            "text",
                            "matched",
                            "match",
                            "span",
                            "groups",
                            "expected_match",
                            "expectation_met",
                        ],
                        "additionalProperties": False,
                        "properties": {
                            "text": {"type": "string"},
                            "matched": {"type": "boolean"},
                            "match": {"type": ["string", "null"]},
                            "span": {
                                "type": ["array", "null"],
                                "items": {"type": "integer"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                            "groups": {
                                "type": "array",
                                "items": {"type": ["string", "null"]},
                            },
                            "expected_match": {"type": ["boolean", "null"]},
                            "expectation_met": {"type": ["boolean", "null"]},
                        },
                    },
                },
                "expectations_evaluated": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": MAX_SAMPLES,
                },
                "all_expectations_met": {"type": "boolean"},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
        },
        runtime="python",
        deterministic=True,
        side_effects=(),
        policy_profiles=("aurora",),
        export_targets=("python", "opaltool", "oci"),
    )

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        del context  # Policy selection is recorded by the registry execution envelope.
        template = payload["template"]
        pattern = _build_pattern(template, payload.get("value"))
        flag_names, flag_value = _validated_flags(payload.get("flags", []))
        samples = _validated_samples(payload.get("samples", []))
        compiled = re.compile(pattern, flag_value)

        results = [
            _evaluate_sample(compiled, text, expected) for text, expected in samples
        ]
        evaluated = sum(item["expected_match"] is not None for item in results)
        all_met = all(
            item["expectation_met"] is not False
            for item in results
            if item["expected_match"] is not None
        )
        warnings = []
        if template == "iso_date":
            warnings.append(
                "iso_date validates lexical shape only, not calendar validity"
            )

        return {
            "pattern": pattern,
            "template": template,
            "flags": list(flag_names),
            "samples": results,
            "expectations_evaluated": evaluated,
            "all_expectations_met": all_met,
            "warnings": warnings,
        }


def _build_pattern(template: str, value: Any) -> str:
    if template in _FIXED_PATTERNS:
        if value is not None:
            raise ToolInputError(f"template '{template}' does not accept value")
        return _FIXED_PATTERNS[template]

    if not isinstance(value, str):
        raise ToolInputError(f"template '{template}' requires a string value")
    if len(value) > MAX_LITERAL_LENGTH:
        raise ToolInputError(f"value exceeds {MAX_LITERAL_LENGTH} characters")

    escaped = re.escape(value)
    return {
        "exact": rf"\A{escaped}\Z",
        "contains": escaped,
        "starts_with": rf"\A{escaped}",
        "ends_with": rf"{escaped}\Z",
        "word": rf"\b{escaped}\b",
    }[template]


def _validated_flags(value: Any) -> tuple[tuple[str, ...], re.RegexFlag]:
    if not isinstance(value, (list, tuple)):
        raise ToolInputError("flags must be an array")
    if any(not isinstance(flag_name, str) for flag_name in value):
        raise ToolInputError("flags must contain only strings")
    if len(value) != len(set(value)):
        raise ToolInputError("flags must not contain duplicates")

    combined = re.NOFLAG
    for flag_name in value:
        if flag_name not in _FLAG_VALUES:
            raise ToolInputError(
                f"unsupported flag: {flag_name}; expected one of {sorted(_FLAG_VALUES)}"
            )
        combined |= _FLAG_VALUES[flag_name]
    return tuple(value), combined


def _validated_samples(value: Any) -> list[tuple[str, bool | None]]:
    if not isinstance(value, (list, tuple)):
        raise ToolInputError("samples must be an array")
    if len(value) > MAX_SAMPLES:
        raise ToolInputError(f"samples exceeds the limit of {MAX_SAMPLES}")

    return [_validated_sample(index, sample) for index, sample in enumerate(value)]


def _validated_sample(index: int, sample: Any) -> tuple[str, bool | None]:
    if not isinstance(sample, Mapping):
        raise ToolInputError(f"samples[{index}] must be an object")
    unexpected = set(sample) - {"text", "expected_match"}
    if unexpected:
        raise ToolInputError(
            f"samples[{index}] contains unexpected field: {min(unexpected)}"
        )
    text = sample.get("text")
    expected = sample.get("expected_match")
    if not isinstance(text, str):
        raise ToolInputError(f"samples[{index}].text must be a string")
    if len(text) > MAX_SAMPLE_LENGTH:
        raise ToolInputError(
            f"samples[{index}].text exceeds {MAX_SAMPLE_LENGTH} characters"
        )
    if expected is not None and not isinstance(expected, bool):
        raise ToolInputError(f"samples[{index}].expected_match must be a boolean")
    return text, expected


def _evaluate_sample(
    compiled: re.Pattern[str], text: str, expected: bool | None
) -> JsonObject:
    match = compiled.search(text)
    matched = match is not None
    return {
        "text": text,
        "matched": matched,
        "match": match.group(0) if match else None,
        "span": list(match.span()) if match else None,
        "groups": list(match.groups()) if match else [],
        "expected_match": expected,
        "expectation_met": matched == expected if expected is not None else None,
    }
