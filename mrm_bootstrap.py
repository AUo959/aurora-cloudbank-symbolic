#!/usr/bin/env python3
"""
Memory Retrieval Module (MRM) Bootstrap Script

This script scaffolds the complete directory structure and stub modules
for the Memory Retrieval Module in AuroraOS.

Usage:
    python3 mrm_bootstrap.py

The script will create:
- modules/memory_retrieval/ directory
- __init__.py package initialization
- config.py - Configuration management
- store.py - Storage backend with vector indexing
- cache.py - TTL-based caching with genealogy
- core.py - Retrieval orchestration and scoring
- api.py - Public API interface

All stub modules include placeholder classes matching the specification.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def create_directory(path: Path) -> bool:
    """Create directory if it doesn't exist."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create directory {path}: {e}")
        return False


def write_file(path: Path, content: str) -> bool:
    """Write content to file."""
    try:
        path.write_text(content)
        print(f"✓ Created file: {path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create file {path}: {e}")
        return False


def generate_init_py() -> str:
    """Generate __init__.py content."""
    return '''"""
Memory Retrieval Module (MRM) for AuroraOS

This module provides context-aware memory retrieval with multi-factor scoring,
DLP compliance, and quantum memory integration.

Core Components:
- Config: Configuration management
- Store: Vector storage and similarity search
- Cache: TTL-based caching with genealogy tracking
- Core: Retrieval orchestration and scoring
- API: Public interface for memory operations
"""

from modules.memory_retrieval.api import add_memory, query_memory

__version__ = "0.1.0"
__all__ = ["add_memory", "query_memory"]
'''


def generate_config_py() -> str:
    """Generate config.py stub."""
    return '''"""
Memory Retrieval Module - Configuration

Centralized configuration management for the MRM.
"""

from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class MemoryRetrievalConfig:
    """
    Configuration for Memory Retrieval Module.
    
    Attributes:
        vector_dimension: Size of embedding vectors
        cache_ttl_seconds: Cache entry lifetime
        storage_backend: Backend type ('memory', 'file', 'vector_db')
        storage_path: File path for persistent storage
        max_results: Maximum query results to return
        score_weights: Weighting factors for scoring components
    """
    
    vector_dimension: int = 384
    cache_ttl_seconds: int = 300
    storage_backend: str = "memory"
    storage_path: Optional[str] = None
    max_results: int = 10
    
    # Score component weights (should sum to ~1.0)
    weight_relevance: float = 0.4
    weight_importance: float = 0.3
    weight_recency: float = 0.2
    weight_cultural: float = 0.1
    
    @classmethod
    def from_env(cls) -> "MemoryRetrievalConfig":
        """
        Load configuration from environment variables.
        
        Environment variables:
            MRM_VECTOR_DIM: Vector dimension (default: 384)
            MRM_CACHE_TTL: Cache TTL in seconds (default: 300)
            MRM_STORAGE_BACKEND: Storage backend type (default: 'memory')
            MRM_STORAGE_PATH: Storage file path (default: None)
            MRM_MAX_RESULTS: Maximum results (default: 10)
        
        Returns:
            MemoryRetrievalConfig instance
        """
        return cls(
            vector_dimension=int(os.getenv("MRM_VECTOR_DIM", 384)),
            cache_ttl_seconds=int(os.getenv("MRM_CACHE_TTL", 300)),
            storage_backend=os.getenv("MRM_STORAGE_BACKEND", "memory"),
            storage_path=os.getenv("MRM_STORAGE_PATH"),
            max_results=int(os.getenv("MRM_MAX_RESULTS", 10)),
        )
    
    def validate(self) -> bool:
        """
        Validate configuration parameters.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        if self.vector_dimension <= 0:
            raise ValueError("vector_dimension must be positive")
        
        if self.cache_ttl_seconds <= 0:
            raise ValueError("cache_ttl_seconds must be positive")
        
        if self.storage_backend not in ["memory", "file", "vector_db"]:
            raise ValueError("storage_backend must be 'memory', 'file', or 'vector_db'")
        
        if self.max_results <= 0 or self.max_results > 1000:
            raise ValueError("max_results must be between 1 and 1000")
        
        return True
'''


def generate_store_py() -> str:
    """Generate store.py stub."""
    return '''"""
Memory Retrieval Module - Storage Backend

Manages persistent memory storage with vector indexing and similarity search.

Exports and imports symbolic vectors through THREAD_TRANSFER_BRIDGE_v1 for 
cross-thread memory continuity.
"""

from typing import List, Optional, Tuple
import uuid
import math
import hashlib
from datetime import datetime


class MemoryStore:
    """
    Storage backend for memory entries with vector similarity search.
    
    Initial implementation uses in-memory list with linear search.
    Future versions will support pluggable backends (file, vector DB).
    """
    
    def __init__(self, config):
        """
        Initialize memory store.
        
        Args:
            config: MemoryRetrievalConfig instance
        """
        self._config = config
        self._memories: List[dict] = []
    
    def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
        """
        Add a new memory entry.
        
        Args:
            context_id: Context isolation identifier
            content: Memory content text
            metadata: Additional metadata dict
        
        Returns:
            Generated memory_id (UUID)
        """
        memory_id = str(uuid.uuid4())
        embedding = self._generate_embedding(content)
        
        memory = {
            "id": memory_id,
            "context_id": context_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
        }
        
        self._memories.append(memory)
        return memory_id
    
    def query_memory(self, context_id: str, query: str, top_k: int) -> List[Tuple]:
        """
        Query memories by semantic similarity.
        
        Args:
            context_id: Context to search within
            query: Search query string
            top_k: Number of top results to return
        
        Returns:
            List of (memory_id, score, content, metadata) tuples ordered by score
        """
        query_embedding = self._generate_embedding(query)
        
        # Filter by context and compute similarities
        results = []
        for memory in self._memories:
            if memory["context_id"] != context_id:
                continue
            
            similarity = self._cosine_similarity(query_embedding, memory["embedding"])
            results.append((
                memory["id"],
                similarity,
                memory["content"],
                memory["metadata"]
            ))
        
        # Sort by score descending and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_memory(self, memory_id: str) -> Optional[dict]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: Memory identifier
        
        Returns:
            Memory dict or None if not found
        """
        for memory in self._memories:
            if memory["id"] == memory_id:
                return memory
        return None
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Remove a memory from storage.
        
        Args:
            memory_id: Memory identifier
        
        Returns:
            True if deleted, False if not found
        """
        for i, memory in enumerate(self._memories):
            if memory["id"] == memory_id:
                del self._memories[i]
                return True
        return False
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.
        
        Initial implementation uses simple mock embeddings.
        Future: integrate sentence-transformers or similar.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        # Mock implementation: simple hash-based embedding
        # TODO: Replace with actual embedding model
        
        hash_val = int(hashlib.sha256(text.encode()).hexdigest(), 16)
        dimension = self._config.vector_dimension
        
        # Generate pseudo-random vector from hash
        embedding = []
        for i in range(dimension):
            val = ((hash_val >> (i % 32)) & 0xFF) / 255.0
            embedding.append(val)
        
        # Normalize to unit length
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
        
        Returns:
            Similarity score (0-1)
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
'''


def generate_cache_py() -> str:
    """Generate cache.py stub."""
    return '''"""
Memory Retrieval Module - Cache

TTL-based caching with genealogy tracking for query results.
"""

from typing import Optional, Any, Dict
import time
import hashlib


class MemoryCache:
    """
    TTL-based cache with hit/miss tracking.
    
    Caches query results to improve performance and tracks statistics
    for monitoring and optimization.
    """
    
    def __init__(self, config):
        """
        Initialize cache.
        
        Args:
            config: MemoryRetrievalConfig instance
        """
        self._config = config
        self._cache: Dict[str, dict] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }
    
    def get(self, cache_key: str) -> Optional[Any]:
        """
        Retrieve cached value if not expired.
        
        Args:
            cache_key: Cache key string
        
        Returns:
            Cached value or None if not found/expired
        """
        if cache_key not in self._cache:
            self._stats["misses"] += 1
            return None
        
        entry = self._cache[cache_key]
        
        # Check TTL expiration
        if time.time() > entry["expires_at"]:
            del self._cache[cache_key]
            self._stats["misses"] += 1
            self._stats["evictions"] += 1
            return None
        
        # Cache hit
        self._stats["hits"] += 1
        entry["hits"] += 1
        entry["last_accessed"] = time.time()
        
        return entry["value"]
    
    def set(self, cache_key: str, value: Any, ttl: Optional[int] = None):
        """
        Store value in cache with TTL.
        
        Args:
            cache_key: Cache key string
            value: Value to cache
            ttl: Time to live in seconds (uses config default if None)
        """
        if ttl is None:
            ttl = self._config.cache_ttl_seconds
        
        entry = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "last_accessed": time.time(),
            "hits": 0,
        }
        
        self._cache[cache_key] = entry
    
    def invalidate(self, pattern: str):
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match (simple prefix matching)
        """
        keys_to_delete = []
        for key in self._cache:
            if key.startswith(pattern):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            del self._cache[key]
            self._stats["evictions"] += 1
    
    def get_stats(self) -> dict:
        """
        Return cache statistics.
        
        Returns:
            Dict with hits, misses, hit_rate, size, evictions
        """
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 0.0
        
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "hit_rate": hit_rate,
            "size": len(self._cache),
        }
    
    def make_query_key(self, context_id: str, query: str, top_k: int) -> str:
        """
        Generate cache key for query.
        
        Args:
            context_id: Context identifier
            query: Query string
            top_k: Number of results
        
        Returns:
            Cache key string
        """
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:8]
        return f"query:{context_id}:{query_hash}:{top_k}"
'''


def generate_core_py() -> str:
    """Generate core.py stub."""
    return '''"""
Memory Retrieval Module - Core Orchestration

Orchestrates retrieval operations combining store, cache, and scoring.
Integrates with DLP tracking and AuMemManager.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=MRM_INIT, symbolic_hash=EOS_SEED_ORION
"""

from typing import List, Dict
import math
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# DLP tracking integration
try:
    from src.core.native_dlp_export import NativeDLPTracker
    DLP_AVAILABLE = True
except ImportError:
    DLP_AVAILABLE = False
    logger.warning("NativeDLPTracker not available, DLP tracking disabled")


class MemoryRetrievalCore:
    """
    Core orchestration layer for memory retrieval.
    
    Combines storage, caching, and multi-factor scoring to provide
    intelligent memory retrieval with DLP compliance.
    """
    
    _instance = None
    
    def __init__(self, config):
        """
        Initialize core retrieval system.
        
        Args:
            config: MemoryRetrievalConfig instance
        """
        from modules.memory_retrieval.config import MemoryRetrievalConfig
        from modules.memory_retrieval.store import MemoryStore
        from modules.memory_retrieval.cache import MemoryCache
        
        self._config = config
        self._store = MemoryStore(config)
        self._cache = MemoryCache(config)
        
        # Initialize DLP tracker if available
        if DLP_AVAILABLE:
            self._dlp_tracker = NativeDLPTracker()
        else:
            self._dlp_tracker = None
    
    @classmethod
    def get_instance(cls):
        """
        Get singleton instance of core retrieval system.
        
        Returns:
            MemoryRetrievalCore instance
        """
        if cls._instance is None:
            from modules.memory_retrieval.config import MemoryRetrievalConfig
            config = MemoryRetrievalConfig.from_env()
            config.validate()
            cls._instance = cls(config)
        return cls._instance
    
    def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
        """
        Add memory with DLP tagging and anchor tracking.
        
        Args:
            context_id: Context isolation identifier
            content: Memory content
            metadata: Additional metadata
        
        Returns:
            Generated memory_id
        """
        # Add DLP tracking with Picard_Delta_3 protocol
        context_tag = f"MRM:add:{context_id}"
        
        if self._dlp_tracker:
            tag_id = self._dlp_tracker.create_tag("add_memory", {
                "context_id": context_id,
                "content_preview": content[:100] if len(content) > 100 else content,
            })
            tag = self._dlp_tracker.tags[tag_id]
            tag.add_anchor_protocol("Picard_Delta_3")
            tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
            tag.add_t1_srb_anchor("SRB_SYMBOLIC_BRIDGE")
            tag.metadata["context_tag"] = context_tag
        
        # Ensure metadata has required fields
        if "importance" not in metadata:
            metadata["importance"] = 0.5
        if "created_at" not in metadata:
            metadata["created_at"] = datetime.now(timezone.utc).isoformat()
        
        # Add DLP context tag to metadata
        metadata["dlp_tag"] = context_tag
        
        memory_id = self._store.add_memory(context_id, content, metadata)
        
        # Invalidate cache for this context
        self._cache.invalidate(f"query:{context_id}:")
        
        logger.info(f"Added memory {memory_id} to context {context_id}", extra={"context_tag": context_tag})
        return memory_id
    
    def retrieve_memories(self, context_id: str, query: str, top_k: int = 10) -> List[Dict]:
        """
        Main retrieval method combining cache, store, and scoring.
        
        Args:
            context_id: Context to search within
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of scored and ranked memory results
        """
        # Add DLP tracking for query operation
        context_tag = f"MRM:query:{context_id}"
        
        if self._dlp_tracker:
            tag_id = self._dlp_tracker.create_tag("query_memory", {
                "context_id": context_id,
                "query_preview": query[:100] if len(query) > 100 else query,
                "top_k": top_k,
            })
            tag = self._dlp_tracker.tags[tag_id]
            tag.add_anchor_protocol("Picard_Delta_3")
            tag.metadata["context_tag"] = context_tag
        
        # Check cache first
        cache_key = self._cache.make_query_key(context_id, query, top_k)
        cached_results = self._cache.get(cache_key)
        
        if cached_results is not None:
            logger.debug(f"Cache hit for query: {query[:50]}")
            return cached_results
        
        # Cache miss - query store
        logger.debug(f"Cache miss for query: {query[:50]}")
        raw_results = self._store.query_memory(context_id, query, top_k)
        
        # Compute multi-factor scores
        scored_results = []
        for memory_id, relevance, content, metadata in raw_results:
            final_score = self._compute_score(relevance, metadata)
            
            result = {
                "id": memory_id,
                "score": final_score,
                "content": content,
                "metadata": metadata,
                "score_breakdown": {
                    "relevance": relevance,
                    "importance": metadata.get("importance", 0.5),
                    "recency": self._compute_recency_score(metadata.get("created_at", "")),
                    "cultural": metadata.get("cultural_score", 1.0),
                }
            }
            scored_results.append(result)
        
        # Re-sort by final score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Cache results
        self._cache.set(cache_key, scored_results)
        
        return scored_results
    
    def _compute_score(self, relevance: float, metadata: dict) -> float:
        """
        Compute final score from multiple factors.
        
        Args:
            relevance: Vector similarity score
            metadata: Memory metadata
        
        Returns:
            Final combined score
        """
        importance = metadata.get("importance", 0.5)
        recency = self._compute_recency_score(metadata.get("created_at", ""))
        cultural = metadata.get("cultural_score", 1.0)
        
        final_score = (
            self._config.weight_relevance * relevance +
            self._config.weight_importance * importance +
            self._config.weight_recency * recency +
            self._config.weight_cultural * cultural
        )
        
        return final_score
    
    def _compute_recency_score(self, created_at: str) -> float:
        """
        Calculate recency score with exponential decay.
        
        Args:
            created_at: ISO 8601 timestamp
        
        Returns:
            Recency score (0-1)
        """
        if not created_at:
            return 0.5
        
        try:
            created = datetime.fromisoformat(created_at)
            # Ensure timezone awareness
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            age_days = (now - created).total_seconds() / 86400
            decay_rate = 0.1  # Configurable
            return math.exp(-decay_rate * age_days)
        except Exception:
            return 0.5
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics dict
        """
        return self._cache.get_stats()
'''


def generate_api_py() -> str:
    """Generate api.py stub."""
    return '''"""
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
    
    try:
        from modules.memory_retrieval.core import MemoryRetrievalCore
        from modules.memory_retrieval.config import MemoryRetrievalConfig
        
        # Get max allowed results from config
        config = MemoryRetrievalConfig.from_env()
        max_allowed = max(100, config.max_results * 10)  # Allow up to 10x config default
        
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
'''


def main():
    """Main bootstrap execution."""
    print("=" * 70)
    print("Memory Retrieval Module (MRM) Bootstrap Script")
    print("=" * 70)
    print()
    
    # Get repository root
    repo_root = Path(__file__).parent.absolute()
    print(f"Repository root: {repo_root}")
    print()
    
    # Define module path
    module_path = repo_root / "modules" / "memory_retrieval"
    print(f"Target module path: {module_path}")
    print()
    
    # Create directory structure
    print("Creating directory structure...")
    if not create_directory(module_path):
        print("Failed to create module directory. Exiting.")
        return 1
    print()
    
    # Generate and write files
    files_to_create = [
        ("__init__.py", generate_init_py()),
        ("config.py", generate_config_py()),
        ("store.py", generate_store_py()),
        ("cache.py", generate_cache_py()),
        ("core.py", generate_core_py()),
        ("api.py", generate_api_py()),
    ]
    
    print("Creating module files...")
    success_count = 0
    for filename, content in files_to_create:
        file_path = module_path / filename
        if write_file(file_path, content):
            success_count += 1
    print()
    
    # Summary
    print("=" * 70)
    print("Bootstrap Summary")
    print("=" * 70)
    print(f"Files created: {success_count}/{len(files_to_create)}")
    print(f"Module location: {module_path}")
    print()
    
    if success_count == len(files_to_create):
        print("✓ Bootstrap completed successfully!")
        print()
        print("Next steps:")
        print("1. Review the specification: docs/AURORA_MRM_SPEC_v0.1.md")
        print("2. Read implementation instructions: COPILOT_INSTRUCTIONS.md")
        print("3. Implement modules according to the spec")
        print("4. Write tests in tests/test_memory_retrieval.py")
        print("5. Run tests: pytest tests/test_memory_retrieval.py")
        print()
        return 0
    else:
        print("✗ Bootstrap completed with errors.")
        print(f"Successfully created {success_count} of {len(files_to_create)} files.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
