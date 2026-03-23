"""Memory Retrieval Module - API Interface."""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


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
