"""Memory Retrieval Module - API Interface.

Provides both a FastAPI router (``router``) for HTTP exposure and plain
Python helper functions for in-process use.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/memory-retrieval", tags=["MemoryRetrieval"])


class AddMemoryRequest(BaseModel):
    context_id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AddMemoryResponse(BaseModel):
    memory_id: str
    status: str = "ok"


class RetrieveMemoriesRequest(BaseModel):
    context_id: str
    query: str
    top_k: int = Field(default=10, ge=1, le=100)
    user_id: str = "default"
    max_tokens: Optional[int] = Field(default=None, ge=1)


class RetrieveMemoriesResponse(BaseModel):
    memories: List[Dict[str, Any]]
    count: int


@router.post("/memories", response_model=AddMemoryResponse)
async def add_memory_endpoint(request: AddMemoryRequest):
    """Add a memory entry to the retrieval store."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        memory_id = core.add_memory(request.context_id, request.content, request.metadata)
        return AddMemoryResponse(memory_id=memory_id)
    except Exception as exc:
        logger.exception("Failed to add memory")
        raise HTTPException(status_code=500, detail="Failed to add memory") from exc


@router.post("/retrieve", response_model=RetrieveMemoriesResponse)
async def retrieve_memories_endpoint(request: RetrieveMemoriesRequest):
    """Retrieve relevant memories for a context/query pair."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        kwargs: Dict[str, Any] = {}
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        memories = core.retrieve_memories(
            request.context_id,
            request.query,
            top_k=request.top_k,
            user_id=request.user_id,
            **kwargs,
        )
        return RetrieveMemoriesResponse(memories=memories, count=len(memories))
    except Exception as exc:
        logger.exception("Failed to retrieve memories")
        raise HTTPException(status_code=500, detail="Failed to retrieve memories") from exc


@router.get("/memories/{memory_id}", response_model=Dict[str, Any])
async def get_memory_endpoint(memory_id: str):
    """Fetch a single memory entry by ID."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        memory = core.get_memory(memory_id)
        if memory is None:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id!r} not found")
        return memory
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get memory %s", memory_id)
        raise HTTPException(status_code=500, detail="Failed to get memory") from exc


@router.delete("/memories/{memory_id}")
async def delete_memory_endpoint(memory_id: str):
    """Delete a memory entry."""
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore

        core = MemoryRetrievalCore.get_instance()
        deleted = core.delete_memory(memory_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id!r} not found")
        return {"status": "deleted", "memory_id": memory_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete memory %s", memory_id)
        raise HTTPException(status_code=500, detail="Failed to delete memory") from exc


@router.get("/cache-stats")
async def get_cache_stats_endpoint():
    """Get memory cache statistics."""
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
