"""
Token Budget Enforcement for Aurora AI Core

Enforces per-request, per-user (hourly/daily), and global (hourly) token
spend caps across all AI provider calls made via UnifiedAIInterface.

Configuration (environment variables):
    AURORA_MAX_TOKENS_PER_REQUEST          Single-call ceiling (default: unlimited)
    AURORA_MAX_TOKENS_PER_USER_PER_HOUR   Per-user rolling 1-hour window
    AURORA_MAX_TOKENS_PER_USER_PER_DAY    Per-user rolling 24-hour window
    AURORA_MAX_TOKENS_GLOBAL_PER_HOUR     Global kill-switch (all users combined)

On overrun a ``TokenBudgetExceededError`` is raised with a ``scope`` attribute
(``request``, ``user_hour``, ``user_day``, ``global_hour``) and an Insight
Ledger row is emitted (best-effort, never blocks the caller).

Anchor: T1-AIB-001
"""

from __future__ import annotations

import collections
import logging
import os
import threading
from typing import Deque, Dict, Optional, Tuple

from src.core.time_utils import utc_now

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public exception
# ---------------------------------------------------------------------------

_SCOPE_DESCRIPTIONS = {
    "request": "per-request token ceiling",
    "user_hour": "per-user hourly token quota",
    "user_day": "per-user daily token quota",
    "global_hour": "global hourly token quota",
}


class TokenBudgetExceededError(Exception):
    """Raised when a token budget cap is exceeded.

    Attributes:
        scope: One of ``request``, ``user_hour``, ``user_day``, ``global_hour``.
        requested: Tokens requested / consumed.
        limit: Configured limit that was breached.
        user_id: The user whose budget was exceeded (may be ``anonymous``).
        context_tag: DLP context tag for the originating request.
    """

    def __init__(
        self,
        scope: str,
        requested: int,
        limit: int,
        user_id: str = "anonymous",
        context_tag: str = "",
    ) -> None:
        self.scope = scope
        self.requested = requested
        self.limit = limit
        self.user_id = user_id
        self.context_tag = context_tag
        desc = _SCOPE_DESCRIPTIONS.get(scope, scope)
        super().__init__(
            f"Token budget exceeded ({desc}): {requested:,} tokens requested / used; "
            f"limit is {limit:,}. user_id={user_id!r}"
        )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SECS_PER_HOUR = 3600
_SECS_PER_DAY = 86400

# Each bucket entry: (unix_timestamp_float, tokens_int)
_BucketEntry = Tuple[float, int]


def _window_total(bucket: Deque[_BucketEntry], window_secs: int, now_ts: float) -> int:
    """Sum tokens in *bucket* within the rolling ``window_secs`` window."""
    cutoff = now_ts - window_secs
    return sum(tokens for ts, tokens in bucket if ts >= cutoff)


def _prune_bucket(bucket: Deque[_BucketEntry], window_secs: int, now_ts: float) -> None:
    """Remove entries older than ``window_secs`` from the left of *bucket*."""
    cutoff = now_ts - window_secs
    while bucket and bucket[0][0] < cutoff:
        bucket.popleft()


# ---------------------------------------------------------------------------
# TokenBudget
# ---------------------------------------------------------------------------

class TokenBudget:
    """Thread-safe token budget tracker with rolling-window enforcement.

    A single instance is created at module level (``token_budget``) and shared
    by ``UnifiedAIInterface``.  Tests can create isolated instances by passing
    explicit ``limits``.

    Args:
        limits: Optional dict to override env-var limits.  Keys:
            ``max_per_request``, ``max_per_user_hour``, ``max_per_user_day``,
            ``max_global_hour``.  ``None`` means unlimited.
    """

    def __init__(self, limits: Optional[Dict[str, Optional[int]]] = None) -> None:
        self._lock = threading.Lock()

        # --- load caps (env vars win, explicit limits override everything) ---
        def _env_int(var: str) -> Optional[int]:
            raw = os.environ.get(var, "").strip()
            return int(raw) if raw.isdigit() and int(raw) > 0 else None

        env_limits: Dict[str, Optional[int]] = {
            "max_per_request": _env_int("AURORA_MAX_TOKENS_PER_REQUEST"),
            "max_per_user_hour": _env_int("AURORA_MAX_TOKENS_PER_USER_PER_HOUR"),
            "max_per_user_day": _env_int("AURORA_MAX_TOKENS_PER_USER_PER_DAY"),
            "max_global_hour": _env_int("AURORA_MAX_TOKENS_GLOBAL_PER_HOUR"),
        }
        if limits:
            env_limits.update(limits)

        self.max_per_request: Optional[int] = env_limits["max_per_request"]
        self.max_per_user_hour: Optional[int] = env_limits["max_per_user_hour"]
        self.max_per_user_day: Optional[int] = env_limits["max_per_user_day"]
        self.max_global_hour: Optional[int] = env_limits["max_global_hour"]

        # per-user deques: user_id -> Deque[_BucketEntry]
        self._user_buckets: Dict[str, Deque[_BucketEntry]] = collections.defaultdict(
            collections.deque
        )
        # global deque
        self._global_bucket: Deque[_BucketEntry] = collections.deque()

        logger.info(
            "TokenBudget initialized — per_request=%s, per_user_hour=%s, "
            "per_user_day=%s, global_hour=%s",
            self.max_per_request,
            self.max_per_user_hour,
            self.max_per_user_day,
            self.max_global_hour,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_pre_call(
        self,
        *,
        user_id: str,
        max_tokens_requested: int,
        context_tag: str = "",
    ) -> None:
        """Check budgets *before* a provider call using requested max tokens.

        Raises ``TokenBudgetExceededError`` if adding ``max_tokens_requested``
        to the current rolling totals would violate any cap.  This is a
        conservative estimate; the actual post-call charge is recorded by
        :meth:`record_usage`.

        Args:
            user_id: Caller identifier (use ``"anonymous"`` when unknown).
            max_tokens_requested: ``AIRequest.max_tokens`` value.
            context_tag: DLP context tag from the request.
        """
        with self._lock:
            now_ts = utc_now().timestamp()
            self._do_check(
                user_id=user_id,
                tokens=max_tokens_requested,
                now_ts=now_ts,
                context_tag=context_tag,
            )

    def record_usage(
        self,
        *,
        user_id: str,
        tokens_used: int,
        context_tag: str = "",
    ) -> None:
        """Record *actual* token usage after a successful provider call.

        This also enforces rolling-window caps on the real usage (not just the
        pre-call estimate) and emits a ledger row if any cap is breached.

        Args:
            user_id: Caller identifier.
            tokens_used: Actual tokens consumed (input + output).
            context_tag: DLP context tag for tracing.
        """
        with self._lock:
            now_ts = utc_now().timestamp()
            entry: _BucketEntry = (now_ts, tokens_used)

            # Append first, then validate — we must reflect actual usage even
            # when raising.
            self._user_buckets[user_id].append(entry)
            self._global_bucket.append(entry)

            # Prune stale entries once per recording
            _prune_bucket(self._user_buckets[user_id], _SECS_PER_DAY, now_ts)
            _prune_bucket(self._global_bucket, _SECS_PER_HOUR, now_ts)

            # Check post-record caps (raises if exceeded)
            try:
                self._do_check(
                    user_id=user_id,
                    tokens=0,  # already recorded; just validate totals
                    now_ts=now_ts,
                    context_tag=context_tag,
                )
            except TokenBudgetExceededError:
                self._emit_ledger_overrun(
                    user_id=user_id,
                    tokens_used=tokens_used,
                    context_tag=context_tag,
                )
                raise

    def get_user_usage(self, user_id: str) -> Dict[str, int]:
        """Return current rolling-window totals for *user_id*.

        Returns:
            Dict with keys ``hour_tokens``, ``day_tokens``.
        """
        with self._lock:
            now_ts = utc_now().timestamp()
            bucket = self._user_buckets.get(user_id, collections.deque())
            return {
                "hour_tokens": _window_total(bucket, _SECS_PER_HOUR, now_ts),
                "day_tokens": _window_total(bucket, _SECS_PER_DAY, now_ts),
            }

    def get_global_usage(self) -> Dict[str, int]:
        """Return current global rolling-window totals.

        Returns:
            Dict with keys ``hour_tokens``, ``limits``.
        """
        with self._lock:
            now_ts = utc_now().timestamp()
            return {
                "hour_tokens": _window_total(self._global_bucket, _SECS_PER_HOUR, now_ts),
                "limits": {
                    "max_per_request": self.max_per_request,
                    "max_per_user_hour": self.max_per_user_hour,
                    "max_per_user_day": self.max_per_user_day,
                    "max_global_hour": self.max_global_hour,
                },
            }

    def reset(self) -> None:
        """Clear all usage data (useful in tests)."""
        with self._lock:
            self._user_buckets.clear()
            self._global_bucket.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _do_check(
        self,
        *,
        user_id: str,
        tokens: int,
        now_ts: float,
        context_tag: str,
    ) -> None:
        """Core validation logic (must be called with ``_lock`` held)."""

        # 1. Per-request ceiling
        if self.max_per_request is not None and tokens > self.max_per_request:
            raise TokenBudgetExceededError(
                scope="request",
                requested=tokens,
                limit=self.max_per_request,
                user_id=user_id,
                context_tag=context_tag,
            )

        # 2. Per-user hourly
        if self.max_per_user_hour is not None:
            user_bucket = self._user_buckets[user_id]
            current = _window_total(user_bucket, _SECS_PER_HOUR, now_ts)
            if current + tokens > self.max_per_user_hour:
                raise TokenBudgetExceededError(
                    scope="user_hour",
                    requested=current + tokens,
                    limit=self.max_per_user_hour,
                    user_id=user_id,
                    context_tag=context_tag,
                )

        # 3. Per-user daily
        if self.max_per_user_day is not None:
            user_bucket = self._user_buckets[user_id]
            current = _window_total(user_bucket, _SECS_PER_DAY, now_ts)
            if current + tokens > self.max_per_user_day:
                raise TokenBudgetExceededError(
                    scope="user_day",
                    requested=current + tokens,
                    limit=self.max_per_user_day,
                    user_id=user_id,
                    context_tag=context_tag,
                )

        # 4. Global hourly kill-switch
        if self.max_global_hour is not None:
            current = _window_total(self._global_bucket, _SECS_PER_HOUR, now_ts)
            if current + tokens > self.max_global_hour:
                raise TokenBudgetExceededError(
                    scope="global_hour",
                    requested=current + tokens,
                    limit=self.max_global_hour,
                    user_id=user_id,
                    context_tag=context_tag,
                )

    @staticmethod
    def _emit_ledger_overrun(*, user_id: str, tokens_used: int, context_tag: str) -> None:
        """Best-effort Insight Ledger row for a budget overrun.

        Errors are swallowed so the primary exception is not masked.
        """
        try:
            from modules.insight_ledger.ledger_core import InsightLedger
            from modules.insight_ledger.schemas import InsightRecord, InsightType

            ledger = InsightLedger(storage_path="token_budget_overruns")
            record = InsightRecord(
                insight_type=InsightType.ALERT,
                content=(
                    f"Token budget exceeded: user_id={user_id!r}, "
                    f"tokens_used={tokens_used:,}, context_tag={context_tag!r}"
                ),
                context={
                    "user_id": user_id,
                    "tokens_used": tokens_used,
                    "context_tag": context_tag,
                },
                source="aurora-token-budget",
                tags=["token-budget", "overrun"],
                severity="warning",
                related_anchor="T1-AIB-001",
            )
            ledger.record_insight(record)
            logger.warning(
                "TokenBudgetExceededError recorded in Insight Ledger — "
                "user_id=%r, tokens_used=%d, context_tag=%r",
                user_id,
                tokens_used,
                context_tag,
            )
        except Exception as ledger_err:  # pragma: no cover
            logger.error("Failed to emit Insight Ledger row for budget overrun: %s", ledger_err)


# ---------------------------------------------------------------------------
# Module-level singleton (shared across the process)
# ---------------------------------------------------------------------------

token_budget = TokenBudget()
