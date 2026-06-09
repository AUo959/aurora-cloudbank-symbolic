"""Unit tests for LLM SDK hardening (issue #796).

Verifies that the UnifiedAIInterface is configured with a concurrency semaphore
to cap simultaneous in-flight requests.
"""

import asyncio

import pytest


@pytest.mark.unit
def test_unified_ai_has_semaphore():
    """UnifiedAIInterface instance must expose a _semaphore attribute."""
    from modules.ai_core.unified_ai_interface import unified_ai

    assert hasattr(unified_ai, "_semaphore"), (
        "UnifiedAIInterface is missing _semaphore — concurrency cap not applied"
    )
    assert isinstance(unified_ai._semaphore, asyncio.Semaphore), (
        "_semaphore must be an asyncio.Semaphore instance"
    )


@pytest.mark.unit
def test_unified_ai_semaphore_default_limit():
    """The semaphore must have a positive internal limit (default 16)."""
    from modules.ai_core.unified_ai_interface import unified_ai

    # asyncio.Semaphore stores the current available count in ._value
    assert unified_ai._semaphore._value > 0, (
        "_semaphore._value must be > 0; check AI_CONCURRENCY_LIMIT env var"
    )
