"""Memory Retrieval Module - Storage Backend.

Manages persistent memory storage with vector indexing and similarity search.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid

from modules.memory_retrieval.config import MemoryRetrievalConfig


logger = logging.getLogger(__name__)


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
        metadata_copy = self._prepare_metadata(metadata)
        created_at = self._normalize_created_at(metadata_copy.get("created_at"))
        metadata_copy["created_at"] = created_at
        memory = {
            "id": memory_id,
            "context_id": context_id,
            "content": content,
            "embedding": self._generate_embedding(content),
            "metadata": metadata_copy,
            "created_at": created_at,
            "t1_anchor": metadata_copy.get("t1_anchor", "T1:MRM:ADD"),
            "srb_anchor": metadata_copy.get("srb_anchor", f"SRB:{context_id}:{memory_id}"),
            "anchor_seed": metadata_copy.get("anchor_seed", self._config.anchor_seed),
            "ethics_protocol": metadata_copy.get("ethics_protocol", self._config.ethics_protocol),
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
                memory_copy = copy.deepcopy(memory)
                metadata = memory_copy.setdefault("metadata", {})
                metadata.setdefault("created_at", memory_copy.get("created_at"))
                metadata.setdefault("t1_anchor", memory_copy.get("t1_anchor"))
                metadata.setdefault("srb_anchor", memory_copy.get("srb_anchor"))
                metadata.setdefault("anchor_seed", memory_copy.get("anchor_seed"))
                metadata.setdefault("ethics_protocol", memory_copy.get("ethics_protocol"))
                return memory_copy
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
        if path.is_dir():
            logger.warning("MRM storage path points to a directory: %s", path)
            self._memories = []
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load MRM store from %s: %s", path, exc)
            self._memories = []
            return
        memories = payload.get("memories", [])
        self._memories = memories if isinstance(memories, list) else []

    def _save_to_disk(self) -> None:
        path = Path(self._config.storage_path or "")
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "anchor_seed": self._config.anchor_seed,
            "ethics_protocol": self._config.ethics_protocol,
            "memories": self._memories,
        }
        temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        temp_path.replace(path)

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic development-time embedding vector."""
        tokens = [token for token in text.lower().split() if token]
        dimension = self._config.vector_dimension
        embedding = [0.0] * dimension
        if not tokens:
            return embedding
        for token in tokens:
            block_index = 0
            value_index = 0
            while value_index < dimension:
                digest = hashlib.sha256(f"{token}:{block_index}".encode("utf-8")).digest()
                for byte in digest:
                    embedding[value_index] += (byte / 255.0) - 0.5
                    value_index += 1
                    if value_index >= dimension:
                        break
                block_index += 1
        magnitude = math.sqrt(sum(value * value for value in embedding))
        if magnitude > 0:
            embedding = [value / magnitude for value in embedding]
        return embedding

    def _prepare_metadata(self, metadata: dict) -> Dict[str, Any]:
        """Create an isolated, JSON-safe copy of caller metadata."""
        return self._make_json_safe(copy.deepcopy(metadata))

    def _make_json_safe(self, value: Any) -> Any:
        """Normalize common Python objects to JSON-safe values."""
        if isinstance(value, dict):
            return {str(key): self._make_json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._make_json_safe(item) for item in value]
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, Enum):
            return self._make_json_safe(value.value)
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        return str(value)

    def _normalize_created_at(self, created_at: Any) -> str:
        """Normalize created_at into an ISO8601 string for scoring and persistence."""
        if isinstance(created_at, datetime):
            timestamp = created_at
        elif isinstance(created_at, (int, float)):
            timestamp = datetime.fromtimestamp(created_at, tz=timezone.utc)
        elif isinstance(created_at, str) and created_at:
            return created_at
        else:
            timestamp = datetime.now(timezone.utc)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.isoformat()

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2)) / (magnitude1 * magnitude2)
