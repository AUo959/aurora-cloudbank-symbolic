"""Exercise real SDK serialization and response decoding without provider traffic."""
import json
from unittest.mock import AsyncMock, patch

import httpx
import openai
import pytest

from modules.ai_core.unified_ai_interface import AIModel, AIRequest, UnifiedAIInterface
from modules.ai_core.gpt5_integration_hub import GPT5IntegrationHub
from modules.ai_core.claude_integration_hub import ClaudeIntegrationHub


@pytest.mark.asyncio
@pytest.mark.parametrize('model', [AIModel.GPT_6_1_SOL, AIModel.GPT_6_ASTRA])
async def test_responses_wire_contract(model):
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(200, json={
            'id': 'resp_test', 'object': 'response', 'created_at': 0,
            'model': model.value, 'status': 'completed',
            'output': [
                {'id': 'msg_test', 'type': 'message', 'role': 'assistant',
                 'status': 'completed', 'content': [
                     {'type': 'output_text', 'text': 'Ready', 'annotations': []}]},
                {'id': 'fc_test', 'type': 'function_call', 'call_id': 'call_test',
                 'name': 'lookup', 'arguments': '{"name":"Aurora"}', 'status': 'completed'},
            ],
            'usage': {'input_tokens': 12, 'output_tokens': 8, 'total_tokens': 20},
        })

    interface = UnifiedAIInterface()
    interface._budget = None
    async with openai.AsyncOpenAI(
        api_key='test-not-a-credential', max_retries=0,
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handle)),
    ) as client:
        interface.openai_client = client
        result = await interface.execute_request(AIRequest(
            prompt='Hello', system_prompt='Be precise.', model_preference=model,
            functions=[{'name': 'lookup', 'parameters': {
                'type': 'object', 'properties': {'name': {'type': 'string'}}}}],
            reasoning_effort='high', max_tokens=2048,
        ))
    assert len(requests) == 1
    assert requests[0].url.path == '/v1/responses'
    body = json.loads(requests[0].content)
    assert body['model'] == model.value
    assert body['instructions'] == 'Be precise.'
    assert body['input'] == [{'role': 'user', 'content': 'Hello'}]
    assert body['reasoning'] == {'effort': 'high'}
    assert body['max_output_tokens'] == 2048
    assert body['store'] is False
    assert not {'messages', 'max_tokens', 'temperature', 'top_p'} & body.keys()
    assert body['tools'][0]['name'] == 'lookup'
    assert body['tools'][0]['strict'] is False
    assert 'function' not in body['tools'][0]
    assert result.success and result.content == 'Ready'
    assert result.model_used is model and result.tokens_used == 20
    assert result.metadata['input_tokens'] == 12
    assert result.function_calls == [{'id': 'call_test', 'type': 'function',
        'function': {'name': 'lookup', 'arguments': '{"name":"Aurora"}'}}]


@pytest.mark.asyncio
async def test_default_routing_retires_4o_and_honors_direct_current_preference():
    interface = UnifiedAIInterface()
    assert not interface.CAPABILITIES[AIModel.GPT_4O].available
    for task in ('general', 'code_generation'):
        assert await interface.select_optimal_model(AIRequest(prompt='test'), task) is AIModel.GPT_6_1_SOL
    for chain in interface.FALLBACK_CHAINS.values():
        assert AIModel.GPT_4O not in chain
    selected = await interface.select_optimal_model(AIRequest(prompt='test', model_preference=AIModel.GPT_6_ASTRA))
    assert selected is AIModel.GPT_6_ASTRA
    hub = GPT5IntegrationHub()
    hub._unified_ai = interface
    assert hub._build_agent_fallback_chain() == [AIModel.GPT_6_1_SOL]
    assert hub._build_codex_fallback_chain() == [AIModel.GPT_6_1_SOL]
    assert ClaudeIntegrationHub()._build_fallback_chain('general')[-1] is AIModel.GPT_6_1_SOL


def test_openai_client_uses_environment_when_no_explicit_config(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test-environment-value')
    with patch('openai.AsyncOpenAI') as factory:
        UnifiedAIInterface()
        assert factory.call_args.kwargs['api_key'] == 'test-environment-value'
        UnifiedAIInterface({'openai_api_key': 'test-explicit-value'})
        assert factory.call_args.kwargs['api_key'] == 'test-explicit-value'


@pytest.mark.asyncio
async def test_incomplete_response_is_not_reported_as_success():
    from types import SimpleNamespace
    interface = UnifiedAIInterface()
    interface.openai_client = AsyncMock()
    interface.openai_client.responses.create.return_value = SimpleNamespace(
        id='resp_incomplete', status='incomplete', output=[], output_text='', usage=None)
    result = await interface._execute_openai(AIRequest(prompt='test'), AIModel.GPT_6_1_SOL)
    assert not result.success
    assert 'incomplete' in result.error


@pytest.mark.asyncio
async def test_incomplete_output_still_counts_toward_token_budget():
    from unittest.mock import MagicMock
    from modules.ai_core.unified_ai_interface import AIProvider, AIResponse
    interface = UnifiedAIInterface()
    interface._budget = MagicMock()
    response = AIResponse(content='', model_used=AIModel.GPT_6_1_SOL,
                          provider=AIProvider.OPENAI, tokens_used=100, latency_ms=1,
                          success=False, error='incomplete')
    with patch.object(interface, '_execute_openai', AsyncMock(return_value=response)):
        result = await interface.execute_request(AIRequest(prompt='test'))
    assert not result.success
    interface._budget.record_usage.assert_called_once_with(
        user_id='anonymous', tokens_used=100, context_tag='aurora_ai_request')


@pytest.mark.asyncio
async def test_failed_responses_result_falls_back_after_accounting_for_usage():
    from types import SimpleNamespace
    from unittest.mock import MagicMock
    from modules.ai_core.unified_ai_interface import AIProvider, AIResponse
    interface = UnifiedAIInterface()
    interface._budget = MagicMock()
    interface.openai_client = AsyncMock()
    interface.openai_client.responses.create.return_value = SimpleNamespace(
        id='resp_failed', status='failed', output=[], output_text='',
        usage=SimpleNamespace(input_tokens=3, output_tokens=0, total_tokens=3))
    expected = AIResponse(content='Recovered', model_used=AIModel.CLAUDE_SONNET_5,
                          provider=AIProvider.ANTHROPIC, tokens_used=5, latency_ms=1)
    with (
        patch.object(interface, '_execute_anthropic', AsyncMock(return_value=expected)) as fallback,
        patch('modules.ai_core.unified_ai_interface.asyncio.sleep', AsyncMock()),
    ):
        result = await interface.execute_request(AIRequest(prompt='test'))
    assert result is expected
    fallback.assert_awaited_once()
    assert [call.kwargs['tokens_used'] for call in interface._budget.record_usage.call_args_list] == [3, 5]


@pytest.mark.asyncio
async def test_astra_requires_explicit_selection_when_other_models_are_disabled():
    interface = UnifiedAIInterface()
    for model, caps in interface.CAPABILITIES.items():
        caps.available = model is AIModel.GPT_6_ASTRA
    with pytest.raises(RuntimeError, match='No AI models available'):
        await interface.select_optimal_model(AIRequest(prompt='test'))
    assert await interface.select_optimal_model(AIRequest(
        prompt='test', model_preference=AIModel.GPT_6_ASTRA)) is AIModel.GPT_6_ASTRA
    assert await interface.select_optimal_model(AIRequest(
        prompt='test', fallback_chain=[AIModel.GPT_6_ASTRA])) is AIModel.GPT_6_ASTRA
