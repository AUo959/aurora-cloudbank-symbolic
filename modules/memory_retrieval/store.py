"""
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
