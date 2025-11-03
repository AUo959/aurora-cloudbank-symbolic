# External Tool Connector SDK/Toolkit

## Overview

The Connector SDK provides templates, utilities, and best practices for developing custom connectors for the Aurora CloudBank External Tool Connector Framework.

## Connector Template

Use this template as a starting point for custom connectors:

```python
"""
[Service Name] Connector

Description of what this connector does and which service it integrates with.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from src.integrations.connectors import (
    BaseConnector,
    ConnectorConfig,
    ConnectorStatus,
)
from src.integrations.connectors.auth import AuthType, create_auth_provider
from src.integrations.connectors.circuit_breaker import CircuitBreaker
from src.integrations.connectors.pooling import RateLimiter
from src.integrations.connectors.retry import RetryPolicy

# Graceful import of required libraries
try:
    import httpx  # or other HTTP client
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class [ServiceName]Connector(BaseConnector):
    """
    [Service Name] API connector for R-2 agents.

    Provides methods to interact with [Service] API endpoints
    while maintaining Aurora's symbolic governance.
    """

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)

        # Initialize service-specific components
        self.base_url = config.metadata.get("base_url", "https://api.[service].com")
        self.api_version = config.metadata.get("api_version", "v1")

        # Authentication
        auth_type = config.metadata.get("auth_type", "bearer_token")
        self._auth_provider = create_auth_provider(
            AuthType(auth_type),
            config.auth_config or {}
        )

        # Resilience components
        self._rate_limiter = RateLimiter(
            requests_per_minute=config.rate_limit_rpm,
            name=f"[service]_{config.name}"
        )
        self._retry_policy = RetryPolicy(
            max_attempts=config.retry_attempts,
            backoff_factor=config.retry_backoff_factor,
            name=f"[service]_{config.name}"
        )
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_threshold,
            timeout_seconds=config.circuit_breaker_timeout,
            name=f"[service]_{config.name}"
        )

        # HTTP client (initialized on connect)
        self._client: Optional[Any] = None

    async def connect(self) -> bool:
        """Establish connection to [Service] API"""
        try:
            # Authenticate
            if not await self._auth_provider.authenticate():
                return False

            # Create HTTP client if available
            if HTTPX_AVAILABLE:
                self._client = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=self.config.timeout_seconds,
                    headers=self._get_default_headers()
                )

            self.status = ConnectorStatus.CONNECTED
            return True

        except Exception as e:
            self.status = ConnectorStatus.ERROR
            return False

    async def disconnect(self) -> bool:
        """Disconnect from [Service] API"""
        try:
            if self._client and HTTPX_AVAILABLE:
                await self._client.aclose()
                self._client = None

            self.status = ConnectorStatus.DISCONNECTED
            return True

        except Exception:
            return False

    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute [Service] API operation.

        Args:
            operation: Operation name
            parameters: Operation parameters

        Returns:
            Dict containing operation result with DLP metadata
        """
        # Validate operation
        if not await self.validate_operation(operation, parameters):
            return {
                "success": False,
                "error": "Operation validation failed",
                **self.get_dlp_metadata()
            }

        # Route to appropriate handler
        handlers = {
            "operation_1": self._operation_1,
            "operation_2": self._operation_2,
            # Add more operation handlers
        }

        handler = handlers.get(operation)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                **self.get_dlp_metadata()
            }

        try:
            # Execute with resilience patterns
            result = await self._execute_with_resilience(handler, parameters)
            return {
                "success": True,
                "operation": operation,
                "result": result,
                **self.get_dlp_metadata()
            }

        except Exception as e:
            return {
                "success": False,
                "operation": operation,
                "error": str(e),
                **self.get_dlp_metadata()
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on [Service] connection"""
        if not self._client and not HTTPX_AVAILABLE:
            return {
                "status": "degraded",
                "message": "HTTP client not available, using mock mode",
                "timestamp": datetime.utcnow().isoformat(),
            }

        try:
            # Simple API call to check connectivity
            if self._client:
                response = await self._client.get("/health")  # Adjust endpoint
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "timestamp": datetime.utcnow().isoformat(),
                    }

            return {
                "status": "healthy",
                "message": "Mock mode active",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        headers.update(self._auth_provider.get_auth_headers())
        return headers

    async def _execute_with_resilience(self, handler, parameters: Dict[str, Any]) -> Any:
        """Execute handler with rate limiting, retry, and circuit breaker"""
        # Rate limiting
        await self._rate_limiter.wait_for_token()

        # Circuit breaker and retry
        async def wrapped_call():
            return await self._retry_policy.execute(handler, parameters)

        return await self._circuit_breaker.call(wrapped_call)

    # Add your operation handler methods here
    async def _operation_1(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle operation 1"""
        # Validate required parameters
        required = ["param1", "param2"]
        for param in required:
            if param not in parameters:
                raise ValueError(f"Missing required parameter: {param}")

        # Make API call
        if self._client:
            response = await self._client.get(
                "/endpoint",
                params=parameters
            )
            response.raise_for_status()
            return response.json()

        # Mock response
        return {"mock": True, "data": "mock_data"}

    async def _operation_2(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle operation 2"""
        # Implementation
        pass
```

## Checklist for Custom Connectors

When developing a custom connector, ensure:

### Required Implementation
- [ ] Inherit from `BaseConnector`
- [ ] Implement `connect()` method
- [ ] Implement `disconnect()` method
- [ ] Implement `execute()` method with operation routing
- [ ] Implement `health_check()` method
- [ ] Handle authentication properly

### Aurora Integration
- [ ] Maintain DLP tracking via `get_dlp_metadata()`
- [ ] Include `context_tag` in all responses
- [ ] Preserve symbolic anchors (`anchor_seed`, `ethics_protocol`)
- [ ] Return `dlp_level` in metadata
- [ ] Use proper `ConnectorStatus` values

### Resilience
- [ ] Initialize `RateLimiter` with appropriate limits
- [ ] Initialize `RetryPolicy` for transient failures
- [ ] Initialize `CircuitBreaker` for fault tolerance
- [ ] Use `_execute_with_resilience()` pattern

### Error Handling
- [ ] Graceful degradation for missing dependencies
- [ ] Proper exception handling in all methods
- [ ] Return structured error responses
- [ ] Log errors with context

### Testing
- [ ] Unit tests for all operations
- [ ] Integration tests with real API (if possible)
- [ ] Mock mode for testing without credentials
- [ ] Test rate limiting behavior
- [ ] Test circuit breaker behavior
- [ ] Test health checks

### Documentation
- [ ] Docstrings for class and all methods
- [ ] Usage examples
- [ ] Configuration guide
- [ ] Required dependencies list
- [ ] Supported operations list

## Testing Template

```python
"""
Tests for [Service Name] Connector
"""

import pytest
from src.integrations.connectors import ConnectorConfig, ConnectorStatus
from src.integrations.connectors.builtin.[service]_connector import [ServiceName]Connector


@pytest.mark.unit
@pytest.mark.integration
class Test[ServiceName]Connector:
    """Test suite for [Service] connector"""

    def test_connector_initialization(self):
        """Test connector initialization"""
        config = ConnectorConfig(
            name="test",
            version="1.0.0",
            connector_type="[service]",
            auth_config={"token": "test_token"}
        )

        connector = [ServiceName]Connector(config)
        assert connector.status == ConnectorStatus.READY
        assert connector.connection_id is not None

    @pytest.mark.asyncio
    async def test_connector_lifecycle(self):
        """Test connect and disconnect"""
        config = ConnectorConfig(
            name="test",
            version="1.0.0",
            connector_type="[service]",
            auth_config={"token": "test_token"}
        )

        connector = [ServiceName]Connector(config)

        # Connect
        result = await connector.connect()
        assert result is True
        assert connector.status == ConnectorStatus.CONNECTED

        # Disconnect
        result = await connector.disconnect()
        assert result is True
        assert connector.status == ConnectorStatus.DISCONNECTED

    @pytest.mark.asyncio
    async def test_operation_execution(self):
        """Test operation execution"""
        config = ConnectorConfig(
            name="test",
            version="1.0.0",
            connector_type="[service]",
            auth_config={"token": "test_token"}
        )

        connector = [ServiceName]Connector(config)
        await connector.connect()

        # Execute operation
        result = await connector.execute("operation_1", {
            "param1": "value1",
            "param2": "value2"
        })

        assert result["success"] is True
        assert "result" in result
        assert "context_tag" in result
        assert result["dlp_level"] == "DLP_L1_OK"

        await connector.disconnect()

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check"""
        config = ConnectorConfig(
            name="test",
            version="1.0.0",
            connector_type="[service]",
            auth_config={"token": "test_token"}
        )

        connector = [ServiceName]Connector(config)
        await connector.connect()

        health = await connector.health_check()
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]

        await connector.disconnect()

    @pytest.mark.asyncio
    async def test_dlp_metadata(self):
        """Test DLP metadata tracking"""
        config = ConnectorConfig(
            name="test",
            version="1.0.0",
            connector_type="[service]",
            auth_config={"token": "test_token"}
        )

        connector = [ServiceName]Connector(config)
        dlp = connector.get_dlp_metadata()

        assert "context_tag" in dlp
        assert dlp["anchor_seed"] == "EOS_SEED_ORION"
        assert dlp["ethics_protocol"] == "Picard_Delta_3"
        assert dlp["dlp_level"] == "DLP_L1_OK"
```

## Configuration Examples

### Development Configuration

```python
from src.integrations.connectors import ConnectorConfig

dev_config = ConnectorConfig(
    name="[service]_dev",
    version="1.0.0",
    connector_type="[service]",
    auth_config={
        "token": "dev_token",
        # Or for API key:
        # "api_key": "dev_key",
        # "header_name": "X-API-Key"
    },
    rate_limit_rpm=60,  # Conservative for dev
    timeout_seconds=30,
    retry_attempts=3,
    metadata={
        "base_url": "https://api-dev.[service].com",
        "api_version": "v1",
        "environment": "development"
    }
)
```

### Production Configuration

```python
import os

prod_config = ConnectorConfig(
    name="[service]_prod",
    version="1.0.0",
    connector_type="[service]",
    auth_config={
        "token": os.getenv("[SERVICE]_TOKEN"),
    },
    rate_limit_rpm=5000,  # Match service limits
    timeout_seconds=60,
    retry_attempts=5,
    retry_backoff_factor=2.0,
    circuit_breaker_threshold=10,
    circuit_breaker_timeout=120,
    metadata={
        "base_url": "https://api.[service].com",
        "api_version": "v2",
        "environment": "production"
    },
    use_vault=True,  # Enable vault for secrets
    vault_path="/path/to/vault/secrets"
)
```

## Common Patterns

### Pagination Support

```python
async def _list_items_paginated(self, parameters: Dict[str, Any]) -> list:
    """List items with pagination support"""
    page = parameters.get("page", 1)
    per_page = parameters.get("per_page", 100)
    all_items = []

    while True:
        if self._client:
            response = await self._client.get(
                "/items",
                params={"page": page, "per_page": per_page}
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            all_items.extend(items)

            # Check if there are more pages
            if len(items) < per_page:
                break

            page += 1
        else:
            # Mock response
            break

    return all_items
```

### Batch Operations

```python
async def _batch_create(self, parameters: Dict[str, Any]) -> list:
    """Create multiple items in batches"""
    items = parameters.get("items", [])
    batch_size = parameters.get("batch_size", 10)
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]

        if self._client:
            response = await self._client.post(
                "/batch",
                json={"items": batch}
            )
            response.raise_for_status()
            results.extend(response.json())
        else:
            # Mock
            results.extend([{"id": j, "mock": True} for j in range(len(batch))])

        # Rate limiting between batches
        await self._rate_limiter.wait_for_token()

    return results
```

### Webhook Support

```python
async def register_webhook(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Register a webhook endpoint"""
    url = parameters.get("url")
    events = parameters.get("events", [])

    if not url:
        raise ValueError("Missing required parameter: url")

    if self._client:
        response = await self._client.post(
            "/webhooks",
            json={"url": url, "events": events}
        )
        response.raise_for_status()
        return response.json()

    # Mock
    return {"id": "webhook_123", "url": url, "events": events, "mock": True}
```

## Utilities

### Connector Builder Helper

```python
def build_connector_config(
    name: str,
    connector_type: str,
    auth_token: str,
    **kwargs
) -> ConnectorConfig:
    """
    Helper to build connector configuration with sensible defaults.

    Args:
        name: Connector name
        connector_type: Type of connector
        auth_token: Authentication token
        **kwargs: Additional config parameters

    Returns:
        ConnectorConfig instance
    """
    return ConnectorConfig(
        name=name,
        version=kwargs.get("version", "1.0.0"),
        connector_type=connector_type,
        auth_config={"token": auth_token},
        rate_limit_rpm=kwargs.get("rate_limit_rpm", 100),
        timeout_seconds=kwargs.get("timeout_seconds", 30),
        retry_attempts=kwargs.get("retry_attempts", 3),
        retry_backoff_factor=kwargs.get("retry_backoff_factor", 2.0),
        circuit_breaker_threshold=kwargs.get("circuit_breaker_threshold", 5),
        circuit_breaker_timeout=kwargs.get("circuit_breaker_timeout", 60),
        metadata=kwargs.get("metadata", {})
    )
```

## Next Steps

1. Copy the template and customize for your service
2. Implement required methods
3. Add service-specific operations
4. Write comprehensive tests
5. Document usage and configuration
6. Register connector type in registry
7. Test in development environment
8. Deploy to production

## Support

For questions or issues:
- Review the [Connector Framework Guide](./CONNECTOR_FRAMEWORK_GUIDE.md)
- Check existing connector implementations
- Create an issue in the repository
