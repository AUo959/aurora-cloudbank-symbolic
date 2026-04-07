"""Checkpoint Vault — FastAPI router.

Exposes endpoints for creating, retrieving and rolling back ethical checkpoints.

DLP: checkpoint_vault_api_v1
Anchors: T1:CHECKPOINT_API, SRB:GUMAS_VAULT
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone

from .models import (
    CheckpointRecord,
    CheckpointSummary,
    CreateCheckpointRequest,
    RollbackRequest,
    VaultHealthResponse,
)
from .store import CheckpointVault

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checkpoint", tags=["ethical-checkpoint-vault"])

# Module-level vault singleton
_vault = CheckpointVault()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/health", response_model=VaultHealthResponse)
async def vault_health() -> VaultHealthResponse:
    """GET /checkpoint/health — vault liveness and capacity statistics."""
    s = _vault.stats()
    return VaultHealthResponse(
        status="healthy",
        total_checkpoints=s["total"],
        active_checkpoints=s["active"],
        agents_tracked=s["agents_tracked"],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/create", response_model=CheckpointRecord, status_code=201)
async def create_checkpoint(request: CreateCheckpointRequest) -> CheckpointRecord:
    """POST /checkpoint/create — snapshot an agent's ethical state.

    DLP: checkpoint_vault_create
    """
    try:
        return _vault.create(request)
    except Exception as exc:
        logger.exception("Failed to create checkpoint")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=List[CheckpointSummary])
async def list_checkpoints(
    agent_id: Optional[str] = Query(default=None, description="Filter by agent_id"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    trigger: Optional[str] = Query(default=None, description="Filter by trigger"),
    limit: int = Query(default=20, ge=1, le=200),
) -> List[CheckpointSummary]:
    """GET /checkpoint — list checkpoints with optional filters."""
    records = _vault.list_all(agent_id=agent_id, status=status, trigger=trigger, limit=limit)
    return [
        CheckpointSummary(
            checkpoint_id=r.checkpoint_id,
            agent_id=r.agent_id,
            version=r.version,
            trigger=r.trigger,
            status=r.status,
            timestamp=r.timestamp,
            tag_count=len(r.tags),
        )
        for r in records
    ]


@router.get("/{checkpoint_id}", response_model=CheckpointRecord)
async def get_checkpoint(checkpoint_id: str) -> CheckpointRecord:
    """GET /checkpoint/{id} — retrieve a full checkpoint record.

    DLP: checkpoint_vault_get
    """
    if not checkpoint_id or len(checkpoint_id) > 64:
        raise HTTPException(status_code=400, detail="Invalid checkpoint_id")
    record = _vault.get(checkpoint_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Checkpoint '{checkpoint_id}' not found")
    return record


@router.post("/{checkpoint_id}/rollback", response_model=CheckpointRecord)
async def rollback_checkpoint(checkpoint_id: str, request: RollbackRequest) -> CheckpointRecord:
    """POST /checkpoint/{id}/rollback — mark a checkpoint as rolled back.

    DLP: checkpoint_vault_rollback
    """
    if not checkpoint_id or len(checkpoint_id) > 64:
        raise HTTPException(status_code=400, detail="Invalid checkpoint_id")
    try:
        return _vault.rollback(
            checkpoint_id=checkpoint_id,
            reason=request.reason,
            performed_by=request.performed_by,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Rollback failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/agent/{agent_id}/history", response_model=List[CheckpointRecord])
async def agent_history(
    agent_id: str,
    limit: int = Query(default=20, ge=1, le=100),
) -> List[CheckpointRecord]:
    """GET /checkpoint/agent/{agent_id}/history — version history for an agent.

    DLP: checkpoint_vault_history
    """
    return _vault.history(agent_id=agent_id, limit=limit)
