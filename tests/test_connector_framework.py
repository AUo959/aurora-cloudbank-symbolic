"""
Tests for External Tool Connector Framework

Validates connector architecture, registry, authentication,
and resilience patterns with Aurora's symbolic governance.
"""

import pytest
from datetime import datetime
from src.integrations.connectors import (
    BaseConnector,
    ConnectorConfig,
    ConnectorStatus,
    ConnectorRegistry,
    connector_registry,
)
from src.integrations.connectors.auth import (
    APIKeyAuth,
    AuthConfig,
    AuthType,
    create_auth_provider,
)
from src.integrations.connectors.circuit_breaker import CircuitBreaker, CircuitState
from src.integrations.connectors.health import HealthMonitor, HealthStatus
from src.integrations.connectors.pooling import RateLimiter, ConnectionPool
from src.integrations.connectors.retry import RetryPolicy
from typing import Any, Dict


# Mock connector for testing
class MockConnector(BaseConnector):
    """Mock connector for testing"""

    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self._connected = False
        self._operations = []

    async def connect(self) -> bool:
        self._connected = True
        self.status = ConnectorStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self._connected = False
        self.status = ConnectorStatus.DISCONNECTED
        return True

    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        self._operations.append((operation, parameters))
        return {
            "success": True,
            "operation": operation,
            "result": "mock_result",
            **self.get_dlp_metadata()
        }

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy" if self._connected else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }


@pytest.mark.unit
@pytest.mark.aurora
class TestConnectorFramework:
    """Test suite for connector framework"""

    def test_connector_config_creation(self):
        """Test connector configuration creation"""
        config = ConnectorConfig(
            name="test_connector",
            version="1.0.0",
            connector_type="test",
            rate_limit_rpm=100,
            timeout_seconds=30,
        )

        assert config.name == "test_connector"
        assert config.version == "1.0.0"
        assert config.connector_type == "test"
        assert config.rate_limit_rpm == 100
        assert config.anchor_seed == "EOS_SEED_ORION"
        assert config.ethics_protocol == "Picard_Delta_3"
        assert config.context_tag.startswith("connector_")

    @pytest.mark.asyncio
    async def test_base_connector_initialization(self):
        """Test base connector initialization with Aurora patterns"""
        config = ConnectorConfig(
            name="test",
            version="1.0.0",
            connector_type="mock"
        )

        connector = MockConnector(config)

        assert connector.status == ConnectorStatus.READY
        assert connector.connection_id is not None
        assert "context_tag" in connector.symbolic_anchors
        assert "symbolic_hash" in connector.symbolic_anchors
        assert connector.symbolic_anchors["anchor_seed"] == "EOS_SEED_ORION"
        assert connector.symbolic_anchors["ethics_protocol"] == "Picard_Delta_3"

    @pytest.mark.asyncio
    async def test_connector_lifecycle(self):
        """Test connector connection lifecycle"""
        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = MockConnector(config)

        # Initial state
        assert connector.status == ConnectorStatus.READY

        # Connect
        result = await connector.connect()
        assert result is True
        assert connector.status == ConnectorStatus.CONNECTED

        # Execute operation
        exec_result = await connector.execute("test_op", {"param": "value"})
        assert exec_result["success"] is True
        assert "context_tag" in exec_result
        assert exec_result["dlp_level"] == "DLP_L1_OK"

        # Disconnect
        result = await connector.disconnect()
        assert result is True
        assert connector.status == ConnectorStatus.DISCONNECTED

    @pytest.mark.asyncio
    async def test_connector_dlp_metadata(self):
        """Test DLP metadata tracking"""
        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = MockConnector(config)

        dlp_metadata = connector.get_dlp_metadata()

        assert "context_tag" in dlp_metadata
        assert "connector_id" in dlp_metadata
        assert "symbolic_hash" in dlp_metadata
        assert dlp_metadata["anchor_seed"] == "EOS_SEED_ORION"
        assert dlp_metadata["ethics_protocol"] == "Picard_Delta_3"
        assert dlp_metadata["dlp_level"] == "DLP_L1_OK"
        assert dlp_metadata["connector_name"] == "test"

    @pytest.mark.asyncio
    async def test_connector_capabilities(self):
        """Test connector capabilities reporting"""
        config = ConnectorConfig(
            name="test",
            version="1.0.0",
            connector_type="mock",
            rate_limit_rpm=100,
            metadata={"custom": "value"}
        )
        connector = MockConnector(config)

        capabilities = connector.get_capabilities()

        assert capabilities["name"] == "test"
        assert capabilities["version"] == "1.0.0"
        assert capabilities["type"] == "mock"
        assert capabilities["rate_limit"] == 100
        assert capabilities["metadata"]["custom"] == "value"
        assert "symbolic_anchors" in capabilities


@pytest.mark.unit
@pytest.mark.aurora
class TestConnectorRegistry:
    """Test suite for connector registry"""

    def test_registry_initialization(self):
        """Test registry initialization"""
        registry = ConnectorRegistry()
        status = registry.get_registry_status()

        assert status["total_connectors"] == 0
        assert status["total_connector_types"] == 0
        assert "context_tag" in status
        assert status["dlp_level"] == "DLP_L1_OK"

    def test_register_connector_type(self):
        """Test connector type registration"""
        registry = ConnectorRegistry()

        result = registry.register_connector_type("mock", MockConnector)
        assert result is True

        # Duplicate registration should fail
        result = registry.register_connector_type("mock", MockConnector)
        assert result is False

        status = registry.get_registry_status()
        assert status["total_connector_types"] == 1
        assert "mock" in status["registered_types"]

    @pytest.mark.asyncio
    async def test_create_connector(self):
        """Test connector creation through registry"""
        registry = ConnectorRegistry()
        registry.register_connector_type("mock", MockConnector)

        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = await registry.create_connector("mock", config)

        assert connector is not None
        assert isinstance(connector, MockConnector)
        assert connector.connection_id in registry.get_all_connectors()

    def test_register_connector_instance(self):
        """Test connector instance registration"""
        registry = ConnectorRegistry()
        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = MockConnector(config)

        result = registry.register_connector(connector)
        assert result is True

        # Duplicate registration should fail
        result = registry.register_connector(connector)
        assert result is False

    def test_get_connector(self):
        """Test connector retrieval"""
        registry = ConnectorRegistry()
        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = MockConnector(config)
        registry.register_connector(connector)

        retrieved = registry.get_connector(connector.connection_id)
        assert retrieved is connector

        # Non-existent connector
        retrieved = registry.get_connector("nonexistent")
        assert retrieved is None

    def test_unregister_connector(self):
        """Test connector unregistration"""
        registry = ConnectorRegistry()
        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = MockConnector(config)
        registry.register_connector(connector)

        result = registry.unregister_connector(connector.connection_id)
        assert result is True

        # Already unregistered
        result = registry.unregister_connector(connector.connection_id)
        assert result is False

    def test_discover_connectors(self):
        """Test connector discovery with filters"""
        registry = ConnectorRegistry()

        # Create multiple connectors
        for i in range(3):
            config = ConnectorConfig(name=f"test_{i}", version="1.0.0", connector_type="mock")
            connector = MockConnector(config)
            registry.register_connector(connector)

        # Discover all
        all_connectors = registry.discover_connectors()
        assert len(all_connectors) == 3

        # Filter by type
        mock_connectors = registry.discover_connectors(filters={"type": "mock"})
        assert len(mock_connectors) == 3


@pytest.mark.unit
@pytest.mark.security
class TestAuthentication:
    """Test suite for authentication framework"""

    @pytest.mark.asyncio
    async def test_api_key_auth(self):
        """Test API key authentication"""
        config = AuthConfig(
            auth_type=AuthType.API_KEY,
            credentials={"api_key": "test_key", "header_name": "X-Test-Key"}
        )

        auth = APIKeyAuth(config)
        assert await auth.authenticate() is True
        assert auth.is_authenticated() is True

        headers = auth.get_auth_headers()
        assert "X-Test-Key" in headers
        assert headers["X-Test-Key"] == "test_key"

    @pytest.mark.asyncio
    async def test_auth_metadata(self):
        """Test authentication metadata for DLP tracking"""
        config = AuthConfig(
            auth_type=AuthType.API_KEY,
            credentials={"api_key": "test_key"}
        )

        auth = APIKeyAuth(config)
        await auth.authenticate()

        metadata = auth.get_auth_metadata()
        assert "context_tag" in metadata
        assert metadata["auth_type"] == "api_key"
        assert metadata["authenticated"] is True
        assert metadata["dlp_level"] == "DLP_L1_OK"

    def test_create_auth_provider(self):
        """Test auth provider factory"""
        credentials = {"api_key": "test"}

        auth = create_auth_provider(AuthType.API_KEY, credentials)
        assert isinstance(auth, APIKeyAuth)


@pytest.mark.unit
@pytest.mark.aurora
class TestCircuitBreaker:
    """Test suite for circuit breaker pattern"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        circuit_breaker = CircuitBreaker(failure_threshold=3, name="test")

        async def successful_call():
            return "success"

        result = await circuit_breaker.call(successful_call)
        assert result == "success"
        assert circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures"""
        circuit_breaker = CircuitBreaker(failure_threshold=3, name="test")

        async def failing_call():
            raise Exception("Test failure")

        # Trigger failures
        for i in range(3):
            try:
                await circuit_breaker.call(failing_call)
            except Exception:
                pass

        # Circuit should be open
        assert circuit_breaker.state == CircuitState.OPEN

        # Further calls should be rejected
        with pytest.raises(Exception, match="Circuit breaker .* is OPEN"):
            await circuit_breaker.call(failing_call)

    def test_circuit_breaker_status(self):
        """Test circuit breaker status reporting"""
        circuit_breaker = CircuitBreaker(failure_threshold=5, name="test")

        status = circuit_breaker.get_status()
        assert status["name"] == "test"
        assert status["state"] == "closed"
        assert status["failure_threshold"] == 5
        assert "context_tag" in status
        assert status["dlp_level"] == "DLP_L1_OK"


@pytest.mark.unit
@pytest.mark.aurora
class TestRateLimiter:
    """Test suite for rate limiter"""

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire(self):
        """Test token acquisition"""
        limiter = RateLimiter(requests_per_minute=60, name="test")

        # Should be able to acquire tokens
        result = await limiter.acquire()
        assert result is True

    def test_rate_limiter_status(self):
        """Test rate limiter status reporting"""
        limiter = RateLimiter(requests_per_minute=100, burst_size=150, name="test")

        status = limiter.get_status()
        assert status["name"] == "test"
        assert status["requests_per_minute"] == 100
        assert status["burst_size"] == 150
        assert "context_tag" in status
        assert status["dlp_level"] == "DLP_L1_OK"


@pytest.mark.unit
@pytest.mark.aurora
class TestRetryPolicy:
    """Test suite for retry policy"""

    @pytest.mark.asyncio
    async def test_retry_successful_call(self):
        """Test retry with successful call"""
        retry_policy = RetryPolicy(max_attempts=3, base_delay=0.1, name="test")

        async def successful_call():
            return "success"

        result = await retry_policy.execute(successful_call)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_eventual_success(self):
        """Test retry with eventual success"""
        retry_policy = RetryPolicy(max_attempts=3, base_delay=0.1, name="test")

        call_count = {"count": 0}

        async def eventually_successful():
            call_count["count"] += 1
            if call_count["count"] < 3:
                raise Exception("Temporary failure")
            return "success"

        result = await retry_policy.execute(eventually_successful)
        assert result == "success"
        assert call_count["count"] == 3

    @pytest.mark.asyncio
    async def test_retry_all_failures(self):
        """Test retry with all attempts failing"""
        retry_policy = RetryPolicy(max_attempts=3, base_delay=0.1, name="test")

        async def always_fails():
            raise ValueError("Persistent failure")

        with pytest.raises(ValueError, match="Persistent failure"):
            await retry_policy.execute(always_fails)

    def test_retry_status(self):
        """Test retry policy status reporting"""
        retry_policy = RetryPolicy(max_attempts=3, base_delay=1.0, name="test")

        status = retry_policy.get_status()
        assert status["name"] == "test"
        assert status["max_attempts"] == 3
        assert status["base_delay"] == 1.0
        assert "context_tag" in status
        assert status["dlp_level"] == "DLP_L1_OK"


@pytest.mark.unit
@pytest.mark.aurora
class TestHealthMonitor:
    """Test suite for health monitor"""

    @pytest.mark.asyncio
    async def test_check_connector_health(self):
        """Test connector health check"""
        monitor = HealthMonitor()
        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = MockConnector(config)
        await connector.connect()

        health_record = await monitor.check_connector_health(connector)

        assert health_record["connector_name"] == "test"
        assert health_record["health_status"] in [s.value for s in HealthStatus]
        assert "timestamp" in health_record
        assert health_record["dlp_level"] == "DLP_L1_OK"

    @pytest.mark.asyncio
    async def test_health_history(self):
        """Test health history tracking"""
        monitor = HealthMonitor()
        config = ConnectorConfig(name="test", version="1.0.0", connector_type="mock")
        connector = MockConnector(config)
        await connector.connect()

        # Generate multiple health checks
        for _ in range(5):
            await monitor.check_connector_health(connector)

        history = monitor.get_connector_health_history(connector.connection_id, limit=3)
        assert len(history) == 3

    @pytest.mark.asyncio
    async def test_system_health_status(self):
        """Test system-wide health status"""
        monitor = HealthMonitor()

        # Create and monitor multiple connectors
        for i in range(3):
            config = ConnectorConfig(name=f"test_{i}", version="1.0.0", connector_type="mock")
            connector = MockConnector(config)
            await connector.connect()
            await monitor.check_connector_health(connector)

        system_health = monitor.get_all_health_status()

        assert system_health["total_connectors"] == 3
        assert "overall_health" in system_health
        assert "status_distribution" in system_health
        assert system_health["dlp_level"] == "DLP_L1_OK"


@pytest.mark.integration
@pytest.mark.aurora
class TestConnectorIntegration:
    """Integration tests for connector framework"""

    @pytest.mark.asyncio
    async def test_end_to_end_connector_usage(self):
        """Test complete connector lifecycle with all components"""
        # Setup registry
        registry = ConnectorRegistry()
        registry.register_connector_type("mock", MockConnector)

        # Create connector
        config = ConnectorConfig(
            name="integration_test",
            version="1.0.0",
            connector_type="mock",
            rate_limit_rpm=60,
            retry_attempts=3,
        )

        connector = await registry.create_connector("mock", config)
        assert connector is not None

        # Connect
        assert await connector.connect()

        # Health check
        monitor = HealthMonitor()
        health = await monitor.check_connector_health(connector)
        assert health["health_status"] == HealthStatus.HEALTHY.value

        # Execute operations
        result = await connector.execute("test_operation", {"test": "data"})
        assert result["success"] is True
        assert "context_tag" in result

        # Verify DLP tracking
        dlp = connector.get_dlp_metadata()
        assert dlp["connector_name"] == "integration_test"
        assert dlp["anchor_seed"] == "EOS_SEED_ORION"

        # Disconnect
        assert await connector.disconnect()

        # Verify status
        final_status = connector.status
        assert final_status == ConnectorStatus.DISCONNECTED
