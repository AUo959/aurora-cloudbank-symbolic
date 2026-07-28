"""Tests for the neutral Universal Thread Beacon preservation profile."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "continuity" / "universal_thread_beacon.schema.json"
EXAMPLE_PATH = REPO_ROOT / "docs" / "continuity" / "universal_thread_beacon.example.json"
VALIDATOR_PATH = REPO_ROOT / "tools" / "continuity" / "validate_beacon.py"
EXPECTED_CANONICAL_SHA256 = "317e046c81f69bb15d1978274f3f9be4d63d9e5d5f1c8806114e9ae4396c39aa"


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
def test_unknown_extension_fields_survive_validation(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["extensions"]["future_reader"] = {"unknown_field": ["preserve", 1, True]}

    validated = validator_module.validate_beacon(candidate, schema)

    assert validated["extensions"]["future_reader"]["unknown_field"] == ["preserve", 1, True]
    assert validator_module.canonical_sha256(validated) != EXPECTED_CANONICAL_SHA256


@pytest.mark.unit
def test_unsupported_major_version_fails_clearly(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["specification"]["schema_version"] = "2.0.0"

    with pytest.raises(validator_module.BeaconValidationError, match="Unsupported UTB schema major version"):
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
def test_digest_cannot_be_claimed_as_verified_signature(validator_module, schema: dict, example: dict) -> None:
    candidate = copy.deepcopy(example)
    candidate["integrity"]["signature_status"] = "verified"
    candidate["integrity"]["signature_ref"] = None

    with pytest.raises(validator_module.BeaconValidationError, match="Schema validation failed"):
        validator_module.validate_beacon(candidate, schema)


@pytest.mark.unit
def test_policy_and_classification_dimensions_remain_explicit(example: dict) -> None:
    assert example["classification"]["canon_status"] == "proposed_design"
    assert example["classification"]["layer"] == "L3"
    assert example["classification"]["execution_mode"] == "not_applicable"
    assert example["classification"]["evidence_authority"] == "reference_evidence"
    assert example["policy_refs"]["consent_policy_ref"] == "AUo959/Aurora_ORIONCORE_Directory_Main#46"
