"""
Test ChatGPT Agent Mode Integration for Aurora CloudBank

Validates agent mode capabilities including tool discovery, execution,
session management, and symbolic processing with Aurora's architecture.
"""

import pytest
from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration, chatgpt_agent_integration


class TestChatGPTAgentModeIntegration:
    """Test suite for ChatGPT Agent Mode integration"""

    def setup_method(self):
        self.agent = ChatGPTAgentModeIntegration()

    def test_initialization(self):
        assert self.agent.agent_status == "ready"
        assert self.agent.anchor_seed == "EOS_SEED_ORION"
        assert self.agent.ethics_protocol == "Picard_Delta_3"
        assert "context_tag" in self.agent.symbolic_anchors
        assert len(self.agent.tools_registry) > 0

    @pytest.mark.asyncio
    async def test_tool_discovery(self):
        tools_info = await self.agent.discover_tools()
        assert "tools" in tools_info
        assert "capabilities" in tools_info
        assert "symbolic_anchors" in tools_info
        assert tools_info["dlp_level"] == "DLP_L1_OK"
        assert "context_tag" in tools_info
        # Verify required tools are registered
        required_tools = ["symbolic_processing", "geometric_algebra", "session_management", "system_status"]
        for tool in required_tools:
            assert tool in tools_info["tools"]
            assert "description" in tools_info["tools"][tool]
            assert "parameters" in tools_info["tools"][tool]

    @pytest.mark.asyncio
    async def test_symbolic_processing_tool(self):
        parameters = {
            "operation": "test_symbolic_operation",
            "data": {"test": "data"},
            "anchor_context": "test_context",
        }
        result = await self.agent.execute_tool("symbolic_processing", parameters)
        assert result["success"] is True
        assert "result" in result
        assert result["symbolic_hash_validation"] is True
        assert result["dlp_level"] == "DLP_L1_OK"
        assert "execution_context" in result
        assert result["execution_context"]["context_tag"].startswith("agent_tool_execution_")

    @pytest.mark.asyncio
    async def test_geometric_algebra_tool(self):
        parameters = {"expression_a": "e1 + e2", "expression_b": "e2 + e3", "operation": "mult"}
        result = await self.agent.execute_tool("geometric_algebra", parameters)
        assert "result" in result
        assert "geometric_result" in result["result"]
        assert result["result"]["operation"] == "mult"
        assert result["symbolic_hash_validation"] is True

    @pytest.mark.asyncio
    async def test_session_management_tool(self):
        # Create session
        create_params = {"action": "create", "state_data": {"test_state": "initial"}}
        create_result = await self.agent.execute_tool("session_management", create_params)
        assert create_result["success"] is True
        session_id = create_result["result"]["session_id"]

        # Update session
        update_params = {"action": "update", "session_id": session_id, "state_data": {"test_state": "updated"}}
        update_result = await self.agent.execute_tool("session_management", update_params)
        assert update_result["success"] is True
        assert update_result["result"]["action"] == "updated"

        # Get session
        get_params = {"action": "get", "session_id": session_id}
        get_result = await self.agent.execute_tool("session_management", get_params)
        assert get_result["success"] is True
        assert get_result["result"]["state"]["state"]["test_state"] == "updated"

        # Delete session
        delete_params = {"action": "delete", "session_id": session_id}
        delete_result = await self.agent.execute_tool("session_management", delete_params)
        assert delete_result["success"] is True
        assert delete_result["result"]["action"] == "deleted"

    @pytest.mark.asyncio
    async def test_system_status_tool(self):
        # Basic status
        basic_params = {"detail_level": "basic"}
        basic_result = await self.agent.execute_tool("system_status", basic_params)
        assert basic_result["success"] is True
        assert "agent_status" in basic_result["result"]
        assert "symbolic_anchors" in basic_result["result"]
        assert "available_tools" in basic_result["result"]

        # Detailed status
        detailed_params = {"detail_level": "detailed"}
        detailed_result = await self.agent.execute_tool("system_status", detailed_params)
        assert detailed_result["success"] is True
        assert "config_version" in detailed_result["result"]
        assert "capabilities" in detailed_result["result"]

        # Full status
        full_params = {"detail_level": "full"}
        full_result = await self.agent.execute_tool("system_status", full_params)
        assert full_result["success"] is True
        assert "session_details" in full_result["result"]
        assert "tool_registry" in full_result["result"]

    @pytest.mark.asyncio
    async def test_invalid_tool_execution(self):
        # Test non-existent tool should raise HTTPException
        with pytest.raises(Exception) as exc:
            await self.agent.execute_tool("non_existent_tool", {})
        assert "not found" in str(exc.value)

        # Test invalid parameters returns structured error
        result = await self.agent.execute_tool("geometric_algebra", {"invalid": "params"})
        assert result["success"] is False
        assert "error" in result
        assert "recovery_suggestions" in result

    @pytest.mark.asyncio
    async def test_agent_status(self):
        status = await self.agent.get_agent_status()
        assert status["integration_status"] == "active"
        assert status["agent_mode"] == "chatgpt_agent_mode"
        assert status["dlp_compliance"] == "DLP_L1_OK"
        assert "symbolic_anchors" in status
        assert "capabilities" in status
        assert "context_tag" in status
        assert status["context_tag"] == "agent_status_report"

    def test_memory_seal_computation(self):
        seal1 = self.agent._compute_memory_seal()
        seal2 = self.agent._compute_memory_seal()
        assert seal1 == seal2
        assert len(seal1) == 16

    def test_parameter_validation(self):
        schema = {"properties": {"required_param": {"type": "string"}}, "required": ["required_param"]}
        # Valid parameters should pass
        valid_params = {"required_param": "test_value"}
        self.agent._validate_parameters(valid_params, schema)
        # Invalid parameters should fail
        invalid_params = {"wrong_param": "test_value"}
        with pytest.raises(ValueError):
            self.agent._validate_parameters(invalid_params, schema)


def test_global_instance():
    assert chatgpt_agent_integration is not None
    assert chatgpt_agent_integration.agent_status == "ready"
    assert len(chatgpt_agent_integration.tools_registry) > 0


def test_config_loading():
    config = chatgpt_agent_integration.config
    assert config["anchor_seed"] == "EOS_SEED_ORION"
    assert config["ethics_protocol"] == "Picard_Delta_3"
    assert "agent_capabilities" in config
