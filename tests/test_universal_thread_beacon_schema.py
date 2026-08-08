"""Tests for the neutral Universal Thread Beacon preservation profile."""

from __future__ import annotations

import copy
import importlib.util
import json
import math
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "continuity" / "universal_thread_beacon.schema.json"
EXAMPLE_PATH = REPO_ROOT / "docs" / "continuity" / "universal_thread_beacon.example.json"
VALIDATOR_PATH = REPO_ROOT / "tools" / "continuity" / "validate_beacon.py"
EXPECTED_CANONICAL_SHA256 = "d2b5b2c564c969d5bc177d6ebb81f50946f2b6c01f9e7f202b5b24c5e37422b6"


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_beacon", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def example() -> dict:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator_module():
    return _load_validator_module()


@pytest.mark.unit
def test_schema_and_example_validate(schema: dict, example: dict) -> None:
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(example)


@pytest.mark.unit
def test_example_has_stable_canonical_digest(validator_module, schema: dict, example: dict) -> None:
    validated = validator_module.validate_beacon(example, schema)
    assert validated is example
    assert validator_module.canonical_sha256(validated) == EXPECTED_CANONICAL_SHA256


@pytest.mark.unit
def test_example_does_not_claim_unverified_integrity_as_verified(example: dict) -> None:
    assert example["integrity"]["integrity_status"] == "unverified"
    assert example["integrity"]["digest_algorithm"] is None
    assert example["integrity"]["digest"] is None


@pytest.mark.unit
def test_unknown_extension_fields_survive_validation(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["future_reader"] = {"unknown_field": ["preserve", 1, True]}

    validated = validator_module.validate_beacon(candidate, schema)

    assert validated["extensions"]["future_reader"]["unknown_field"] == ["preserve", 1, True]
    assert validator_module.canonical_sha256(validated) != EXPECTED_CANONICAL_SHA256


@pytest.mark.unit
def test_strict_loader_rejects_duplicate_keys(tmp_path: Path, validator_module) -> None:
    candidate = tmp_path / "duplicate.json"
    candidate.write_text('{"specification": {}, "specification": {}}', encoding="utf-8")

    with pytest.raises(validator_module.BeaconValidationError, match="Duplicate JSON object key"):
        validator_module.load_json(candidate)


@pytest.mark.unit
def test_strict_loader_rejects_nonfinite_numbers(tmp_path: Path, validator_module) -> None:
    candidate = tmp_path / "nonfinite.json"
    candidate.write_text('{"value": NaN}', encoding="utf-8")

    with pytest.raises(validator_module.BeaconValidationError, match="Non-finite JSON number"):
        validator_module.load_json(candidate)


@pytest.mark.unit
def test_strict_loader_rejects_floating_numbers(tmp_path: Path, validator_module) -> None:
    candidate = tmp_path / "float.json"
    candidate.write_text('{"value": 0.5}', encoding="utf-8")

    with pytest.raises(validator_module.BeaconValidationError, match="Floating-point JSON numbers"):
        validator_module.load_json(candidate)


@pytest.mark.unit
def test_strict_loader_rejects_oversized_integer_without_traceback(tmp_path: Path, validator_module) -> None:
    candidate = tmp_path / "oversized-integer.json"
    candidate.write_text('{"value": ' + ("9" * 5000) + "}", encoding="utf-8")

    with pytest.raises(validator_module.BeaconValidationError, match="safe canonical range"):
        validator_module.load_json(candidate)


@pytest.mark.unit
def test_strict_loader_wraps_invalid_utf8(tmp_path: Path, validator_module) -> None:
    candidate = tmp_path / "invalid-utf8.json"
    candidate.write_bytes(b'{"value":"\xff"}')

    with pytest.raises(validator_module.BeaconValidationError, match="Unable to read UTF-8 JSON"):
        validator_module.load_json(candidate)


@pytest.mark.unit
def test_canonical_subset_rejects_python_float(validator_module, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["bad"] = math.inf

    with pytest.raises(validator_module.BeaconValidationError, match="Floating-point value"):
        validator_module.canonical_json(candidate)


@pytest.mark.unit
def test_canonical_subset_rejects_unsafe_integer(validator_module, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["bad"] = validator_module.MAX_SAFE_INTEGER + 1

    with pytest.raises(validator_module.BeaconValidationError, match="outside canonical range"):
        validator_module.canonical_json(candidate)


@pytest.mark.unit
def test_canonical_subset_rejects_non_ascii_object_keys(validator_module, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["é"] = "ambiguous ordering"

    with pytest.raises(validator_module.BeaconValidationError, match="outside printable ASCII"):
        validator_module.canonical_json(candidate)


@pytest.mark.unit
def test_canonical_bytes_define_order_escaping_and_utf8(validator_module) -> None:
    payload = {"text": '<\n"\\é', "a": 1}

    canonical = validator_module.canonical_json(payload).encode("utf-8")

    assert canonical == b'{"a":1,"text":"<\\n\\"\\\\\xc3\xa9"}'
    assert b"\\u003c" not in canonical
    assert not canonical.endswith(b"\n")


@pytest.mark.unit
def test_canonical_serializer_rejects_lone_surrogate(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["bad_unicode"] = "\ud800"

    with pytest.raises(validator_module.BeaconValidationError, match="Invalid Unicode scalar value"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_unsupported_schema_version_fails_clearly(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["specification"]["schema_version"] = "1.1.0"

    with pytest.raises(validator_module.BeaconValidationError, match="Unsupported UTB schema version"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_minimum_reader_version_is_enforced(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["compatibility"]["minimum_reader_version"] = "1.0.1"

    with pytest.raises(validator_module.BeaconValidationError, match="requires reader version 1.0.1"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_oversized_semver_component_fails_cleanly(validator_module) -> None:
    oversized = ("9" * 5000) + ".0.0"

    with pytest.raises(validator_module.BeaconValidationError, match="Invalid minimum reader version"):
        validator_module.semantic_version_tuple(oversized, "minimum reader version")


@pytest.mark.unit
def test_unrelated_custom_schema_is_rejected(validator_module, example: dict) -> None:
    with pytest.raises(validator_module.BeaconValidationError, match="does not match the committed bundled"):
        validator_module.validate_beacon(example, {})


@pytest.mark.unit
def test_spoofed_schema_identity_cannot_bypass_committed_constraints(
    validator_module,
    schema: dict,
    example: dict,
) -> None:
    spoofed_schema = {
        "$schema": schema["$schema"],
        "$id": schema["$id"],
        "x-utb-specification": schema["x-utb-specification"],
        "x-utb-schema-version": schema["x-utb-schema-version"],
        "type": "object",
    }
    candidate = copy.deepcopy(example)
    candidate["profile"] = "full"

    with pytest.raises(validator_module.BeaconValidationError, match="does not match the committed bundled"):
        validator_module.validate_beacon(candidate, spoofed_schema)


@pytest.mark.unit
def test_undefined_full_profile_is_rejected(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["profile"] = "full"

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
@pytest.mark.parametrize(
    "field",
    ["residency_layer", "operational_scope_layers", "implementation_status", "deployment_status"],
)
def test_all_classification_dimensions_are_required(
    validator_module,
    schema: dict,
    example: dict,
    field: str,
) -> None:
    candidate = copy.deepcopy(example)
    candidate["classification"].pop(field)

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_residency_and_operational_scope_are_independent(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["classification"]["residency_layer"] = "L1"
    candidate["classification"]["operational_scope_layers"] = ["L2", "L3"]

    validated = validator_module.validate_beacon(candidate, schema)

    assert validated["classification"]["residency_layer"] == "L1"
    assert validated["classification"]["operational_scope_layers"] == ["L2", "L3"]


@pytest.mark.unit
def test_required_deliverable_cannot_be_unavailable(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    deliverable = candidate["manifests"]["deliverables"][0]
    deliverable["inclusion_state"] = "unavailable"
    deliverable["missing_reason"] = "fixture deliberately removed"

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_included_deliverable_requires_path_and_integrity(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    deliverable = candidate["manifests"]["deliverables"][0]
    deliverable["inclusion_state"] = "included"
    deliverable["external_ref"] = None
    deliverable["path"] = None
    deliverable["integrity_ref"] = None

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_external_deliverable_requires_integrity_reference(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["manifests"]["deliverables"][0]["integrity_ref"] = None

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_digest_cannot_be_claimed_as_verified_signature(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["integrity"]["signature_status"] = "verified"
    candidate["integrity"]["signature_ref"] = None

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_verified_integrity_requires_real_digest_fields(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["integrity"]["integrity_status"] = "verified"
    candidate["integrity"]["digest_algorithm"] = None
    candidate["integrity"]["digest"] = None

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_policy_and_classification_dimensions_remain_explicit(example: dict) -> None:
    assert example["classification"]["canon_status"] == "proposed_design"
    assert example["classification"]["residency_layer"] == "L3"
    assert example["classification"]["operational_scope_layers"] == ["L3"]
    assert example["classification"]["execution_mode"] == "not_applicable"
    assert example["classification"]["evidence_authority"] == "reference_evidence"
    assert example["classification"]["implementation_status"] == "partial"
    assert example["classification"]["deployment_status"] == "not_applicable"
    assert example["compatibility"]["canonicalization"] == "utb-json-subset-v1"
    assert example["policy_refs"]["consent_policy_ref"] == "AUo959/Aurora_ORIONCORE_Directory_Main#46"


@pytest.mark.unit
def test_published_digest_in_design_doc_matches_computed_digest(
    validator_module, schema: dict, example: dict
) -> None:
    """The digest published in the design doc must match the real one.

    The canonical SHA-256 appears twice: pinned in this file, and published in
    UNIVERSAL_THREAD_BEACON_FIELD_OWNERSHIP.md as the value external verifiers
    check against. Nothing bound the two together, so a change that updated the
    test pin could leave the published copy stale and silently hand independent
    verifiers a mismatch. This binds them.
    """
    doc = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "continuity"
        / "UNIVERSAL_THREAD_BEACON_FIELD_OWNERSHIP.md"
    ).read_text(encoding="utf-8")

    computed = validator_module.canonical_sha256(
        validator_module.validate_beacon(example, schema)
    )

    assert computed == EXPECTED_CANONICAL_SHA256
    assert computed in doc, (
        "The canonical digest published in UNIVERSAL_THREAD_BEACON_FIELD_OWNERSHIP.md "
        f"does not match the computed digest {computed}."
    )
