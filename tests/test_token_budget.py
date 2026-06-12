"""
Tests for Token Budget enforcement (Issue #798).

Covers:
- Per-request ceiling: exceeding raises TokenBudgetExceededError(scope="request")
- Per-user hourly cap: rolling-window total exceeds limit
- Per-user daily cap: rolling-window total exceeds limit
- Global hourly kill-switch: blocks all users when exhausted
- Below-cap requests always succeed
- Insight Ledger row emitted on overrun
- UnifiedAIInterface integration: pre-call check blocks oversized requests
- Usage stats queries (get_user_usage / get_global_usage)
"""
from unittest.mock import patch

import pytest

from modules.ai_core.token_budget import (
    TokenBudget,
    TokenBudgetExceededError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_budget(**limits) -> TokenBudget:
    """Create a fresh isolated TokenBudget with the given limits."""
    return TokenBudget(limits=limits)


# ---------------------------------------------------------------------------
# TokenBudgetExceededError attributes
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTokenBudgetExceededError:
    def test_attributes_populated(self):
        err = TokenBudgetExceededError(
            scope="request",
            requested=9000,
            limit=4096,
            user_id="alice",
            context_tag="ctx_001",
        )
        assert err.scope == "request"
        assert err.requested == 9000
        assert err.limit == 4096
        assert err.user_id == "alice"
        assert err.context_tag == "ctx_001"
        assert "9,000" in str(err)
        assert "4,096" in str(err)

    def test_is_exception_subclass(self):
        assert issubclass(TokenBudgetExceededError, Exception)


# ---------------------------------------------------------------------------
# Per-request ceiling
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPerRequestCeiling:
    def test_below_limit_does_not_raise(self):
        budget = _make_budget(max_per_request=1000)
        # Should not raise
        budget.check_pre_call(user_id="alice", max_tokens_requested=500)

    def test_at_limit_does_not_raise(self):
        budget = _make_budget(max_per_request=1000)
        budget.check_pre_call(user_id="alice", max_tokens_requested=1000)

    def test_above_limit_raises(self):
        budget = _make_budget(max_per_request=1000)
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.check_pre_call(user_id="alice", max_tokens_requested=1001)
        assert exc_info.value.scope == "request"
        assert exc_info.value.limit == 1000
        assert exc_info.value.requested == 1001

    def test_no_limit_never_raises(self):
        budget = _make_budget(max_per_request=None)
        # Large value with no cap — must not raise
        budget.check_pre_call(user_id="alice", max_tokens_requested=10_000_000)


# ---------------------------------------------------------------------------
# Per-user hourly cap
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPerUserHourlyCap:
    def test_accumulates_and_raises_on_overflow(self):
        budget = _make_budget(max_per_user_hour=500)
        budget.record_usage(user_id="alice", tokens_used=400)
        # 400 already used; 200 more would exceed 500
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.record_usage(user_id="alice", tokens_used=200)
        assert exc_info.value.scope == "user_hour"

    def test_different_users_have_independent_budgets(self):
        budget = _make_budget(max_per_user_hour=500)
        budget.record_usage(user_id="alice", tokens_used=490)
        # bob has zero usage — should not raise
        budget.record_usage(user_id="bob", tokens_used=490)

    def test_below_hourly_cap_succeeds(self):
        budget = _make_budget(max_per_user_hour=1000)
        budget.record_usage(user_id="alice", tokens_used=300)
        budget.record_usage(user_id="alice", tokens_used=300)
        # 600 < 1000 — no raise

    def test_check_pre_call_uses_projected_total(self):
        budget = _make_budget(max_per_user_hour=500)
        budget.record_usage(user_id="alice", tokens_used=400)
        # 400 + 200 > 500 — pre-call should raise
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.check_pre_call(user_id="alice", max_tokens_requested=200)
        assert exc_info.value.scope == "user_hour"


# ---------------------------------------------------------------------------
# Per-user daily cap
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestPerUserDailyCap:
    def test_daily_cap_enforced(self):
        budget = _make_budget(max_per_user_day=1000)
        budget.record_usage(user_id="alice", tokens_used=800)
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.record_usage(user_id="alice", tokens_used=300)
        assert exc_info.value.scope == "user_day"

    def test_hourly_and_daily_caps_both_enforced(self):
        # Hourly is tighter — hits hourly first
        budget = _make_budget(max_per_user_hour=100, max_per_user_day=10_000)
        budget.record_usage(user_id="alice", tokens_used=90)
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.record_usage(user_id="alice", tokens_used=20)
        assert exc_info.value.scope == "user_hour"


# ---------------------------------------------------------------------------
# Global hourly kill-switch
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGlobalHourlyCap:
    def test_global_cap_blocks_all_users(self):
        budget = _make_budget(max_global_hour=1000)
        budget.record_usage(user_id="alice", tokens_used=800)
        # Now the global window has 800 tokens; bob adds 300 => exceeds 1000
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.record_usage(user_id="bob", tokens_used=300)
        assert exc_info.value.scope == "global_hour"

    def test_global_cap_not_exceeded_stays_below(self):
        budget = _make_budget(max_global_hour=2000)
        budget.record_usage(user_id="alice", tokens_used=500)
        budget.record_usage(user_id="bob", tokens_used=500)
        # 1000 < 2000 — no raise

    def test_pre_call_enforces_global_cap(self):
        budget = _make_budget(max_global_hour=500)
        budget.record_usage(user_id="alice", tokens_used=450)
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.check_pre_call(user_id="bob", max_tokens_requested=100)
        assert exc_info.value.scope == "global_hour"


# ---------------------------------------------------------------------------
# Usage stats
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestUsageStats:
    def test_get_user_usage_reflects_records(self):
        budget = _make_budget()
        budget.record_usage(user_id="alice", tokens_used=300)
        budget.record_usage(user_id="alice", tokens_used=200)
        stats = budget.get_user_usage("alice")
        assert stats["hour_tokens"] == 500
        assert stats["day_tokens"] == 500

    def test_get_global_usage_reflects_all_users(self):
        budget = _make_budget(max_global_hour=10_000)
        budget.record_usage(user_id="alice", tokens_used=300)
        budget.record_usage(user_id="bob", tokens_used=400)
        global_stats = budget.get_global_usage()
        assert global_stats["hour_tokens"] == 700

    def test_get_global_usage_includes_limits(self):
        budget = _make_budget(
            max_per_request=512,
            max_per_user_hour=5000,
            max_per_user_day=50_000,
            max_global_hour=100_000,
        )
        limits = budget.get_global_usage()["limits"]
        assert limits["max_per_request"] == 512
        assert limits["max_per_user_hour"] == 5000
        assert limits["max_per_user_day"] == 50_000
        assert limits["max_global_hour"] == 100_000

    def test_unknown_user_returns_zero(self):
        budget = _make_budget()
        stats = budget.get_user_usage("nobody")
        assert stats["hour_tokens"] == 0
        assert stats["day_tokens"] == 0

    def test_reset_clears_all_data(self):
        budget = _make_budget(max_per_user_hour=100)
        budget.record_usage(user_id="alice", tokens_used=90)
        budget.reset()
        # After reset, usage should be zero
        stats = budget.get_user_usage("alice")
        assert stats["hour_tokens"] == 0


# ---------------------------------------------------------------------------
# Insight Ledger emission on overrun
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestInsightLedgerEmission:
    def test_ledger_row_emitted_on_record_overrun(self):
        """TokenBudget must call _emit_ledger_overrun when an overrun is
        detected inside record_usage."""
        budget = _make_budget(max_per_user_hour=100)
        budget.record_usage(user_id="alice", tokens_used=90)

        emitted: list = []

        def mock_emit(*, user_id, tokens_used, context_tag):
            emitted.append(
                {"user_id": user_id, "tokens_used": tokens_used, "context_tag": context_tag}
            )

        with patch.object(TokenBudget, "_emit_ledger_overrun", staticmethod(mock_emit)):
            with pytest.raises(TokenBudgetExceededError):
                budget.record_usage(
                    user_id="alice", tokens_used=20, context_tag="ctx_test"
                )

        assert len(emitted) == 1
        assert emitted[0]["user_id"] == "alice"
        assert emitted[0]["context_tag"] == "ctx_test"


# ---------------------------------------------------------------------------
# UnifiedAIInterface integration
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.ai
class TestUnifiedAIInterfaceBudgetIntegration:
    """Verify that UnifiedAIInterface respects the token budget."""

    @pytest.fixture()
    def interface_with_tight_budget(self):
        """Create an UnifiedAIInterface with a tiny per-request cap."""
        from modules.ai_core.unified_ai_interface import UnifiedAIInterface
        from modules.ai_core.token_budget import TokenBudget

        iface = UnifiedAIInterface()
        iface._budget = TokenBudget(limits={"max_per_request": 10})
        return iface

    @pytest.fixture()
    def interface_with_user_cap(self):
        """Create an UnifiedAIInterface with a tight per-user hourly cap."""
        from modules.ai_core.unified_ai_interface import UnifiedAIInterface
        from modules.ai_core.token_budget import TokenBudget

        iface = UnifiedAIInterface()
        iface._budget = TokenBudget(limits={"max_per_user_hour": 100})
        return iface

    @pytest.mark.asyncio
    async def test_pre_call_blocks_oversized_request(self, interface_with_tight_budget):
        """execute_request must raise before hitting the provider when max_tokens > cap."""
        from modules.ai_core.unified_ai_interface import AIRequest, AIModel

        # Make GPT-4O available so model selection works
        interface_with_tight_budget.CAPABILITIES[AIModel.GPT_4O].available = True

        request = AIRequest(
            prompt="hello",
            max_tokens=50,  # > cap of 10
            user_id="alice",
            model_preference=AIModel.GPT_4O,
        )

        with pytest.raises(TokenBudgetExceededError) as exc_info:
            await interface_with_tight_budget.execute_request(request)

        assert exc_info.value.scope == "request"

    @pytest.mark.asyncio
    async def test_below_cap_request_proceeds_to_provider(self, interface_with_tight_budget):
        """A request within budget must reach the provider (even if provider fails)."""
        from modules.ai_core.unified_ai_interface import AIRequest, AIModel

        interface_with_tight_budget.CAPABILITIES[AIModel.GPT_4O].available = True

        request = AIRequest(
            prompt="hello",
            max_tokens=5,  # <= cap of 10
            user_id="alice",
            model_preference=AIModel.GPT_4O,
        )

        # Provider will raise (no real client) — budget check must NOT raise first
        response = await interface_with_tight_budget.execute_request(request)
        # Response will have success=False because provider isn't configured,
        # but TokenBudgetExceededError must NOT have been raised.
        assert response is not None
        assert not isinstance(response, TokenBudgetExceededError)

    @pytest.mark.asyncio
    async def test_post_record_usage_budget_enforced(self, interface_with_user_cap):
        """After recording actual usage that exceeds the per-user hourly cap, raise."""
        from modules.ai_core.token_budget import TokenBudgetExceededError

        budget = interface_with_user_cap._budget
        # Pre-load 90 tokens
        budget.record_usage(user_id="charlie", tokens_used=90)

        # Simulate that 20 more tokens were used — direct record_usage call
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.record_usage(user_id="charlie", tokens_used=20, context_tag="test_ctx")

        assert exc_info.value.scope == "user_hour"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestEdgeCases:
    def test_zero_tokens_never_triggers_cap_with_none_limit(self):
        budget_none = _make_budget(max_per_request=None)
        budget_none.check_pre_call(user_id="x", max_tokens_requested=999_999)

    def test_context_tag_included_in_exception(self):
        budget = _make_budget(max_per_request=100)
        with pytest.raises(TokenBudgetExceededError) as exc_info:
            budget.check_pre_call(
                user_id="alice", max_tokens_requested=200, context_tag="my_tag"
            )
        assert exc_info.value.context_tag == "my_tag"
