"""
Tests for Schema Validation

DLP: test_schema_validation_v1
"""

import pytest
from src.aurora.core.schema_validation import (
    SchemaValidator,
    SchemaValidationError,
    get_validator
)


@pytest.fixture
def validator():
    """Create a fresh validator for each test"""
    return SchemaValidator()


@pytest.mark.unit
@pytest.mark.aurora
def test_validator_initialization(validator):
    """Test validator initializes and loads schemas"""
    assert validator is not None
    assert len(validator.schemas) == 3
    assert "L1" in validator.schemas
    assert "L2" in validator.schemas
    assert "L3" in validator.schemas


@pytest.mark.unit
@pytest.mark.aurora
def test_validate_l1_message_success(validator):
    """Test valid L1 message passes validation"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l1_action",
        "action_type": "api_response",
        "parameters": {"data": "test"},
        "context_tag": "test_l1"
    }

    result = validator.validate(message, "L1")
    assert result is not None
    assert result["schema_version"] == "1.0.0"
    assert "timestamp" in result


@pytest.mark.unit
@pytest.mark.aurora
def test_validate_l1_message_missing_field(validator):
    """Test L1 message fails without required fields"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l1_action",
        # Missing action_type
        "parameters": {},
        "context_tag": "test_l1_fail"
    }

    with pytest.raises(SchemaValidationError) as exc_info:
        validator.validate(message, "L1")

    assert exc_info.value.layer == "L1"


@pytest.mark.unit
@pytest.mark.aurora
def test_validate_l2_message_success(validator):
    """Test valid L2 message passes validation"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "quantum_simulation",
        "parameters": {"num_qubits": 8},
        "context_tag": "test_l2"
    }

    result = validator.validate(message, "L2")
    assert result["message_type"] == "l2_simulation_event"
    assert result["event_type"] == "quantum_simulation"


@pytest.mark.unit
@pytest.mark.aurora
def test_validate_l3_message_success(validator):
    """Test valid L3 message passes validation"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "The cosmos speaks",
            "symbols": ["cosmos", "voice"]
        },
        "context_tag": "test_l3"
    }

    result = validator.validate(message, "L3")
    assert result["content_type"] == "symbolic_metaphor"


@pytest.mark.unit
@pytest.mark.aurora
def test_is_l1_compliant_true(validator):
    """Test L1 compliance check for valid message"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l1_action",
        "action_type": "data_export",
        "parameters": {},
        "context_tag": "test"
    }

    assert validator.is_l1_compliant(message) is True


@pytest.mark.unit
@pytest.mark.aurora
def test_is_l1_compliant_false_symbolic_content(validator):
    """Test L1 compliance fails for symbolic content"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l1_action",
        "action_type": "api_response",
        "content_type": "symbolic_metaphor",  # Not allowed in L1
        "parameters": {},
        "context_tag": "test"
    }

    assert validator.is_l1_compliant(message) is False


@pytest.mark.unit
@pytest.mark.aurora
def test_is_l2_compliant(validator):
    """Test L2 compliance check"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "entity_interaction",
        "parameters": {},
        "context_tag": "test"
    }

    assert validator.is_l2_compliant(message) is True


@pytest.mark.unit
@pytest.mark.aurora
def test_is_l3_compliant(validator):
    """Test L3 compliance check"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "narrative_expression",
        "payload": {"text": "test"},
        "context_tag": "test"
    }

    assert validator.is_l3_compliant(message) is True


@pytest.mark.unit
@pytest.mark.aurora
def test_get_schema(validator):
    """Test retrieving schema for specific layer"""
    l1_schema = validator.get_schema("L1")
    assert l1_schema is not None
    assert "properties" in l1_schema
    assert "required" in l1_schema


@pytest.mark.unit
@pytest.mark.aurora
def test_get_available_layers(validator):
    """Test getting list of available layers"""
    layers = validator.get_available_layers()
    assert "L1" in layers
    assert "L2" in layers
    assert "L3" in layers


@pytest.mark.unit
@pytest.mark.aurora
def test_global_validator_singleton():
    """Test global validator is singleton"""
    v1 = get_validator()
    v2 = get_validator()
    assert v1 is v2


@pytest.mark.unit
@pytest.mark.aurora
def test_invalid_layer_raises_error(validator):
    """Test validation with invalid layer raises error"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "test",
        "context_tag": "test"
    }

    with pytest.raises(SchemaValidationError) as exc_info:
        validator.validate(message, "L99")

    assert "Unknown target layer" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.aurora
def test_schema_version_added_if_missing(validator):
    """Test schema_version is added if not present"""
    message = {
        # No schema_version
        "message_type": "l2_simulation_event",
        "event_type": "memory_operation",
        "parameters": {},
        "context_tag": "test"
    }

    result = validator.validate(message, "L2")
    assert "schema_version" in result
    assert result["schema_version"] == "1.0.0"


@pytest.mark.unit
@pytest.mark.aurora
def test_timestamp_added_if_missing(validator):
    """Test timestamp is added if not present"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "drift_measurement",
        "parameters": {},
        "context_tag": "test"
    }

    result = validator.validate(message, "L2")
    assert "timestamp" in result
    assert isinstance(result["timestamp"], float)
