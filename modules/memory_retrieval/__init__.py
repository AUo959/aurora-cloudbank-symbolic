"""
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
