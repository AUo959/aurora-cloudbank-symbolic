"""Memory management models."""

from typing import Any, Literal

from pydantic import Field

from aurora_sdk.models.base import AuroraBaseModel

# Memory tier types
MemoryTier = Literal["active", "compressed", "archived"]


class Memory(AuroraBaseModel):
    """Memory object.

    Attributes:
        memory_id: Unique memory identifier
        content: Memory content
        tier: Storage tier
        tags: Categorization tags
        metadata: Additional metadata
        attention_score: Attention/relevance score
        access_count: Number of times accessed
    """

    memory_id: str = Field(..., description="Unique memory identifier")
    content: str = Field(..., description="Memory content")
    tier: MemoryTier = Field(..., description="Storage tier")
    tags: list[str] = Field(default_factory=list, description="Tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata")
    attention_score: float = Field(0.0, description="Attention score")
    access_count: int = Field(0, description="Access count")


class MemoryStats(AuroraBaseModel):
    """Memory system statistics.

    Attributes:
        total_memories: Total number of memories
        active_count: Memories in active tier
        compressed_count: Memories in compressed tier
        archived_count: Memories in archived tier
        total_capacity: Total memory capacity
        used_capacity: Used memory capacity
        compression_ratio: Overall compression ratio
    """

    total_memories: int = Field(..., description="Total memories")
    active_count: int = Field(0, description="Active tier count")
    compressed_count: int = Field(0, description="Compressed tier count")
    archived_count: int = Field(0, description="Archived tier count")
    total_capacity: int = Field(..., description="Total capacity")
    used_capacity: int = Field(..., description="Used capacity")
    compression_ratio: float = Field(1.0, description="Compression ratio")
