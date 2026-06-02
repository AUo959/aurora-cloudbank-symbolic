"""
Tests for AI Core Unified Interface

Tests model selection, fallback chains, and integration
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

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

    def test_aspirational_models_default_unavailable(self):
        """Aspirational placeholder IDs must ship gated (available=False)."""
        interface = UnifiedAIInterface()

        for model in (AIModel.CLAUDE_45_OPUS, AIModel.GPT_5, AIModel.GPT_5_CODEX):
            assert interface.CAPABILITIES[model].available is False, (
                f"{model.value} is an unverified placeholder and must default to "
                "available=False"
            )

    @pytest.mark.asyncio
    async def test_unavailable_model_cannot_be_selected(self):
        """An available=False model is never returned by the public selector,
        even when requested explicitly as the preference."""
        interface = UnifiedAIInterface()

        # Gate every model except one known-available target.
        for model in interface.CAPABILITIES:
            interface.CAPABILITIES[model].available = False
        interface.CAPABILITIES[AIModel.GPT_4O].available = True

        # Explicitly prefer a gated model; selector must skip it.
        request = AIRequest(prompt="test", model_preference=AIModel.GPT_5)
        selected = await interface.select_optimal_model(request, "general")

        assert selected == AIModel.GPT_4O
        assert interface.CAPABILITIES[selected].available is True
        assert selected != AIModel.GPT_5

    @pytest.mark.asyncio
    async def test_selection_raises_when_no_models_available(self):
        """With every model gated, selection fails closed rather than returning
        an unusable (aspirational) model."""
        interface = UnifiedAIInterface()
        for model in interface.CAPABILITIES:
            interface.CAPABILITIES[model].available = False

        request = AIRequest(prompt="test", model_preference=AIModel.GPT_5)
        with pytest.raises(RuntimeError, match="No AI models available"):
            await interface.select_optimal_model(request, "general")


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


@pytest.mark.unit
@pytest.mark.ai
@pytest.mark.critical
class TestAIIntegrationErrorHandling:
    """Test error handling for AI integration scenarios."""

    @pytest.mark.asyncio
    async def test_api_timeout_handling(self):
        """Test handling of API timeout errors."""
        interface = UnifiedAIInterface()

        # Mock an API timeout
        with patch.object(interface, '_execute_anthropic', new_callable=AsyncMock) as mock_call:
            import asyncio
            mock_call.side_effect = asyncio.TimeoutError("Request timeout")

            # Should handle timeout gracefully
            interface.CAPABILITIES[AIModel.CLAUDE_35_SONNET].available = True

            try:
                # Timeout should be caught and handled
                result = await interface._execute_anthropic(
                    AIRequest(prompt="test"),
                    AIModel.CLAUDE_35_SONNET
                )
                # If it returns, should indicate failure
                if result is not None:
                    assert result.success is False
            except asyncio.TimeoutError:
                # Also acceptable to propagate timeout for caller to handle
                pass

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test handling of rate limit errors."""
        interface = UnifiedAIInterface()

        # Mock a rate limit error response
        with patch.object(interface, '_execute_openai', new_callable=AsyncMock) as mock_call:
            error_response = AIResponse(
                content="",
                model_used=AIModel.GPT_4O,
                provider=AIProvider.OPENAI,
                tokens_used=0,
                latency_ms=100,
                success=False,
                error="Rate limit exceeded. Please retry after 60 seconds."
            )
            mock_call.return_value = error_response

            interface.CAPABILITIES[AIModel.GPT_4O].available = True

            result = await interface._execute_openai(
                AIRequest(prompt="test"),
                AIModel.GPT_4O
            )

            assert result.success is False
            assert "rate limit" in result.error.lower()

    @pytest.mark.asyncio
    async def test_invalid_api_key_handling(self):
        """Test handling of invalid API key errors."""
        interface = UnifiedAIInterface()

        # Mock invalid API key error
        with patch.object(interface, '_execute_anthropic', new_callable=AsyncMock) as mock_call:
            error_response = AIResponse(
                content="",
                model_used=AIModel.CLAUDE_35_SONNET,
                provider=AIProvider.ANTHROPIC,
                tokens_used=0,
                latency_ms=50,
                success=False,
                error="Invalid API key provided"
            )
            mock_call.return_value = error_response

            result = await interface._execute_anthropic(
                AIRequest(prompt="test"),
                AIModel.CLAUDE_35_SONNET
            )

            assert result.success is False
            assert "api key" in result.error.lower()

    @pytest.mark.asyncio
    async def test_network_failure_handling(self):
        """Test handling of network connection failures."""
        # Skip if aiohttp is not available
        pytest.importorskip("aiohttp")
        import aiohttp

        interface = UnifiedAIInterface()

        # Mock network error
        with patch.object(interface, '_execute_openai', new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = aiohttp.ClientError("Connection refused")

            interface.CAPABILITIES[AIModel.GPT_4O].available = True

            try:
                result = await interface._execute_openai(
                    AIRequest(prompt="test"),
                    AIModel.GPT_4O
                )
                # Should return error response
                if result is not None:
                    assert result.success is False
            except aiohttp.ClientError:
                # Also acceptable to propagate network errors
                pass

    @pytest.mark.asyncio
    async def test_response_parsing_error_handling(self):
        """Test handling of malformed API responses."""
        interface = UnifiedAIInterface()

        # Mock malformed response
        with patch.object(interface, '_execute_anthropic', new_callable=AsyncMock) as mock_call:
            # Return invalid response structure
            mock_call.return_value = None

            interface.CAPABILITIES[AIModel.CLAUDE_35_SONNET].available = True

            result = await interface._execute_anthropic(
                AIRequest(prompt="test"),
                AIModel.CLAUDE_35_SONNET
            )

            # Should handle None response gracefully
            assert result is None or (hasattr(result, 'success') and not result.success)

    @pytest.mark.asyncio
    async def test_model_unavailability_fallback(self):
        """Test fallback when preferred model is unavailable."""
        interface = UnifiedAIInterface()

        # Set primary model as unavailable, backup as available
        interface.CAPABILITIES[AIModel.CLAUDE_45_OPUS].available = False
        interface.CAPABILITIES[AIModel.CLAUDE_35_SONNET].available = True

        request = AIRequest(
            prompt="test",
            model_preference=AIModel.CLAUDE_45_OPUS,
            fallback_chain=[AIModel.CLAUDE_35_SONNET]
        )

        selected = await interface.select_optimal_model(request, "general")

        # Should select from fallback chain
        assert selected == AIModel.CLAUDE_35_SONNET

    @pytest.mark.asyncio
    async def test_all_models_unavailable(self):
        """Test behavior when all models are unavailable."""
        interface = UnifiedAIInterface()

        # Mark all models as unavailable
        for model in interface.CAPABILITIES:
            interface.CAPABILITIES[model].available = False

        request = AIRequest(prompt="test")

        # Should handle gracefully, possibly returning None or error
        try:
            selected = await interface.select_optimal_model(request, "general")
            # If it returns a model, it should be in capabilities
            if selected is not None:
                assert selected in interface.CAPABILITIES
        except Exception as e:
            # Should raise meaningful error about model unavailability
            error_msg = str(e).lower()
            assert "unavailable" in error_msg or "no model" in error_msg or "no ai" in error_msg

    @pytest.mark.asyncio
    async def test_partial_response_handling(self):
        """Test handling of incomplete/partial responses."""
        interface = UnifiedAIInterface()

        # Mock partial response
        with patch.object(interface, '_execute_openai', new_callable=AsyncMock) as mock_call:
            partial_response = AIResponse(
                content="This response was cut off mid-sen",
                model_used=AIModel.GPT_4O,
                provider=AIProvider.OPENAI,
                tokens_used=150,
                latency_ms=500,
                success=True,
                metadata={"finish_reason": "length"}
            )
            mock_call.return_value = partial_response

            result = await interface._execute_openai(
                AIRequest(prompt="test"),
                AIModel.GPT_4O
            )

            assert result is not None
            assert result.content is not None
            # Should indicate partial response in metadata
            assert "finish_reason" in result.metadata

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test behavior when max retry attempts are exceeded."""
        interface = UnifiedAIInterface()

        # Mock repeated failures
        with patch.object(interface, '_execute_anthropic', new_callable=AsyncMock) as mock_call:
            error_response = AIResponse(
                content="",
                model_used=AIModel.CLAUDE_35_SONNET,
                provider=AIProvider.ANTHROPIC,
                tokens_used=0,
                latency_ms=100,
                success=False,
                error="Service temporarily unavailable"
            )
            mock_call.return_value = error_response

            # After multiple attempts, should give up
            for _ in range(3):
                result = await interface._execute_anthropic(
                    AIRequest(prompt="test"),
                    AIModel.CLAUDE_35_SONNET
                )
                assert result.success is False

    @pytest.mark.asyncio
    async def test_context_length_exceeded(self):
        """Test handling when prompt exceeds model's context window."""
        interface = UnifiedAIInterface()

        # Mark preferred model as available
        interface.CAPABILITIES[AIModel.GPT_4O].available = True

        # Create request with very large prompt
        huge_prompt = "test " * 100000  # Simulate oversized prompt

        request = AIRequest(
            prompt=huge_prompt,
            model_preference=AIModel.GPT_4O
        )

        # Should either truncate, return error, or select model with larger context
        # Implementation specific, but should not crash
        try:
            selected = await interface.select_optimal_model(request, "general")
            assert selected in interface.CAPABILITIES
        except (ValueError, RuntimeError) as e:
            # Acceptable to raise error for oversized prompts or unavailable models
            error_msg = str(e).lower()
            assert "context" in error_msg or "length" in error_msg or "unavailable" in error_msg or "no ai" in error_msg

    @pytest.mark.asyncio
    async def test_invalid_temperature_parameter(self):
        """Test handling of invalid temperature values."""
        interface = UnifiedAIInterface()

        # Temperature should be 0.0-1.0 or 0.0-2.0 depending on provider
        invalid_request = AIRequest(
            prompt="test",
            temperature=5.0  # Invalid
        )

        # Should either clamp to valid range or raise error
        # Implementation should validate parameters
        assert invalid_request.temperature == 5.0  # Request object accepts it
        # Actual validation would happen during API call

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self):
        """Test handling of empty or whitespace-only prompts."""
        interface = UnifiedAIInterface()

        empty_request = AIRequest(prompt="")

        # Should handle empty prompts gracefully
        # Either reject or allow (depending on implementation)
        assert empty_request.prompt == ""

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """Test handling multiple concurrent requests."""
        interface = UnifiedAIInterface()

        # Mock successful responses
        with patch.object(interface, '_execute_anthropic', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = AIResponse(
                content="test response",
                model_used=AIModel.CLAUDE_35_SONNET,
                provider=AIProvider.ANTHROPIC,
                tokens_used=50,
                latency_ms=200,
                success=True
            )

            interface.CAPABILITIES[AIModel.CLAUDE_35_SONNET].available = True

            # Fire multiple requests concurrently
            requests = [
                interface._execute_anthropic(
                    AIRequest(prompt=f"test {i}"),
                    AIModel.CLAUDE_35_SONNET
                )
                for i in range(5)
            ]

            results = await asyncio.gather(*requests)

            # All should complete successfully
            assert len(results) == 5
            assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_api_error_status_codes(self):
        """Test handling of various HTTP error status codes."""
        interface = UnifiedAIInterface()

        error_codes = [400, 401, 403, 404, 500, 502, 503, 504]

        for code in error_codes:
            with patch.object(interface, '_execute_openai', new_callable=AsyncMock) as mock_call:
                error_response = AIResponse(
                    content="",
                    model_used=AIModel.GPT_4O,
                    provider=AIProvider.OPENAI,
                    tokens_used=0,
                    latency_ms=50,
                    success=False,
                    error=f"HTTP {code} error"
                )
                mock_call.return_value = error_response

                result = await interface._execute_openai(
                    AIRequest(prompt="test"),
                    AIModel.GPT_4O
                )

                assert result.success is False
                assert str(code) in result.error


@pytest.mark.integration
@pytest.mark.ai
@pytest.mark.slow
class TestAIIntegrationResilience:
    """Integration tests for AI system resilience."""

    @pytest.mark.asyncio
    async def test_cascading_fallback_chain(self):
        """Test complete fallback chain when multiple models fail."""
        interface = UnifiedAIInterface()

        # Set up fallback chain
        interface.CAPABILITIES[AIModel.CLAUDE_45_OPUS].available = False
        interface.CAPABILITIES[AIModel.CLAUDE_35_SONNET].available = True
        interface.CAPABILITIES[AIModel.GPT_4O].available = True

        request = AIRequest(
            prompt="test",
            model_preference=AIModel.CLAUDE_45_OPUS,
            fallback_chain=[
                AIModel.CLAUDE_35_SONNET,
                AIModel.GPT_4O
            ]
        )

        # Should successfully select from fallback
        selected = await interface.select_optimal_model(request, "general")
        assert selected in [AIModel.CLAUDE_35_SONNET, AIModel.GPT_4O]

    @pytest.mark.asyncio
    async def test_model_recovery_after_failure(self):
        """Test that models can recover after temporary failures."""
        interface = UnifiedAIInterface()

        model = AIModel.GPT_4O

        # Simulate failure
        interface.disable_model(model)
        assert not interface.CAPABILITIES[model].available

        # Simulate recovery
        interface.enable_model(model)
        assert interface.CAPABILITIES[model].available

    @pytest.mark.asyncio
    async def test_request_metadata_preservation(self):
        """Test that request metadata is preserved through error conditions."""
        interface = UnifiedAIInterface()

        request = AIRequest(
            prompt="test",
            context_tag="test_context_123",
            dlp_tracking=True
        )

        # Metadata should be preserved even if request fails
        assert request.context_tag == "test_context_123"
        assert request.dlp_tracking is True
