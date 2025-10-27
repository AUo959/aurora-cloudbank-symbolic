# Aurora Memory Retrieval Module (MRM) Specification v0.1

## Purpose

The Memory Retrieval Module (MRM) provides context-aware memory retrieval for AuroraOS by indexing and retrieving memories using multi-factor scoring. The MRM enables the system to:

- Store and retrieve contextual memories with vector embeddings
- Score memories based on relevance, importance, recency, and cultural sensitivity
- Maintain DLP (Data Lineage Protocol) compliance throughout memory operations
- Provide efficient caching with genealogy tracking for optimal performance
- Support pluggable backend architectures for future extensibility

The MRM integrates with AuMemManager for quantum memory management and ensures all memory operations maintain T1/SRB anchor protocols.

## Requirements

### Functional Requirements

1. **Memory Storage**: Store memories with content, embeddings, metadata, and context identifiers
2. **Vector Similarity Search**: Query memories using semantic similarity via vector embeddings
3. **Multi-Factor Scoring**: Rank results by combining relevance, importance, recency, and cultural sensitivity
4. **Context Isolation**: Maintain separate memory spaces per context_id
5. **DLP Compliance**: Tag all operations with context tags and maintain symbolic validation
6. **API Interface**: Expose both internal Python functions and HTTP endpoints for memory operations

### Non-Functional Requirements

1. **Persistent Storage**: Support durable storage of memories across system restarts
2. **Pluggable Backends**: Architecture supports switching between in-memory, file-based, and vector DB backends
3. **TTL-Based Caching**: Implement time-to-live cache with 60-80% target hit rate
4. **Concurrency**: Handle concurrent read/write operations safely
5. **Security**: Validate inputs and maintain access control per context
6. **Test Coverage**: Minimum 80% code coverage with unit and integration tests
7. **Performance**: Query latency < 100ms for cached results, < 500ms for uncached

## Core Components

### Config Module (`config.py`)

**Responsibilities:**
- Centralize all configurable parameters
- Load configuration from environment variables and files
- Provide safe defaults for all settings
- Validate configuration at startup

**Key Configuration Parameters:**
- `VECTOR_DIMENSION`: Embedding vector size (default: 384)
- `CACHE_TTL_SECONDS`: Cache entry lifetime (default: 300)
- `STORAGE_BACKEND`: Backend type ('memory', 'file', 'vector_db')
- `STORAGE_PATH`: File path for persistent storage
- `MAX_RESULTS`: Maximum query results to return (default: 10)
- `SCORE_WEIGHTS`: Weighting factors for scoring components

### Store Module (`store.py`)

**Responsibilities:**
- Manage persistent vector index and metadata storage
- Handle memory addition and updates
- Execute vector similarity queries
- Provide abstract interface for multiple backend implementations

**Core Methods:**
```python
def add_memory(context_id: str, content: str, metadata: dict) -> str:
    """
    Add a new memory entry with auto-generated embedding.
    Returns: memory_id
    """

def query_memory(context_id: str, query: str, top_k: int) -> list:
    """
    Query memories by semantic similarity.
    Returns: List of (memory_id, score, content, metadata) tuples, ordered by score
    """

def get_memory(memory_id: str) -> dict:
    """
    Retrieve a specific memory by ID.
    Returns: Memory dict with all fields
    """

def delete_memory(memory_id: str) -> bool:
    """
    Remove a memory from storage.
    Returns: Success boolean
    """
```

**Backend Interface:**
- In-memory: List-based storage with linear search (initial implementation)
- File-based: JSON serialization with pickle for vectors
- Vector DB: Future integration with ChromaDB, Pinecone, or similar

### Cache Module (`cache.py`)

**Responsibilities:**
- Implement TTL-based caching of query results
- Track cache genealogy (hits, misses, evictions)
- Maintain target hit rate of 60-80%
- Provide cache statistics and monitoring

**Core Methods:**
```python
def get(cache_key: str) -> Optional[Any]:
    """
    Retrieve cached result if valid.
    Returns: Cached value or None
    """

def set(cache_key: str, value: Any, ttl: Optional[int] = None):
    """
    Store value in cache with TTL.
    """

def invalidate(pattern: str):
    """
    Invalidate cache entries matching pattern.
    """

def get_stats() -> dict:
    """
    Return cache statistics (hits, misses, hit_rate, size).
    """
```

**Cache Key Format:**
- Query cache: `query:{context_id}:{query_hash}:{top_k}`
- Memory cache: `memory:{memory_id}`

### Core Module (`core.py`)

**Responsibilities:**
- Orchestrate retrieval operations combining store and cache
- Compute multi-factor similarity scores
- Integrate with AuMemManager for DLP tagging
- Apply T1/SRB anchor protocols

**Scoring Algorithm:**
```
final_score = (
    w_relevance * cosine_similarity(query_embedding, memory_embedding) +
    w_importance * importance_score +
    w_recency * recency_score +
    w_cultural * cultural_sensitivity_score
)
```

**Score Components:**
- **Relevance**: Cosine similarity on embeddings (0-1)
- **Importance**: User-assigned or auto-calculated importance (0-1)
- **Recency**: Exponential decay based on age (0-1)
- **Cultural Sensitivity**: Context-specific cultural alignment (0-1)

**Core Methods:**
```python
def retrieve_memories(context_id: str, query: str, top_k: int = 10) -> list:
    """
    Main retrieval method combining cache, store, and scoring.
    Returns: Scored and ranked memory results
    """

def add_memory(context_id: str, content: str, metadata: dict) -> str:
    """
    Add memory with DLP tagging and anchor tracking.
    Returns: memory_id
    """
```

### API Module (`api.py`)

**Responsibilities:**
- Expose Python function interface for internal use
- Define HTTP endpoint contracts (future FastAPI integration)
- Handle input validation and error responses
- Maintain request/response logging with DLP tags

**Core Functions:**
```python
def add_memory(context_id: str, content: str, metadata: dict = None) -> dict:
    """
    Add a new memory.
    Returns: {"success": bool, "memory_id": str, "context_tag": str}
    """

def query_memory(context_id: str, query: str, top_k: int = 10) -> dict:
    """
    Query memories by content.
    Returns: {
        "success": bool,
        "results": [{"id": str, "score": float, "content": str, "metadata": dict}],
        "context_tag": str
    }
    """
```

**Future HTTP Endpoints:**
- `POST /memory/add` - Add new memory
- `GET /memory/query` - Query memories with parameters
- `GET /memory/{memory_id}` - Retrieve specific memory
- `DELETE /memory/{memory_id}` - Delete memory

## Data Structures

### Memory Entry
```python
{
    "id": str,                    # Unique identifier (UUID)
    "context_id": str,            # Context isolation identifier
    "content": str,               # Original text content
    "embedding": List[float],     # Vector embedding (dimension: 384)
    "metadata": {
        "created_at": str,        # ISO 8601 timestamp
        "importance": float,      # 0-1 importance score
        "tags": List[str],        # User-defined tags
        "source": str,            # Origin of memory
        "cultural_context": str,  # Cultural sensitivity marker
        "dlp_tag": str,          # Data Lineage Protocol tag
    },
    "t1_anchor": str,            # T1 temporal anchor
    "srb_anchor": str,           # SRB symbolic reference anchor
}
```

### Cache Entry
```python
{
    "key": str,                  # Cache key
    "value": Any,                # Cached data
    "ttl": int,                  # Time to live in seconds
    "created_at": float,         # Timestamp
    "hits": int,                 # Access count
}
```

### Retrieval Result
```python
{
    "id": str,                   # Memory ID
    "score": float,              # Combined relevance score (0-1)
    "content": str,              # Memory content
    "metadata": dict,            # Full metadata
    "score_breakdown": {
        "relevance": float,
        "importance": float,
        "recency": float,
        "cultural": float,
    }
}
```

## DLP and Anchor Integration

### DLP Tagging
All memory operations must include:
- `context_tag`: Identifies the operation context
- `symbolic_hash_validation`: Ensures data integrity
- Integration with `NativeDLPTracker` for export manifests

### Anchor Protocols
- **T1 Anchor**: Temporal tracking for memory lifecycle
- **SRB Anchor**: Symbolic reference base for memory relationships
- Anchors advance with each operation following chain notation (`001//999//`)

## Future Considerations

### Phase 2 Enhancements
1. **Custom Weighting**: User-configurable score component weights per query
2. **Cross-Project Retrieval**: Query across multiple context_id spaces
3. **Memory Clustering**: Group related memories automatically
4. **Incremental Updates**: Update embeddings without full recomputation
5. **Memory Decay**: Automatic archival of old, low-importance memories

### Plugin Architecture
1. **Embedding Providers**: Support multiple embedding models (sentence-transformers, OpenAI, etc.)
2. **Storage Backends**: ChromaDB, Pinecone, Weaviate, Qdrant integration
3. **Scoring Strategies**: Pluggable scoring algorithms
4. **Cache Backends**: Redis, Memcached support

### Performance Optimization
1. **Batch Operations**: Add/query multiple memories in single call
2. **Async API**: Non-blocking operations for high concurrency
3. **Index Optimization**: HNSW or similar for faster vector search
4. **Sharding**: Distribute memories across multiple storage nodes

### Advanced Features
1. **Memory Relationships**: Graph-based memory connections
2. **Temporal Queries**: Retrieve memories from specific time ranges
3. **Memory Summarization**: Compress older memories to save space
4. **Access Control**: Fine-grained permissions per context and user

## Implementation Guidelines

1. **Type Hints**: Use type hints for all function signatures
2. **Docstrings**: Document all public methods with parameters and return values
3. **Error Handling**: Graceful degradation with informative error messages
4. **Logging**: Structured logging with DLP context tags
5. **Testing**: Unit tests for each module, integration tests for workflows
6. **Code Style**: Follow Flake8 with 120-character line limit
7. **Async Pattern**: Use `async def` where appropriate for I/O operations

## Version History

- **v0.1** (2025-10-27): Initial specification
  - Core component definitions
  - Data structure specifications
  - API interface design
  - DLP and anchor integration requirements
