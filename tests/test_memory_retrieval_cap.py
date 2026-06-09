"""Tests for memory token cap and dedup in retrieve_memories."""
import pytest
from modules.memory_retrieval.core import _dedup_memories, _estimate_tokens, _apply_cap


@pytest.mark.unit
def test_estimate_tokens_heuristic():
    # 40 chars → ~10 tokens
    text = "a" * 40
    assert _estimate_tokens(text) >= 1


@pytest.mark.unit
def test_estimate_tokens_nonempty():
    assert _estimate_tokens("Hello world") > 0


@pytest.mark.unit
def test_dedup_removes_identical_content():
    memories = [
        {"id": "1", "score": 0.9, "content": "same content"},
        {"id": "2", "score": 0.5, "content": "same content"},
    ]
    result = _dedup_memories(memories)
    assert len(result) == 1
    # Keeps first occurrence (highest score comes first from sort)
    assert result[0]["id"] == "1"


@pytest.mark.unit
def test_dedup_keeps_different_content():
    memories = [
        {"id": "1", "score": 0.9, "content": "content A"},
        {"id": "2", "score": 0.5, "content": "content B"},
    ]
    result = _dedup_memories(memories)
    assert len(result) == 2


@pytest.mark.unit
def test_apply_cap_limits_by_tokens():
    # 10 memories each of 1000 chars (~250 tokens each), cap at 300 tokens
    memories = [
        {"id": str(i), "score": float(i), "content": "x" * 1000}
        for i in range(10)
    ]
    result = _apply_cap(memories, max_tokens=300)
    assert len(result) <= 2  # at most 2 fit under 300 tokens


@pytest.mark.unit
def test_apply_cap_none_returns_all():
    memories = [{"id": str(i), "content": "x" * 100} for i in range(5)]
    result = _apply_cap(memories, max_tokens=None)
    assert len(result) == 5


@pytest.mark.unit
def test_apply_cap_empty_input():
    assert _apply_cap([], max_tokens=1000) == []
