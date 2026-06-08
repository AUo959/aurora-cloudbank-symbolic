"""Tests for src/core/request_envelope.py — canonical DLP request envelope."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helper: import the module under test
# ---------------------------------------------------------------------------
from src.core.request_envelope import generate_context_tag, request_envelope

# Patch targets — the lazy imports live inside the envelope function body
_DLP_TARGET = "src.core.native_dlp_export.NativeDLPTracker"
_AUDIT_TARGET = "src.monitoring.audit_logger.AuditLogger"
_MEMORY_TARGET = "modules.memory_retrieval.core.MemoryRetrievalCore"


# ===========================================================================
# generate_context_tag
# ===========================================================================


@pytest.mark.unit
@pytest.mark.aurora
def test_generate_context_tag_format():
    """Tag follows the expected aurora:<agent>:<op>:<ts>:<rand> pattern."""
    tag = generate_context_tag("my_op", "agent1")
    parts = tag.split(":")
    assert parts[0] == "aurora"
    assert parts[1] == "agent1"
    assert parts[2] == "my_op"
    assert len(parts) == 5, f"Expected 5 colon-separated parts, got {len(parts)}"


@pytest.mark.unit
@pytest.mark.aurora
def test_generate_context_tag_unique():
    """Two consecutive calls must produce distinct tags."""
    tag1 = generate_context_tag("op")
    tag2 = generate_context_tag("op")
    assert tag1 != tag2


@pytest.mark.unit
@pytest.mark.aurora
def test_generate_context_tag_default_agent_id():
    """Default agent_id is 'api'."""
    tag = generate_context_tag("op")
    assert tag.startswith("aurora:api:op:")


# ===========================================================================
# request_envelope — basic context dict
# ===========================================================================


@pytest.mark.unit
@pytest.mark.aurora
def test_request_envelope_yields_dict_with_context_tag():
    """request_envelope yields a dict containing 'context_tag'."""
    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET):
        with request_envelope("test_op", agent_id="svc") as ctx:
            assert "context_tag" in ctx
            assert ctx["context_tag"].startswith("aurora:svc:test_op:")


@pytest.mark.unit
@pytest.mark.aurora
def test_request_envelope_completed_at_set_after_exit():
    """'completed_at' key is absent inside the body but set after exit."""
    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET):
        with request_envelope("test_op") as ctx:
            assert "completed_at" not in ctx
        assert "completed_at" in ctx


@pytest.mark.unit
@pytest.mark.aurora
def test_request_envelope_metadata_merged():
    """Extra metadata is merged into ctx before yield."""
    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET):
        with request_envelope("test_op", metadata={"user_id": "u42", "priority": 1}) as ctx:
            assert ctx["user_id"] == "u42"
            assert ctx["priority"] == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_request_envelope_caller_updates_visible():
    """Updates made to ctx inside the body are present in the final ctx."""
    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET):
        with request_envelope("test_op") as ctx:
            ctx["result_summary"] = "hello world"
        assert ctx["result_summary"] == "hello world"


# ===========================================================================
# request_envelope — failure resilience
# ===========================================================================


@pytest.mark.unit
@pytest.mark.aurora
def test_dlp_failure_does_not_raise():
    """DLP tracker construction failure must not propagate to caller."""
    with patch(_DLP_TARGET, side_effect=RuntimeError("dlp boom")):
        # Should not raise
        with request_envelope("test_op") as ctx:
            assert "context_tag" in ctx


@pytest.mark.unit
@pytest.mark.aurora
def test_audit_failure_does_not_raise():
    """Audit logger failure must not propagate to caller."""
    with patch(_DLP_TARGET), \
         patch(_AUDIT_TARGET, side_effect=ValueError("no signing key")):
        with request_envelope("test_op") as ctx:
            pass  # must not raise
        assert "completed_at" in ctx


@pytest.mark.unit
@pytest.mark.aurora
def test_exception_in_body_propagates():
    """An exception raised inside the with-block must propagate normally."""
    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET):
        with pytest.raises(ValueError, match="oops"):
            with request_envelope("test_op"):
                raise ValueError("oops")


# ===========================================================================
# request_envelope — memory storage
# ===========================================================================


@pytest.mark.unit
@pytest.mark.aurora
def test_memory_storage_called_when_enabled():
    """MemoryRetrievalCore.add_memory is called when store_to_memory=True."""
    mock_core = MagicMock()
    mock_cls = MagicMock()
    mock_cls.get_instance.return_value = mock_core

    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET, mock_cls):
        with request_envelope("test_op", agent_id="a1", store_to_memory=True) as ctx:
            ctx["result_summary"] = "summary text"

    mock_core.add_memory.assert_called_once()
    args = mock_core.add_memory.call_args[0]
    assert args[0] == "a1"                # context_id defaults to agent_id
    assert "summary text" in args[1]      # content


@pytest.mark.unit
@pytest.mark.aurora
def test_memory_storage_not_called_when_disabled():
    """MemoryRetrievalCore.add_memory is NOT called when store_to_memory=False."""
    mock_core = MagicMock()
    mock_cls = MagicMock()
    mock_cls.get_instance.return_value = mock_core

    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET, mock_cls):
        with request_envelope("test_op", store_to_memory=False):
            pass

    mock_core.add_memory.assert_not_called()


@pytest.mark.unit
@pytest.mark.aurora
def test_memory_storage_uses_custom_context_id():
    """memory_context_id overrides the default agent_id bucket."""
    mock_core = MagicMock()
    mock_cls = MagicMock()
    mock_cls.get_instance.return_value = mock_core

    with patch(_DLP_TARGET), patch(_AUDIT_TARGET), patch(_MEMORY_TARGET, mock_cls):
        with request_envelope(
            "test_op",
            agent_id="agent-x",
            store_to_memory=True,
            memory_context_id="custom-bucket",
        ):
            pass

    args = mock_core.add_memory.call_args[0]
    assert args[0] == "custom-bucket"
