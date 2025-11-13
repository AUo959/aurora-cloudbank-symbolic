"""
Tests for Narrative Firewall

DLP: test_narrative_firewall_v1
"""

import pytest
from src.aurora.core.narrative_firewall import (
    NarrativeFirewall,
    MetaphorTranslationError,
    get_firewall
)


@pytest.fixture
def firewall():
    """Create a fresh firewall for each test"""
    return NarrativeFirewall()


@pytest.mark.unit
@pytest.mark.aurora
def test_firewall_initialization(firewall):
    """Test firewall initializes with default rules"""
    assert firewall is not None
    assert len(firewall.translation_rules) > 0
    assert "the stars weep" in firewall.translation_rules
    assert firewall.translation_rules["the stars weep"] == "solar_storm"


@pytest.mark.unit
@pytest.mark.aurora
def test_add_translation_rule(firewall):
    """Test adding custom translation rule"""
    firewall.add_translation_rule("night falls", "scenario_execution")
    assert "night falls" in firewall.translation_rules
    assert firewall.translation_rules["night falls"] == "scenario_execution"


@pytest.mark.unit
@pytest.mark.aurora
def test_classify_message_symbolic(firewall):
    """Test classifying symbolic message"""
    message = {
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "The universe contemplates itself"
        },
        "context_tag": "test"
    }

    classification = firewall.classify_message(message)
    assert classification == "symbolic"


@pytest.mark.unit
@pytest.mark.aurora
def test_classify_message_literal(firewall):
    """Test classifying literal message"""
    message = {
        "message_type": "l2_simulation_event",
        "event_type": "quantum_simulation",
        "parameters": {},
        "context_tag": "test"
    }

    classification = firewall.classify_message(message)
    assert classification == "literal"


@pytest.mark.unit
@pytest.mark.aurora
def test_classify_message_mixed(firewall):
    """Test classifying mixed message"""
    message = {
        "message_type": "l3_symbolic",
        "content_type": "lore_fragment",
        "payload": {
            "text": "This text contains a metaphor",
            "metaphor_mapping": {"stars": "sensors"}
        },
        "context_tag": "test"
    }

    classification = firewall.classify_message(message)
    assert classification in ["symbolic", "mixed"]


@pytest.mark.unit
@pytest.mark.aurora
def test_translate_l3_to_l2_exact_match(firewall):
    """Test translating symbolic content with exact match"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "the stars weep"
        },
        "context_tag": "test_translation"
    }

    result = firewall.translate_l3_to_l2(message)

    assert result["message_type"] == "l2_simulation_event"
    assert result["event_type"] == "solar_storm"
    assert "translation_metadata" in result
    assert result["translation_metadata"]["translation_applied"] is True


@pytest.mark.unit
@pytest.mark.aurora
def test_translate_l3_to_l2_partial_match(firewall):
    """Test translating with partial match in text"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "As the stars weep across the void"
        },
        "context_tag": "test_partial"
    }

    result = firewall.translate_l3_to_l2(message)

    assert result["event_type"] == "solar_storm"


@pytest.mark.unit
@pytest.mark.aurora
def test_translate_l3_to_l2_via_symbols(firewall):
    """Test translating via symbol matching"""
    # Add rule for symbol
    firewall.add_translation_rule("crystal", "memory_operation")

    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "Unknown metaphor",
            "symbols": ["crystal", "memory"]
        },
        "context_tag": "test_symbols"
    }

    result = firewall.translate_l3_to_l2(message)

    assert result["event_type"] == "memory_operation"


@pytest.mark.unit
@pytest.mark.aurora
def test_translate_l3_to_l2_literal_content(firewall):
    """Test translating literal content (no translation needed)"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "lore_fragment",
        "payload": {
            "text": "The system initialized successfully"
        },
        "context_tag": "test_literal"
    }

    result = firewall.translate_l3_to_l2(message)

    # Should repackage as L2
    assert result["message_type"] == "l2_simulation_event"
    assert result["event_type"] == "symbolic_computation"


@pytest.mark.unit
@pytest.mark.aurora
def test_translate_l3_to_l2_untranslatable(firewall):
    """Test untranslatable symbolic content raises error"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "quantum foam whispers ancient secrets"
        },
        "context_tag": "test_untranslatable"
    }

    with pytest.raises(MetaphorTranslationError) as exc_info:
        firewall.translate_l3_to_l2(message)

    assert "No matching translation rule" in exc_info.value.reason


@pytest.mark.unit
@pytest.mark.aurora
def test_untranslatable_message_quarantined(firewall):
    """Test untranslatable messages are quarantined"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "ineffable mysteries"
        },
        "context_tag": "test_quarantine"
    }

    try:
        firewall.translate_l3_to_l2(message)
    except MetaphorTranslationError:
        pass

    quarantined = firewall.get_quarantined_messages()
    assert len(quarantined) > 0
    assert quarantined[0]["reason"] == "No translation rule found"


@pytest.mark.unit
@pytest.mark.aurora
def test_clear_quarantine(firewall):
    """Test clearing quarantined messages"""
    message = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "unknown symbolic content"
        },
        "context_tag": "test"
    }

    try:
        firewall.translate_l3_to_l2(message)
    except MetaphorTranslationError:
        pass

    assert len(firewall.get_quarantined_messages()) > 0

    firewall.clear_quarantine()
    assert len(firewall.get_quarantined_messages()) == 0


@pytest.mark.unit
@pytest.mark.aurora
def test_is_safe_for_l2_true(firewall):
    """Test message safety check returns true for translatable"""
    message = {
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "the stars weep"
        },
        "context_tag": "test"
    }

    is_safe, reason = firewall.is_safe_for_l2(message)
    assert is_safe is True
    assert reason is None


@pytest.mark.unit
@pytest.mark.aurora
def test_is_safe_for_l2_false(firewall):
    """Test message safety check returns false for untranslatable"""
    message = {
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "unknowable cosmic truth"
        },
        "context_tag": "test"
    }

    is_safe, reason = firewall.is_safe_for_l2(message)
    assert is_safe is False
    assert reason is not None
    assert "No translation rule" in reason


@pytest.mark.unit
@pytest.mark.aurora
def test_get_translation_rules(firewall):
    """Test getting all translation rules"""
    rules = firewall.get_translation_rules()

    assert isinstance(rules, dict)
    assert "the stars weep" in rules
    assert rules["the stars weep"] == "solar_storm"


@pytest.mark.unit
@pytest.mark.aurora
def test_global_firewall_singleton():
    """Test global firewall is singleton"""
    f1 = get_firewall()
    f2 = get_firewall()
    assert f1 is f2


@pytest.mark.unit
@pytest.mark.aurora
def test_multiple_metaphor_translations(firewall):
    """Test various metaphor translations"""
    test_cases = [
        ("the stars weep", "solar_storm"),
        ("system trembles", "drift_measurement"),
        ("memory fades", "memory_operation"),
        ("wisdom flows", "symbolic_computation"),
        ("the fleet gathers", "faction_event")
    ]

    for metaphor, expected_event in test_cases:
        message = {
            "schema_version": "1.0.0",
            "message_type": "l3_symbolic",
            "content_type": "symbolic_metaphor",
            "payload": {
                "text": metaphor
            },
            "context_tag": f"test_{metaphor}"
        }

        result = firewall.translate_l3_to_l2(message)
        assert result["event_type"] == expected_event
