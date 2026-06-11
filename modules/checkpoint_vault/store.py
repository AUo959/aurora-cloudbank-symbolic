"""Checkpoint Vault — in-memory store with versioning.

Provides create / get / list / rollback operations on CheckpointRecord objects.
All state is held in memory; persistence can be layered in later.

DLP: checkpoint_vault_store_v1
"""

import logging
import threading
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from .models import (
    CheckpointRecord,
    CheckpointStatus,
    CreateCheckpointRequest,
)

logger = logging.getLogger(__name__)

# Guard against concurrent creates from async tasks
_LOCK = threading.Lock()


class CheckpointVault:
    """Thread-safe in-memory checkpoint store."""

    def __init__(self) -> None:
        # Primary store: checkpoint_id -> CheckpointRecord
        self._store: Dict[str, CheckpointRecord] = {}
        # Version counters: agent_id -> latest version number
        self._versions: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create(self, request: CreateCheckpointRequest) -> CheckpointRecord:
        """Create and store a new checkpoint.  Returns the persisted record."""
        with _LOCK:
            version = self._versions.get(request.agent_id, 0) + 1
            self._versions[request.agent_id] = version
            checkpoint_id = f"CHKP-{uuid4().hex[:12].upper()}"

            record = CheckpointRecord(
                checkpoint_id=checkpoint_id,
                agent_id=request.agent_id,
                version=version,
                trigger=request.trigger,
                status=CheckpointStatus.ACTIVE,
                timestamp=datetime.now(timezone.utc).isoformat(),
                state_snapshot=request.state_snapshot,
                ethics_profile=request.ethics_profile,
                parent_checkpoint_id=request.parent_checkpoint_id,
                tags=request.tags,
                context_tag=request.context_tag,
                meta=request.meta,
            )
            self._store[checkpoint_id] = record

            # Mark previous ACTIVE checkpoints for this agent as SUPERSEDED
            for rec in self._store.values():
                if (
                    rec.agent_id == request.agent_id
                    and rec.checkpoint_id != checkpoint_id
                    and rec.status == CheckpointStatus.ACTIVE
                ):
                    self._store[rec.checkpoint_id] = rec.model_copy(
                        update={"status": CheckpointStatus.SUPERSEDED}
                    )

            logger.info(
                "[CheckpointVault] Created %s for agent=%s version=%d trigger=%s",
                checkpoint_id, request.agent_id, version, request.trigger,
            )
            return record

    def rollback(self, checkpoint_id: str, reason: str, performed_by: str) -> CheckpointRecord:
        """Mark a checkpoint as rolled-back and return the stored record."""
        with _LOCK:
            record = self._store.get(checkpoint_id)
            if record is None:
                raise KeyError(f"Checkpoint '{checkpoint_id}' not found")
            if record.status == CheckpointStatus.ROLLED_BACK:
                raise ValueError(f"Checkpoint '{checkpoint_id}' is already rolled back")

            updated = record.model_copy(
                update={
                    "status": CheckpointStatus.ROLLED_BACK,
                    "meta": {
                        **record.meta,
                        "rollback_reason": reason,
                        "rolled_back_by": performed_by,
                        "rolled_back_at": datetime.now(timezone.utc).isoformat(),
                    },
                }
            )
            self._store[checkpoint_id] = updated
            logger.warning(
                "[CheckpointVault] Rolled back %s for agent=%s reason='%s' by='%s'",
                checkpoint_id, record.agent_id, reason, performed_by,
            )
            return updated

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, checkpoint_id: str) -> Optional[CheckpointRecord]:
        """Return a checkpoint by ID, or None if not found."""
        return self._store.get(checkpoint_id)

    @staticmethod
    def _matches_filters(
        r: CheckpointRecord,
        agent_id: Optional[str],
        status: Optional[str],
        trigger: Optional[str],
    ) -> bool:
        if agent_id and r.agent_id != agent_id:
            return False
        if status and r.status != status:
            return False
        if trigger and r.trigger != trigger:
            return False
        return True

    def list_all(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        trigger: Optional[str] = None,
        limit: int = 50,
    ) -> List[CheckpointRecord]:
        """Return filtered checkpoints ordered by timestamp descending."""
        results = [
            r for r in self._store.values()
            if self._matches_filters(r, agent_id, status, trigger)
        ]
        results.sort(key=lambda r: r.timestamp, reverse=True)
        return results[:limit]

    def history(self, agent_id: str, limit: int = 20) -> List[CheckpointRecord]:
        """Return version history for a specific agent, newest first."""
        results = [r for r in self._store.values() if r.agent_id == agent_id]
        results.sort(key=lambda r: r.version, reverse=True)
        return results[:limit]

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, int]:
        """Return aggregate counts."""
        active = sum(1 for r in self._store.values() if r.status == CheckpointStatus.ACTIVE)
        return {
            "total": len(self._store),
            "active": active,
            "agents_tracked": len(self._versions),
        }
