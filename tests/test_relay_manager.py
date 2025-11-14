"""
Tests for Relay Manager and L1-L3 boundary enforcement

DLP: test_relay_manager_v1
Anchors: T1, SRB
"""

import pytest
import time
from src.aurora.relays.relay_manager import (
    RelayManager,
    get_relay_manager,
    SchemaViolation,
    AnchorViolation,
    EthicsViolation,
    RelayUnavailable
)


@pytest.fixture
def relay_manager():
    """Create a fresh relay manager for each test"""
    return RelayManager()


@pytest.mark.unit
@pytest.mark.aurora
def test_relay_manager_initialization(relay_manager):
    """Test relay manager initializes correctly"""
    assert relay_manager is not None
    assert relay_manager.validator is not None
    assert relay_manager.firewall is not None
    assert relay_manager.dlp_tracker is not None
    assert relay_manager.messages_processed == 0
    assert relay_manager.messages_blocked == 0


@pytest.mark.unit
@pytest.mark.aurora
def test_send_l2_to_l2_message_success(relay_manager):
    """Test successful L2→L2 message with valid schema"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "quantum_simulation",
        "parameters": {
            "num_qubits": 8,
            "shots": 1024
        },
        "context_tag": "test_l2_message"
    }

    result = relay_manager.send_cross_layer_message(
        source_layer="L2",
        target_layer="L2",
        payload=payload
    )

    assert result["success"] is True
    assert result["source_layer"] == "L2"
    assert result["target_layer"] == "L2"
    assert "request_id" in result
    assert "dlp_tag_id" in result
    assert result["checks_performed"]["schema_validation"] is True
    assert result["checks_performed"]["anchor_resolution"] is True
    assert relay_manager.messages_processed == 1
    assert relay_manager.messages_blocked == 0


@pytest.mark.unit
@pytest.mark.aurora
def test_send_l1_message_with_required_fields(relay_manager):
    """Test L1 message requires specific fields"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l1_action",
        "action_type": "api_response",
        "parameters": {
            "response_data": {"status": "ok"}
        },
        "context_tag": "test_l1_action"
    }

    result = relay_manager.send_cross_layer_message(
        source_layer="L2",
        target_layer="L1",
        payload=payload
    )

    assert result["success"] is True
    assert result["target_layer"] == "L1"
    # L1 transitions require ethics check
    assert result["checks_performed"]["ethics_check"] is True


@pytest.mark.unit
@pytest.mark.aurora
def test_schema_violation_missing_required_field(relay_manager):
    """Test schema validation fails for missing required field"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        # Missing required "event_type" field
        "parameters": {},
        "context_tag": "test_missing_field"
    }

    with pytest.raises(SchemaViolation) as exc_info:
        relay_manager.send_cross_layer_message(
            source_layer="L2",
            target_layer="L2",
            payload=payload
        )

    assert "event_type" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()
    assert relay_manager.messages_blocked == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_l3_to_l2_literal_message(relay_manager):
    """Test L3→L2 with literal (non-symbolic) content"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "lore_fragment",
        "payload": {
            "text": "The station operates at full capacity",
            "narrative_context": "station_status"
        },
        "context_tag": "test_literal_l3"
    }

    result = relay_manager.send_cross_layer_message(
        source_layer="L3",
        target_layer="L2",
        payload=payload
    )

    assert result["success"] is True
    assert result["checks_performed"]["narrative_firewall"] is True
    assert relay_manager.messages_translated == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_l3_to_l2_symbolic_translation_success(relay_manager):
    """Test L3→L2 with translatable symbolic content"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "the stars weep",
            "symbols": ["stellar", "tears"]
        },
        "context_tag": "test_symbolic_translatable"
    }

    result = relay_manager.send_cross_layer_message(
        source_layer="L3",
        target_layer="L2",
        payload=payload
    )

    assert result["success"] is True
    # Should have been translated to "solar_storm"
    translated_payload = result["payload"]
    assert translated_payload["event_type"] == "solar_storm"
    assert "translation_metadata" in translated_payload


@pytest.mark.unit
@pytest.mark.aurora
def test_l3_to_l2_untranslatable_symbolic_blocked(relay_manager):
    """Test L3→L2 blocks untranslatable symbolic content"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "symbolic_metaphor",
        "payload": {
            "text": "the quantum foam whispers ancient secrets of forgotten dreams",
            "symbols": ["unknowable", "ineffable"]
        },
        "context_tag": "test_symbolic_untranslatable"
    }

    with pytest.raises(SchemaViolation) as exc_info:
        relay_manager.send_cross_layer_message(
            source_layer="L3",
            target_layer="L2",
            payload=payload
        )

    assert "firewall" in str(exc_info.value).lower() or "translation" in str(exc_info.value).lower()
    assert relay_manager.messages_blocked == 1

    # Message should be quarantined
    quarantined = relay_manager.firewall.get_quarantined_messages()
    assert len(quarantined) > 0


@pytest.mark.unit
@pytest.mark.aurora
def test_anchor_resolution_adds_protocols(relay_manager):
    """Test anchor resolution adds appropriate protocols"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "entity_interaction",
        "parameters": {},
        "context_tag": "test_anchors"
    }

    result = relay_manager.send_cross_layer_message(
        source_layer="L3",
        target_layer="L2",
        payload=payload
    )

    assert result["success"] is True
    processed_payload = result["payload"]

    # Should have anchor_id
    assert "anchor_id" in processed_payload
    assert "T1" in processed_payload["anchor_id"]

    # Should have anchor protocols
    assert "anchor_protocols" in processed_payload
    assert "EOS_SEED_ORION" in processed_payload["anchor_protocols"]

    # Should have T1/SRB anchors
    assert "t1_srb_anchors" in processed_payload
    assert "T1_TEMPORAL_ANCHOR" in processed_payload["t1_srb_anchors"]
    assert "SRB_BOUNDARY_ANCHOR" in processed_payload["t1_srb_anchors"]


@pytest.mark.unit
@pytest.mark.aurora
def test_dlp_tag_creation(relay_manager):
    """Test DLP tag is created for relay operations"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "memory_operation",
        "parameters": {},
        "context_tag": "test_dlp_tag"
    }

    result = relay_manager.send_cross_layer_message(
        source_layer="L2",
        target_layer="L2",
        payload=payload
    )

    assert result["success"] is True
    dlp_tag_id = result["dlp_tag_id"]

    # Verify DLP tag was created
    assert dlp_tag_id in relay_manager.dlp_tracker.tags
    tag = relay_manager.dlp_tracker.tags[dlp_tag_id]

    assert tag.operation == "relay_L2_to_L2"
    assert "source_layer" in tag.metadata
    assert tag.metadata["source_layer"] == "L2"
    assert tag.metadata["target_layer"] == "L2"


@pytest.mark.unit
@pytest.mark.aurora
def test_relay_statistics(relay_manager):
    """Test relay manager tracks statistics correctly"""
    # Send successful messages
    for i in range(3):
        payload = {
            "schema_version": "1.0.0",
            "message_type": "l2_simulation_event",
            "event_type": "quantum_simulation",
            "parameters": {},
            "context_tag": f"test_stats_{i}"
        }
        relay_manager.send_cross_layer_message("L2", "L2", payload)

    # Try to send invalid message
    try:
        bad_payload = {
            "schema_version": "1.0.0",
            "message_type": "l2_simulation_event",
            # Missing required field
            "context_tag": "test_stats_bad"
        }
        relay_manager.send_cross_layer_message("L2", "L2", bad_payload)
    except SchemaViolation:
        pass

    stats = relay_manager.get_statistics()
    assert stats["messages_processed"] == 3
    assert stats["messages_blocked"] == 1
    assert stats["success_rate"] == 0.75


@pytest.mark.unit
@pytest.mark.aurora
def test_export_relay_manifest(relay_manager):
    """Test relay manifest export"""
    # Process some messages
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "symbolic_computation",
        "parameters": {},
        "context_tag": "test_manifest"
    }
    relay_manager.send_cross_layer_message("L2", "L2", payload)

    # Export manifest
    manifest = relay_manager.export_relay_manifest("test_export")

    assert manifest["manifest_name"] == "test_export"
    assert "relay_statistics" in manifest
    assert "firewall_statistics" in manifest
    assert "dlp_manifest" in manifest
    assert manifest["anchors"] == ["T1", "SRB", "EOS_SEED_ORION"]
    assert "L1_L3_BOUNDARY_ENFORCEMENT" in manifest["symbolic_tags"]


@pytest.mark.unit
@pytest.mark.aurora
def test_global_relay_manager_singleton():
    """Test global relay manager is singleton"""
    manager1 = get_relay_manager()
    manager2 = get_relay_manager()

    assert manager1 is manager2


@pytest.mark.unit
@pytest.mark.aurora
def test_request_id_generation(relay_manager):
    """Test unique request IDs are generated"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "drift_measurement",
        "parameters": {},
        "context_tag": "test_request_id"
    }

    result1 = relay_manager.send_cross_layer_message("L2", "L2", payload)
    result2 = relay_manager.send_cross_layer_message("L2", "L2", payload)

    assert result1["request_id"] != result2["request_id"]


@pytest.mark.unit
@pytest.mark.aurora
def test_relay_metadata_added(relay_manager):
    """Test relay metadata is added to processed messages"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l2_simulation_event",
        "event_type": "scenario_execution",
        "parameters": {},
        "context_tag": "test_metadata"
    }

    result = relay_manager.send_cross_layer_message(
        source_layer="L3",
        target_layer="L2",
        payload=payload
    )

    processed = result["payload"]
    assert "relay_metadata" in processed
    assert processed["relay_metadata"]["source_layer"] == "L3"
    assert processed["relay_metadata"]["target_layer"] == "L2"
    assert "relay_timestamp" in processed["relay_metadata"]


@pytest.mark.integration
@pytest.mark.aurora
def test_l3_to_l1_full_pipeline(relay_manager):
    """Test full pipeline L3→L1 with all checks"""
    payload = {
        "schema_version": "1.0.0",
        "message_type": "l3_symbolic",
        "content_type": "lore_fragment",
        "payload": {
            "text": "Execute system output",
            "narrative_context": "system_action"
        },
        "context_tag": "test_l3_to_l1",
        "intended_layer": "L1"
    }

    # First translate to L2, then to L1
    l2_result = relay_manager.send_cross_layer_message(
        source_layer="L3",
        target_layer="L2",
        payload=payload
    )

    assert l2_result["success"] is True

    # Now L2 to L1
    l2_payload = l2_result["payload"]

    # Convert to L1 format
    l1_payload = {
        "schema_version": "1.0.0",
        "message_type": "l1_action",
        "action_type": "system_output",
        "parameters": l2_payload.get("parameters", {}),
        "context_tag": l2_payload["context_tag"],
        "anchor_id": l2_payload["anchor_id"]
    }

    l1_result = relay_manager.send_cross_layer_message(
        source_layer="L2",
        target_layer="L1",
        payload=l1_payload
    )

    assert l1_result["success"] is True
    assert l1_result["checks_performed"]["ethics_check"] is True
    assert "REALITY_BRIDGE" in l1_result["payload"]["anchor_protocols"]
