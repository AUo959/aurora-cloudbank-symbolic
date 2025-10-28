"""
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
