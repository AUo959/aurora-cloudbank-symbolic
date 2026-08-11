"""Portable SHERLOCK -> WATSON evidence-to-understanding protocol core.

This module deliberately separates *investigation* from *interpretation*.
SHERLOCK seals a provenance-sensitive evidence case file. WATSON may consume
that exact case file and attach contextual synthesis, but it cannot rewrite the
SHERLOCK record without invalidating the digest chain.

The core is provider-neutral. It does not fetch sources or call a language
model. Retrieval/model adapters can produce the evidence and synthesis payloads
while this module provides the portable integrity boundary that makes those
agents auditable across OPAL2, Aurora, or a neutral host.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from ..tool_contract import (
    JsonObject,
    Opal2Tool,
    ToolExecutionContext,
    ToolInputError,
    ToolManifest,
)

SHERLOCK_TOOL_ID = "opal2.sherlock.casefile"
WATSON_TOOL_ID = "opal2.watson.brief"
SHERLOCK_WATSON_VERIFY_TOOL_ID = "opal2.sherlock-watson.verify"

SHERLOCK_SCHEMA = "opal2.sherlock.casefile.v1"
WATSON_SCHEMA = "opal2.watson.brief.v1"
BUNDLE_SCHEMA = "opal2.sherlock-watson.bundle.v1"

_REQUIRED_CASE_FIELDS = (
    "subject",
    "sources",
    "observations",
    "established_facts",
    "derived_findings",
    "contradictions",
    "unresolved",
)
_REQUIRED_BRIEF_FIELDS = (
    "summary",
    "correlations",
    "interpretations",
    "hypotheses",
    "recommendations",
    "residual_uncertainty",
)


def _canonical_bytes(value: Any) -> bytes:
    try:
        encoded = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ToolInputError("artifact must be canonical JSON data") from exc
    return encoded.encode("utf-8")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ToolInputError(f"{name} must be an object")
    return value


def _require_array(value: Any, name: str) -> Sequence[Any]:
    if not isinstance(value, (list, tuple)) or isinstance(value, (str, bytes)):
        raise ToolInputError(f"{name} must be an array")
    return value


def _require_nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ToolInputError(f"{name} must be a non-empty string")
    return value


def _validate_case(case: Any) -> JsonObject:
    case_map = _require_mapping(case, "case")
    for field_name in _REQUIRED_CASE_FIELDS:
        if field_name not in case_map:
            raise ToolInputError(f"case missing required field: {field_name}")

    _require_nonempty_string(case_map["subject"], "case.subject")
    for field_name in (
        "sources",
        "observations",
        "established_facts",
        "derived_findings",
        "contradictions",
        "unresolved",
    ):
        _require_array(case_map[field_name], f"case.{field_name}")

    sources = case_map["sources"]
    seen_source_ids: set[str] = set()
    for index, source in enumerate(sources):
        source_map = _require_mapping(source, f"case.sources[{index}]")
        source_id = _require_nonempty_string(
            source_map.get("source_id"), f"case.sources[{index}].source_id"
        )
        _require_nonempty_string(
            source_map.get("locator"), f"case.sources[{index}].locator"
        )
        if source_id in seen_source_ids:
            raise ToolInputError(f"duplicate source_id: {source_id}")
        seen_source_ids.add(source_id)

    return json.loads(_canonical_bytes(case_map).decode("utf-8"))


def seal_sherlock_case(case: Any) -> JsonObject:
    """Create an immutable, digest-addressed SHERLOCK evidence case file."""

    normalized = _validate_case(case)
    digest_subject = {"schema": SHERLOCK_SCHEMA, "record": normalized}
    digest = _sha256(digest_subject)
    return {
        "schema": SHERLOCK_SCHEMA,
        "case_id": f"sherlock-{digest.removeprefix('sha256:')[:16]}",
        "record": normalized,
        "digest": digest,
    }


def verify_sherlock_case(casefile: Any) -> JsonObject:
    """Verify a SHERLOCK case file and return its normalized form."""

    case_map = _require_mapping(casefile, "casefile")
    if case_map.get("schema") != SHERLOCK_SCHEMA:
        raise ToolInputError(f"casefile.schema must be {SHERLOCK_SCHEMA}")
    record = _validate_case(case_map.get("record"))
    expected = _sha256({"schema": SHERLOCK_SCHEMA, "record": record})
    if case_map.get("digest") != expected:
        raise ToolInputError("SHERLOCK case digest mismatch")
    expected_id = f"sherlock-{expected.removeprefix('sha256:')[:16]}"
    if case_map.get("case_id") != expected_id:
        raise ToolInputError("SHERLOCK case_id does not match case digest")
    return {
        "schema": SHERLOCK_SCHEMA,
        "case_id": expected_id,
        "record": record,
        "digest": expected,
    }


def _validate_brief(brief: Any) -> JsonObject:
    brief_map = _require_mapping(brief, "brief")
    for field_name in _REQUIRED_BRIEF_FIELDS:
        if field_name not in brief_map:
            raise ToolInputError(f"brief missing required field: {field_name}")
    _require_nonempty_string(brief_map["summary"], "brief.summary")
    for field_name in (
        "correlations",
        "interpretations",
        "hypotheses",
        "recommendations",
        "residual_uncertainty",
    ):
        _require_array(brief_map[field_name], f"brief.{field_name}")
    return json.loads(_canonical_bytes(brief_map).decode("utf-8"))


def bind_watson_brief(casefile: Any, brief: Any) -> JsonObject:
    """Bind WATSON synthesis to one exact, verified SHERLOCK case file."""

    sherlock = verify_sherlock_case(casefile)
    normalized_brief = _validate_brief(brief)
    watson_payload = {
        "schema": WATSON_SCHEMA,
        "sherlock_case_digest": sherlock["digest"],
        "brief": normalized_brief,
    }
    watson_digest = _sha256(watson_payload)
    watson = {**watson_payload, "digest": watson_digest}
    bundle_payload = {
        "schema": BUNDLE_SCHEMA,
        "sherlock": sherlock,
        "watson": watson,
    }
    return {**bundle_payload, "digest": _sha256(bundle_payload)}


def verify_sherlock_watson_bundle(bundle: Any) -> JsonObject:
    """Verify the full evidence -> interpretation digest chain."""

    bundle_map = _require_mapping(bundle, "bundle")
    if bundle_map.get("schema") != BUNDLE_SCHEMA:
        raise ToolInputError(f"bundle.schema must be {BUNDLE_SCHEMA}")

    sherlock = verify_sherlock_case(bundle_map.get("sherlock"))
    watson_map = _require_mapping(bundle_map.get("watson"), "bundle.watson")
    if watson_map.get("schema") != WATSON_SCHEMA:
        raise ToolInputError(f"bundle.watson.schema must be {WATSON_SCHEMA}")
    if watson_map.get("sherlock_case_digest") != sherlock["digest"]:
        raise ToolInputError("WATSON brief is bound to a different SHERLOCK case")
    brief = _validate_brief(watson_map.get("brief"))
    watson_payload = {
        "schema": WATSON_SCHEMA,
        "sherlock_case_digest": sherlock["digest"],
        "brief": brief,
    }
    watson_digest = _sha256(watson_payload)
    if watson_map.get("digest") != watson_digest:
        raise ToolInputError("WATSON brief digest mismatch")

    normalized_payload = {
        "schema": BUNDLE_SCHEMA,
        "sherlock": sherlock,
        "watson": {**watson_payload, "digest": watson_digest},
    }
    bundle_digest = _sha256(normalized_payload)
    if bundle_map.get("digest") != bundle_digest:
        raise ToolInputError("SHERLOCK/WATSON bundle digest mismatch")
    return {**normalized_payload, "digest": bundle_digest}


class SherlockCasefileTool(Opal2Tool):
    """Seal a provider-produced evidence investigation into a case file."""

    manifest = ToolManifest(
        tool_id=SHERLOCK_TOOL_ID,
        name="SHERLOCK",
        version="1.0.0",
        description=(
            "Seal a provenance-sensitive evidence investigation into an immutable "
            "case file for downstream analysis."
        ),
        capabilities=(
            "evidence-provenance",
            "casefile-sealing",
            "fact-inference-separation",
        ),
        input_schema={
            "type": "object",
            "required": ["case"],
            "additionalProperties": False,
            "properties": {"case": {"type": "object"}},
        },
        output_schema={
            "type": "object",
            "required": ["casefile"],
            "additionalProperties": False,
            "properties": {"casefile": {"type": "object"}},
        },
        runtime="python",
        deterministic=True,
        side_effects=(),
        policy_profiles=(),
        export_targets=("python", "opaltool", "oci"),
    )

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        del context
        return {"casefile": seal_sherlock_case(payload["case"])}


class WatsonBriefTool(Opal2Tool):
    """Bind provider-produced contextual synthesis to a SHERLOCK case."""

    manifest = ToolManifest(
        tool_id=WATSON_TOOL_ID,
        name="WATSON",
        version="1.0.0",
        description=(
            "Attach contextual synthesis to an exact verified SHERLOCK case file "
            "without permitting evidence-log mutation."
        ),
        capabilities=(
            "contextual-synthesis-binding",
            "immutable-evidence-handoff",
            "hypothesis-provenance",
        ),
        input_schema={
            "type": "object",
            "required": ["casefile", "brief"],
            "additionalProperties": False,
            "properties": {
                "casefile": {"type": "object"},
                "brief": {"type": "object"},
            },
        },
        output_schema={
            "type": "object",
            "required": ["bundle"],
            "additionalProperties": False,
            "properties": {"bundle": {"type": "object"}},
        },
        runtime="python",
        deterministic=True,
        side_effects=(),
        policy_profiles=(),
        export_targets=("python", "opaltool", "oci"),
    )

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        del context
        return {
            "bundle": bind_watson_brief(payload["casefile"], payload["brief"])
        }


class SherlockWatsonVerifyTool(Opal2Tool):
    """Verify a SHERLOCK -> WATSON artifact without interpreting its content."""

    manifest = ToolManifest(
        tool_id=SHERLOCK_WATSON_VERIFY_TOOL_ID,
        name="SHERLOCK / WATSON Verify",
        version="1.0.0",
        description=(
            "Verify the immutable evidence-to-analysis digest chain for a "
            "SHERLOCK/WATSON bundle."
        ),
        capabilities=("artifact-verification", "handoff-integrity"),
        input_schema={
            "type": "object",
            "required": ["bundle"],
            "additionalProperties": False,
            "properties": {"bundle": {"type": "object"}},
        },
        output_schema={
            "type": "object",
            "required": ["valid", "bundle_digest", "sherlock_case_digest"],
            "additionalProperties": False,
            "properties": {
                "valid": {"type": "boolean"},
                "bundle_digest": {"type": "string"},
                "sherlock_case_digest": {"type": "string"},
            },
        },
        runtime="python",
        deterministic=True,
        side_effects=(),
        policy_profiles=(),
        export_targets=("python", "opaltool", "oci"),
    )

    async def run(
        self, payload: JsonObject, context: ToolExecutionContext
    ) -> JsonObject:
        del context
        bundle = verify_sherlock_watson_bundle(payload["bundle"])
        return {
            "valid": True,
            "bundle_digest": bundle["digest"],
            "sherlock_case_digest": bundle["sherlock"]["digest"],
        }
