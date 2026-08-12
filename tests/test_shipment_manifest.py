"""Validation tests for the OPAL2 shipment-manifest schema (#1510)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "constellation-contracts"
    / "schemas"
    / "shipment-manifest.schema.json"
)
EXAMPLE_PATH = (
    Path(__file__).resolve().parent.parent
    / "constellation-contracts"
    / "manifests"
    / "shipment-manifest.example.json"
)


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def example():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def test_schema_is_valid_draft07(schema):
    jsonschema.Draft7Validator.check_schema(schema)


def test_committed_example_validates(schema, example):
    jsonschema.validate(example, schema)


def test_neutral_product_requires_no_canon(schema, example):
    doc = copy.deepcopy(example)
    doc["canon_license"]["includes_canon"] = True  # without license_ref
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, schema)


def test_licensed_variant_requires_license_ref(schema, example):
    doc = copy.deepcopy(example)
    doc["canon_license"]["includes_canon"] = True
    doc["canon_license"]["license_ref"] = "urn:aurora:license:example"
    jsonschema.validate(doc, schema)


def test_execution_default_off_is_const(schema, example):
    doc = copy.deepcopy(example)
    doc["ethics"]["execution_default_off"] = False
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, schema)


def test_missing_blocks_fail(schema, example):
    for block in ("shipment", "capabilities", "provenance", "ethics", "canon_license"):
        doc = copy.deepcopy(example)
        del doc[block]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(doc, schema)


def test_source_ref_must_be_full_sha(schema, example):
    doc = copy.deepcopy(example)
    doc["shipment"]["extracted_from"]["source_ref"] = "9c34d8e"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, schema)


def test_capabilities_must_be_nonempty(schema, example):
    doc = copy.deepcopy(example)
    doc["capabilities"] = []
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(doc, schema)
