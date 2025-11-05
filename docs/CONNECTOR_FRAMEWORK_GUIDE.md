# External Tool Connector Framework - Developer Guide

## Overview

The External Tool Connector Framework provides a flexible, Aurora-compatible architecture for R-2 agents to integrate with external tools, APIs, and services. The framework maintains Aurora's symbolic governance, DLP tracking, and ethical compliance while enabling seamless integration with external systems.

## Architecture

### Core Components

#### 1. BaseConnector
Abstract base class for all connectors with Aurora integration:
- DLP tracking with context tags
- T1/SRB anchor protocols
- Symbolic hash validation
- Async-first design
- Ethics validation

#### 2. ConnectorRegistry
Central discovery and registration system:
- Register connector types and instances
- Discover available connectors with filtering
- Manage connector lifecycle
- Track registry statistics

#### 3. Authentication Framework
Multiple authentication patterns:
- API Key authentication
- OAuth 2.0 flow
- Bearer token
- Basic HTTP auth
- Custom authentication

#### 4. Resilience Components
Fault-tolerant operation:
- **CircuitBreaker**: Prevent cascading failures
- **RateLimiter**: Token bucket rate limiting
- **RetryPolicy**: Exponential backoff with jitter
- **ConnectionPool**: Connection pooling and reuse

#### 5. HealthMonitor
Comprehensive health monitoring:
- Connector status tracking
- Performance metrics
- Health history
- System-wide health overview

## Quick Start

### Creating a Custom Connector

```python
from src.integrations.connectors import BaseConnector, ConnectorConfig, ConnectorStatus
from typing import Any, Dict

class MyCustomConnector(BaseConnector):
    """Custom connector for My Service"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        # Initialize custom components
        self.api_key = config.auth_config.get("api_key")
    
    async def connect(self) -> bool:
        """Establish connection"""
        try:
            # Perform connection logic
            self.status = ConnectorStatus.CONNECTED
            return True
        except Exception:
            self.status = ConnectorStatus.ERROR
            return False
    
    async def disconnect(self) -> bool:
        """Gracefully disconnect"""
        self.status = ConnectorStatus.DISCONNECTED
        return True
    
    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an operation"""
        if not await self.validate_operation(operation, parameters):
            return {
                "success": False,
                "error": "Validation failed",
                **self.get_dlp_metadata()
            }
        
        # Execute operation
        result = await self._perform_operation(operation, parameters)
        
        return {
            "success": True,
            "result": result,
            **self.get_dlp_metadata()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "status": "healthy" if self.status == ConnectorStatus.CONNECTED else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
```

### Registering and Using Connectors

```python
from src.integrations.connectors import connector_registry, ConnectorConfig

# Register connector type
connector_registry.register_connector_type("my_service", MyCustomConnector)

# Create configuration
config = ConnectorConfig(
    name="my_service_prod",
    version="1.0.0",
    connector_type="my_service",
    auth_config={"api_key": "your-api-key"},
    rate_limit_rpm=100,
    timeout_seconds=30,
    retry_attempts=3
)

# Create and register connector
connector = await connector_registry.create_connector("my_service", config)

# Connect and use
await connector.connect()
result = await connector.execute("some_operation", {"param": "value"})
await connector.disconnect()
```

### Using Built-in Connectors

```python
from src.integrations.connectors.builtin import GitHubConnector
from src.integrations.connectors import ConnectorConfig

# Configure GitHub connector
config = ConnectorConfig(
    name="github_prod",
    version="1.0.0",
    connector_type="github",
    auth_config={"token": "ghp_your_token"},
    rate_limit_rpm=5000,  # GitHub's rate limit
    metadata={
        "auth_type": "bearer_token",
        "base_url": "https://api.github.com"
    }
)

# Create and use
github = GitHubConnector(config)
await github.connect()

# Get repository info
repo_result = await github.execute("get_repository", {
    "owner": "AUo959",
    "repo": "aurora-cloudbank-symbolic"
})

# List issues
issues_result = await github.execute("list_issues", {
    "owner": "AUo959",
    "repo": "aurora-cloudbank-symbolic",
    "state": "open"
})

# Create issue
create_result = await github.execute("create_issue", {
    "owner": "AUo959",
    "repo": "aurora-cloudbank-symbolic",
    "title": "New feature request",
    "body": "Description of the feature"
})

await github.disconnect()
```

## Authentication

### API Key Authentication

```python
from src.integrations.connectors.auth import APIKeyAuth, AuthConfig, AuthType

config = AuthConfig(
    auth_type=AuthType.API_KEY,
    credentials={
        "api_key": "your-api-key",
        "header_name": "X-API-Key"  # Optional, defaults to X-API-Key
    }
)

auth = APIKeyAuth(config)
await auth.authenticate()
headers = auth.get_auth_headers()
```

### OAuth 2.0 Authentication

```python
from src.integrations.connectors.auth import OAuthAuth, AuthConfig, AuthType

config = AuthConfig(
    auth_type=AuthType.OAUTH,
    credentials={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret"
    },
    auto_refresh=True,
    refresh_threshold_seconds=300
)

auth = OAuthAuth(config)
await auth.authenticate()  # Performs OAuth flow
headers = auth.get_auth_headers()

# Auto-refresh when needed
if auth.needs_refresh():
    await auth.refresh()
```

### Bearer Token Authentication

```python
from src.integrations.connectors.auth import BearerTokenAuth, AuthConfig, AuthType

config = AuthConfig(
    auth_type=AuthType.BEARER_TOKEN,
    credentials={"token": "your-bearer-token"}
)

auth = BearerTokenAuth(config)
await auth.authenticate()
headers = auth.get_auth_headers()
```

## Resilience Patterns

### Circuit Breaker

```python
from src.integrations.connectors import CircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout_seconds=60,
    name="my_service_breaker"
)

async def risky_operation():
    # Operation that might fail
    pass

try:
    result = await circuit_breaker.call(risky_operation)
except Exception as e:
    print(f"Circuit breaker opened: {e}")

# Check status
status = circuit_breaker.get_status()
print(f"Circuit state: {status['state']}")
```

### Rate Limiting

```python
from src.integrations.connectors.pooling import RateLimiter

rate_limiter = RateLimiter(
    requests_per_minute=60,
    burst_size=100,
    name="api_limiter"
)

# Acquire token before making request
if await rate_limiter.acquire():
    # Make API call
    pass
else:
    # Rate limited, wait
    await rate_limiter.wait_for_token()
    # Make API call
```

### Retry with Exponential Backoff

```python
from src.integrations.connectors.retry import RetryPolicy

retry_policy = RetryPolicy(
    max_attempts=3,
    base_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    jitter=True
)

async def flaky_operation():
    # Operation that might fail transiently
    pass

result = await retry_policy.execute(flaky_operation)
```

## Health Monitoring

```python
from src.integrations.connectors.health import HealthMonitor

health_monitor = HealthMonitor()

# Check connector health
health_record = await health_monitor.check_connector_health(connector)

# Get current health status
current_health = health_monitor.get_connector_health(connector.connection_id)

# Get health history
history = health_monitor.get_connector_health_history(
    connector.connection_id,
    limit=10
)

# Get system-wide health
system_health = health_monitor.get_all_health_status()
```

## Aurora Integration

### DLP Tracking

All connectors automatically maintain DLP tracking:

```python
# Get DLP metadata
dlp_metadata = connector.get_dlp_metadata()
# Returns:
# {
#     "context_tag": "connector_abc123",
#     "connector_id": "uuid",
#     "symbolic_hash": "hash",
#     "anchor_seed": "EOS_SEED_ORION",
#     "ethics_protocol": "Picard_Delta_3",
#     "dlp_level": "DLP_L1_OK"
# }
```

### Symbolic Anchors

Connectors maintain symbolic anchors following Aurora patterns:

```python
# Access symbolic anchors
anchors = connector.symbolic_anchors
# Contains: context_tag, anchor_seed, ethics_protocol, connector_id, etc.
```

### Ethics Validation

Override `validate_operation` for custom ethics checks:

```python
async def validate_operation(self, operation: str, parameters: Dict[str, Any]) -> bool:
    # Custom validation logic
    if operation == "delete_all_data":
        return False  # Ethical violation
    
    return await super().validate_operation(operation, parameters)
```

## Best Practices

### 1. Error Handling
Always wrap connector operations in try/except blocks:

```python
try:
    result = await connector.execute("operation", params)
    if not result["success"]:
        # Handle operation failure
        pass
except Exception as e:
    # Handle connection/system failure
    pass
```

### 2. Resource Cleanup
Always disconnect connectors when done:

```python
try:
    await connector.connect()
    # Use connector
finally:
    await connector.disconnect()
```

Or use context managers (if implemented):

```python
async with connector:
    result = await connector.execute("operation", params)
```

### 3. Configuration Management
Store sensitive credentials securely:

```python
config = ConnectorConfig(
    name="production",
    version="1.0.0",
    connector_type="service",
    auth_config={"api_key": os.getenv("SERVICE_API_KEY")},
    use_vault=True,  # Enable vault integration
    vault_path="/path/to/secrets"
)
```

### 4. Monitoring
Regularly check connector health:

```python
# Periodic health check
async def monitor_connectors():
    while True:
        for connector in connectors:
            health = await health_monitor.check_connector_health(connector)
            if health["health_status"] != "healthy":
                # Alert or take action
                pass
        await asyncio.sleep(60)
```

### 5. Rate Limiting
Respect service rate limits:

```python
# Configure appropriate rate limits
config = ConnectorConfig(
    name="service",
    version="1.0.0",
    connector_type="service",
    rate_limit_rpm=100,  # Match service limits
    # ...
)
```

## Advanced Topics

### Custom Authentication Providers

Implement `AuthProvider` for custom auth:

```python
from src.integrations.connectors.auth import AuthProvider, AuthConfig

class CustomAuth(AuthProvider):
    async def authenticate(self) -> bool:
        # Custom authentication logic
        pass
    
    async def refresh(self) -> bool:
        # Custom refresh logic
        pass
    
    def get_auth_headers(self) -> Dict[str, str]:
        # Return custom headers
        pass
```

### Connector Versioning

Manage multiple connector versions:

```python
# Register different versions
connector_registry.register_connector_type("service_v1", ServiceConnectorV1)
connector_registry.register_connector_type("service_v2", ServiceConnectorV2)

# Create specific version
v1_connector = await connector_registry.create_connector("service_v1", config)
v2_connector = await connector_registry.create_connector("service_v2", config)
```

### Connector Discovery

Discover available connectors:

```python
# Get all connectors
all_connectors = connector_registry.discover_connectors()

# Filter by type
github_connectors = connector_registry.discover_connectors(
    filters={"type": "github"}
)

# Filter by status
active_connectors = connector_registry.discover_connectors(
    filters={"status": "connected"}
)
```

## Testing

### Unit Testing Connectors

```python
import pytest
from src.integrations.connectors import ConnectorConfig

@pytest.mark.asyncio
async def test_custom_connector():
    config = ConnectorConfig(
        name="test",
        version="1.0.0",
        connector_type="custom",
        auth_config={"api_key": "test_key"}
    )
    
    connector = MyCustomConnector(config)
    
    # Test connection
    assert await connector.connect()
    assert connector.status == ConnectorStatus.CONNECTED
    
    # Test operation
    result = await connector.execute("test_operation", {})
    assert result["success"]
    
    # Test disconnect
    assert await connector.disconnect()
```

### Integration Testing

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_github_integration():
    config = ConnectorConfig(
        name="test_github",
        version="1.0.0",
        connector_type="github",
        auth_config={"token": os.getenv("GITHUB_TOKEN")}
    )
    
    github = GitHubConnector(config)
    await github.connect()
    
    result = await github.execute("get_repository", {
        "owner": "octocat",
        "repo": "Hello-World"
    })
    
    assert result["success"]
    assert "result" in result
    
    await github.disconnect()
```

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Check network connectivity
   - Verify credentials
   - Check rate limits

2. **Circuit Breaker Open**
   - Wait for timeout period
   - Manually reset: `circuit_breaker.reset()`
   - Investigate root cause of failures

3. **Rate Limiting**
   - Adjust `rate_limit_rpm` in config
   - Implement request batching
   - Use connection pooling

4. **Authentication Failures**
   - Verify credentials are correct
   - Check token expiration
   - Enable auto-refresh for OAuth

## Support and Contributing

For issues or questions:
- Check existing issues in the repository
- Review this documentation
- Create a new issue with detailed information

For contributions:
- Follow Aurora's coding standards (120-char limit)
- Add tests for new connectors
- Update documentation
- Maintain DLP tracking and symbolic anchors
- Ensure graceful degradation
