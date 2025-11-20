"""
Tests for ThreadCore registry functionality and payload validation.

Thread: T1→TEST→THREADCORE_REGISTRY
DLP: context_tag=test_threadcore_registry
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import sys
from pathlib import Path

import pytest

# Import functions from threadcore_classifier
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from threadcore_classifier import (  # noqa: E402
    load_threadcore_registry,
    validate_payload_against_registry,
    classify_payload_status,
)


@pytest.fixture
def registry():
    """Load the ThreadCore registry for testing."""
    repo_root = Path(__file__).parent.parent
    return load_threadcore_registry(str(repo_root / "threadcore_registry.json"))


@pytest.fixture
def valid_payload():
    """Example of a valid ThreadCore payload."""
    return {
        "augmentation": "THREADCORE",
        "version": "v3.5.1_macroready",
        "role": "Symbolic Constellation Loom + Reflection Module",
        "threadcore_directives": ["directive1", "directive2"],
        "anchor_seed": "EOS_SEED_ORION",
        "ethics_protocol": "Picard_Delta_3",
        "symbolic_drift": "0.0%",
    }


@pytest.fixture
def invalid_payload():
    """Example of an invalid ThreadCore payload."""
    return {
        "augmentation": "THREADCORE",
        "version": "v3.5.1_test",
        # Missing required fields
        "anchor_seed": "WRONG_SEED",
    }


def test_load_registry(registry):
    """Test that registry loads successfully."""
    assert registry is not None
    assert "registry_version" in registry
    assert "canonical_version" in registry
    assert "payloads" in registry
    assert registry["canonical_version"] == "v3.5.1"


def test_registry_has_canonical_payload(registry):
    """Test that registry defines a canonical payload."""
    payloads = registry["payloads"]
    canonical_payloads = [
        name for name, info in payloads.items()
        if info.get("status") == "canonical"
    ]
    assert len(canonical_payloads) > 0
    assert "threadcore_v3.5.1_macroready" in canonical_payloads


def test_registry_payload_structure(registry):
    """Test that all payloads have required registry fields."""
    required_fields = ["version", "variant", "status", "file_path", "description"]

    for payload_name, payload_info in registry["payloads"].items():
        for field in required_fields:
            assert field in payload_info, f"Payload {payload_name} missing field {field}"


def test_validate_payload_valid(registry, valid_payload):
    """Test validation of a valid payload."""
    result = validate_payload_against_registry(valid_payload, registry)

    assert result["valid"] is True
    assert result["status"] in ["valid", "valid_with_warnings"]
    assert len(result["errors"]) == 0


def test_validate_payload_missing_fields(registry):
    """Test validation catches missing required fields."""
    incomplete_payload = {
        "augmentation": "THREADCORE",
        "anchor_seed": "EOS_SEED_ORION",
    }

    result = validate_payload_against_registry(incomplete_payload, registry)

    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert any("required field" in error.lower() for error in result["errors"])


def test_validate_payload_wrong_anchor(registry, valid_payload):
    """Test validation catches incorrect anchor seed."""
    invalid_anchor = valid_payload.copy()
    invalid_anchor["anchor_seed"] = "WRONG_ANCHOR"

    result = validate_payload_against_registry(invalid_anchor, registry)

    assert result["valid"] is False
    assert any("anchor seed" in error.lower() for error in result["errors"])


def test_validate_payload_wrong_ethics(registry, valid_payload):
    """Test validation catches incorrect ethics protocol."""
    invalid_ethics = valid_payload.copy()
    invalid_ethics["ethics_protocol"] = "Wrong_Protocol"

    result = validate_payload_against_registry(invalid_ethics, registry)

    assert result["valid"] is False
    assert any("ethics protocol" in error.lower() for error in result["errors"])


def test_validate_payload_high_drift(registry, valid_payload):
    """Test validation warns about high drift."""
    high_drift = valid_payload.copy()
    high_drift["symbolic_drift"] = "5.0%"  # Above threshold

    result = validate_payload_against_registry(high_drift, registry)

    # High drift should generate warning, not necessarily error
    assert len(result["warnings"]) > 0
    assert any("drift" in warning.lower() for warning in result["warnings"])


def test_classify_existing_payload(registry):
    """Test classification of an existing payload file."""
    repo_root = Path(__file__).parent.parent
    payload_path = repo_root / "modules/reflective_autonomy/threadcore_payloads/threadcore_v3.5.1_macroready.json"

    if payload_path.exists():
        result = classify_payload_status(str(payload_path), registry)

        assert result["payload_name"] == "threadcore_v3.5.1_macroready"
        assert result["registry_status"] == "canonical"
        assert result["is_canonical"] is True
        assert result["is_deprecated"] is False
        assert result["valid"] is True


def test_classify_nonexistent_payload(registry):
    """Test classification of a non-existent payload file."""
    result = classify_payload_status("/nonexistent/path.json", registry)

    assert result["status"] == "not_found"
    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_registry_validation_rules(registry):
    """Test that registry has proper validation rules."""
    validation_rules = registry["validation_rules"]

    assert "required_fields" in validation_rules
    assert "anchor_seed_required" in validation_rules
    assert "ethics_protocol_required" in validation_rules
    assert "max_drift_threshold" in validation_rules

    assert validation_rules["anchor_seed_required"] == "EOS_SEED_ORION"
    assert validation_rules["ethics_protocol_required"] == "Picard_Delta_3"
    assert validation_rules["max_drift_threshold"] == 0.002


def test_registry_no_deprecated_in_active(registry):
    """Test that no deprecated payloads are marked as canonical or specialized."""
    payloads = registry["payloads"]

    for payload_name, payload_info in payloads.items():
        if payload_info.get("status") == "deprecated":
            # Deprecated payloads should not be marked as canonical or specialized
            assert payload_info.get("status") != "canonical"
            assert payload_info.get("status") != "specialized"


def test_registry_has_metadata(registry):
    """Test that registry has metadata section."""
    assert "metadata" in registry
    metadata = registry["metadata"]

    assert "created" in metadata
    assert "last_modified" in metadata
    assert "maintainer" in metadata
    assert "schema_version" in metadata


def test_all_payload_files_exist(registry):
    """Test that all payload files referenced in registry exist."""
    repo_root = Path(__file__).parent.parent
    payloads = registry["payloads"]

    for payload_name, payload_info in payloads.items():
        file_path = repo_root / payload_info["file_path"]
        assert file_path.exists(), f"Payload file not found: {file_path}"


def test_registry_usage_guidelines(registry):
    """Test that registry has usage guidelines."""
    assert "usage_guidelines" in registry
    guidelines = registry["usage_guidelines"]

    assert "default_payload" in guidelines
    assert "when_to_use_variants" in guidelines
    assert "extension_guidelines" in guidelines
    assert "deprecation_policy" in guidelines


def test_registry_integration_points(registry):
    """Test that registry documents integration points."""
    assert "integration_points" in registry
    integration = registry["integration_points"]

    # Check key integration files are documented
    assert "validator" in integration
    assert "classifier" in integration
    assert "tagging_engine" in integration
    assert "tests" in integration
