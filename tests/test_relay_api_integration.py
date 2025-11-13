"""
Integration tests for Relay Manager API endpoints

DLP: test_relay_api_integration_v1
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add api directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "api"))

from aurora_api import app


@pytest.fixture(scope="module")
def client():
    """Create test client for Aurora API"""
    return TestClient(app)


@pytest.mark.integration
@pytest.mark.api
def test_relay_health_endpoint(client):
    """Test relay manager health endpoint"""
    response = client.get("/relay/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "Relay Manager"
    assert data["available"] is True
    assert "timestamp" in data


@pytest.mark.integration
@pytest.mark.api
def test_relay_send_l2_to_l2_message(client):
    """Test sending L2→L2 message via API"""
    payload = {
        "source_layer": "L2",
        "target_layer": "L2",
        "payload": {
            "schema_version": "1.0.0",
            "message_type": "l2_simulation_event",
            "event_type": "quantum_simulation",
            "parameters": {"num_qubits": 8},
            "context_tag": "api_test_l2"
        }
    }
    
    response = client.post("/relay/send", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["source_layer"] == "L2"
    assert data["target_layer"] == "L2"
    assert "request_id" in data
    assert "dlp_tag_id" in data


@pytest.mark.integration
@pytest.mark.api
def test_relay_send_l3_to_l2_symbolic_translation(client):
    """Test L3→L2 with symbolic translation via API"""
    payload = {
        "source_layer": "L3",
        "target_layer": "L2",
        "payload": {
            "schema_version": "1.0.0",
            "message_type": "l3_symbolic",
            "content_type": "symbolic_metaphor",
            "payload": {
                "text": "the stars weep"
            },
            "context_tag": "api_test_symbolic"
        }
    }
    
    response = client.post("/relay/send", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["checks_performed"]["narrative_firewall"] is True
    assert data["payload"]["event_type"] == "solar_storm"


@pytest.mark.integration
@pytest.mark.api
def test_relay_send_invalid_message_schema_violation(client):
    """Test sending invalid message triggers schema violation"""
    payload = {
        "source_layer": "L2",
        "target_layer": "L2",
        "payload": {
            # Missing required fields
            "context_tag": "api_test_invalid"
        }
    }
    
    response = client.post("/relay/send", json=payload)
    assert response.status_code == 400
    
    data = response.json()
    assert "error" in data["detail"]
    assert data["detail"]["error_type"] == "schema_violation"


@pytest.mark.integration
@pytest.mark.api
def test_relay_statistics_endpoint(client):
    """Test relay statistics endpoint"""
    response = client.get("/relay/statistics")
    assert response.status_code == 200
    
    data = response.json()
    assert "messages_processed" in data
    assert "messages_blocked" in data
    assert "success_rate" in data
    assert isinstance(data["messages_processed"], int)


@pytest.mark.integration
@pytest.mark.api
def test_relay_manifest_export(client):
    """Test relay manifest export endpoint"""
    response = client.get("/relay/manifest")
    assert response.status_code == 200
    
    data = response.json()
    assert "manifest_name" in data
    assert "relay_statistics" in data
    assert "firewall_statistics" in data
    assert "dlp_manifest" in data
    assert data["anchors"] == ["T1", "SRB", "EOS_SEED_ORION"]


@pytest.mark.integration
@pytest.mark.api
def test_firewall_rules_list(client):
    """Test listing firewall translation rules"""
    response = client.get("/relay/firewall/rules")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "total_rules" in data
    assert "rules" in data
    assert data["total_rules"] > 0


@pytest.mark.integration
@pytest.mark.api
def test_firewall_add_translation_rule(client):
    """Test adding custom translation rule"""
    payload = {
        "metaphor": "test metaphor",
        "concrete_event": "entity_interaction"
    }
    
    response = client.post("/relay/firewall/rules", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "Translation rule added" in data["message"]


@pytest.mark.integration
@pytest.mark.api
def test_firewall_quarantined_messages(client):
    """Test getting quarantined messages"""
    response = client.get("/relay/firewall/quarantined")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "total_quarantined" in data
    assert "messages" in data


@pytest.mark.integration
@pytest.mark.api
def test_schema_definitions(client):
    """Test getting schema definitions"""
    # Test listing schemas
    response = client.get("/relay/schemas")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "L1" in data["available_layers"]
    assert "L2" in data["available_layers"]
    assert "L3" in data["available_layers"]
    
    # Test getting specific schema
    response = client.get("/relay/schemas/L2")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["layer"] == "L2"
    assert "schema" in data


@pytest.mark.integration
@pytest.mark.api
def test_relay_full_l3_to_l1_pipeline(client):
    """Test full L3→L2→L1 pipeline via API"""
    # First L3→L2
    l3_payload = {
        "source_layer": "L3",
        "target_layer": "L2",
        "payload": {
            "schema_version": "1.0.0",
            "message_type": "l3_symbolic",
            "content_type": "lore_fragment",
            "payload": {
                "text": "Execute system action"
            },
            "context_tag": "api_test_pipeline"
        }
    }
    
    response = client.post("/relay/send", json=l3_payload)
    assert response.status_code == 200
    l2_result = response.json()
    
    # Now L2→L1
    l1_payload = {
        "source_layer": "L2",
        "target_layer": "L1",
        "payload": {
            "schema_version": "1.0.0",
            "message_type": "l1_action",
            "action_type": "api_response",
            "parameters": {},
            "context_tag": l2_result["payload"]["context_tag"],
            "anchor_id": l2_result["payload"]["anchor_id"]
        }
    }
    
    response = client.post("/relay/send", json=l1_payload)
    assert response.status_code == 200
    l1_result = response.json()
    
    assert l1_result["success"] is True
    assert l1_result["target_layer"] == "L1"
    assert l1_result["checks_performed"]["ethics_check"] is True
