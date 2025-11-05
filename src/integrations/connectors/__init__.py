"""
External Tool Connector Framework for Aurora CloudBank

This module provides a flexible connector architecture for R-2 agents to integrate
with external tools, APIs, and services while maintaining Aurora's symbolic governance
and DLP tracking protocols.
"""

from .base import BaseConnector, ConnectorConfig, ConnectorStatus
from .registry import ConnectorRegistry, connector_registry
from .auth import AuthProvider, AuthConfig, APIKeyAuth, OAuthAuth
from .health import HealthMonitor, HealthStatus
from .circuit_breaker import CircuitBreaker, CircuitState

__all__ = [
    "BaseConnector",
    "ConnectorConfig",
    "ConnectorStatus",
    "ConnectorRegistry",
    "connector_registry",
    "AuthProvider",
    "AuthConfig",
    "APIKeyAuth",
    "OAuthAuth",
    "HealthMonitor",
    "HealthStatus",
    "CircuitBreaker",
    "CircuitState",
]
