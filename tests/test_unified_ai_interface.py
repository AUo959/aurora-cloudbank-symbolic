"""
Tests for AI Core Unified Interface

Tests model selection, fallback chains, and integration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from modules.ai_core.unified_ai_interface import (
    AIModel,
    AIProvider,
    AIRequest,
    AIResponse,
    ModelCapabilities,
    UnifiedAIInterface,
)


@pytest.mark.unit
@pytest.mark.ai
class TestUnifiedAIInterface:
    """Test suite for Unified AI Interface"""

    def test_model_capabilities_registry(self):
        """Test that all models have capability profiles"""
        interface = UnifiedAIInterface()

        assert len(interface.CAPABILITIES) > 0
        assert AIModel.CLAUDE_35_SONNET in interface.CAPABILITIES
        assert AIModel.CLAUDE_45_OPUS in interface.CAPABILITIES
        assert AIModel.GPT_4O in interface.CAPABILITIES
        assert AIModel.GPT_5 in interface.CAPABILITIES
        assert AIModel.GPT_5_CODEX in interface.CAPABILITIES

    def test_model_capabilities_structure(self):
        """Test model capabilities have required fields"""
        interface = UnifiedAIInterface()

        for model, caps in interface.CAPABILITIES.items():
            assert isinstance(caps, ModelCapabilities)
            assert caps.model == model
            assert caps.context_window > 0
            assert caps.max_output_tokens > 0
            assert 1 <= caps.reasoning_strength <= 10
            assert 1 <= caps.code_generation_strength <= 10
            assert 1 <= caps.mathematical_strength <= 10

    def test_fallback_chains(self):
        """Test fallback chains are defined for each task type"""
        interface = UnifiedAIInterface()

        required_chains = ["reasoning", "code_generation", "mathematical", "general"]

        for chain_type in required_chains:
            assert chain_type in interface.FALLBACK_CHAINS
            chain = interface.FALLBACK_CHAINS[chain_type]
            assert len(chain) > 0
            assert all(isinstance(m, AIModel) for m in chain)

    @pytest.mark.asyncio
    async def test_optimal_model_selection_with_preference(self):
        """Test model selection respects user preference"""
        interface = UnifiedAIInterface()

        # Mark GPT-4O as available
        interface.CAPABILITIES[AIModel.GPT_4O].available = True

        request = AIRequest(prompt="test", model_preference=AIModel.GPT_4O)

        selected = await interface.select_optimal_model(request, "general")
        assert selected == AIModel.GPT_4O

    @pytest.mark.asyncio
    async def test_optimal_model_selection_fallback(self):
        """Test model selection uses fallback when preference unavailable"""
        interface = UnifiedAIInterface()

        # Mark GPT-5 as unavailable, GPT-4O as available
        interface.CAPABILITIES[AIModel.GPT_5].available = False
        interface.CAPABILITIES[AIModel.GPT_4O].available = True

        request = AIRequest(prompt="test", model_preference=AIModel.GPT_5)

        selected = await interface.select_optimal_model(request, "general")
        # Should fallback to an available model
        assert selected in interface.CAPABILITIES
        assert interface.CAPABILITIES[selected].available

    @pytest.mark.asyncio
    async def test_optimal_model_selection_task_specific(self):
        """Test model selection is optimized for task type"""
        interface = UnifiedAIInterface()

        # Make all models available
        for model in interface.CAPABILITIES:
            interface.CAPABILITIES[model].available = True

        request = AIRequest(prompt="test")

        # For code generation, should prefer Codex
        selected_code = await interface.select_optimal_model(request, "code_generation")
        assert selected_code == AIModel.GPT_5_CODEX  # First in code gen chain

        # For reasoning, should prefer Claude 4.5 Opus
        selected_reasoning = await interface.select_optimal_model(request, "reasoning")
        assert selected_reasoning == AIModel.CLAUDE_45_OPUS  # First in reasoning chain

    def test_get_available_models(self):
        """Test getting list of available models"""
        interface = UnifiedAIInterface()

        # Set some models as available
        interface.CAPABILITIES[AIModel.GPT_4O].available = True
        interface.CAPABILITIES[AIModel.CLAUDE_35_SONNET].available = True
        interface.CAPABILITIES[AIModel.GPT_5].available = False

        available = interface.get_available_models()

        assert AIModel.GPT_4O in available
        assert AIModel.CLAUDE_35_SONNET in available
        assert AIModel.GPT_5 not in available

    def test_enable_disable_models(self):
        """Test runtime model enable/disable"""
        interface = UnifiedAIInterface()

        # Disable GPT-5
        interface.disable_model(AIModel.GPT_5)
        assert not interface.CAPABILITIES[AIModel.GPT_5].available

        # Enable GPT-5
        interface.enable_model(AIModel.GPT_5)
        assert interface.CAPABILITIES[AIModel.GPT_5].available


@pytest.mark.unit
@pytest.mark.ai
class TestAIRequestResponse:
    """Test AI request/response data structures"""

    def test_ai_request_defaults(self):
        """Test AIRequest has sensible defaults"""
        request = AIRequest(prompt="test prompt")

        assert request.prompt == "test prompt"
        assert request.max_tokens == 4096
        assert request.temperature == 0.7
        assert request.top_p == 0.9
        assert request.dlp_tracking is True
        assert request.safety_level == "high"

    def test_ai_request_custom_values(self):
        """Test AIRequest accepts custom values"""
        request = AIRequest(
            prompt="test",
            system_prompt="system context",
            max_tokens=8192,
            temperature=0.5,
            model_preference=AIModel.CLAUDE_45_OPUS,
            fallback_chain=[AIModel.CLAUDE_35_SONNET, AIModel.GPT_4O],
            context_tag="custom_tag",
        )

        assert request.system_prompt == "system context"
        assert request.max_tokens == 8192
        assert request.temperature == 0.5
        assert request.model_preference == AIModel.CLAUDE_45_OPUS
        assert len(request.fallback_chain) == 2
        assert request.context_tag == "custom_tag"

    def test_ai_response_structure(self):
        """Test AIResponse has required fields"""
        response = AIResponse(
            content="response content",
            model_used=AIModel.GPT_4O,
            provider=AIProvider.OPENAI,
            tokens_used=150,
            latency_ms=523.5,
        )

        assert response.content == "response content"
        assert response.model_used == AIModel.GPT_4O
        assert response.provider == AIProvider.OPENAI
        assert response.tokens_used == 150
        assert response.latency_ms == 523.5
        assert response.success is True
        assert response.error is None
        assert isinstance(response.timestamp, str)


@pytest.mark.integration
@pytest.mark.ai
class TestModelIntegration:
    """Integration tests for AI model interactions"""

    @pytest.mark.asyncio
    async def test_fallback_chain_execution(self):
        """Test that fallback chain is tried in order when models fail"""
        interface = UnifiedAIInterface()

        # Mock all models as available
        for model in interface.CAPABILITIES:
            interface.CAPABILITIES[model].available = True

        request = AIRequest(
            prompt="test",
            fallback_chain=[
                AIModel.CLAUDE_45_OPUS,
                AIModel.CLAUDE_35_SONNET,
                AIModel.GPT_4O,
            ],
        )

        # Note: This test would need actual API mocking to fully test
        # For now, verify fallback chain is properly constructed
        selected = await interface.select_optimal_model(request, "general")
        assert selected in request.fallback_chain


@pytest.mark.smoke
@pytest.mark.ai
def test_ai_core_imports():
    """Smoke test that all AI core components can be imported"""
    from modules.ai_core import (
        AIModel,
        AIProvider,
        AIRequest,
        AIResponse,
        ModelCapabilities,
        UnifiedAIInterface,
        unified_ai,
    )

    assert AIModel is not None
    assert AIProvider is not None
    assert AIRequest is not None
    assert AIResponse is not None
    assert ModelCapabilities is not None
    assert UnifiedAIInterface is not None
    assert unified_ai is not None
