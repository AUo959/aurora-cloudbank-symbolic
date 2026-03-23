"""Memory Retrieval Module - Storage Backend.

Manages persistent memory storage with vector indexing and similarity search.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid

from modules.memory_retrieval.config import MemoryRetrievalConfig


class MemoryStore:
    """Storage backend for memory entries with vector similarity search."""

    def __init__(self, config: MemoryRetrievalConfig):
        self._config = config
        self._memories: List[Dict] = []
        if self._config.storage_backend == "file":
            self._load_from_disk()

    def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
        """Add a new memory entry and return its identifier."""
        memory_id = str(uuid.uuid4())
        created_at = metadata.get("created_at", datetime.now(timezone.utc).isoformat())
        memory = {
            "id": memory_id,
            "context_id": context_id,
            "content": content,
            "embedding": self._generate_embedding(content),
            "metadata": metadata,
            "created_at": created_at,
            "t1_anchor": metadata.get("t1_anchor", "T1:MRM:ADD"),
            "srb_anchor": metadata.get("srb_anchor", f"SRB:{context_id}:{memory_id}"),
            "anchor_seed": metadata.get("anchor_seed", self._config.anchor_seed),
            "ethics_protocol": metadata.get("ethics_protocol", self._config.ethics_protocol),
        }
        self._memories.append(memory)
        self._persist_if_needed()
        return memory_id

    def query_memory(self, context_id: str, query: str, top_k: int) -> List[Tuple[str, float, str, dict]]:
        """Query memories by semantic similarity within a context."""
        query_embedding = self._generate_embedding(query)
        results: List[Tuple[str, float, str, dict]] = []
        for memory in self._memories:
            if memory["context_id"] != context_id:
                continue
            similarity = self._cosine_similarity(query_embedding, memory["embedding"])
            metadata = dict(memory["metadata"])
            metadata.setdefault("created_at", memory["created_at"])
            metadata.setdefault("t1_anchor", memory["t1_anchor"])
            metadata.setdefault("srb_anchor", memory["srb_anchor"])
            metadata.setdefault("anchor_seed", memory["anchor_seed"])
            metadata.setdefault("ethics_protocol", memory["ethics_protocol"])
            results.append((memory["id"], similarity, memory["content"], metadata))
        results.sort(key=lambda item: item[1], reverse=True)
        return results[:top_k]

    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Retrieve a specific memory by ID."""
        for memory in self._memories:
            if memory["id"] == memory_id:
                return dict(memory)
        return None

    def delete_memory(self, memory_id: str) -> bool:
        """Remove a memory from storage."""
        for index, memory in enumerate(self._memories):
            if memory["id"] == memory_id:
                del self._memories[index]
                self._persist_if_needed()
                return True
        return False

    def _persist_if_needed(self) -> None:
        if self._config.storage_backend == "file":
            self._save_to_disk()

    def _load_from_disk(self) -> None:
        path = Path(self._config.storage_path or "")
        if not path.exists():
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
        self._memories = payload.get("memories", [])

    def _save_to_disk(self) -> None:
        path = Path(self._config.storage_path or "")
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "anchor_seed": self._config.anchor_seed,
            "ethics_protocol": self._config.ethics_protocol,
            "memories": self._memories,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic development-time embedding vector."""
        tokens = [token for token in text.lower().split() if token]
        dimension = self._config.vector_dimension
        embedding = [0.0] * dimension
        if not tokens:
            return embedding
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for index, byte in enumerate(digest):
                bucket = index % dimension
                embedding[bucket] += (byte / 255.0) - 0.5
        magnitude = math.sqrt(sum(value * value for value in embedding))
        if magnitude > 0:
            embedding = [value / magnitude for value in embedding]
        return embedding

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2)) / (magnitude1 * magnitude2)
