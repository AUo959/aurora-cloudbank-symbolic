# Python SDK Technical Specification

**Project:** Aurora CloudBank Symbolic Python SDK
**Version:** 0.1.0
**Date:** 2025-11-09
**Status:** Design

---

## 1. Overview

The Aurora Python SDK provides a pythonic interface to the Aurora CloudBank Symbolic API, enabling developers to interact with quantum simulations, memory management, thread transfer bridges, and decision intelligence tools.

### 1.1 Goals

- **Simplicity:** Intuitive API that follows Python conventions
- **Type Safety:** Full type hints and runtime validation
- **Async First:** Native async/await support with sync wrapper
- **Developer Experience:** Clear errors, good documentation, helpful defaults
- **Performance:** Efficient HTTP handling, connection pooling, caching
- **Reliability:** Automatic retries, circuit breakers, timeout handling

### 1.2 Non-Goals

- Synchronous-only API (async is primary, sync is convenience wrapper)
- CLI tools (separate package: `aurora-cli`)
- Web framework integrations (separate packages)

---

## 2. Architecture

### 2.1 Package Structure

```
aurora-sdk/
├── src/
│   └── aurora_sdk/
│       ├── __init__.py              # Public API exports
│       ├── __version__.py           # Version info
│       ├── client.py                # AuroraClient
│       ├── config.py                # Configuration
│       ├── exceptions.py            # Custom exceptions
│       │
│       ├── models/                  # Pydantic models
│       │   ├── __init__.py
│       │   ├── base.py              # Base model classes
│       │   ├── quantum.py           # Quantum models
│       │   ├── memory.py            # Memory models
│       │   ├── thread_bridge.py    # Thread bridge models
│       │   ├── decision.py          # Decision models
│       │   └── common.py            # Common/shared models
│       │
│       ├── resources/               # API resource clients
│       │   ├── __init__.py
│       │   ├── base.py              # Base resource
│       │   ├── quantum.py           # QuantumResource
│       │   ├── memory.py            # MemoryResource
│       │   ├── thread_bridge.py    # ThreadBridgeResource
│       │   └── decision.py          # DecisionResource
│       │
│       ├── transport/               # HTTP/WebSocket layer
│       │   ├── __init__.py
│       │   ├── http.py              # HTTP client
│       │   ├── websocket.py         # WebSocket client
│       │   ├── retry.py             # Retry logic
│       │   └── auth.py              # Authentication
│       │
│       └── utils/
│           ├── __init__.py
│           ├── pagination.py        # Pagination helpers
│           ├── cache.py             # Response caching
│           └── logging.py           # Logging setup
│
├── tests/
│   ├── unit/                        # Unit tests
│   ├── integration/                 # Integration tests
│   └── conftest.py                  # Pytest configuration
│
├── examples/                        # Usage examples
├── docs/                            # Sphinx documentation
├── pyproject.toml                   # Project metadata
├── README.md
└── LICENSE
```

### 2.2 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    AuroraClient                          │
│  - config: Config                                        │
│  - quantum: QuantumResource                              │
│  - memory: MemoryResource                                │
│  - thread_bridge: ThreadBridgeResource                   │
│  - decision: DecisionResource                            │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼─────────┐   ┌────────▼──────────┐
│  Resources       │   │  Transport        │
│  - quantum       │   │  - HTTPTransport  │
│  - memory        │   │  - WSTransport    │
│  - thread_bridge │   │  - RetryPolicy    │
│  - decision      │   │  - Auth           │
└────────┬─────────┘   └───────────────────┘
         │
         │
┌────────▼─────────┐
│  Models          │
│  - Pydantic      │
│  - Validation    │
│  - Serialization │
└──────────────────┘
```

---

## 3. Core Components

### 3.1 AuroraClient

**Purpose:** Main entry point for SDK, manages configuration and resources.

**Interface:**

```python
from typing import Optional
from aurora_sdk.config import Config

class AuroraClient:
    """Main client for Aurora CloudBank Symbolic API.

    Examples:
        >>> client = AuroraClient(api_key="sk_test_...")
        >>> result = await client.quantum.run_scenario("supply_chain")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        max_retries: int = 3,
        config: Optional[Config] = None
    ):
        """Initialize Aurora client.

        Args:
            api_key: API key for authentication. If not provided, reads from
                AURORA_API_KEY environment variable.
            base_url: Base URL for API. Defaults to localhost.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            config: Custom configuration object. If provided, other params ignored.

        Raises:
            AuthenticationError: If no API key provided or found.
        """

    @property
    def quantum(self) -> QuantumResource:
        """Access quantum simulation operations."""

    @property
    def memory(self) -> MemoryResource:
        """Access memory management operations."""

    @property
    def thread_bridge(self) -> ThreadBridgeResource:
        """Access thread transfer bridge operations."""

    @property
    def decision(self) -> DecisionResource:
        """Access decision intelligence operations."""

    async def close(self) -> None:
        """Close client and cleanup resources."""

    async def __aenter__(self) -> "AuroraClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args) -> None:
        """Async context manager exit."""
        await self.close()
```

**Usage:**

```python
# Basic usage
client = AuroraClient(api_key="sk_test_...")
result = await client.quantum.run_scenario("supply_chain")

# Context manager
async with AuroraClient(api_key="sk_test_...") as client:
    result = await client.quantum.run_scenario("supply_chain")

# Custom configuration
config = Config(
    api_key="sk_test_...",
    base_url="https://api.aurora.example.com",
    timeout=60.0,
    max_retries=5
)
client = AuroraClient(config=config)
```

---

### 3.2 Config

**Purpose:** Centralized configuration management with environment variable support.

**Interface:**

```python
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass
class Config:
    """Configuration for Aurora SDK.

    Attributes:
        api_key: API key for authentication
        base_url: Base URL for API
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        cache_ttl: Cache TTL in seconds (0 = disabled)
        log_level: Logging level
    """

    api_key: str
    base_url: str = "http://localhost:8000"
    timeout: float = 30.0
    max_retries: int = 3
    cache_ttl: int = 0
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables.

        Environment variables:
            AURORA_API_KEY: API key
            AURORA_BASE_URL: Base URL
            AURORA_TIMEOUT: Request timeout
            AURORA_MAX_RETRIES: Max retries
            AURORA_CACHE_TTL: Cache TTL
            AURORA_LOG_LEVEL: Log level

        Args:
            env_file: Optional path to .env file

        Returns:
            Config instance
        """

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
```

**Usage:**

```python
# From environment
config = Config.from_env()

# From .env file
config = Config.from_env(env_file=Path(".env"))

# Programmatic
config = Config(
    api_key="sk_test_...",
    base_url="https://api.aurora.example.com",
    timeout=60.0
)
```

---

### 3.3 Resources

#### 3.3.1 QuantumResource

**Purpose:** Quantum simulation operations.

**Interface:**

```python
from typing import Literal, Optional, Callable, AsyncIterator
from aurora_sdk.models.quantum import (
    QuantumScenarioResult,
    QuantumCircuit,
    QuantumBackend,
    ScenarioType
)

class QuantumResource:
    """Quantum simulation operations."""

    async def run_scenario(
        self,
        scenario: ScenarioType,
        **params
    ) -> QuantumScenarioResult:
        """Run a quantum scenario simulation.

        Args:
            scenario: Scenario type (supply_chain, energy_grid, etc.)
            **params: Scenario-specific parameters

        Returns:
            Scenario execution result

        Raises:
            ValidationError: Invalid parameters
            ResourceNotFoundError: Invalid scenario type

        Examples:
            >>> result = await client.quantum.run_scenario(
            ...     "supply_chain_optimization",
            ...     num_suppliers=5,
            ...     demand_variance=0.2
            ... )
        """

    async def create_circuit(
        self,
        circuit_type: Literal["bell", "ghz", "custom"],
        num_qubits: Optional[int] = None,
        gates: Optional[list[dict]] = None,
        **params
    ) -> QuantumCircuit:
        """Create and simulate a quantum circuit.

        Args:
            circuit_type: Type of circuit
            num_qubits: Number of qubits (for custom circuits)
            gates: Gate operations (for custom circuits)
            **params: Additional parameters

        Returns:
            Circuit execution result
        """

    async def list_scenarios(self) -> list[str]:
        """List available quantum scenarios.

        Returns:
            List of scenario names
        """

    async def list_backends(self) -> list[QuantumBackend]:
        """List available quantum backends.

        Returns:
            List of backend configurations
        """

    async def stream_scenario(
        self,
        scenario: ScenarioType,
        callback: Callable[[dict], None],
        **params
    ) -> AsyncIterator[dict]:
        """Stream scenario execution via WebSocket.

        Args:
            scenario: Scenario type
            callback: Function called for each update
            **params: Scenario parameters

        Yields:
            Status updates during execution

        Examples:
            >>> async for update in client.quantum.stream_scenario(
            ...     "supply_chain",
            ...     callback=lambda u: print(f"Progress: {u['progress']}%")
            ... ):
            ...     print(update)
        """
```

#### 3.3.2 MemoryResource

**Purpose:** Memory management operations.

**Interface:**

```python
from typing import Optional, AsyncIterator, Literal
from aurora_sdk.models.memory import Memory, MemoryTier, MemoryStats

class MemoryResource:
    """Memory management operations."""

    async def create(
        self,
        content: str,
        tier: MemoryTier = "active",
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None
    ) -> Memory:
        """Create a new memory.

        Args:
            content: Memory content
            tier: Storage tier (active, compressed, archived)
            tags: Optional tags for categorization
            metadata: Optional metadata

        Returns:
            Created memory object

        Examples:
            >>> memory = await client.memory.create(
            ...     "User preferences for quantum algorithms",
            ...     tier="active",
            ...     tags=["preferences", "quantum"]
            ... )
        """

    async def get(self, memory_id: str) -> Memory:
        """Retrieve a memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory object

        Raises:
            ResourceNotFoundError: Memory not found
        """

    async def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        metadata: Optional[dict] = None
    ) -> Memory:
        """Update an existing memory.

        Args:
            memory_id: Memory identifier
            content: New content (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)

        Returns:
            Updated memory object
        """

    async def delete(self, memory_id: str) -> None:
        """Delete a memory.

        Args:
            memory_id: Memory identifier
        """

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

        Examples:
            >>> results = await client.memory.search(
            ...     "quantum algorithms",
            ...     top_k=5
            ... )
        """

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

        Examples:
            >>> async for memory in client.memory.list(tier="active"):
            ...     print(memory.content)
        """

    async def get_stats(self) -> MemoryStats:
        """Get memory system statistics.

        Returns:
            Memory statistics (counts, capacity, etc.)
        """
```

#### 3.3.3 ThreadBridgeResource

**Purpose:** Thread transfer bridge operations.

**Interface:**

```python
from typing import Optional
from aurora_sdk.models.thread_bridge import (
    Node,
    ClusterStatus,
    Repository,
    DriftPrediction
)

class ThreadBridgeResource:
    """Thread transfer bridge operations."""

    async def register_node(
        self,
        node_id: str,
        port: int,
        region: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Node:
        """Register a new node in the thread bridge cluster.

        Args:
            node_id: Unique node identifier
            port: Port number
            region: Geographic region
            metadata: Additional metadata

        Returns:
            Registered node
        """

    async def get_node(self, node_id: str) -> Node:
        """Get node information."""

    async def list_nodes(self) -> list[Node]:
        """List all registered nodes."""

    async def get_cluster_status(self) -> ClusterStatus:
        """Get cluster-wide status."""

    async def register_repository(
        self,
        repo_name: str,
        repo_url: str,
        branch: str = "main"
    ) -> Repository:
        """Register a repository for sync."""

    async def sync_repository(
        self,
        repo_name: str,
        force: bool = False
    ) -> dict:
        """Sync a registered repository."""

    async def predict_drift(
        self,
        node_id: str,
        horizon_hours: int = 24
    ) -> DriftPrediction:
        """Predict context drift for a node."""
```

#### 3.3.4 DecisionResource

**Purpose:** Decision intelligence operations.

**Interface:**

```python
from typing import Optional
from aurora_sdk.models.decision import (
    OracleResult,
    MonteCarloResult,
    ForecastResult
)

class DecisionResource:
    """Decision intelligence operations."""

    async def oracle(
        self,
        options: list[str],
        criteria: dict[str, float],
        monte_carlo_samples: int = 10000
    ) -> OracleResult:
        """Multi-criteria decision analysis.

        Args:
            options: List of options to evaluate
            criteria: Criteria weights (must sum to 1.0)
            monte_carlo_samples: Number of simulation samples

        Returns:
            Ranked options with confidence scores

        Examples:
            >>> result = await client.decision.oracle(
            ...     options=["Option A", "Option B", "Option C"],
            ...     criteria={"cost": 0.4, "risk": 0.3, "speed": 0.3}
            ... )
        """

    async def monte_carlo(
        self,
        config: dict,
        samples: int = 10000
    ) -> MonteCarloResult:
        """Run Monte Carlo simulation.

        Args:
            config: Simulation configuration
            samples: Number of samples

        Returns:
            Simulation results with statistics
        """

    async def forecast(
        self,
        data: list[float],
        periods: int,
        method: str = "arima"
    ) -> ForecastResult:
        """Time series forecasting.

        Args:
            data: Historical data points
            periods: Number of periods to forecast
            method: Forecasting method

        Returns:
            Forecast with confidence intervals
        """
```

---

### 3.4 Models

All models use Pydantic v2 for validation and serialization.

**Base Model:**

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AuroraBaseModel(BaseModel):
    """Base model for all Aurora SDK models."""

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True
    )

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump(mode="json")

    @classmethod
    def from_dict(cls, data: dict) -> "AuroraBaseModel":
        """Create from dictionary."""
        return cls.model_validate(data)
```

**Example Models:**

```python
from typing import Literal
from pydantic import Field

# Quantum models
class QuantumScenarioResult(AuroraBaseModel):
    """Result from quantum scenario execution."""

    scenario_id: str
    scenario_type: str
    status: Literal["pending", "running", "completed", "failed"]
    optimal_state: list[int]
    metrics: dict[str, float]
    execution_time: float = Field(description="Execution time in seconds")
    circuit_depth: Optional[int] = None
    qubit_count: Optional[int] = None

# Memory models
class Memory(AuroraBaseModel):
    """Memory object."""

    memory_id: str
    content: str
    tier: Literal["active", "compressed", "archived"]
    tags: list[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    attention_score: Optional[float] = None
    access_count: int = 0

# Thread Bridge models
class Node(AuroraBaseModel):
    """Thread bridge node."""

    node_id: str
    status: Literal["online", "offline", "syncing"]
    port: int
    region: Optional[str] = None
    last_heartbeat: datetime
    is_leader: bool = False

# Decision models
class OracleResult(AuroraBaseModel):
    """Decision oracle result."""

    ranked_options: list[dict]
    confidence_scores: dict[str, float]
    recommendation: str
    monte_carlo_samples: int
```

---

### 3.5 Transport Layer

**HTTPTransport:**

```python
from typing import Any, Optional
import httpx
from aurora_sdk.config import Config
from aurora_sdk.transport.retry import RetryPolicy

class HTTPTransport:
    """HTTP client with retry and error handling."""

    def __init__(self, config: Config):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=self._build_headers()
        )
        self.retry_policy = RetryPolicy(max_retries=config.max_retries)

    def _build_headers(self) -> dict[str, str]:
        """Build request headers."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": f"aurora-sdk-python/{VERSION}",
            "Content-Type": "application/json"
        }

    async def get(self, path: str, **kwargs) -> dict[str, Any]:
        """GET request with retry."""
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> dict[str, Any]:
        """POST request with retry."""
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> dict[str, Any]:
        """PUT request with retry."""
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> dict[str, Any]:
        """DELETE request with retry."""
        return await self._request("DELETE", path, **kwargs)

    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> dict[str, Any]:
        """Execute request with retry and error handling."""

        async def _execute():
            response = await self.client.request(method, path, **kwargs)

            # Handle errors
            if response.status_code >= 400:
                self._handle_error(response)

            return response.json()

        return await self.retry_policy.execute(_execute)

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle HTTP errors."""
        # Map status codes to exceptions
        # Raise appropriate exception

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
```

**RetryPolicy:**

```python
import asyncio
from typing import Callable, TypeVar, Any

T = TypeVar('T')

class RetryPolicy:
    """Exponential backoff retry policy."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    async def execute(self, func: Callable[[], Any]) -> T:
        """Execute function with retry."""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    delay = min(
                        self.initial_delay * (self.exponential_base ** attempt),
                        self.max_delay
                    )
                    await asyncio.sleep(delay)

        raise last_exception
```

---

### 3.6 Exceptions

```python
class AuroraError(Exception):
    """Base exception for Aurora SDK."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message)
        self.message = message
        self.kwargs = kwargs

class AuthenticationError(AuroraError):
    """Authentication failed."""
    pass

class AuthorizationError(AuroraError):
    """Authorization failed (insufficient permissions)."""
    pass

class RateLimitError(AuroraError):
    """Rate limit exceeded."""

    def __init__(self, message: str, retry_after: int):
        super().__init__(message)
        self.retry_after = retry_after

class ValidationError(AuroraError):
    """Request validation failed."""

    def __init__(self, message: str, details: dict):
        super().__init__(message)
        self.details = details

class ResourceNotFoundError(AuroraError):
    """Resource not found (404)."""
    pass

class ServerError(AuroraError):
    """Server error (5xx)."""
    pass

class NetworkError(AuroraError):
    """Network/connection error."""
    pass

class TimeoutError(AuroraError):
    """Request timeout."""
    pass
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

- Test each component in isolation
- Mock HTTP transport
- Cover edge cases and error conditions
- Target: >90% coverage

**Example:**

```python
import pytest
from unittest.mock import AsyncMock
from aurora_sdk import AuroraClient
from aurora_sdk.models.quantum import QuantumScenarioResult

@pytest.mark.asyncio
async def test_run_scenario():
    """Test quantum scenario execution."""
    client = AuroraClient(api_key="sk_test_123")

    # Mock transport
    client._quantum._transport.post = AsyncMock(return_value={
        "scenario_id": "scen_123",
        "scenario_type": "supply_chain",
        "status": "completed",
        "optimal_state": [1, 0, 1, 0, 1],
        "metrics": {"cost_reduction": 23.4},
        "execution_time": 1.24
    })

    result = await client.quantum.run_scenario(
        "supply_chain_optimization",
        num_suppliers=5
    )

    assert isinstance(result, QuantumScenarioResult)
    assert result.scenario_id == "scen_123"
    assert result.optimal_state == [1, 0, 1, 0, 1]
```

### 4.2 Integration Tests

- Test against live API (local dev server)
- Verify real API interactions
- Test error scenarios
- Run in CI against staging

### 4.3 Performance Tests

- Benchmark request overhead
- Test concurrent requests
- Measure memory usage
- Profile hot paths

---

## 5. Dependencies

```toml
[project]
dependencies = [
    "httpx>=0.28.0",          # Async HTTP client
    "pydantic>=2.5.0",        # Data validation
    "python-dotenv>=1.0.0",   # Environment variables
    "typing-extensions>=4.8.0", # Type hints backport
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.7.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
]
docs = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=2.0.0",
    "sphinx-autodoc-typehints>=1.25.0",
]
```

---

## 6. Versioning & Release

### 6.1 Semantic Versioning

- **Major:** Breaking API changes
- **Minor:** New features (backward compatible)
- **Patch:** Bug fixes

### 6.2 Deprecation Policy

- Deprecation warnings for 1 major version
- Clear migration guides
- Runtime warnings with upgrade path

### 6.3 Release Process

1. Update CHANGELOG.md
2. Bump version in `__version__.py`
3. Run full test suite
4. Build package: `python -m build`
5. Test on TestPyPI
6. Publish to PyPI: `twine upload dist/*`
7. Create GitHub release
8. Update documentation

---

## 7. Documentation

### 7.1 Code Documentation

- Docstrings for all public APIs (Google style)
- Type hints everywhere
- Usage examples in docstrings

### 7.2 User Documentation

- README with quickstart
- Sphinx-generated API reference
- Detailed guides for each resource
- Migration guides for upgrades

---

## 8. Security

### 8.1 API Key Handling

- Never log API keys
- Redact in error messages
- Support environment variables
- Warn if hardcoded in code

### 8.2 Input Validation

- Validate all inputs with Pydantic
- Sanitize user data
- Prevent injection attacks

### 8.3 HTTPS Only

- Enforce HTTPS in production
- Warn if using HTTP

---

## 9. Performance

### 9.1 Connection Pooling

- Reuse HTTP connections
- Configure pool size limits
- Connection timeout handling

### 9.2 Caching

- Optional response caching
- Configurable TTL
- Cache invalidation

### 9.3 Async Best Practices

- Concurrent request support
- Avoid blocking operations
- Proper resource cleanup

---

## 10. Open Questions

1. Should we support Python 3.10, or only 3.11+?
   - **Decision:** Support 3.11+ for modern type hints
2. Sync wrapper for blocking code?
   - **Decision:** Phase 2, focus on async first
3. WebSocket vs HTTP for streaming?
   - **Decision:** Support both, WebSocket preferred
4. Rate limit handling strategy?
   - **Decision:** Auto-retry with exponential backoff

---

## 11. Future Enhancements

- Sync wrapper (`AuroraSyncClient`)
- Response caching with Redis backend
- Request batching
- Circuit breaker pattern
- Metrics/telemetry integration
- GraphQL support

---

**Status:** Ready for Implementation
**Next Steps:** Create repository structure and implement core client
