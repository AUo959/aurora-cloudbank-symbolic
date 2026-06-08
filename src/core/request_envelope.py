"""Canonical request envelope: DLP context_tag, audit log, optional memory storage."""
from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def generate_context_tag(operation: str, agent_id: str = "api") -> str:
    """Generate a unique DLP context tag for an operation."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    return f"aurora:{agent_id}:{operation}:{ts}:{uuid.uuid4().hex[:8]}"


@contextmanager
def request_envelope(
    operation: str,
    *,
    agent_id: str = "api",
    metadata: Optional[Dict[str, Any]] = None,
    store_to_memory: bool = False,
    memory_context_id: Optional[str] = None,
):
    """Wrap an operation with DLP tracking, audit logging, and optional memory storage.

    Yields a dict ``ctx`` that callers can populate with result metadata.
    All failures in DLP/audit/memory are swallowed (logged at DEBUG) so that
    observability plumbing never breaks the business logic it wraps.

    Args:
        operation: Short name for the operation (e.g. ``"chat_response"``).
        agent_id: Identifies the calling agent/service; baked into the context tag.
        metadata: Optional extra key-value pairs merged into ctx at entry.
        store_to_memory: When True, store ctx[``"result_summary"``] to the memory
            retrieval module after the body exits.
        memory_context_id: Context ID passed to ``MemoryRetrievalCore.add_memory``.
            Defaults to *agent_id* when not provided.

    Yields:
        Dict[str, Any]: mutable context dict containing at minimum
        ``context_tag``, ``operation``, ``agent_id``, and ``started_at``.
    """
    context_tag = generate_context_tag(operation, agent_id)
    ctx: Dict[str, Any] = {
        "context_tag": context_tag,
        "operation": operation,
        "agent_id": agent_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    if metadata:
        ctx.update(metadata)

    # DLP tracking — create a provenance tag before the body runs
    try:
        from src.core.native_dlp_export import NativeDLPTracker

        tracker = NativeDLPTracker()
        tracker.create_tag(operation, {"context_tag": context_tag, "agent_id": agent_id})
    except Exception as exc:
        logger.debug("DLP tracking unavailable: %s", exc)

    try:
        yield ctx
    finally:
        ctx["completed_at"] = datetime.now(timezone.utc).isoformat()

        # Audit log — use AuditLogger._create_entry with SYSTEM_CHANGE event type.
        # AuditLogger requires a signing key; if the env-var is absent this will raise
        # ValueError during construction — that is swallowed here intentionally.
        try:
            from src.monitoring.audit_logger import AuditLogger, AuditEventType

            auditor = AuditLogger()
            auditor._create_entry(
                event_type=AuditEventType.SYSTEM_CHANGE,
                agent_id=agent_id,
                severity="low",
                description=f"request_envelope: {operation}",
                data=ctx,
                context_tag=context_tag,
            )
        except Exception as exc:
            logger.debug("Audit logging failed: %s", exc)

        # Optional memory storage
        if store_to_memory:
            try:
                from modules.memory_retrieval.core import MemoryRetrievalCore

                core = MemoryRetrievalCore.get_instance()
                cid = memory_context_id or agent_id
                content = ctx.get("result_summary", operation)
                core.add_memory(
                    cid,
                    str(content),
                    {
                        "context_tag": context_tag,
                        "operation": operation,
                        "agent_id": agent_id,
                        "importance": 0.5,
                    },
                )
            except Exception as exc:
                logger.debug("Memory storage failed: %s", exc)
