"""Tests for memory-augmented RAG chat (issue #775)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Minimal stubs so we can import rag_chat without real backend deps
# ---------------------------------------------------------------------------

@dataclass
class _FakeAIResponse:
    content: str
    model_used: object = None
    provider: object = None
    tokens_used: int = 0
    latency_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_tag: str = "test"
    timestamp: str = "2026-01-01T00:00:00Z"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_memories(n: int) -> List[Dict]:
    return [{"id": f"mem-{i}", "content": f"memory snippet {i}", "score": 1.0 - i * 0.1} for i in range(n)]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.ai
async def test_retrieve_memories_called_with_correct_args():
    """rag_chat should call retrieve_memories with context_id, message and top_k."""
    fake_memories = _make_memories(3)
    fake_core = MagicMock()
    fake_core.retrieve_memories.return_value = fake_memories
    fake_core.add_memory.return_value = "mem-new"

    fake_ai_response = _FakeAIResponse(content="Hello from LLM")
    fake_interface = MagicMock()
    fake_interface.execute_request = AsyncMock(return_value=fake_ai_response)

    with (
        patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", return_value=fake_core),
        patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
    ):
        from modules.ai_core.rag_chat import rag_chat

        await rag_chat("test question", context_id="ctx-1", user_id="user-A", top_k=7)

    fake_core.retrieve_memories.assert_called_once_with("ctx-1", "test question", top_k=7, user_id="user-A")


@pytest.mark.unit
@pytest.mark.ai
async def test_llm_receives_augmented_prompt_with_memory_context():
    """When memories exist, the prompt sent to the LLM should contain memory context."""
    fake_memories = _make_memories(2)
    fake_core = MagicMock()
    fake_core.retrieve_memories.return_value = fake_memories
    fake_core.add_memory.return_value = "mem-new"

    captured_requests = []

    fake_ai_response = _FakeAIResponse(content="LLM answer")

    async def _capture_execute(req):
        captured_requests.append(req)
        return fake_ai_response

    fake_interface = MagicMock()
    fake_interface.execute_request = _capture_execute

    with (
        patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", return_value=fake_core),
        patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
    ):
        from modules.ai_core import rag_chat as _module
        import importlib
        importlib.reload(_module)
        from modules.ai_core.rag_chat import rag_chat

        await rag_chat("user message", context_id="ctx-2")

    assert captured_requests, "execute_request was never called"
    prompt_sent = captured_requests[0].prompt
    assert "[Relevant context from memory]" in prompt_sent
    assert "memory snippet 0" in prompt_sent
    assert "[Current message]" in prompt_sent
    assert "user message" in prompt_sent


@pytest.mark.unit
@pytest.mark.ai
async def test_memory_failure_does_not_prevent_llm_call():
    """If memory retrieval raises, the LLM call should still proceed."""
    fake_ai_response = _FakeAIResponse(content="LLM answer despite memory failure")
    fake_interface = MagicMock()
    fake_interface.execute_request = AsyncMock(return_value=fake_ai_response)

    fake_core_for_add = MagicMock()
    fake_core_for_add.add_memory.return_value = "mem-new"

    def _side_effect_get_instance():
        # First call (retrieve) raises; second call (add) succeeds
        m = MagicMock()
        m.retrieve_memories.side_effect = RuntimeError("store unavailable")
        m.add_memory.return_value = "mem-new"
        return m

    with (
        patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", side_effect=_side_effect_get_instance),
        patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
    ):
        from modules.ai_core.rag_chat import rag_chat

        result = await rag_chat("question", context_id="ctx-3")

    assert result["response"] == "LLM answer despite memory failure"
    fake_interface.execute_request.assert_called_once()


@pytest.mark.unit
@pytest.mark.ai
async def test_llm_response_stored_back_to_memory():
    """The Q&A exchange should be written back to memory after a successful LLM call."""
    fake_memories = _make_memories(1)
    fake_core = MagicMock()
    fake_core.retrieve_memories.return_value = fake_memories
    fake_core.add_memory.return_value = "mem-stored"

    fake_ai_response = _FakeAIResponse(content="stored answer")
    fake_interface = MagicMock()
    fake_interface.execute_request = AsyncMock(return_value=fake_ai_response)

    with (
        patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", return_value=fake_core),
        patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
    ):
        from modules.ai_core.rag_chat import rag_chat

        await rag_chat("my question", context_id="ctx-4", user_id="user-B")

    fake_core.add_memory.assert_called_once()
    call_args = fake_core.add_memory.call_args
    context_arg, content_arg, metadata_arg = call_args[0]
    assert context_arg == "ctx-4"
    assert "my question" in content_arg
    assert "stored answer" in content_arg
    assert metadata_arg.get("user_id") == "user-B"


@pytest.mark.unit
@pytest.mark.ai
async def test_memory_store_failure_does_not_raise():
    """A failure to store the Q&A to memory should be swallowed, not re-raised."""
    fake_core = MagicMock()
    fake_core.retrieve_memories.return_value = []
    fake_core.add_memory.side_effect = RuntimeError("store write failed")

    fake_ai_response = _FakeAIResponse(content="some answer")
    fake_interface = MagicMock()
    fake_interface.execute_request = AsyncMock(return_value=fake_ai_response)

    with (
        patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", return_value=fake_core),
        patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
    ):
        from modules.ai_core.rag_chat import rag_chat

        # Should NOT raise
        result = await rag_chat("question", context_id="ctx-5")

    assert result["response"] == "some answer"


@pytest.mark.unit
@pytest.mark.ai
async def test_empty_memories_message_sent_unchanged():
    """When no memories are found, the message is sent verbatim to the LLM."""
    fake_core = MagicMock()
    fake_core.retrieve_memories.return_value = []
    fake_core.add_memory.return_value = "mem-new"

    captured_requests = []

    async def _capture(req):
        captured_requests.append(req)
        return _FakeAIResponse(content="direct answer")

    fake_interface = MagicMock()
    fake_interface.execute_request = _capture

    with (
        patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", return_value=fake_core),
        patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
    ):
        from modules.ai_core.rag_chat import rag_chat

        await rag_chat("plain question", context_id="ctx-6")

    assert captured_requests[0].prompt == "plain question"


@pytest.mark.unit
@pytest.mark.ai
async def test_return_dict_has_required_keys():
    """Return value must contain 'response', 'memories_used', and 'context_id' keys."""
    fake_memories = _make_memories(3)
    fake_core = MagicMock()
    fake_core.retrieve_memories.return_value = fake_memories
    fake_core.add_memory.return_value = "mem-new"

    fake_ai_response = _FakeAIResponse(content="answer text")
    fake_interface = MagicMock()
    fake_interface.execute_request = AsyncMock(return_value=fake_ai_response)

    with (
        patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", return_value=fake_core),
        patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
    ):
        from modules.ai_core.rag_chat import rag_chat

        result = await rag_chat("hello", context_id="ctx-7")

    assert "response" in result
    assert "memories_used" in result
    assert "context_id" in result
    assert result["response"] == "answer text"
    assert result["memories_used"] == 3
    assert result["context_id"] == "ctx-7"


@pytest.mark.unit
@pytest.mark.ai
async def test_memories_used_count_matches_retrieved():
    """memories_used in the result must equal the number of memories returned."""
    for n in (0, 1, 5):
        fake_memories = _make_memories(n)
        fake_core = MagicMock()
        fake_core.retrieve_memories.return_value = fake_memories
        fake_core.add_memory.return_value = "mem-new"

        fake_interface = MagicMock()
        fake_interface.execute_request = AsyncMock(return_value=_FakeAIResponse(content="ok"))

        with (
            patch("modules.memory_retrieval.core.MemoryRetrievalCore.get_instance", return_value=fake_core),
            patch("modules.ai_core.unified_ai_interface.UnifiedAIInterface", return_value=fake_interface),
        ):
            from modules.ai_core.rag_chat import rag_chat

            result = await rag_chat("q", context_id=f"ctx-n{n}")

        assert result["memories_used"] == n, f"expected {n}, got {result['memories_used']}"
