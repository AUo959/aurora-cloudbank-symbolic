"""
Base Connector Interface for External Tool Integration

Provides the foundational architecture for all external tool connectors,
maintaining Aurora's DLP tracking and symbolic governance protocols.
"""

import hashlib
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class ConnectorStatus(Enum):
    """Connector lifecycle status"""
    INITIALIZING = "initializing"
    READY = "ready"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SUSPENDED = "suspended"


@dataclass
class ConnectorConfig:
    """Configuration for external tool connectors"""
    name: str
    version: str
    connector_type: str
    auth_config: Optional[Dict[str, Any]] = None
    rate_limit_rpm: int = 60  # Requests per minute
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff_factor: float = 2.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Aurora-specific fields
    context_tag: str = field(default_factory=lambda: f"connector_{uuid.uuid4().hex[:8]}")
    anchor_seed: str = "EOS_SEED_ORION"
    ethics_protocol: str = "Picard_Delta_3"


class BaseConnector(ABC):
    """
    Abstract base class for all external tool connectors.

    Implements Aurora's canonical patterns:
    - DLP tracking with context tags
    - T1/SRB anchor protocols
    - Graceful degradation
    - Async-first design
    """

    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.status = ConnectorStatus.INITIALIZING
        self.connection_id = str(uuid.uuid4())
        self._initialize_symbolic_anchors()
        self.status = ConnectorStatus.READY

    def _initialize_symbolic_anchors(self):
        """Initialize symbolic anchors following Aurora canonical patterns"""
        self.symbolic_anchors = {
            "context_tag": self.config.context_tag,
            "anchor_seed": self.config.anchor_seed,
            "ethics_protocol": self.config.ethics_protocol,
            "connector_id": self.connection_id,
            "connector_name": self.config.name,
            "connector_type": self.config.connector_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._create_symbolic_hash()

    def _create_symbolic_hash(self) -> str:
        """Create symbolic hash for DLP validation"""
        hash_input = f"{self.symbolic_anchors['context_tag']}::{self.symbolic_anchors['connector_id']}::"
        hash_input += f"{self.symbolic_anchors['timestamp']}"
        symbolic_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        self.symbolic_anchors["symbolic_hash"] = symbolic_hash
        return symbolic_hash

    def get_dlp_metadata(self) -> Dict[str, Any]:
        """Get DLP tracking metadata for audit trails"""
        return {
            "context_tag": self.config.context_tag,
            "connector_id": self.connection_id,
            "connector_name": self.config.name,
            "connector_type": self.config.connector_type,
            "symbolic_hash": self.symbolic_anchors.get("symbolic_hash"),
            "anchor_seed": self.config.anchor_seed,
            "ethics_protocol": self.config.ethics_protocol,
            "status": self.status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dlp_level": "DLP_L1_OK",
        }

    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to external service.

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Gracefully disconnect from external service.

        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation on the external service.

        Args:
            operation: Operation name/identifier
            parameters: Operation parameters

        Returns:
            Dict containing operation result with DLP metadata
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the connector.

        Returns:
            Dict containing health status and metrics
        """
        pass

    async def validate_operation(self, operation: str, parameters: Dict[str, Any]) -> bool:
        """
        Validate operation against ethics protocol.

        Args:
            operation: Operation to validate
            parameters: Operation parameters

        Returns:
            bool: True if operation is ethical and valid
        """
        # Default implementation - override for specific validation logic
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get connector capabilities and metadata.

        Returns:
            Dict describing connector capabilities
        """
        return {
            "name": self.config.name,
            "version": self.config.version,
            "type": self.config.connector_type,
            "status": self.status.value,
            "connection_id": self.connection_id,
            "rate_limit": self.config.rate_limit_rpm,
            "timeout": self.config.timeout_seconds,
            "retry_attempts": self.config.retry_attempts,
            "metadata": self.config.metadata,
            "symbolic_anchors": self.symbolic_anchors,
        }
