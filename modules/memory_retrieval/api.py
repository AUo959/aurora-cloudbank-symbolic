"""Memory Retrieval Module - API Interface.

Provides both a FastAPI router (``router``) for authenticated HTTP exposure and
plain Python helper functions for trusted in-process use.
"""

from __future__ import annotations

import copy
import hashlib
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from src.middleware.fastapi_security import limiter, verify_csrf_token
from src.security.oauth2 import User, get_current_active_user

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/memory-retrieval", tags=["MemoryRetrieval"])

MEMORY_WRITE_RATE_LIMIT = "60/minute"
MEMORY_READ_RATE_LIMIT = "120/minute"
_OWNER_METADATA_KEY = "_aurora_owner"
_CONTEXT_METADATA_KEY = "_aurora_context_id"


class AddMemoryRequest(BaseModel):
    context_id: str = Field(min_length=1, max_length=256)
    content: str = Field(min_length=1, max_length=100_000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AddMemoryResponse(BaseModel):
    memory_id: str
    status: str = "ok"


class RetrieveMemoriesRequest(BaseModel):
    context_id: str = Field(min_length=1, max_length=256)
    query: str = Field(min_length=1, max_length=10_000)
    top_k: int = Field(default=10, ge=1, le=100)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=1_000_000)


class RetrieveMemoriesResponse(BaseModel):
    memories: List[Dict[str, Any]]
    count: int


def require_memory_mutation_auth(
    csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token"),
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require JWT authentication plus a separate CSRF token for writes."""
    if not csrf_token:
        raise HTTPException(status_code=403, detail="Missing CSRF token")
    verify_csrf_token(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=csrf_token)
    )
    return current_user


def _scoped_context_id(username: str, context_id: str) -> str:
    """Build a deterministic tenant-private storage key."""
    user_digest = hashlib.sha256(username.encode("utf-8")).hexdigest()
    return f"tenant:{user_digest}:context:{context_id}"


def _owned_by(memory: Dict[str, Any], username: str) -> bool:
    metadata = memory.get("metadata")
    return isinstance(metadata, dict) and metadata.get(_OWNER_METADATA_KEY) == username


def _public_memory(memory: Dict[str, Any]) -> Dict[str, Any]:
    """Remove internal ownership fields and restore the caller-facing context ID."""
    public_memory = copy.deepcopy(memory)
    metadata = public_memory.get("metadata")
    if not isinstance(metadata, dict):
        return public_memory

    original_context_id = metadata.pop(_CONTEXT_METADATA_KEY, None)
    metadata.pop(_OWNER_METADATA_KEY, None)
    if original_context_id is not None:
        public_memory["context_id"] = original_context_id
    return public_memory


@router.post("/memories", response_model=AddMemoryResponse)
@limiter.limit(MEMORY_WRITE_RATE_LIMIT)
async def add_memory_endpoint(
    payload: AddMemoryRequest,
    request: Request,
    current_user: User = Depends(require_memory_mutation_auth),
):
    """Add a memory entry scoped to the authenticated user."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        metadata = dict(payload.metadata)
        metadata[_OWNER_METADATA_KEY] = current_user.username
        metadata[_CONTEXT_METADATA_KEY] = payload.context_id
        memory_id = core.add_memory(
            _scoped_context_id(current_user.username, payload.context_id),
            payload.content,
            metadata,
        )
        return AddMemoryResponse(memory_id=memory_id)
    except Exception as exc:
        logger.exception("Failed to add memory")
        raise HTTPException(status_code=500, detail="Failed to add memory") from exc


@router.post("/retrieve", response_model=RetrieveMemoriesResponse)
@limiter.limit(MEMORY_READ_RATE_LIMIT)
async def retrieve_memories_endpoint(
    payload: RetrieveMemoriesRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve memories from the authenticated user's scoped context."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        kwargs: Dict[str, Any] = {}
        if payload.max_tokens is not None:
            kwargs["max_tokens"] = payload.max_tokens
        memories = core.retrieve_memories(
            _scoped_context_id(current_user.username, payload.context_id),
            payload.query,
            top_k=payload.top_k,
            user_id=current_user.username,
            **kwargs,
        )
        public_memories = [_public_memory(memory) for memory in memories]
        return RetrieveMemoriesResponse(
            memories=public_memories,
            count=len(public_memories),
        )
    except Exception as exc:
        logger.exception("Failed to retrieve memories")
        raise HTTPException(status_code=500, detail="Failed to retrieve memories") from exc


@router.get("/memories/{memory_id}", response_model=Dict[str, Any])
@limiter.limit(MEMORY_READ_RATE_LIMIT)
async def get_memory_endpoint(
    memory_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """Fetch a memory only when it belongs to the authenticated user."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        memory = core.get_memory(memory_id)
        if memory is None or not _owned_by(memory, current_user.username):
            raise HTTPException(status_code=404, detail="Memory not found")
        return _public_memory(memory)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get memory %s", memory_id)
        raise HTTPException(status_code=500, detail="Failed to get memory") from exc


@router.delete("/memories/{memory_id}")
@limiter.limit(MEMORY_WRITE_RATE_LIMIT)
async def delete_memory_endpoint(
    memory_id: str,
    request: Request,
    current_user: User = Depends(require_memory_mutation_auth),
):
    """Delete a memory only when it belongs to the authenticated user."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        memory = core.get_memory(memory_id)
        if memory is None or not _owned_by(memory, current_user.username):
            raise HTTPException(status_code=404, detail="Memory not found")
        if not core.delete_memory(memory_id):
            raise HTTPException(status_code=404, detail="Memory not found")
        return {"status": "deleted", "memory_id": memory_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete memory %s", memory_id)
        raise HTTPException(status_code=500, detail="Failed to delete memory") from exc


@router.get("/cache-stats")
@limiter.limit(MEMORY_WRITE_RATE_LIMIT)
async def get_cache_stats_endpoint(
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """Get memory cache statistics for authenticated operators."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        return core.get_cache_stats()
    except Exception as exc:
        logger.exception("Failed to get cache stats")
        raise HTTPException(status_code=500, detail="Failed to get cache stats") from exc


# ---------------------------------------------------------------------------
# Plain Python helpers (in-process use / backward compatibility)
# ---------------------------------------------------------------------------


def add_memory(context_id: str, content: str, metadata: Optional[dict] = None) -> Dict:
    """Add a new memory to the retrieval system."""
    if not context_id or not isinstance(context_id, str):
        return {"success": False, "error": "Invalid context_id"}
    if not content or not isinstance(content, str):
        return {"success": False, "error": "Invalid content"}
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        return {"success": False, "error": "metadata must be a dict"}

    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        memory_id = core.add_memory(context_id, content, metadata)
        return {
            "success": True,
            "memory_id": memory_id,
            "context_tag": f"mrm:add:{context_id}",
        }
    except Exception as exc:
        logger.error("Failed to add memory: %s", exc, exc_info=True)
        return {"success": False, "error": str(exc)}


def query_memory(context_id: str, query: str, top_k: int = 10) -> Dict:
    """Query memories by content similarity."""
    if not context_id or not isinstance(context_id, str):
        return {"success": False, "error": "Invalid context_id"}
    if not query or not isinstance(query, str):
        return {"success": False, "error": "Invalid query"}

    try:
        from modules.memory_retrieval.config import MemoryRetrievalConfig
        from modules.memory_retrieval.core import MemoryRetrievalCore

        config = MemoryRetrievalConfig.from_env()
        max_allowed = max(100, config.max_results * 10)
        if not isinstance(top_k, int) or top_k < 1 or top_k > max_allowed:
            return {"success": False, "error": f"top_k must be between 1 and {max_allowed}"}

        core = MemoryRetrievalCore.get_instance()
        results = core.retrieve_memories(context_id, query, top_k)
        return {
            "success": True,
            "results": results,
            "context_tag": f"mrm:query:{context_id}",
            "cache_stats": core.get_cache_stats(),
        }
    except Exception as exc:
        logger.error("Failed to query memories: %s", exc, exc_info=True)
        return {"success": False, "error": str(exc)}


def get_memory(memory_id: str) -> Dict:
    """Retrieve a specific memory by identifier."""
    if not memory_id or not isinstance(memory_id, str):
        return {"success": False, "error": "Invalid memory_id"}
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        memory = MemoryRetrievalCore.get_instance().get_memory(memory_id)
        if memory is None:
            return {"success": False, "error": "Memory not found"}
        return {"success": True, "memory": memory, "context_tag": "mrm:get"}
    except Exception as exc:
        logger.error("Failed to get memory: %s", exc, exc_info=True)
        return {"success": False, "error": str(exc)}


def delete_memory(memory_id: str) -> Dict:
    """Delete a specific memory by identifier."""
    if not memory_id or not isinstance(memory_id, str):
        return {"success": False, "error": "Invalid memory_id"}
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        deleted = MemoryRetrievalCore.get_instance().delete_memory(memory_id)
        if not deleted:
            return {"success": False, "error": "Memory not found"}
        return {"success": True, "memory_id": memory_id, "context_tag": "mrm:delete"}
    except Exception as exc:
        logger.error("Failed to delete memory: %s", exc, exc_info=True)
        return {"success": False, "error": str(exc)}
