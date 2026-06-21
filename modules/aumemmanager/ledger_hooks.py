"""
AuMemManager Ledger Hooks

Optional integration between AuMemManager and InsightLedger.
When the insight_ledger module is available, high-importance memory
operations are automatically recorded as AUDIT entries, creating
an immutable audit trail of significant memory events.

Gracefully degrades: if insight_ledger is unavailable, all operations
succeed silently with no ledger writes.

DLP: context_tag=aumemmanager_ledger_hook
"""

import logging
from types import SimpleNamespace
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from modules.insight_ledger.ledger_core import InsightLedger
    from modules.insight_ledger.schemas import InsightRecord, InsightType
    _LEDGER_AVAILABLE = True
except Exception:
    # Catches ImportError AND environment failures (e.g. broken C-extension builds
    # that raise pyo3 panics — now handled by secure_storage.py's BaseException guard)
    InsightLedger = None  # type: ignore
    InsightRecord = None  # type: ignore
    InsightType = None  # type: ignore
    _LEDGER_AVAILABLE = False


# Importance threshold above which a memory event is ledger-worthy
LEDGER_IMPORTANCE_THRESHOLD = 7.0


def _make_record(**kwargs: Any) -> Any:
    """Build an insight record using InsightRecord when available, else SimpleNamespace.

    SimpleNamespace provides attribute access (.content, .source, etc.) identical
    to InsightRecord objects, making tests with mock ledgers work even when the
    real InsightRecord type cannot be imported (e.g. broken cryptography package).
    """
    if InsightRecord is not None and InsightType is not None:
        insight_type = kwargs.pop("insight_type_name", "audit")
        try:
            kwargs["insight_type"] = InsightType(insight_type)
        except Exception:
            kwargs["insight_type"] = insight_type
        return InsightRecord(**kwargs)
    # Fallback: attribute-accessible namespace
    return SimpleNamespace(**kwargs)


class AuMemLedgerHook:
    """
    Thin bridge between AuMemManager and InsightLedger.

    Attach one instance to a HierarchicalMemoryManager; call
    on_memory_added() / on_memory_retrieved() from the manager.
    All methods are no-ops if insight_ledger is unavailable.

    The hook is enabled when a ledger is provided (either real or mock),
    regardless of whether _LEDGER_AVAILABLE is True. This allows unit
    tests to inject a mock ledger and verify hook behavior without
    needing the full cryptography stack.
    """

    def __init__(
        self,
        ledger: Optional[Any] = None,
        importance_threshold: float = LEDGER_IMPORTANCE_THRESHOLD,
    ) -> None:
        self._ledger = ledger
        self._threshold = importance_threshold
        # Enabled whenever a ledger is explicitly provided (real or mock)
        self._enabled = ledger is not None

    @classmethod
    def create(
        cls,
        storage_path: Optional[str] = None,
        importance_threshold: float = LEDGER_IMPORTANCE_THRESHOLD,
    ) -> "AuMemLedgerHook":
        """
        Factory that creates a real InsightLedger instance and returns a wired hook.

        Returns a disabled no-op hook if insight_ledger is unavailable.
        """
        if not _LEDGER_AVAILABLE or InsightLedger is None:
            logger.debug("InsightLedger not available — AuMemLedgerHook disabled")
            return cls(ledger=None, importance_threshold=importance_threshold)

        try:
            path = storage_path or ".aurora/ledger"
            ledger = InsightLedger(storage_path=path)
            logger.info("AuMemLedgerHook: ledger wired at %s", path)
            return cls(ledger=ledger, importance_threshold=importance_threshold)
        except Exception as exc:
            logger.warning("AuMemLedgerHook: failed to init ledger (%s) — disabled", exc)
            return cls(ledger=None, importance_threshold=importance_threshold)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def on_memory_added(
        self,
        memory_id: str,
        owner: str,
        importance: float,
        memory_type: str,
        tags: Optional[list] = None,
        context_tag: str = "",
    ) -> None:
        """Record a high-importance memory creation in the ledger."""
        if not self._enabled or importance < self._threshold:
            return

        try:
            record = _make_record(
                insight_type_name="audit",
                content=(
                    f"High-importance memory created: id={memory_id} "
                    f"owner={owner} importance={importance:.2f} type={memory_type}"
                ),
                source="aumemmanager",
                context={
                    "memory_id": memory_id,
                    "owner": owner,
                    "importance": importance,
                    "memory_type": memory_type,
                    "tags": tags or [],
                    "context_tag": context_tag,
                },
                tags=["aumemmanager", "memory_created", memory_type],
                severity="info",
                related_anchor=context_tag or None,
            )
            self._ledger.record_insight(record)
        except Exception as exc:
            logger.warning("AuMemLedgerHook.on_memory_added failed: %s", exc)

    def on_memory_retrieved(
        self,
        memory_id: str,
        owner: str,
        importance: float,
        query: str,
        context_tag: str = "",
    ) -> None:
        """Record retrieval of a high-importance memory in the ledger."""
        if not self._enabled or importance < self._threshold:
            return

        try:
            record = _make_record(
                insight_type_name="audit",
                content=(
                    f"High-importance memory retrieved: id={memory_id} "
                    f"owner={owner} importance={importance:.2f}"
                ),
                source="aumemmanager",
                context={
                    "memory_id": memory_id,
                    "owner": owner,
                    "importance": importance,
                    "query_preview": query[:100],
                    "context_tag": context_tag,
                },
                tags=["aumemmanager", "memory_retrieved"],
                severity="info",
                related_anchor=context_tag or None,
            )
            self._ledger.record_insight(record)
        except Exception as exc:
            logger.warning("AuMemLedgerHook.on_memory_retrieved failed: %s", exc)

    def on_capacity_warning(
        self,
        current_count: int,
        capacity_limit: int,
        tier: str,
    ) -> None:
        """Record a capacity warning alert in the ledger."""
        if not self._enabled:
            return

        try:
            fill_pct = (current_count / capacity_limit * 100) if capacity_limit else 0
            record = _make_record(
                insight_type_name="alert",
                content=(
                    f"AuMemManager capacity warning: {tier} tier at "
                    f"{fill_pct:.1f}% ({current_count}/{capacity_limit})"
                ),
                source="aumemmanager",
                context={
                    "tier": tier,
                    "current_count": current_count,
                    "capacity_limit": capacity_limit,
                    "fill_percent": fill_pct,
                },
                tags=["aumemmanager", "capacity_warning", tier],
                severity="warning",
            )
            self._ledger.record_insight(record)
        except Exception as exc:
            logger.warning("AuMemLedgerHook.on_capacity_warning failed: %s", exc)
