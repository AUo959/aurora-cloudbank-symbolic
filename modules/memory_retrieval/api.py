"""
Memory Retrieval Module - API Interface

Public Python function interface for memory operations.
"""

from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


def add_memory(context_id: str, content: str, metadata: Optional[dict] = None) -> Dict:
    """
    Add a new memory to the retrieval system.
    
    Args:
        context_id: Context isolation identifier
        content: Memory content text
        metadata: Optional metadata dictionary
    
    Returns:
        {"success": bool, "memory_id": str, "context_tag": str} or error dict
    
    Example:
        >>> result = add_memory("user_session_123", "Python is a great language", 
        ...                     {"importance": 0.8, "tags": ["programming"]})
        >>> print(result["memory_id"])
    """
    # Validate inputs
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
    except Exception as e:
        logger.error(f"Failed to add memory: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def query_memory(context_id: str, query: str, top_k: int = 10) -> Dict:
    """
    Query memories by content similarity.
    
    Args:
        context_id: Context to search within
        query: Search query string
        top_k: Number of top results to return (default: 10)
    
    Returns:
        {
            "success": bool,
            "results": [{"id": str, "score": float, "content": str, "metadata": dict}],
            "context_tag": str
        } or error dict
    
    Example:
        >>> result = query_memory("user_session_123", "Python programming", top_k=5)
        >>> for memory in result["results"]:
        ...     print(f"{memory['score']:.2f}: {memory['content']}")
    """
    # Validate inputs
    if not context_id or not isinstance(context_id, str):
        return {"success": False, "error": "Invalid context_id"}
    
    if not query or not isinstance(query, str):
        return {"success": False, "error": "Invalid query"}
    
    if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
        return {"success": False, "error": "top_k must be between 1 and 100"}
    
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore
        
        core = MemoryRetrievalCore.get_instance()
        results = core.retrieve_memories(context_id, query, top_k)
        
        return {
            "success": True,
            "results": results,
            "context_tag": f"mrm:query:{context_id}",
            "cache_stats": core.get_cache_stats(),
        }
    except Exception as e:
        logger.error(f"Failed to query memories: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


# Future HTTP endpoint integration with FastAPI:
# 
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# 
# router = APIRouter(prefix="/memory", tags=["memory"])
# 
# class AddMemoryRequest(BaseModel):
#     context_id: str
#     content: str
#     metadata: Optional[dict] = None
# 
# @router.post("/add")
# async def add_memory_endpoint(request: AddMemoryRequest):
#     result = add_memory(request.context_id, request.content, request.metadata)
#     if not result["success"]:
#         raise HTTPException(status_code=400, detail=result["error"])
#     return result
# 
# class QueryMemoryRequest(BaseModel):
#     context_id: str
#     query: str
#     top_k: int = 10
# 
# @router.post("/query")
# async def query_memory_endpoint(request: QueryMemoryRequest):
#     result = query_memory(request.context_id, request.query, request.top_k)
#     if not result["success"]:
#         raise HTTPException(status_code=400, detail=result["error"])
#     return result
