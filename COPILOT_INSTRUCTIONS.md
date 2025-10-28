# Copilot Instructions: Memory Retrieval Module Implementation

## Overview

This document provides detailed implementation guidelines for the Memory Retrieval Module (MRM) after scaffolding. Follow these instructions to ensure consistency, quality, and compliance with AuroraOS standards.

## General Requirements

### Code Quality Standards

1. **Type Hints**: All function signatures must include type hints
   ```python
   def add_memory(context_id: str, content: str, metadata: dict) -> str:
       pass
   ```

2. **Docstrings**: Use clear docstrings for all public methods
   ```python
   def query_memory(context_id: str, query: str, top_k: int = 10) -> list:
       """
       Query memories by semantic similarity.
       
       Args:
           context_id: Context isolation identifier
           query: Search query string
           top_k: Number of top results to return
           
       Returns:
           List of (memory_id, score, content, metadata) tuples ordered by score
       """
       pass
   ```

3. **Error Handling**: Implement graceful error handling with informative messages
   ```python
   try:
       result = operation()
   except SpecificError as e:
       logger.error(f"Operation failed: {e}", extra={"context_tag": context_tag})
       return {"success": False, "error": str(e)}
   ```

4. **Logging**: Use structured logging with DLP context tags
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info("Memory added", extra={
       "context_tag": context_tag,
       "memory_id": memory_id,
       "dlp_tag": dlp_tag
   })
   ```

### Testing Requirements

1. **Coverage**: Aim for minimum 80% test coverage per module
2. **Test Types**: Include both unit tests and integration tests
3. **Test Structure**: Place tests in `tests/test_memory_retrieval.py`
4. **Markers**: Use pytest markers for selective execution
   ```python
   @pytest.mark.unit
   @pytest.mark.memory_retrieval
   async def test_add_memory():
       pass
   ```

## Module-Specific Guidelines

### Config Module (`modules/memory_retrieval/config.py`)

**Responsibilities:**
- Centralize all configurable parameters
- Load configuration from environment variables and files
- Provide safe defaults
- Validate configuration at startup

**Implementation Notes:**

1. **Use dataclasses or Pydantic** for configuration structure:
   ```python
   from dataclasses import dataclass
   from typing import Optional
   import os
   
   @dataclass
   class MemoryRetrievalConfig:
       vector_dimension: int = 384
       cache_ttl_seconds: int = 300
       storage_backend: str = "memory"
       storage_path: Optional[str] = None
       max_results: int = 10
       
       @classmethod
       def from_env(cls):
           """Load configuration from environment variables."""
           return cls(
               vector_dimension=int(os.getenv("MRM_VECTOR_DIM", 384)),
               cache_ttl_seconds=int(os.getenv("MRM_CACHE_TTL", 300)),
               # ... etc
           )
   ```

2. **Validation**: Validate all parameters and raise clear errors for invalid configs

3. **Environment Variables**: Prefix all env vars with `MRM_` to avoid conflicts

4. **Defaults**: Ensure all defaults enable the system to run without configuration

### Store Module (`modules/memory_retrieval/store.py`)

**Responsibilities:**
- Manage persistent memory storage
- Handle vector similarity search
- Support multiple backend implementations

**Implementation Notes:**

1. **Start Simple**: Initial implementation should use in-memory list with linear search
   ```python
   class MemoryStore:
       def __init__(self, config: MemoryRetrievalConfig):
           self._memories: List[dict] = []
           self._config = config
       
       def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
           """Add memory and return generated ID."""
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
   ```

2. **Embedding Generation**: Use simple sentence-transformers or mock embeddings initially
   ```python
   def _generate_embedding(self, text: str) -> List[float]:
       """Generate embedding vector for text."""
       # Initial: use mock or simple hash-based embeddings
       # Future: integrate sentence-transformers
       return [0.0] * self._config.vector_dimension
   ```

3. **Vector Similarity**: Implement cosine similarity for query matching
   ```python
   def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
       """Compute cosine similarity between two vectors."""
       import math
       dot_product = sum(a * b for a, b in zip(vec1, vec2))
       magnitude1 = math.sqrt(sum(a * a for a in vec1))
       magnitude2 = math.sqrt(sum(b * b for b in vec2))
       if magnitude1 == 0 or magnitude2 == 0:
           return 0.0
       return dot_product / (magnitude1 * magnitude2)
   ```

4. **Interface Design**: Design abstract interface to support future backends
   ```python
   class StorageBackend(ABC):
       @abstractmethod
       def add_memory(self, memory: dict) -> str:
           pass
       
       @abstractmethod
       def query_memory(self, context_id: str, query_embedding: List[float], top_k: int) -> list:
           pass
   ```

### Cache Module (`modules/memory_retrieval/cache.py`)

**Responsibilities:**
- Implement TTL-based caching
- Track genealogy (hits, misses, evictions)
- Maintain 60-80% hit rate target
- Provide statistics

**Implementation Notes:**

1. **TTL Implementation**: Use timestamp-based expiration
   ```python
   class MemoryCache:
       def __init__(self, config: MemoryRetrievalConfig):
           self._cache: Dict[str, dict] = {}
           self._stats = {"hits": 0, "misses": 0}
           self._config = config
       
       def get(self, cache_key: str) -> Optional[Any]:
           """Retrieve cached value if not expired."""
           if cache_key not in self._cache:
               self._stats["misses"] += 1
               return None
           
           entry = self._cache[cache_key]
           if time.time() > entry["expires_at"]:
               del self._cache[cache_key]
               self._stats["misses"] += 1
               return None
           
           self._stats["hits"] += 1
           entry["hits"] += 1
           return entry["value"]
   ```

2. **Cache Keys**: Use consistent key format
   ```python
   def _make_query_key(self, context_id: str, query: str, top_k: int) -> str:
       """Generate cache key for query."""
       query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
       return f"query:{context_id}:{query_hash}:{top_k}"
   ```

3. **Genealogy Tracking**: Record access patterns
   ```python
   def get_stats(self) -> dict:
       """Return cache statistics."""
       total = self._stats["hits"] + self._stats["misses"]
       hit_rate = self._stats["hits"] / total if total > 0 else 0.0
       return {
           "hits": self._stats["hits"],
           "misses": self._stats["misses"],
           "hit_rate": hit_rate,
           "size": len(self._cache),
       }
   ```

4. **Eviction**: Implement LRU or TTL-based eviction

### Core Module (`modules/memory_retrieval/core.py`)

**Responsibilities:**
- Orchestrate retrieval combining store and cache
- Compute multi-factor scores
- Integrate with AuMemManager and DLP
- Apply T1/SRB anchor protocols

**Implementation Notes:**

1. **Multi-Factor Scoring**: Combine relevance, importance, recency, cultural sensitivity
   ```python
   def _compute_score(self, memory: dict, query_embedding: List[float], weights: dict) -> float:
       """Compute final score from multiple factors."""
       relevance = self._cosine_similarity(memory["embedding"], query_embedding)
       importance = memory["metadata"].get("importance", 0.5)
       recency = self._compute_recency_score(memory["created_at"])
       cultural = memory["metadata"].get("cultural_score", 1.0)
       
       return (
           weights["relevance"] * relevance +
           weights["importance"] * importance +
           weights["recency"] * recency +
           weights["cultural"] * cultural
       )
   ```

2. **Recency Calculation**: Use exponential decay
   ```python
   def _compute_recency_score(self, created_at: str) -> float:
       """Calculate recency score with exponential decay."""
       from datetime import datetime
       import math
       
       created = datetime.fromisoformat(created_at)
       age_days = (datetime.now() - created).total_seconds() / 86400
       decay_rate = 0.1  # Configurable
       return math.exp(-decay_rate * age_days)
   ```

3. **DLP Integration**: Use NativeDLPTracker for all operations
   ```python
   from src.core.native_dlp_export import NativeDLPTracker
   
   def add_memory(self, context_id: str, content: str, metadata: dict) -> str:
       """Add memory with DLP tracking."""
       context_tag = f"mrm:add:{context_id}"
       tracker = NativeDLPTracker(context_tag=context_tag)
       
       # Add memory
       memory_id = self._store.add_memory(context_id, content, metadata)
       
       # Track in DLP
       tracker.track_operation("add_memory", {
           "memory_id": memory_id,
           "context_id": context_id,
       })
       
       return memory_id
   ```

4. **Graceful Degradation**: Handle optional AuMemManager import
   ```python
   try:
       from modules.aumemmanager import AuMemManager
       AUMEM_AVAILABLE = True
   except ImportError:
       AUMEM_AVAILABLE = False
       logger.warning("AuMemManager not available, using mock")
   ```

### API Module (`modules/memory_retrieval/api.py`)

**Responsibilities:**
- Expose Python function interface
- Define HTTP endpoint contracts (future)
- Handle input validation
- Maintain request/response logging

**Implementation Notes:**

1. **Function Interface**: Provide clean Python API
   ```python
   from typing import Optional
   
   def add_memory(context_id: str, content: str, metadata: Optional[dict] = None) -> dict:
       """
       Add a new memory to the retrieval system.
       
       Args:
           context_id: Context isolation identifier
           content: Memory content text
           metadata: Optional metadata dictionary
           
       Returns:
           {"success": bool, "memory_id": str, "context_tag": str}
       """
       try:
           core = MemoryRetrievalCore.get_instance()
           memory_id = core.add_memory(context_id, content, metadata or {})
           return {
               "success": True,
               "memory_id": memory_id,
               "context_tag": f"mrm:add:{context_id}",
           }
       except Exception as e:
           logger.error(f"Failed to add memory: {e}")
           return {
               "success": False,
               "error": str(e),
           }
   ```

2. **Input Validation**: Validate all inputs
   ```python
   def query_memory(context_id: str, query: str, top_k: int = 10) -> dict:
       """Query memories with validation."""
       if not context_id or not isinstance(context_id, str):
           return {"success": False, "error": "Invalid context_id"}
       
       if not query or not isinstance(query, str):
           return {"success": False, "error": "Invalid query"}
       
       if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
           return {"success": False, "error": "top_k must be between 1 and 100"}
       
       # Proceed with query...
   ```

3. **Future HTTP Endpoints**: Document endpoint structure for FastAPI integration
   ```python
   # Future FastAPI integration:
   # @router.post("/memory/add")
   # async def add_memory_endpoint(request: AddMemoryRequest):
   #     return add_memory(request.context_id, request.content, request.metadata)
   ```

4. **Singleton Pattern**: Use singleton for core instance
   ```python
   class MemoryRetrievalCore:
       _instance = None
       
       @classmethod
       def get_instance(cls):
           if cls._instance is None:
               config = MemoryRetrievalConfig.from_env()
               cls._instance = cls(config)
           return cls._instance
   ```

## DLP Compliance Checklist

For every public method that modifies state:
- [ ] Create context_tag following pattern `mrm:{operation}:{context_id}`
- [ ] Initialize NativeDLPTracker with context_tag
- [ ] Track operation with relevant parameters
- [ ] Include dlp_tag in return values and logs
- [ ] Generate export manifest for deliverables

## Integration with Existing Systems

### AuMemManager Integration
```python
# Optional integration - gracefully degrade if unavailable
try:
    from modules.aumemmanager import AuMemManager
    # Use AuMemManager for quantum memory features
except ImportError:
    # Fall back to standard memory management
    pass
```

### DLP Tracker Integration
```python
from src.core.native_dlp_export import NativeDLPTracker

tracker = NativeDLPTracker(context_tag=context_tag)
tracker.track_operation("operation_name", metadata)
manifest = tracker.create_export_manifest()
```

### Anchor Protocol Integration
```python
# Advance T1/SRB anchors with chain notation
t1_anchor = f"001//999//mrm:{operation}"
srb_anchor = f"symbolic_ref:{memory_id}"
```

## Testing Guidelines

### Unit Tests
```python
@pytest.mark.unit
@pytest.mark.memory_retrieval
async def test_add_memory():
    """Test adding a memory."""
    from modules.memory_retrieval.api import add_memory
    
    result = add_memory("test_context", "test content", {"importance": 0.8})
    assert result["success"] is True
    assert "memory_id" in result
    assert "context_tag" in result
```

### Integration Tests
```python
@pytest.mark.integration
@pytest.mark.memory_retrieval
async def test_end_to_end_retrieval():
    """Test complete add-query workflow."""
    # Add memories
    add_result = add_memory("ctx1", "Python programming tips")
    assert add_result["success"]
    
    # Query memories
    query_result = query_memory("ctx1", "Python coding", top_k=5)
    assert query_result["success"]
    assert len(query_result["results"]) > 0
```

## Adherence to Specification

- **Always reference** `docs/AURORA_MRM_SPEC_v0.1.md` for requirements
- **Follow milestone** `.github/milestones/M1_foundation.yml` for progress tracking
- **Use issue matrix** `GITHUB_ISSUE_MATRIX.yml` for task breakdown
- **Maintain consistency** with existing AuroraOS patterns and conventions

## Code Style

1. **Line Length**: Maximum 120 characters (Flake8 configured)
2. **Imports**: Group by stdlib, third-party, local; alphabetize within groups
3. **Naming**: snake_case for functions/variables, PascalCase for classes
4. **Async**: Use `async def` for I/O operations, mark tests with `asyncio_mode = "auto"`

## Review Checklist

Before submitting implementation:
- [ ] All type hints present
- [ ] Docstrings complete
- [ ] Tests written and passing
- [ ] DLP tags included
- [ ] Error handling implemented
- [ ] Logging with context tags
- [ ] Code passes `make lint-tools` (or `make check`)
- [ ] Integration verified with existing modules
- [ ] Documentation updated if needed
- [ ] No hardcoded values (use config)
