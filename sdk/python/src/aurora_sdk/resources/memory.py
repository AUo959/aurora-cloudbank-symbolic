"""Memory management operations."""

from typing import Any, AsyncIterator, Optional

from aurora_sdk.models.memory import Memory, MemoryStats, MemoryTier
from aurora_sdk.transport.http import HTTPTransport


class MemoryResource:
    """Memory management operations.

    This resource provides access to the AuMemManager for creating,
    searching, and managing memories across hierarchical tiers.

    Example:
        >>> memory = client.memory
        >>> created = await memory.create("Important note", tier="active")
        >>> results = await memory.search("important", top_k=5)
    """

    def __init__(self, transport: HTTPTransport) -> None:
        """Initialize memory resource.

        Args:
            transport: HTTP transport layer
        """
        self._transport = transport

    async def create(
        self,
        content: str,
        tier: MemoryTier = "active",
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> Memory:
        """Create a new memory.

        Args:
            content: Memory content
            tier: Storage tier (active, compressed, archived)
            tags: Optional tags for categorization
            metadata: Optional metadata

        Returns:
            Created memory object

        Example:
            >>> memory = await client.memory.create(
            ...     "User preferences for quantum algorithms",
            ...     tier="active",
            ...     tags=["preferences", "quantum"],
            ...     metadata={"source": "user_input"}
            ... )
            >>> print(memory.memory_id)
        """
        payload: dict[str, Any] = {
            "content": content,
            "tier": tier,
        }

        if tags:
            payload["tags"] = tags

        if metadata:
            payload["metadata"] = metadata

        response = await self._transport.post("/aumem/memories", json=payload)
        return Memory.from_dict(response)

    async def get(self, memory_id: str) -> Memory:
        """Retrieve a memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory object

        Raises:
            ResourceNotFoundError: Memory not found

        Example:
            >>> memory = await client.memory.get("mem_abc123")
            >>> print(memory.content)
        """
        response = await self._transport.get(f"/aumem/memories/{memory_id}")
        return Memory.from_dict(response)

    async def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None
    ) -> Memory:
        """Update an existing memory.

        Args:
            memory_id: Memory identifier
            content: New content (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)

        Returns:
            Updated memory object

        Example:
            >>> updated = await client.memory.update(
            ...     "mem_abc123",
            ...     tags=["preferences", "quantum", "updated"]
            ... )
        """
        payload: dict[str, Any] = {}

        if content is not None:
            payload["content"] = content

        if tags is not None:
            payload["tags"] = tags

        if metadata is not None:
            payload["metadata"] = metadata

        response = await self._transport.put(f"/aumem/memories/{memory_id}", json=payload)
        return Memory.from_dict(response)

    async def delete(self, memory_id: str) -> None:
        """Delete a memory.

        Args:
            memory_id: Memory identifier

        Example:
            >>> await client.memory.delete("mem_abc123")
        """
        await self._transport.delete(f"/aumem/memories/{memory_id}")

    async def search(
        self,
        query: str,
        top_k: int = 10,
        tier: Optional[MemoryTier] = None
    ) -> list[Memory]:
        """Search memories semantically.

        Args:
            query: Search query
            top_k: Number of results to return
            tier: Optional tier filter

        Returns:
            List of matching memories

        Example:
            >>> results = await client.memory.search(
            ...     "quantum algorithms",
            ...     top_k=5,
            ...     tier="active"
            ... )
            >>> for memory in results:
            ...     print(f"• {memory.content} (score: {memory.attention_score:.2f})")
        """
        params: dict[str, Any] = {
            "query": query,
            "top_k": top_k,
        }

        if tier:
            params["tier"] = tier

        response = await self._transport.get("/aumem/search", params=params)
        memories_data = response.get("memories", [])
        return [Memory.from_dict(m) for m in memories_data]

    async def list(
        self,
        page: int = 1,
        page_size: int = 20,
        tier: Optional[MemoryTier] = None,
        tags: Optional[list[str]] = None
    ) -> AsyncIterator[Memory]:
        """List memories with automatic pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page
            tier: Optional tier filter
            tags: Optional tag filter

        Yields:
            Memory objects

        Example:
            >>> async for memory in client.memory.list(tier="active"):
            ...     print(memory.content)
        """
        current_page = page

        while True:
            params: dict[str, Any] = {
                "page": current_page,
                "page_size": page_size,
            }

            if tier:
                params["tier"] = tier

            if tags:
                params["tags"] = ",".join(tags)

            response = await self._transport.get("/aumem/memories", params=params)
            memories_data = response.get("memories", [])

            if not memories_data:
                break

            for memory_data in memories_data:
                yield Memory.from_dict(memory_data)

            # Check if there are more pages
            if not response.get("has_more", False):
                break

            current_page += 1

    async def get_stats(self) -> MemoryStats:
        """Get memory system statistics.

        Returns:
            Memory statistics

        Example:
            >>> stats = await client.memory.get_stats()
            >>> print(f"Total memories: {stats.total_memories}")
            >>> print(f"Active: {stats.active_count}")
            >>> print(f"Capacity: {stats.used_capacity}/{stats.total_capacity}")
        """
        response = await self._transport.get("/aumem/health")
        return MemoryStats.from_dict(response)
