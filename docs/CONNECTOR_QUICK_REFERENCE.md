# External Tool Connector Framework - Quick Reference

## Table of Contents
- [Quick Start](#quick-start)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Install and Import
```python
from src.integrations.connectors import (
    BaseConnector,
    ConnectorConfig,
    ConnectorStatus,
    connector_registry,
)
```

### Create a Connector
```python
# Configure
config = ConnectorConfig(
    name="my_connector",
    version="1.0.0",
    connector_type="github",
    auth_config={"token": "your_token"}
)

# Create and connect
from src.integrations.connectors.builtin import GitHubConnector
connector = GitHubConnector(config)
await connector.connect()

# Use
result = await connector.execute("get_repository", {
    "owner": "user",
    "repo": "repo"
})

# Cleanup
await connector.disconnect()
```

## Common Patterns

### Pattern: Basic Connector Usage
```python
connector = MyConnector(config)
try:
    await connector.connect()
    result = await connector.execute("operation", params)
finally:
    await connector.disconnect()
```

### Pattern: With Health Monitoring
```python
from src.integrations.connectors.health import HealthMonitor

monitor = HealthMonitor()
health = await monitor.check_connector_health(connector)
if health["health_status"] == "healthy":
    result = await connector.execute("operation", params)
```

### Pattern: Registry-Based Creation
```python
connector_registry.register_connector_type("mytype", MyConnector)
connector = await connector_registry.create_connector("mytype", config)
```

### Pattern: Rate-Limited Operations
```python
from src.integrations.connectors.pooling import RateLimiter

limiter = RateLimiter(requests_per_minute=60)
await limiter.wait_for_token()
result = await connector.execute("operation", params)
```

### Pattern: Resilient Operations
```python
from src.integrations.connectors.retry import RetryPolicy
from src.integrations.connectors.circuit_breaker import CircuitBreaker

retry = RetryPolicy(max_attempts=3)
circuit = CircuitBreaker(failure_threshold=5)

async def safe_operation():
    result = await retry.execute(connector.execute, "op", params)
    return result

result = await circuit.call(safe_operation)
```

## API Reference

### BaseConnector
```python
class BaseConnector(ABC):
    async def connect() -> bool
    async def disconnect() -> bool
    async def execute(operation: str, parameters: Dict) -> Dict
    async def health_check() -> Dict
    async def validate_operation(operation: str, parameters: Dict) -> bool
    def get_dlp_metadata() -> Dict
    def get_capabilities() -> Dict
```

### ConnectorRegistry
```python
registry.register_connector_type(type: str, class: Type[BaseConnector]) -> bool
registry.register_connector(connector: BaseConnector) -> bool
registry.unregister_connector(connector_id: str) -> bool
registry.get_connector(connector_id: str) -> Optional[BaseConnector]
registry.get_connectors_by_type(type: str) -> List[BaseConnector]
registry.get_all_connectors() -> Dict[str, BaseConnector]
registry.create_connector(type: str, config: ConnectorConfig) -> Optional[BaseConnector]
registry.discover_connectors(filters: Optional[Dict]) -> List[Dict]
registry.get_registry_status() -> Dict
```

### AuthProvider
```python
class AuthProvider(ABC):
    async def authenticate() -> bool
    async def refresh() -> bool
    def get_auth_headers() -> Dict[str, str]
    def is_authenticated() -> bool
    def needs_refresh() -> bool
    def get_auth_metadata() -> Dict
```

### CircuitBreaker
```python
breaker = CircuitBreaker(
    failure_threshold=5,
    timeout_seconds=60,
    expected_exception=Exception,
    name="breaker"
)
result = await breaker.call(async_function, *args, **kwargs)
breaker.reset()
status = breaker.get_status()
```

### RateLimiter
```python
limiter = RateLimiter(
    requests_per_minute=60,
    burst_size=100,
    name="limiter"
)
acquired = await limiter.acquire(tokens=1)
await limiter.wait_for_token(tokens=1)
status = limiter.get_status()
limiter.reset()
```

### RetryPolicy
```python
retry = RetryPolicy(
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    jitter=True,
    name="retry"
)
result = await retry.execute(async_function, *args, **kwargs)
status = retry.get_status()
retry.reset()
```

### HealthMonitor
```python
monitor = HealthMonitor()
health_record = await monitor.check_connector_health(connector)
current_health = monitor.get_connector_health(connector_id)
history = monitor.get_connector_health_history(connector_id, limit=10)
system_health = monitor.get_all_health_status()
monitor.clear_history(connector_id=None)
```

## Configuration

### ConnectorConfig Options
```python
ConnectorConfig(
    name: str,                          # Required
    version: str,                       # Required
    connector_type: str,                # Required
    auth_config: Optional[Dict] = None, # Auth credentials
    rate_limit_rpm: int = 60,           # Requests per minute
    timeout_seconds: int = 30,          # Request timeout
    retry_attempts: int = 3,            # Max retry attempts
    retry_backoff_factor: float = 2.0,  # Backoff multiplier
    circuit_breaker_threshold: int = 5, # Failures before open
    circuit_breaker_timeout: int = 60,  # Seconds before reset
    metadata: Dict = {},                # Custom metadata
    context_tag: str = "auto",          # DLP context tag
    anchor_seed: str = "EOS_SEED_ORION",# Symbolic anchor
    ethics_protocol: str = "Picard_Delta_3" # Ethics protocol
)
```

### Environment Variables
```bash
# Example service token
export GITHUB_TOKEN="ghp_your_token_here"
export SLACK_TOKEN="xoxb-your-token"
export JIRA_TOKEN="your-jira-token"
```

### Config File Example
```yaml
# connector_config.yaml
connectors:
  github:
    name: github_prod
    version: "1.0.0"
    type: github
    auth:
      type: bearer_token
      token: ${GITHUB_TOKEN}
    rate_limit_rpm: 5000
    timeout_seconds: 30
    retry_attempts: 3

  slack:
    name: slack_prod
    version: "1.0.0"
    type: slack
    auth:
      type: bearer_token
      token: ${SLACK_TOKEN}
    rate_limit_rpm: 100
    timeout_seconds: 10
```

## Troubleshooting

### Issue: Connection Fails
```python
# Check status
print(f"Status: {connector.status}")
print(f"Connected: {connector._connected if hasattr(connector, '_connected') else 'N/A'}")

# Check authentication
auth_meta = connector._auth_provider.get_auth_metadata()
print(f"Authenticated: {auth_meta['authenticated']}")

# Check health
health = await connector.health_check()
print(f"Health: {health}")
```

### Issue: Rate Limited
```python
# Check rate limiter status
limiter_status = connector._rate_limiter.get_status()
print(f"Available tokens: {limiter_status['available_tokens']}")
print(f"Throttled requests: {limiter_status['throttled_requests']}")

# Increase rate limit
config.rate_limit_rpm = 120
```

### Issue: Circuit Breaker Open
```python
# Check circuit state
cb_status = connector._circuit_breaker.get_status()
print(f"Circuit state: {cb_status['state']}")
print(f"Failures: {cb_status['failure_count']}")

# Manual reset
connector._circuit_breaker.reset()
```

### Issue: Operations Failing
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check DLP metadata
dlp = connector.get_dlp_metadata()
print(f"DLP metadata: {dlp}")

# Validate operation
is_valid = await connector.validate_operation("op", params)
print(f"Operation valid: {is_valid}")
```

### Issue: Import Errors
```python
# Check optional dependencies
try:
    import httpx
    print("✅ httpx available")
except ImportError:
    print("❌ httpx not available - install with: pip install httpx")

# Connectors should work in mock mode without httpx
```

## Performance Tips

### 1. Connection Pooling
```python
from src.integrations.connectors.pooling import ConnectionPool

pool = ConnectionPool(max_connections=10)
conn_id = await pool.acquire()
# Use connection
await pool.release(conn_id)
```

### 2. Batch Operations
```python
# Instead of many single operations
for item in items:
    await connector.execute("create", {"item": item})

# Use batch operations
await connector.execute("batch_create", {"items": items})
```

### 3. Async Parallel Operations
```python
import asyncio

# Run multiple operations in parallel
results = await asyncio.gather(
    connector.execute("op1", params1),
    connector.execute("op2", params2),
    connector.execute("op3", params3),
)
```

### 4. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_config(name: str) -> ConnectorConfig:
    # Load and return config
    pass
```

## Security Best Practices

### 1. Never Hardcode Credentials
```python
# ❌ Bad
config = ConnectorConfig(
    name="service",
    auth_config={"token": "hardcoded_token"}
)

# ✅ Good
import os
config = ConnectorConfig(
    name="service",
    auth_config={"token": os.getenv("SERVICE_TOKEN")}
)
```

### 2. Use Vault for Secrets
```python
config = ConnectorConfig(
    name="service",
    use_vault=True,
    vault_path="/path/to/vault/secrets"
)
```

### 3. Validate Operations
```python
async def validate_operation(self, operation: str, parameters: Dict) -> bool:
    # Custom validation
    if operation == "delete_all":
        return False  # Prevent dangerous operations
    return await super().validate_operation(operation, parameters)
```

### 4. Monitor and Audit
```python
# Log all operations
result = await connector.execute("operation", params)
print(f"Operation: {result['operation']}")
print(f"Context: {result['context_tag']}")
print(f"DLP: {result['dlp_level']}")
```

## Quick Commands

```bash
# Run tests
pytest tests/test_connector_framework.py -v

# Run specific test
pytest tests/test_connector_framework.py::TestConnectorFramework::test_connector_lifecycle -v

# Run with markers
pytest -m unit tests/test_connector_framework.py
pytest -m integration tests/test_connector_framework.py

# Check imports
python -c "from src.integrations.connectors import BaseConnector; print('✅ OK')"

# Run example
python examples/connector_integration_example.py
```

## Additional Resources

- [Full Developer Guide](./CONNECTOR_FRAMEWORK_GUIDE.md)
- [SDK/Toolkit Guide](./CONNECTOR_SDK.md)
- [Example Integrations](../examples/connector_integration_example.py)
- [Test Suite](../tests/test_connector_framework.py)
- [GitHub Connector Source](../src/integrations/connectors/builtin/github_connector.py)
