#!/usr/bin/env python3
"""
Tests for L2 Meta-Agent Bridge
==============================
Target: src/bridges/l2_meta_agent_bridge.py
Coverage Goal: 90%+

DLP: COVERAGE_IMPROVEMENT_CRITICAL
Chain: #932//. Integration Coverage Sprint
"""

import pytest
from datetime import datetime
from unittest.mock import patch

# Import the module under test
from src.bridges.l2_meta_agent_bridge import (
    CustomGptAgent,
    L2MetaAgentBridge,
    l2_bridge,
)


class TestCustomGptAgent:
    """Test CustomGptAgent dataclass"""

    def test_create_agent_with_required_fields(self):
        """Test creating agent with required fields only"""
        agent = CustomGptAgent(
            agent_id="TEST_AGENT",
            role="Test Role",
            type="META_AGENT",
            status="disconnected",
            description="Test agent",
            capabilities=["test_capability"],
            api_endpoint="/api/test",
        )
        assert agent.agent_id == "TEST_AGENT"
        assert agent.status == "disconnected"
        assert agent.connected is None
        assert agent.last_heartbeat is None
        assert agent.drift_lock is None
        assert agent.handshake_log == []

    def test_create_agent_with_all_fields(self):
        """Test creating agent with all fields"""
        now = datetime.now()
        agent = CustomGptAgent(
            agent_id="TEST_AGENT",
            role="Test Role",
            type="META_AGENT",
            status="connected",
            description="Test agent",
            capabilities=["cap1", "cap2"],
            api_endpoint="/api/test",
            connected=now,
            last_heartbeat=now,
            drift_lock=0.001,
            handshake_log=[{"step": "test"}],
        )
        assert agent.connected == now
        assert agent.drift_lock == 0.001
        assert len(agent.handshake_log) == 1

    def test_agent_handshake_log_default(self):
        """Test handshake_log defaults to empty list"""
        agent = CustomGptAgent(
            agent_id="TEST",
            role="Test",
            type="META_AGENT",
            status="disconnected",
            description="Test",
            capabilities=[],
            api_endpoint="/api",
        )
        assert agent.handshake_log == []
        assert isinstance(agent.handshake_log, list)


class TestL2MetaAgentBridgeInit:
    """Test L2MetaAgentBridge initialization"""

    def test_bridge_initializes_five_agents(self):
        """Test bridge initializes with 5 predefined agents"""
        bridge = L2MetaAgentBridge()
        assert len(bridge.agents) == 5
        assert "ARCHY" in bridge.agents
        assert "OPPY" in bridge.agents
        assert "LIORA" in bridge.agents
        assert "STARLING_AU" in bridge.agents
        assert "RIVERTHREAD_808" in bridge.agents

    def test_archy_agent_configuration(self):
        """Test ARCHY agent is properly configured"""
        bridge = L2MetaAgentBridge()
        archy = bridge.agents["ARCHY"]
        assert archy.role == "Bridge Coordinator"
        assert archy.type == "META_AGENT"
        assert "bridge_coordination" in archy.capabilities
        assert archy.api_endpoint == "/api/relay/archy"

    def test_oppy_agent_configuration(self):
        """Test OPPY agent is properly configured"""
        bridge = L2MetaAgentBridge()
        oppy = bridge.agents["OPPY"]
        assert oppy.role == "Vector/Data Processor"
        assert "vector_analysis" in oppy.capabilities

    def test_liora_agent_configuration(self):
        """Test LIORA agent is properly configured"""
        bridge = L2MetaAgentBridge()
        liora = bridge.agents["LIORA"]
        assert liora.role == "Handshake/Synchronization"
        assert "handshake_protocols" in liora.capabilities

    def test_activation_phrases_configured(self):
        """Test activation phrases are set for all agents"""
        bridge = L2MetaAgentBridge()
        assert len(bridge.activation_phrases) == 5
        assert bridge.activation_phrases["ARCHY"] == "ORION_ARCHY_RELAY_ACTIVATE//"
        assert bridge.activation_phrases["OPPY"] == "ORION_OPPY_RELAY_ACTIVATE//"

    def test_handshake_sequence_defined(self):
        """Test handshake sequence is properly defined"""
        bridge = L2MetaAgentBridge()
        expected = ["MESH_RUNTIME_ACTIVATE", "MESH_STATUS_CONFIRM"]
        assert bridge.handshake_sequence == expected

    def test_orion_core_config_set(self):
        """Test Orion core configuration is properly set"""
        bridge = L2MetaAgentBridge()
        config = bridge.orion_core_config
        assert config["anchor_seed"] == "EOS_SEED_ORION"
        assert config["ethics_protocol"] == "Picard_Delta_3"
        assert config["drift_threshold"] == 0.001
        assert config["version"] == "v3.5.1_macroready"


class TestL2MetaAgentBridgeActivation:
    """Test agent activation functionality"""

    @pytest.fixture
    def bridge(self):
        """Create fresh bridge instance for each test"""
        return L2MetaAgentBridge()

    @pytest.mark.asyncio
    async def test_activate_unknown_agent_returns_error(self, bridge):
        """Test activating unknown agent returns error"""
        result = await bridge.activate_agent("UNKNOWN", "phrase")
        assert result["success"] is False
        assert "Unknown agent" in result["error"]

    @pytest.mark.asyncio
    async def test_activate_with_wrong_phrase_returns_error(self, bridge):
        """Test activating with wrong phrase returns error"""
        result = await bridge.activate_agent("ARCHY", "WRONG_PHRASE")
        assert result["success"] is False
        assert "Invalid activation phrase" in result["error"]

    @pytest.mark.asyncio
    async def test_successful_agent_activation(self, bridge):
        """Test successful agent activation"""
        result = await bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
        assert result["success"] is True
        assert result["agent_id"] == "ARCHY"
        assert result["status"] == "connected"
        assert "handshake" in result
        assert "capabilities" in result

    @pytest.mark.asyncio
    async def test_activation_updates_agent_state(self, bridge):
        """Test activation updates agent internal state"""
        await bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
        archy = bridge.agents["ARCHY"]
        assert archy.status == "connected"
        assert archy.connected is not None
        assert archy.last_heartbeat is not None

    @pytest.mark.asyncio
    async def test_activate_all_agents(self, bridge):
        """Test activating all five agents"""
        activation_results = []
        for agent_id in bridge.agents:
            phrase = bridge.activation_phrases[agent_id]
            result = await bridge.activate_agent(agent_id, phrase)
            activation_results.append(result["success"])

        assert all(activation_results)

    @pytest.mark.asyncio
    async def test_activation_exception_handling(self, bridge):
        """Test activation handles exceptions gracefully"""
        # Mock _perform_zipwiz_handshake to raise exception
        with patch.object(
            bridge, "_perform_zipwiz_handshake", side_effect=Exception("Test error")
        ):
            result = await bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
            assert result["success"] is False
            assert "Test error" in result["error"]


class TestZIPWIZHandshake:
    """Test ZIPWIZ handshake protocol"""

    @pytest.fixture
    def bridge(self):
        """Create fresh bridge instance"""
        return L2MetaAgentBridge()

    @pytest.mark.asyncio
    async def test_handshake_sequence_order(self, bridge):
        """Test handshake follows correct sequence"""
        agent = bridge.agents["ARCHY"]
        result = await bridge._perform_zipwiz_handshake(agent)

        assert result["success"] is True
        assert "log" in result
        log_steps = [entry["step"] for entry in result["log"]]
        assert log_steps == bridge.handshake_sequence

    @pytest.mark.asyncio
    async def test_zipwiz_beacon(self, bridge):
        """Legacy ZIPWIZ beacon helper is explicitly non-production."""
        agent = bridge.agents["ARCHY"]
        result = await bridge._send_zipwiz_beacon(agent)

        assert result["success"] is False
        assert result["degraded"] is True
        assert result["transport"] == "demo_disabled"
        assert result["step"] == "ZIPWIZ_BEACON"
        assert result["agent_id"] == "ARCHY"

    @pytest.mark.asyncio
    async def test_orion_anchor_sync(self, bridge):
        """Legacy anchor sync helper is explicitly non-production."""
        agent = bridge.agents["OPPY"]
        result = await bridge._sync_orion_anchor(agent)

        assert result["success"] is False
        assert result["degraded"] is True
        assert result["transport"] == "demo_disabled"
        assert result["step"] == "ANCHOR_SYNC"

    @pytest.mark.asyncio
    async def test_ethics_audit(self, bridge):
        """Legacy ethics audit helper is explicitly non-production."""
        agent = bridge.agents["LIORA"]
        result = await bridge._perform_ethics_audit(agent)

        assert result["success"] is False
        assert result["degraded"] is True
        assert result["transport"] == "demo_disabled"
        assert result["step"] == "ETHICS_AUDIT"

    @pytest.mark.asyncio
    async def test_drift_validation(self, bridge):
        """Legacy drift validation helper is explicitly non-production."""
        agent = bridge.agents["STARLING_AU"]
        result = await bridge._validate_drift_lock(agent)

        assert result["success"] is False
        assert result["degraded"] is True
        assert result["transport"] == "demo_disabled"
        assert result["step"] == "DRIFT_VALIDATION"

    @pytest.mark.asyncio
    async def test_handshake_returns_runtime_transport(self, bridge):
        """Test activation handshake reports the real runtime boundary."""
        agent = bridge.agents["ARCHY"]
        result = await bridge._perform_zipwiz_handshake(agent)

        assert "drift_lock" not in result
        assert result["transport"]["mode"] == "mesh_runtime"
        assert result["transport"]["acknowledgement"] == "agent_state_persisted"

    def test_handshake_failure_helper(self, bridge):
        """Test handshake failure helper method"""
        log = [{"step": "test"}]
        result = bridge._handshake_failure("Error message", {"detail": "info"}, log)

        assert result["success"] is False
        assert result["error"] == "Error message"
        assert result["details"] == {"detail": "info"}
        assert result["log"] == log


class TestConstellationStatus:
    """Test constellation status functionality"""

    @pytest.fixture
    def bridge(self):
        """Create fresh bridge instance"""
        return L2MetaAgentBridge()

    def test_get_constellation_status_structure(self, bridge):
        """Test constellation status returns proper structure"""
        status = bridge.get_constellation_status()

        assert "relay_tier" in status
        assert "orion_core" in status
        assert "activation_phrases" in status
        assert "timestamp" in status

    def test_constellation_counts_disconnected(self, bridge):
        """Test constellation counts when all disconnected"""
        status = bridge.get_constellation_status()
        relay_tier = status["relay_tier"]

        assert relay_tier["total_capsules"] == 5
        assert relay_tier["connected_capsules"] == 0

    @pytest.mark.asyncio
    async def test_constellation_counts_after_activation(self, bridge):
        """Test constellation counts after activation"""
        await bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
        status = bridge.get_constellation_status()

        assert status["relay_tier"]["connected_capsules"] == 1

    def test_constellation_includes_agent_details(self, bridge):
        """Test constellation status includes agent details"""
        status = bridge.get_constellation_status()
        capsules = status["relay_tier"]["capsules"]

        assert len(capsules) == 5
        for capsule in capsules:
            assert "agent_id" in capsule
            assert "role" in capsule
            assert "status" in capsule
            assert "capabilities" in capsule


class TestMessageRelay:
    """Test message relay functionality"""

    @pytest.fixture
    async def connected_bridge(self):
        """Create bridge with connected agents"""
        bridge = L2MetaAgentBridge()
        await bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
        await bridge.activate_agent("OPPY", "ORION_OPPY_RELAY_ACTIVATE//")
        return bridge

    @pytest.mark.asyncio
    async def test_relay_unknown_source_agent(self):
        """Test relay from unknown source agent"""
        bridge = L2MetaAgentBridge()
        result = await bridge.relay_message("UNKNOWN", "ARCHY", "test")

        assert result["success"] is False
        assert "Unknown source agent" in result["error"]

    @pytest.mark.asyncio
    async def test_relay_from_disconnected_agent(self):
        """Test relay from disconnected agent"""
        bridge = L2MetaAgentBridge()
        result = await bridge.relay_message("ARCHY", "OPPY", "test")

        assert result["success"] is False
        assert "not connected" in result["error"]

    @pytest.mark.asyncio
    async def test_relay_direct_message(self, connected_bridge):
        """Test direct message relay"""
        result = await connected_bridge.relay_message("ARCHY", "OPPY", "Hello OPPY", "direct")

        assert result["success"] is True
        assert result["from"] == "ARCHY"
        assert "OPPY" in result["to"]
        assert result["type"] == "direct"
        assert result["relay_status"] == "accepted"
        assert result["delivery_acknowledgements"][0]["event_id"] > 0

    @pytest.mark.asyncio
    async def test_relay_to_aurora(self, connected_bridge):
        """Test message relay to Aurora core"""
        result = await connected_bridge.relay_message("ARCHY", "Aurora", "Report", "direct")

        assert result["success"] is True
        assert "Aurora" in result["to"]

    @pytest.mark.asyncio
    async def test_relay_to_au_alias(self, connected_bridge):
        """Test message relay to AU alias"""
        result = await connected_bridge.relay_message("ARCHY", "AU", "Report", "direct")

        assert result["success"] is True
        assert "Aurora" in result["to"]

    @pytest.mark.asyncio
    async def test_broadcast_message(self, connected_bridge):
        """Test broadcast message to mesh"""
        result = await connected_bridge.relay_message(
            "ARCHY", "all", "Broadcast message", "broadcast"
        )

        assert result["success"] is True
        assert result["type"] == "broadcast"
        assert "OPPY" in result["to"]
        assert "ARCHY" not in result["to"]  # Sender excluded

    @pytest.mark.asyncio
    async def test_relay_updates_heartbeat(self, connected_bridge):
        """Test relay updates sender heartbeat"""
        old_heartbeat = connected_bridge.agents["ARCHY"].last_heartbeat
        await connected_bridge.relay_message("ARCHY", "Aurora", "test")
        new_heartbeat = connected_bridge.agents["ARCHY"].last_heartbeat

        assert new_heartbeat >= old_heartbeat

    @pytest.mark.asyncio
    async def test_relay_unknown_target_direct(self, connected_bridge):
        """Test relay to unknown target in direct mode"""
        result = await connected_bridge.relay_message("ARCHY", "UNKNOWN_AGENT", "test", "direct")

        assert result["success"] is False
        assert "Unknown target agent" in result["error"]


class TestAgentDisconnection:
    """Test agent disconnection functionality"""

    @pytest.fixture
    async def connected_bridge(self):
        """Create bridge with a connected agent"""
        bridge = L2MetaAgentBridge()
        await bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
        return bridge

    @pytest.mark.asyncio
    async def test_disconnect_unknown_agent(self):
        """Test disconnecting unknown agent"""
        bridge = L2MetaAgentBridge()
        result = await bridge.disconnect_agent("UNKNOWN")

        assert result["success"] is False
        assert "Unknown agent" in result["error"]

    @pytest.mark.asyncio
    async def test_disconnect_connected_agent(self, connected_bridge):
        """Test disconnecting connected agent"""
        result = await connected_bridge.disconnect_agent("ARCHY")

        assert result["success"] is True
        assert result["agent_id"] == "ARCHY"
        assert result["status"] == "disconnected"

    @pytest.mark.asyncio
    async def test_disconnect_clears_agent_state(self, connected_bridge):
        """Test disconnect clears agent state"""
        await connected_bridge.disconnect_agent("ARCHY")
        archy = connected_bridge.agents["ARCHY"]

        assert archy.status == "disconnected"
        assert archy.connected is None
        assert archy.last_heartbeat is None
        assert archy.handshake_log == []


class TestGetAgentStatus:
    """Test get_agent_status functionality"""

    @pytest.fixture
    def bridge(self):
        """Create fresh bridge instance"""
        return L2MetaAgentBridge()

    def test_get_status_unknown_agent(self, bridge):
        """Test getting status of unknown agent"""
        result = bridge.get_agent_status("UNKNOWN")

        assert result["success"] is False
        assert "Unknown agent" in result["error"]

    def test_get_status_disconnected_agent(self, bridge):
        """Test getting status of disconnected agent"""
        result = bridge.get_agent_status("ARCHY")

        assert result["success"] is True
        assert result["status"] == "disconnected"
        assert "connected" not in result
        assert "uptime" not in result

    @pytest.mark.asyncio
    async def test_get_status_connected_agent(self, bridge):
        """Test getting status of connected agent"""
        await bridge.activate_agent("ARCHY", "ORION_ARCHY_RELAY_ACTIVATE//")
        result = bridge.get_agent_status("ARCHY")

        assert result["success"] is True
        assert result["status"] == "connected"
        assert "connected" in result
        assert "uptime" in result
        assert "last_heartbeat" in result
        assert "handshake_log" in result


class TestGlobalBridgeInstance:
    """Test global l2_bridge instance"""

    def test_global_bridge_exists(self):
        """Test global bridge instance is available"""
        assert l2_bridge is not None
        assert isinstance(l2_bridge, L2MetaAgentBridge)

    def test_global_bridge_has_agents(self):
        """Test global bridge has agents configured"""
        assert len(l2_bridge.agents) == 5


class TestCLIFunction:
    """Test CLI function"""

    def test_constellation_status_cli_flag(self):
        """Test CLI with --constellation-status flag"""
        import sys
        from io import StringIO
        from src.bridges.l2_meta_agent_bridge import cli

        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        old_argv = sys.argv

        try:
            sys.argv = ["l2_meta_agent_bridge.py", "--constellation-status"]
            result = cli()
            output = sys.stdout.getvalue()

            assert result == 0
            assert "relay_tier" in output
        finally:
            sys.stdout = old_stdout
            sys.argv = old_argv
