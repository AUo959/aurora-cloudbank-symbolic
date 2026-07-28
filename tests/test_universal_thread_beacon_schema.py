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
EXPECTED_CANONICAL_SHA256 = "13a5c6bf5806d2129a43db58ef8f7a16ec638cd0ca5929d16997b8dd9e7f1633"


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
def test_strict_loader_wraps_invalid_utf8(tmp_path: Path, validator_module) -> None:
    candidate = tmp_path / "invalid-utf8.json"
    candidate.write_bytes(b'{"value":"\xff"}')

    with pytest.raises(validator_module.BeaconValidationError, match="Unable to read UTF-8 JSON"):
        validator_module.load_json(candidate)


@pytest.mark.unit
def test_canonical_serializer_rejects_nonfinite_python_values(validator_module, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["bad"] = math.inf

    with pytest.raises(validator_module.BeaconValidationError, match="strict UTF-8 JSON"):
        validator_module.canonical_json(candidate)


@pytest.mark.unit
def test_canonical_serializer_rejects_lone_surrogate(validator_module, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["bad_unicode"] = "\ud800"

    with pytest.raises(validator_module.BeaconValidationError, match="strict UTF-8 JSON"):
        validator_module.validate_beacon(candidate, json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))


@pytest.mark.unit
def test_unsupported_major_version_fails_clearly(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["specification"]["schema_version"] = "2.0.0"

    with pytest.raises(validator_module.BeaconValidationError, match="Unsupported UTB schema major version"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_minimum_reader_version_is_enforced(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["compatibility"]["minimum_reader_version"] = "1.0.1"

    with pytest.raises(validator_module.BeaconValidationError, match="requires reader version 1.0.1"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_invalid_reader_schema_fails_as_validation_error(validator_module, example: dict) -> None:
    invalid_schema = {"type": "definitely-not-a-json-schema-type"}

    with pytest.raises(validator_module.BeaconValidationError, match="Invalid reader schema"):
        validator_module.validate_beacon(example, invalid_schema)


@pytest.mark.unit
@pytest.mark.parametrize("field", ["implementation_status", "deployment_status"])
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
    assert example["classification"]["layer"] == "L3"
    assert example["classification"]["execution_mode"] == "not_applicable"
    assert example["classification"]["evidence_authority"] == "reference_evidence"
    assert example["classification"]["implementation_status"] == "partial"
    assert example["classification"]["deployment_status"] == "not_applicable"
    assert example["policy_refs"]["consent_policy_ref"] == "AUo959/Aurora_ORIONCORE_Directory_Main#46"
