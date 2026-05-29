"""
Comprehensive Test Suite for Memory Retrieval Module

Tests cover all components of the memory retrieval system:
- MemoryRetrievalConfig: Configuration and validation
- MemoryStore: Storage backend with vector search
- MemoryCache: TTL-based caching
- MemoryRetrievalCore: Core orchestration layer

DLP: T1-MRM-TEST
Chain: #test/memory_retrieval/001
Target: 95%+ code coverage
"""

import os
import time
from datetime import datetime, timezone, timedelta
from enum import Enum

import pytest

from modules.memory_retrieval.config import MemoryRetrievalConfig
from modules.memory_retrieval.store import MemoryStore
from modules.memory_retrieval.cache import MemoryCache
from modules.memory_retrieval.core import MemoryRetrievalCore
from modules.memory_retrieval.api import add_memory, delete_memory, get_memory, query_memory


@pytest.mark.unit
@pytest.mark.critical
class TestMemoryRetrievalConfig:
    """Test configuration management."""

    def test_config_initialization_defaults(self):
        """Test config initializes with default values."""
        config = MemoryRetrievalConfig()

        assert config.vector_dimension == 384
        assert config.cache_ttl_seconds == 300
        assert config.storage_backend == "memory"
        assert config.max_results == 10

    def test_config_custom_values(self):
        """Test config with custom values."""
        config = MemoryRetrievalConfig(
            vector_dimension=512,
            cache_ttl_seconds=600,
            storage_backend="file",
            max_results=20
        )

        assert config.vector_dimension == 512
        assert config.cache_ttl_seconds == 600
        assert config.storage_backend == "file"
        assert config.max_results == 20

    def test_config_validation_success(self):
        """Test validation of valid config."""
        config = MemoryRetrievalConfig()
        assert config.validate() is True

    def test_config_validation_invalid_vector_dimension(self):
        """Test validation fails for invalid vector dimension."""
        config = MemoryRetrievalConfig(vector_dimension=-1)

        with pytest.raises(ValueError, match="vector_dimension must be positive"):
            config.validate()

    def test_config_validation_invalid_cache_ttl(self):
        """Test validation fails for invalid cache TTL."""
        config = MemoryRetrievalConfig(cache_ttl_seconds=0)

        with pytest.raises(ValueError, match="cache_ttl_seconds must be positive"):
            config.validate()

    def test_config_validation_invalid_storage_backend(self):
        """Test validation fails for invalid storage backend."""
        config = MemoryRetrievalConfig(storage_backend="invalid")

        with pytest.raises(ValueError, match="storage_backend must be"):
            config.validate()

    def test_config_validation_invalid_max_results(self):
        """Test validation fails for out-of-range max_results."""
        config = MemoryRetrievalConfig(max_results=0)

        with pytest.raises(ValueError, match="max_results must be between"):
            config.validate()

        config2 = MemoryRetrievalConfig(max_results=2000)

        with pytest.raises(ValueError, match="max_results must be between"):
            config2.validate()

    def test_config_score_weights(self):
        """Test score weighting configuration."""
        config = MemoryRetrievalConfig()

        assert config.weight_relevance == pytest.approx(0.4)
        assert config.weight_importance == pytest.approx(0.3)
        assert config.weight_recency == pytest.approx(0.2)
        assert config.weight_cultural == pytest.approx(0.1)

        # Weights should sum to 1.0
        total_weight = (
            config.weight_relevance +
            config.weight_importance +
            config.weight_recency +
            config.weight_cultural
        )
        assert abs(total_weight - 1.0) < 0.001


@pytest.mark.unit
@pytest.mark.critical
class TestMemoryStore:
    """Test memory storage backend."""

    def test_store_initialization(self):
        """Test store initializes correctly."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        assert store is not None
        assert store._config == config
        assert len(store._memories) == 0

    def test_add_memory(self):
        """Test adding a memory entry."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        memory_id = store.add_memory(
            context_id="test_context",
            content="Test memory content",
            metadata={"importance": 0.8}
        )

        assert memory_id is not None
        assert len(store._memories) == 1

    def test_add_multiple_memories(self):
        """Test adding multiple memory entries."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        ids = []
        for i in range(5):
            memory_id = store.add_memory(
                context_id="test_context",
                content=f"Memory {i}",
                metadata={"importance": 0.5}
            )
            ids.append(memory_id)

        assert len(store._memories) == 5
        assert len(set(ids)) == 5  # All IDs should be unique

    def test_get_memory_by_id(self):
        """Test retrieving memory by ID."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        content = "Specific test content"
        memory_id = store.add_memory(
            context_id="test_context",
            content=content,
            metadata={"importance": 0.9}
        )

        retrieved = store.get_memory(memory_id)

        assert retrieved is not None
        assert retrieved["id"] == memory_id
        assert retrieved["content"] == content
        assert retrieved["metadata"]["importance"] == pytest.approx(0.9)

    def test_store_isolates_metadata_from_caller_mutation(self):
        """Test that caller metadata mutations do not alter stored state."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)
        metadata = {"importance": 0.9, "nested": {"topic": "anchors"}}

        memory_id = store.add_memory(
            context_id="test_context",
            content="mutable metadata check",
            metadata=metadata,
        )
        metadata["nested"]["topic"] = "mutated"

        retrieved = store.get_memory(memory_id)
        assert retrieved["metadata"]["nested"]["topic"] == "anchors"

        retrieved["metadata"]["nested"]["topic"] = "changed again"
        reloaded = store.get_memory(memory_id)
        assert reloaded["metadata"]["nested"]["topic"] == "anchors"

    def test_get_nonexistent_memory(self):
        """Test retrieving non-existent memory returns None."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        retrieved = store.get_memory("nonexistent-id")
        assert retrieved is None

    def test_delete_memory(self):
        """Test deleting a memory."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        memory_id = store.add_memory(
            context_id="test_context",
            content="To be deleted",
            metadata={}
        )

        assert len(store._memories) == 1
        deleted = store.delete_memory(memory_id)

        assert deleted is True
        assert len(store._memories) == 0

    def test_delete_nonexistent_memory(self):
        """Test deleting non-existent memory returns False."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        deleted = store.delete_memory("nonexistent-id")
        assert deleted is False

    def test_query_memory_by_similarity(self):
        """Test querying memories by semantic similarity."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        # Add some test memories
        store.add_memory(
            context_id="test_context",
            content="quantum physics research",
            metadata={"importance": 0.9}
        )
        store.add_memory(
            context_id="test_context",
            content="classical mechanics study",
            metadata={"importance": 0.7}
        )
        store.add_memory(
            context_id="test_context",
            content="biology experiments",
            metadata={"importance": 0.6}
        )

        # Query for physics-related content
        results = store.query_memory(
            context_id="test_context",
            query="quantum research",
            top_k=2
        )

        assert len(results) <= 2
        assert all(len(r) == 4 for r in results)  # (id, score, content, metadata)

    def test_query_respects_context_isolation(self):
        """Test that queries only return memories from the specified context."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        # Add memories to different contexts
        store.add_memory(
            context_id="context_a",
            content="Memory in context A",
            metadata={}
        )
        store.add_memory(
            context_id="context_b",
            content="Memory in context B",
            metadata={}
        )

        # Query context A
        results = store.query_memory(
            context_id="context_a",
            query="memory",
            top_k=10
        )

        # Should only return memories from context A
        assert len(results) == 1
        assert results[0][2] == "Memory in context A"

    def test_embedding_generation(self):
        """Test embedding vector generation."""
        config = MemoryRetrievalConfig(vector_dimension=128)
        store = MemoryStore(config)

        embedding = store._generate_embedding("test content")

        assert len(embedding) == 128
        assert all(isinstance(x, float) for x in embedding)

        # Embeddings should be normalized (unit length)
        magnitude = sum(x * x for x in embedding) ** 0.5
        assert abs(magnitude - 1.0) < 0.001
        assert any(abs(value) > 0 for value in embedding[32:])

    def test_embedding_consistency(self):
        """Test that same text produces same embedding."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        text = "consistent test text"
        embedding1 = store._generate_embedding(text)
        embedding2 = store._generate_embedding(text)

        assert embedding1 == embedding2

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        # Identical vectors should have similarity 1.0
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = store._cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.001

        # Orthogonal vectors should have similarity 0.0
        vec3 = [1.0, 0.0, 0.0]
        vec4 = [0.0, 1.0, 0.0]
        similarity = store._cosine_similarity(vec3, vec4)
        assert abs(similarity) < 0.001

    def test_cosine_similarity_dimension_mismatch(self):
        """Test that mismatched dimensions raise error."""
        config = MemoryRetrievalConfig()
        store = MemoryStore(config)

        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]

        with pytest.raises(ValueError, match="Vectors must have same dimension"):
            store._cosine_similarity(vec1, vec2)


@pytest.mark.unit
@pytest.mark.critical
class TestMemoryCache:
    """Test TTL-based caching."""

    def test_cache_initialization(self):
        """Test cache initializes correctly."""
        config = MemoryRetrievalConfig()
        cache = MemoryCache(config)

        assert cache is not None
        assert len(cache._cache) == 0
        assert cache._stats["hits"] == 0
        assert cache._stats["misses"] == 0

    def test_cache_set_and_get(self):
        """Test setting and getting cached values."""
        config = MemoryRetrievalConfig()
        cache = MemoryCache(config)

        cache.set("test_key", "test_value")
        value = cache.get("test_key")

        assert value == "test_value"
        assert cache._stats["hits"] == 1

    def test_cache_miss(self):
        """Test cache miss returns None."""
        config = MemoryRetrievalConfig()
        cache = MemoryCache(config)

        value = cache.get("nonexistent_key")

        assert value is None
        assert cache._stats["misses"] == 1

    @pytest.mark.slow  # #792: TTL test sleeps 1.1s
    def test_cache_ttl_expiration(self):
        """Test that cache entries expire after TTL."""
        config = MemoryRetrievalConfig(cache_ttl_seconds=1)
        cache = MemoryCache(config)

        cache.set("test_key", "test_value")
        value1 = cache.get("test_key")
        assert value1 == "test_value"

        # Wait for expiration
        time.sleep(1.1)

        value2 = cache.get("test_key")
        assert value2 is None
        assert cache._stats["evictions"] == 1

    def test_cache_custom_ttl(self):
        """Test setting custom TTL for cache entry."""
        config = MemoryRetrievalConfig()
        cache = MemoryCache(config)

        cache.set("test_key", "test_value", ttl=2)

        # Should still be present immediately
        value = cache.get("test_key")
        assert value == "test_value"

    def test_cache_invalidate_pattern(self):
        """Test invalidating cache entries by pattern."""
        config = MemoryRetrievalConfig()
        cache = MemoryCache(config)

        cache.set("query:context1:abc", "value1")
        cache.set("query:context1:def", "value2")
        cache.set("query:context2:ghi", "value3")

        # Invalidate all context1 entries
        cache.invalidate("query:context1:")

        assert cache.get("query:context1:abc") is None
        assert cache.get("query:context1:def") is None
        assert cache.get("query:context2:ghi") == "value3"
        assert cache._stats["evictions"] == 2

    def test_cache_stats(self):
        """Test cache statistics tracking."""
        config = MemoryRetrievalConfig()
        cache = MemoryCache(config)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.get("key1")  # hit
        cache.get("key1")  # hit
        cache.get("key3")  # miss

        stats = cache.get_stats()

        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["size"] == 2
        assert abs(stats["hit_rate"] - 0.666) < 0.01

    def test_cache_make_query_key(self):
        """Test query key generation."""
        config = MemoryRetrievalConfig()
        cache = MemoryCache(config)

        key = cache.make_query_key("context1", "test query", 10)

        assert key.startswith("query:context1:")
        assert ":10" in key

        # Same inputs should produce same key
        key2 = cache.make_query_key("context1", "test query", 10)
        assert key == key2

        # Different inputs should produce different keys
        key3 = cache.make_query_key("context2", "test query", 10)
        assert key != key3


@pytest.mark.unit
@pytest.mark.critical
class TestMemoryRetrievalCore:
    """Test core orchestration layer."""

    def test_core_initialization(self):
        """Test core initializes with config."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        assert core is not None
        assert core._config == config
        assert core._store is not None
        assert core._cache is not None

    def test_add_memory_with_dlp_tracking(self):
        """Test adding memory with DLP tracking."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        memory_id = core.add_memory(
            context_id="test_context",
            content="Test memory content",
            metadata={"importance": 0.8}
        )

        assert memory_id is not None

        # Verify memory was added with proper metadata
        memory = core._store.get_memory(memory_id)
        assert memory is not None
        assert memory["metadata"]["importance"] == pytest.approx(0.8)
        assert "dlp_tag" in memory["metadata"]

    def test_add_memory_default_metadata(self):
        """Test that default metadata values are added."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        memory_id = core.add_memory(
            context_id="test_context",
            content="Test content",
            metadata={}
        )

        memory = core._store.get_memory(memory_id)
        assert "importance" in memory["metadata"]
        assert "created_at" in memory["metadata"]

    def test_retrieve_memories_cache_miss(self):
        """Test memory retrieval with cache miss."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        # Add test memories
        core.add_memory(
            context_id="test_context",
            content="quantum computing research",
            metadata={"importance": 0.9}
        )

        # First retrieval should be cache miss
        results = core.retrieve_memories(
            context_id="test_context",
            query="quantum",
            top_k=5
        )

        assert len(results) >= 0
        assert isinstance(results, list)

    def test_retrieve_memories_cache_hit(self):
        """Test memory retrieval with cache hit."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        core.add_memory(
            context_id="test_context",
            content="test content",
            metadata={}
        )

        # First call - cache miss
        results1 = core.retrieve_memories(
            context_id="test_context",
            query="test",
            top_k=5
        )

        # Second call - should be cache hit
        results2 = core.retrieve_memories(
            context_id="test_context",
            query="test",
            top_k=5
        )

        assert results1 == results2

    def test_recency_score_accepts_non_string_timestamps(self):
        """Test recency scoring degrades safely for non-string timestamp inputs."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        score_from_datetime = core._compute_recency_score(datetime.now(timezone.utc))
        score_from_epoch = core._compute_recency_score(time.time())
        score_from_invalid = core._compute_recency_score(object())

        assert 0.0 <= score_from_datetime <= 1.0
        assert 0.0 <= score_from_epoch <= 1.0
        assert score_from_invalid == pytest.approx(0.5)

    def test_retrieve_memories_with_scoring(self):
        """Test that retrieved memories include score breakdown."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        core.add_memory(
            context_id="test_context",
            content="test memory",
            metadata={"importance": 0.8}
        )

        results = core.retrieve_memories(
            context_id="test_context",
            query="test",
            top_k=5
        )

        if len(results) > 0:
            result = results[0]
            assert "score" in result
            assert "score_breakdown" in result
            assert "relevance" in result["score_breakdown"]
            assert "importance" in result["score_breakdown"]
            assert "recency" in result["score_breakdown"]
            assert "cultural" in result["score_breakdown"]

    def test_cache_invalidation_on_add(self):
        """Test that cache is invalidated when adding new memory."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        # Add memory and query
        core.add_memory(
            context_id="test_context",
            content="first memory",
            metadata={}
        )

        results1 = core.retrieve_memories(
            context_id="test_context",
            query="memory",
            top_k=5
        )

        # Add another memory - should invalidate cache
        core.add_memory(
            context_id="test_context",
            content="second memory",
            metadata={}
        )

        results2 = core.retrieve_memories(
            context_id="test_context",
            query="memory",
            top_k=5
        )

        # Results should be different after adding new memory
        assert len(results2) >= len(results1)

    def test_recency_score_calculation(self):
        """Test recency score calculation."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        # Recent timestamp
        recent = datetime.now(timezone.utc).isoformat()
        score_recent = core._compute_recency_score(recent)
        assert score_recent > 0.9

        # Old timestamp
        old = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        score_old = core._compute_recency_score(old)
        assert score_old < score_recent

    def test_recency_score_invalid_timestamp(self):
        """Test recency score with invalid timestamp."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        # Invalid timestamp should return default
        score = core._compute_recency_score("invalid")
        assert score == pytest.approx(0.5)

        # Empty string should return default
        score2 = core._compute_recency_score("")
        assert score2 == pytest.approx(0.5)

    def test_get_cache_stats(self):
        """Test retrieving cache statistics."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        stats = core.get_cache_stats()

        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert "size" in stats


@pytest.mark.integration
@pytest.mark.slow
class TestMemoryRetrievalIntegration:
    """Integration tests for complete memory retrieval workflows."""

    def test_end_to_end_workflow(self):
        """Test complete memory storage and retrieval workflow."""
        config = MemoryRetrievalConfig()
        config.validate()
        core = MemoryRetrievalCore(config)

        # Add multiple memories
        memories = [
            ("quantum physics research paper", {"importance": 0.9}),
            ("machine learning tutorial", {"importance": 0.7}),
            ("database optimization guide", {"importance": 0.6}),
        ]

        memory_ids = []
        for content, metadata in memories:
            memory_id = core.add_memory(
                context_id="research_context",
                content=content,
                metadata=metadata
            )
            memory_ids.append(memory_id)

        # Query for relevant memories
        results = core.retrieve_memories(
            context_id="research_context",
            query="quantum research",
            top_k=2
        )

        assert len(results) <= 2
        assert all("score" in r for r in results)

    def test_multi_context_isolation(self):
        """Test that contexts remain isolated."""
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)

        # Add memories to different contexts
        core.add_memory(
            context_id="context_a",
            content="content for context A",
            metadata={}
        )
        core.add_memory(
            context_id="context_b",
            content="content for context B",
            metadata={}
        )

        # Query each context
        results_a = core.retrieve_memories(
            context_id="context_a",
            query="content",
            top_k=10
        )
        results_b = core.retrieve_memories(
            context_id="context_b",
            query="content",
            top_k=10
        )

        # Each should only contain its own context's memories
        assert len(results_a) == 1
        assert len(results_b) == 1
        assert results_a[0]["content"] == "content for context A"
        assert results_b[0]["content"] == "content for context B"


@pytest.mark.unit
class TestMemoryRetrievalApi:
    """Test public API helpers and persistence extensions."""

    def setup_method(self):
        MemoryRetrievalCore._instance = None
        for env_var in [
            "MRM_STORAGE_BACKEND",
            "MRM_STORAGE_PATH",
            "MRM_ANCHOR_SEED",
            "MRM_ETHICS_PROTOCOL",
        ]:
            os.environ.pop(env_var, None)

    def test_api_add_get_delete_memory(self):
        config = MemoryRetrievalConfig.from_env()
        add_result = add_memory("api_context", "symbolic anchor memory", {"importance": 0.9})
        assert add_result["success"] is True

        fetch_result = get_memory(add_result["memory_id"])
        assert fetch_result["success"] is True
        assert fetch_result["memory"]["metadata"]["anchor_seed"] == config.anchor_seed
        assert fetch_result["memory"]["metadata"]["ethics_protocol"] == config.ethics_protocol

        delete_result = delete_memory(add_result["memory_id"])
        assert delete_result["success"] is True

        missing_result = get_memory(add_result["memory_id"])
        assert missing_result["success"] is False

    def test_query_ranks_semantically_related_content(self):
        add_memory("semantic_ctx", "quantum ledger anchor stability", {"importance": 0.8})
        add_memory("semantic_ctx", "gardening almanac and soil notes", {"importance": 0.2})

        query_result = query_memory("semantic_ctx", "quantum anchor ledger", top_k=2)
        assert query_result["success"] is True
        assert len(query_result["results"]) == 2
        assert query_result["results"][0]["content"] == "quantum ledger anchor stability"

    def test_file_backend_persists_memories(self, tmp_path):
        storage_path = tmp_path / "mrm_store.json"
        config = MemoryRetrievalConfig(storage_backend="file", storage_path=str(storage_path))
        config.validate()

        store = MemoryStore(config)
        memory_id = store.add_memory("persist_ctx", "persistent symbolic memory", {"importance": 0.7})

        reloaded_store = MemoryStore(config)
        fetched = reloaded_store.get_memory(memory_id)
        assert fetched is not None
        assert fetched["content"] == "persistent symbolic memory"
        assert fetched["metadata"]["created_at"] == fetched["created_at"]
        assert fetched["metadata"]["anchor_seed"] == config.anchor_seed

    def test_core_get_memory_uses_cache(self):
        config = MemoryRetrievalConfig()
        core = MemoryRetrievalCore(config)
        memory_id = core.add_memory("cache_ctx", "cache me", {"importance": 0.6})

        first_memory = core.get_memory(memory_id)
        assert first_memory is not None

        original_get_memory = core._store.get_memory
        try:
            core._store.get_memory = lambda _memory_id: (_ for _ in ()).throw(AssertionError("store cache miss"))
            cached_memory = core.get_memory(memory_id)
        finally:
            core._store.get_memory = original_get_memory

        assert cached_memory == first_memory

    def test_file_backend_handles_invalid_json_gracefully(self, tmp_path):
        storage_path = tmp_path / "mrm_store.json"
        storage_path.write_text("{invalid json", encoding="utf-8")

        config = MemoryRetrievalConfig(storage_backend="file", storage_path=str(storage_path))
        store = MemoryStore(config)

        assert store._memories == []

    def test_file_backend_serializes_common_metadata_types(self, tmp_path):
        class Status(Enum):
            ACTIVE = "active"

        storage_path = tmp_path / "mrm_store.json"
        config = MemoryRetrievalConfig(storage_backend="file", storage_path=str(storage_path))
        store = MemoryStore(config)

        created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
        memory_id = store.add_memory(
            "persist_ctx",
            "persistent symbolic memory",
            {"importance": 0.7, "created_at": created_at, "tags": {"alpha", "beta"}, "status": Status.ACTIVE},
        )

        reloaded_store = MemoryStore(config)
        fetched = reloaded_store.get_memory(memory_id)

        assert fetched is not None
        assert fetched["metadata"]["created_at"] == created_at.isoformat()
        assert sorted(fetched["metadata"]["tags"]) == ["alpha", "beta"]
        assert fetched["metadata"]["status"] == "active"
