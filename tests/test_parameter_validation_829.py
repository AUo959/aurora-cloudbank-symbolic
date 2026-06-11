"""
Tests for issue #829 — parameter schema enforcement in ChatGPT and Gemini integrations.

Covers:
  ChatGPT integration
    - bad enum value is rejected
    - non-string expression is rejected
    - expression with disallowed operator/token is rejected
    - valid input is accepted end-to-end

  Gemini integration
    - missing required field (target_resource) is rejected
    - extra unknown field is rejected
    - valid input is accepted end-to-end
"""

import pytest

from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration
from src.integrations.gemini_agent_integration import GeminiAgentIntegration


# ---------------------------------------------------------------------------
# ChatGPT integration
# ---------------------------------------------------------------------------

class TestChatGPTParameterValidation:
    """Schema-enforcement tests for ChatGPTAgentModeIntegration._validate_parameters."""

    def setup_method(self):
        self.agent = ChatGPTAgentModeIntegration()

    # --- enum enforcement ---

    def test_bad_enum_value_raises(self):
        """An enum field with an unsupported value must raise ValueError."""
        schema = {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["mult", "add", "sub"],
                }
            },
            "required": ["operation"],
        }
        with pytest.raises(ValueError, match="must be one of"):
            self.agent._validate_parameters({"operation": "div"}, schema)

    def test_valid_enum_value_accepted(self):
        """A value that is in the enum list must not raise."""
        schema = {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["mult", "add", "sub"],
                }
            },
            "required": ["operation"],
        }
        # Should not raise
        self.agent._validate_parameters({"operation": "add"}, schema)

    # --- type enforcement ---

    def test_non_string_expression_raises(self):
        """expression_a must be a string; an integer must be rejected."""
        schema = {
            "type": "object",
            "properties": {
                "expression_a": {"type": "string"},
                "expression_b": {"type": "string"},
                "operation": {"type": "string", "enum": ["mult", "add", "sub"]},
            },
            "required": ["expression_a", "expression_b", "operation"],
        }
        with pytest.raises(TypeError):
            self.agent._validate_parameters(
                {"expression_a": 123, "expression_b": "e2", "operation": "mult"},
                schema,
            )

    def test_non_string_both_expressions_raises(self):
        """Both expressions being non-strings: at least one TypeError must be raised."""
        schema = {
            "type": "object",
            "properties": {
                "expression_a": {"type": "string"},
                "expression_b": {"type": "string"},
                "operation": {"type": "string", "enum": ["mult"]},
            },
            "required": ["expression_a", "expression_b", "operation"],
        }
        with pytest.raises(TypeError):
            self.agent._validate_parameters(
                {"expression_a": [], "expression_b": {}, "operation": "mult"},
                schema,
            )

    # --- GA expression syntax validation (via execute_tool) ---

    @pytest.mark.asyncio
    async def test_expression_with_disallowed_token_rejected(self):
        """Expressions containing '__import__' must be rejected by the handler."""
        params = {
            "expression_a": "__import__('os')",
            "expression_b": "e2",
            "operation": "mult",
        }
        result = await self.agent.execute_tool("geometric_algebra", params)
        # The error is caught inside execute_tool and surfaced as success=False
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_expression_with_unsupported_shell_chars_rejected(self):
        """Expressions containing shell-injection characters must be rejected."""
        params = {
            "expression_a": "e1; rm -rf /",
            "expression_b": "e2",
            "operation": "mult",
        }
        result = await self.agent.execute_tool("geometric_algebra", params)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_expression_non_string_rejected_via_execute_tool(self):
        """Passing a non-string expression through execute_tool must return success=False."""
        params = {
            "expression_a": 42,
            "expression_b": "e2",
            "operation": "mult",
        }
        result = await self.agent.execute_tool("geometric_algebra", params)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_bad_enum_via_execute_tool_returns_error(self):
        """Passing an unsupported 'operation' value must surface as success=False."""
        params = {
            "expression_a": "e1",
            "expression_b": "e2",
            "operation": "invalid_op",
        }
        result = await self.agent.execute_tool("geometric_algebra", params)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_valid_ga_input_accepted(self):
        """A correctly-formed geometric-algebra call must succeed."""
        params = {
            "expression_a": "e1 + e2",
            "expression_b": "e3",
            "operation": "mult",
        }
        result = await self.agent.execute_tool("geometric_algebra", params)
        assert result["success"] is True
        assert "geometric_result" in result["result"]


# ---------------------------------------------------------------------------
# Gemini integration
# ---------------------------------------------------------------------------

class TestGeminiParameterValidation:
    """Schema-enforcement tests for GeminiAgentIntegration.handle_tool_call."""

    def setup_method(self):
        self.integration = GeminiAgentIntegration()

    @pytest.mark.asyncio
    async def test_missing_target_resource_rejected(self):
        """Omitting required field target_resource must return a validation error."""
        result = await self.integration.handle_tool_call(
            "execute_sensitive_operation",
            {"dry_run": True},
        )
        assert result["success"] is False
        assert "details" in result
        # At least one error entry should reference the missing field
        fields = [d["field"] for d in result["details"]]
        assert any("target_resource" in f for f in fields)

    @pytest.mark.asyncio
    async def test_extra_unknown_field_rejected(self):
        """Including an unrecognised extra field must return a validation error."""
        result = await self.integration.handle_tool_call(
            "execute_sensitive_operation",
            {
                "target_resource": "quantum_memory_bank_1",
                "dry_run": True,
                "unknown_extra_field": "should_be_rejected",
            },
        )
        assert result["success"] is False
        assert "details" in result

    @pytest.mark.asyncio
    async def test_wrong_type_for_dry_run_rejected(self):
        """dry_run must be a boolean; passing a list must be rejected."""
        result = await self.integration.handle_tool_call(
            "execute_sensitive_operation",
            {"target_resource": "res_1", "dry_run": [True]},
        )
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_valid_dry_run_accepted(self):
        """A valid dry-run call must return success with an impact_report."""
        result = await self.integration.handle_tool_call(
            "execute_sensitive_operation",
            {"target_resource": "quantum_memory_bank_1", "dry_run": True},
        )
        assert result["success"] is True
        assert result.get("dry_run") is True
        assert "impact_report" in result

    @pytest.mark.asyncio
    async def test_valid_committed_run_accepted(self):
        """A valid committed-run call (dry_run=False) must return success."""
        result = await self.integration.handle_tool_call(
            "execute_sensitive_operation",
            {"target_resource": "quantum_memory_bank_1", "dry_run": False},
        )
        assert result["success"] is True
        assert result.get("dry_run") is False
