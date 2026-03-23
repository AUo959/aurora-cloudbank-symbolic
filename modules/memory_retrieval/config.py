"""Memory Retrieval Module - Configuration.

Centralized configuration management for the MRM.
"""

from dataclasses import dataclass
import os
from typing import Optional


@dataclass
class MemoryRetrievalConfig:
    """Configuration for Memory Retrieval Module."""

    vector_dimension: int = 384
    cache_ttl_seconds: int = 300
    storage_backend: str = "memory"
    storage_path: Optional[str] = None
    max_results: int = 10
    recency_decay_rate: float = 0.1
    anchor_seed: str = "EOS_SEED_ORION"
    ethics_protocol: str = "Picard_Delta_3"

    # Score component weights (should sum to 1.0)
    weight_relevance: float = 0.4
    weight_importance: float = 0.3
    weight_recency: float = 0.2
    weight_cultural: float = 0.1

    @classmethod
    def from_env(cls) -> "MemoryRetrievalConfig":
        """Load configuration from environment variables."""
        return cls(
            vector_dimension=int(os.getenv("MRM_VECTOR_DIM", 384)),
            cache_ttl_seconds=int(os.getenv("MRM_CACHE_TTL", 300)),
            storage_backend=os.getenv("MRM_STORAGE_BACKEND", "memory"),
            storage_path=os.getenv("MRM_STORAGE_PATH"),
            max_results=int(os.getenv("MRM_MAX_RESULTS", 10)),
            recency_decay_rate=float(os.getenv("MRM_RECENCY_DECAY_RATE", 0.1)),
            anchor_seed=os.getenv("MRM_ANCHOR_SEED", "EOS_SEED_ORION"),
            ethics_protocol=os.getenv("MRM_ETHICS_PROTOCOL", "Picard_Delta_3"),
        )

    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.vector_dimension <= 0:
            raise ValueError("vector_dimension must be positive")
        if self.cache_ttl_seconds <= 0:
            raise ValueError("cache_ttl_seconds must be positive")
        if self.storage_backend not in ["memory", "file", "vector_db"]:
            raise ValueError("storage_backend must be 'memory', 'file', or 'vector_db'")
        if self.max_results <= 0 or self.max_results > 1000:
            raise ValueError("max_results must be between 1 and 1000")
        if self.recency_decay_rate <= 0:
            raise ValueError("recency_decay_rate must be positive")
        if not self.anchor_seed:
            raise ValueError("anchor_seed must not be empty")
        if not self.ethics_protocol:
            raise ValueError("ethics_protocol must not be empty")
        if self.storage_backend == "file" and not self.storage_path:
            raise ValueError("storage_path is required when storage_backend='file'")

        total_weight = (
            self.weight_relevance
            + self.weight_importance
            + self.weight_recency
            + self.weight_cultural
        )
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError("score weights must sum to 1.0")
        return True
