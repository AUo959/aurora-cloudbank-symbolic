"""
Test L2 Meta-Agent Bridge API
Aurora CloudBank Symbolic v3.5.1

Tests for the L2 Meta-Agent Bridge REST API endpoints including:
- Health check endpoint
- Constellation status retrieval
- Agent activation (success and failure cases)
- Agent status queries (valid and invalid agent IDs)
- Message relay functionality
- Agent disconnection

DLP: test_l2_meta_agent_api_v1
Anchors: EOS_SEED_ORION, Picard_Delta_3
"""

import pytest
from fastapi.testclient import TestClient

# Import the app
from api.aurora_api import app

# Import the bridge for direct testing
from src.bridges.l2_meta_agent_bridge import l2_bridge

# Import security dependencies for mocking
from src.middleware.fastapi_security import security


@pytest.fixture
def api_client():
    """Create test client with security dependency overridden and CSRF patched."""
    from unittest.mock import patch

    def override_security():
        """Mock security dependency - return mock credentials."""
        class MockCredentials:
            credentials = "test-token"
        return MockCredentials()

    # Apply dependency overrides
    app.dependency_overrides[security] = override_security

    # Patch verify_csrf_token to bypass CSRF validation
    with patch("src.api.l2_meta_agent_api.verify_csrf_token"):
        # Create client with overrides
        client = TestClient(app)
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_bridge_state():
    """Reset bridge state for each test."""
    # Reset before test
    for agent in l2_bridge.agents.values():
        agent.status = "disconnected"
        agent.connected = None
        agent.last_heartbeat = None
        agent.handshake_log = []
    yield
    # Reset after test
    for agent in l2_bridge.agents.values():
        agent.status = "disconnected"
        agent.connected = None
        agent.last_heartbeat = None
        agent.handshake_log = []


class TestL2MetaAgentAPI:
    """Test suite for L2 Meta-Agent Bridge API endpoints"""

    def test_health_endpoint(self, api_client):
        """Test health check endpoint returns correct status"""
        response = api_client.get("/api/l2-agents/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["bridge_available"] is True
        assert data["total_agents"] == 5
        assert data["connected_agents"] == 0
        assert data["anchor_seed"] == "EOS_SEED_ORION"
        assert data["ethics_protocol"] == "Picard_Delta_3"
        assert "version" in data
        assert "timestamp" in data

    def test_constellation_status(self, api_client):
        """Test constellation status returns full relay tier info"""
        response = api_client.get("/api/l2-agents/constellation")
        assert response.status_code == 200

        data = response.json()
        assert "relay_tier" in data
        assert "orion_core" in data
        assert "activation_phrases" in data
        assert "timestamp" in data

        # Check relay tier structure
        relay_tier = data["relay_tier"]
        assert relay_tier["constellation"] == "RELAY_TIER_CAPSULES"
        assert relay_tier["total_capsules"] == 5
        assert "capsules" in relay_tier

        # Check orion core config
        orion_core = data["orion_core"]
        assert orion_core["anchor_seed"] == "EOS_SEED_ORION"
        assert orion_core["ethics_protocol"] == "Picard_Delta_3"

        # Check activation phrases
        assert "ARCHY" in data["activation_phrases"]
        assert "OPPY" in data["activation_phrases"]

    def test_get_agent_status_valid(self, api_client):
        """Test getting status of a valid agent"""
        response = api_client.get("/api/l2-agents/agent/ARCHY")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["agent_id"] == "ARCHY"
        assert data["role"] == "Bridge Coordinator"
        assert data["status"] == "disconnected"
        assert "capabilities" in data
        assert "architectural_planning" in data["capabilities"]

    def test_get_agent_status_invalid(self, api_client):
        """Test getting status of invalid agent returns 404"""
        response = api_client.get("/api/l2-agents/agent/INVALID_AGENT")
        assert response.status_code == 404

    def test_activation_phrases(self, api_client):
        """Test activation phrases endpoint"""
        response = api_client.get(
            "/api/l2-agents/activation-phrases",
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        data = response.json()
        assert "activation_phrases" in data
        assert "agents" in data
        assert "handshake_sequence" in data
        assert "timestamp" in data

        # Check phrases
        phrases = data["activation_phrases"]
        assert phrases["ARCHY"] == "ORION_ARCHY_RELAY_ACTIVATE//"
        assert phrases["OPPY"] == "ORION_OPPY_RELAY_ACTIVATE//"
        assert phrases["LIORA"] == "ORION_LIORA_RELAY_ACTIVATE//"

        # Check handshake sequence
        sequence = data["handshake_sequence"]
        assert "ZIPWIZ_BEACON" in sequence
        assert "ANCHOR_SYNC" in sequence
        assert "ETHICS_AUDIT" in sequence
        assert "DRIFT_VALIDATION" in sequence

    @pytest.mark.asyncio
    async def test_activate_agent_success(self, api_client):
        """Test successful agent activation with valid credentials"""
        response = api_client.post(
            "/api/l2-agents/activate",
            json={
                "agent_id": "ARCHY",
                "activation_phrase": "ORION_ARCHY_RELAY_ACTIVATE//"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["agent_id"] == "ARCHY"
        assert data["status"] == "connected"
        assert "handshake" in data
        assert "capabilities" in data
        assert "description" in data

        # Verify handshake details
        handshake = data["handshake"]
        assert handshake["success"] is True
        assert "log" in handshake
        assert "drift_lock" in handshake

    @pytest.mark.asyncio
    async def test_activate_agent_invalid_phrase(self, api_client):
        """Test activation with invalid phrase fails"""
        response = api_client.post(
            "/api/l2-agents/activate",
            json={
                "agent_id": "ARCHY",
                "activation_phrase": "INVALID_PHRASE"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is False
        assert data["error"] == "Invalid activation phrase"

    @pytest.mark.asyncio
    async def test_activate_agent_unknown_agent(self, api_client):
        """Test activation of unknown agent fails"""
        response = api_client.post(
            "/api/l2-agents/activate",
            json={
                "agent_id": "UNKNOWN_AGENT",
                "activation_phrase": "ORION_UNKNOWN_RELAY_ACTIVATE//"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is False
        assert "Unknown agent" in data["error"]

    @pytest.mark.asyncio
    async def test_relay_message_success(self, api_client):
        """Test successful message relay between agents"""
        # Activate ARCHY first
        api_client.post(
            "/api/l2-agents/activate",
            json={
                "agent_id": "ARCHY",
                "activation_phrase": "ORION_ARCHY_RELAY_ACTIVATE//"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        # Relay message
        response = api_client.post(
            "/api/l2-agents/relay",
            json={
                "from_agent": "ARCHY",
                "to_agent": "Aurora",
                "message": "Test message from ARCHY",
                "message_type": "direct"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "message_id" in data
        assert data["from_agent"] == "ARCHY"
        assert data["processed"] is True

    @pytest.mark.asyncio
    async def test_relay_message_disconnected_agent(self, api_client):
        """Test message relay fails when source agent is disconnected"""
        response = api_client.post(
            "/api/l2-agents/relay",
            json={
                "from_agent": "OPPY",
                "to_agent": "Aurora",
                "message": "Test message",
                "message_type": "direct"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is False
        assert "not connected" in data["error"]

    @pytest.mark.asyncio
    async def test_disconnect_agent_success(self, api_client):
        """Test successful agent disconnection"""
        # First activate an agent
        api_client.post(
            "/api/l2-agents/activate",
            json={
                "agent_id": "LIORA",
                "activation_phrase": "ORION_LIORA_RELAY_ACTIVATE//"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        # Now disconnect
        response = api_client.post(
            "/api/l2-agents/disconnect/LIORA",
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["agent_id"] == "LIORA"
        assert data["status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_disconnect_unknown_agent(self, api_client):
        """Test disconnection of unknown agent returns error"""
        response = api_client.post(
            "/api/l2-agents/disconnect/UNKNOWN",
            headers={"Authorization": "Bearer test-token"}
        )
        assert response.status_code == 404

    def test_all_agents_present_in_constellation(self, api_client):
        """Test all expected agents are in constellation"""
        response = api_client.get("/api/l2-agents/constellation")
        data = response.json()

        expected_agents = ["ARCHY", "OPPY", "LIORA", "STARLING_AU", "RIVERTHREAD_808"]
        capsules = data["relay_tier"]["capsules"]
        agent_ids = [c["agent_id"] for c in capsules]

        for agent in expected_agents:
            assert agent in agent_ids

    def test_handshake_sequence_complete(self, api_client):
        """Test handshake sequence contains all required steps"""
        response = api_client.get(
            "/api/l2-agents/activation-phrases",
            headers={"Authorization": "Bearer test-token"}
        )
        data = response.json()

        expected_steps = ["ZIPWIZ_BEACON", "ANCHOR_SYNC", "ETHICS_AUDIT", "DRIFT_VALIDATION"]
        for step in expected_steps:
            assert step in data["handshake_sequence"]


class TestL2MetaAgentBridgeDirect:
    """Direct tests for L2MetaAgentBridge class"""

    def setup_method(self):
        """Reset bridge state before each test"""
        for agent in l2_bridge.agents.values():
            agent.status = "disconnected"
            agent.connected = None
            agent.last_heartbeat = None
            agent.handshake_log = []

    def test_bridge_initialization(self):
        """Test bridge initializes with correct configuration"""
        assert len(l2_bridge.agents) == 5
        assert l2_bridge.orion_core_config["anchor_seed"] == "EOS_SEED_ORION"
        assert l2_bridge.orion_core_config["ethics_protocol"] == "Picard_Delta_3"
        assert l2_bridge.orion_core_config["drift_threshold"] == 0.001

    def test_agent_configuration(self):
        """Test individual agent configurations"""
        # ARCHY
        archy = l2_bridge.agents["ARCHY"]
        assert archy.role == "Bridge Coordinator"
        assert "architectural_planning" in archy.capabilities

        # RIVERTHREAD_808
        riverthread = l2_bridge.agents["RIVERTHREAD_808"]
        assert riverthread.role == "Narrative/Stream"
        assert "temporal_flow" in riverthread.capabilities

    @pytest.mark.asyncio
    async def test_full_activation_flow(self):
        """Test complete agent activation flow"""
        # Activate agent
        result = await l2_bridge.activate_agent(
            "STARLING_AU",
            "ORION_STARLING_AU_RELAY_ACTIVATE//"
        )
        assert result["success"] is True

        # Check agent state
        agent = l2_bridge.agents["STARLING_AU"]
        assert agent.status == "connected"
        assert agent.connected is not None
        assert agent.drift_lock == 0.000
        assert len(agent.handshake_log) == 4  # 4 handshake steps

        # Disconnect
        disconnect_result = await l2_bridge.disconnect_agent("STARLING_AU")
        assert disconnect_result["success"] is True
        assert agent.status == "disconnected"

    @pytest.mark.asyncio
    async def test_broadcast_message(self):
        """Test broadcast message to all connected agents"""
        # Activate multiple agents
        await l2_bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
        await l2_bridge.activate_agent("OPPY", "ORION_OPPY_RELAY_ACTIVATE//")

        # Broadcast from ARCHY
        result = await l2_bridge.relay_message(
            from_agent="ARCHY",
            to_agent="broadcast",
            message="Broadcast test",
            message_type="broadcast"
        )
        assert result["success"] is True
        assert result["type"] == "broadcast"
        assert "OPPY" in result["to"]

    def test_get_constellation_status_structure(self):
        """Test constellation status has complete structure"""
        status = l2_bridge.get_constellation_status()

        # Verify top-level keys
        assert "relay_tier" in status
        assert "orion_core" in status
        assert "activation_phrases" in status
        assert "timestamp" in status

        # Verify relay tier
        relay_tier = status["relay_tier"]
        assert relay_tier["constellation"] == "RELAY_TIER_CAPSULES"
        assert relay_tier["total_capsules"] == 5
        assert len(relay_tier["capsules"]) == 5

        # Verify each capsule has required fields
        for capsule in relay_tier["capsules"]:
            assert "agent_id" in capsule
            assert "role" in capsule
            assert "status" in capsule
            assert "capabilities" in capsule
