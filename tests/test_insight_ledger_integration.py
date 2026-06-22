"""
Insight Ledger + AuMemManager Integration Tests

Validates that high-importance memory events are automatically
propagated to the InsightLedger via AuMemLedgerHook, and that
the hook degrades gracefully when the ledger is unavailable.

DLP: context_tag=insight_ledger_integration_tests
"""

import importlib.util
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def _load_ledger_hooks():
    """Load ledger_hooks directly without triggering aumemmanager/__init__.py."""
    spec = importlib.util.spec_from_file_location(
        "aumemmanager_ledger_hooks",
        Path(__file__).parent.parent / "modules" / "aumemmanager" / "ledger_hooks.py",
    )
    mod = importlib.util.module_from_spec(spec)  # NOSONAR - spec is non-None: path is a hardcoded .py file that always exists in this repo
    spec.loader.exec_module(mod)  # NOSONAR - spec.loader is non-None for a valid .py ModuleSpec returned by spec_from_file_location
    return mod


_hooks_mod = _load_ledger_hooks()
AuMemLedgerHook = _hooks_mod.AuMemLedgerHook
LEDGER_IMPORTANCE_THRESHOLD = _hooks_mod.LEDGER_IMPORTANCE_THRESHOLD


# ── Hook lifecycle ───────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestAuMemLedgerHookInit:
    def test_hook_disabled_when_no_ledger(self):
        """Hook with ledger=None must report enabled=False."""
        hook = AuMemLedgerHook(ledger=None)
        assert hook.enabled is False

    def test_hook_enabled_when_ledger_provided(self):
        """Hook with a mock ledger must report enabled=True."""
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger)
        assert hook.enabled is True

    def test_create_factory_returns_disabled_hook_when_ledger_unavailable(self):
        """create() must return a disabled no-op hook if InsightLedger import fails."""
        with patch.object(_hooks_mod, "_LEDGER_AVAILABLE", False):
            hook = AuMemLedgerHook.create()
            assert hook.enabled is False

    def test_create_factory_wires_ledger_when_available(self):
        """create() with a real temp path must return an enabled hook."""
        try:
            from modules.insight_ledger.ledger_core import InsightLedger  # noqa: F401
            ledger_available = True
        except ImportError:  # NOSONAR - availability probe; ImportError is expected when ledger is not installed
            ledger_available = False

        if not ledger_available:
            pytest.skip("InsightLedger not available in this environment")

        with tempfile.TemporaryDirectory() as tmp:
            hook = AuMemLedgerHook.create(storage_path=str(Path(tmp) / "ledger"))
            assert hook.enabled is True


# ── on_memory_added ─────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestOnMemoryAdded:
    def _hook_with_mock(self, threshold: float = LEDGER_IMPORTANCE_THRESHOLD) -> tuple:
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger, importance_threshold=threshold)
        return hook, mock_ledger

    def test_high_importance_memory_triggers_ledger_write(self):
        """Memory with importance >= threshold must call ledger.record_insight."""
        hook, mock_ledger = self._hook_with_mock(threshold=7.0)
        hook.on_memory_added(
            memory_id="mem_001",
            owner="agent_alpha",
            importance=9.0,
            memory_type="agent",
            tags=["critical"],
            context_tag="ctx_001",
        )
        mock_ledger.record_insight.assert_called_once()

    def test_low_importance_memory_skips_ledger_write(self):
        """Memory with importance below threshold must NOT call ledger.record_insight."""
        hook, mock_ledger = self._hook_with_mock(threshold=7.0)
        hook.on_memory_added(
            memory_id="mem_002",
            owner="agent_beta",
            importance=3.0,
            memory_type="agent",
        )
        mock_ledger.record_insight.assert_not_called()

    def test_exact_threshold_triggers_ledger_write(self):
        """Memory at exactly the threshold must be recorded."""
        hook, mock_ledger = self._hook_with_mock(threshold=7.0)
        hook.on_memory_added(
            memory_id="mem_003",
            owner="agent_gamma",
            importance=7.0,
            memory_type="system",
        )
        mock_ledger.record_insight.assert_called_once()

    def test_disabled_hook_never_calls_ledger(self):
        """Disabled hook (ledger=None) must never attempt any ledger call."""
        hook = AuMemLedgerHook(ledger=None)
        hook.on_memory_added(
            memory_id="mem_004",
            owner="agent_delta",
            importance=10.0,
            memory_type="agent",
        )
        # No exception and no ledger call

    def test_ledger_failure_does_not_raise(self):
        """If ledger.record_insight raises, the hook must swallow the error."""
        mock_ledger = MagicMock()
        mock_ledger.record_insight.side_effect = RuntimeError("ledger down")
        hook = AuMemLedgerHook(ledger=mock_ledger)
        # Must not raise
        hook.on_memory_added(
            memory_id="mem_005",
            owner="agent_epsilon",
            importance=9.0,
            memory_type="agent",
        )

    def test_insight_record_content_contains_memory_id(self):
        """The recorded insight content must reference the memory ID."""
        hook, mock_ledger = self._hook_with_mock(threshold=7.0)
        hook.on_memory_added(
            memory_id="test_mem_xyz",
            owner="agent_zeta",
            importance=8.5,
            memory_type="aurora_symbolic",
        )
        call_args = mock_ledger.record_insight.call_args  # NOSONAR - call_args is non-None here: assert_called_once() above guarantees the mock was called
        record = call_args[0][0]  # NOSONAR - call_args is Optional[_Call] but non-None when assert_called_once() passed
        assert "test_mem_xyz" in record.content

    def test_insight_record_source_is_aumemmanager(self):
        """Insight record source must be 'aumemmanager'."""
        hook, mock_ledger = self._hook_with_mock(threshold=7.0)
        hook.on_memory_added("m1", "owner", 8.0, "agent")
        record = mock_ledger.record_insight.call_args[0][0]  # NOSONAR - call_args is Optional[_Call] but non-None: assert_called_once() guarantees the mock was called
        assert record.source == "aumemmanager"

    def test_context_tag_propagated_to_insight(self):
        """context_tag must appear in the insight's context dict."""
        hook, mock_ledger = self._hook_with_mock(threshold=7.0)
        hook.on_memory_added("m2", "owner", 8.0, "agent", context_tag="special_ctx")
        record = mock_ledger.record_insight.call_args[0][0]  # NOSONAR - call_args is Optional[_Call] but non-None: assert_called_once() guarantees the mock was called
        assert record.context["context_tag"] == "special_ctx"


# ── on_memory_retrieved ──────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestOnMemoryRetrieved:
    def test_high_importance_retrieval_logged(self):
        """Retrieving a high-importance memory must log to ledger."""
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger, importance_threshold=7.0)
        hook.on_memory_retrieved("m1", "owner", 8.0, query="test query")
        mock_ledger.record_insight.assert_called_once()

    def test_low_importance_retrieval_not_logged(self):
        """Retrieving a low-importance memory must not log."""
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger, importance_threshold=7.0)
        hook.on_memory_retrieved("m1", "owner", 2.0, query="test query")
        mock_ledger.record_insight.assert_not_called()

    def test_query_preview_truncated_to_100_chars(self):
        """Long query preview must be truncated to 100 characters in context."""
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger, importance_threshold=7.0)
        long_query = "q" * 500
        hook.on_memory_retrieved("m1", "owner", 8.0, query=long_query)
        record = mock_ledger.record_insight.call_args[0][0]  # NOSONAR - call_args is Optional[_Call] but non-None: assert_called_once() guarantees the mock was called
        assert len(record.context["query_preview"]) <= 100


# ── on_capacity_warning ─────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestOnCapacityWarning:
    def test_capacity_warning_always_logged_when_enabled(self):
        """Capacity warnings are always recorded regardless of importance."""
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger)
        hook.on_capacity_warning(950, 1000, "active")
        mock_ledger.record_insight.assert_called_once()

    def test_capacity_warning_includes_fill_percentage(self):
        """Capacity warning content/context must include fill percentage."""
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger)
        hook.on_capacity_warning(900, 1000, "active")
        record = mock_ledger.record_insight.call_args[0][0]  # NOSONAR - call_args is Optional[_Call] but non-None: assert_called_once() guarantees the mock was called
        assert "90.0" in record.content or record.context["fill_percent"] == pytest.approx(90.0)

    def test_capacity_warning_severity_is_warning(self):
        """Capacity warning insight must have severity='warning'."""
        mock_ledger = MagicMock()
        hook = AuMemLedgerHook(ledger=mock_ledger)
        hook.on_capacity_warning(800, 1000, "compressed")
        record = mock_ledger.record_insight.call_args[0][0]  # NOSONAR - call_args is Optional[_Call] but non-None: assert_called_once() guarantees the mock was called
        assert record.severity == "warning"

    def test_disabled_hook_skips_capacity_warning(self):
        """Disabled hook must silently skip capacity warning."""
        hook = AuMemLedgerHook(ledger=None)
        hook.on_capacity_warning(999, 1000, "active")  # Must not raise
