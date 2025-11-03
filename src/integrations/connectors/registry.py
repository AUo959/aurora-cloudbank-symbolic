"""
Connector Registry - Discovery and Registration System

Provides centralized registry for discovering, registering, and managing
external tool connectors with Aurora's symbolic governance.
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from .base import BaseConnector, ConnectorConfig, ConnectorStatus


class ConnectorRegistry:
    """
    Central registry for external tool connectors.

    Manages connector lifecycle, discovery, and symbolic tracking
    following Aurora's canonical patterns.
    """

    def __init__(self):
        self._connectors: Dict[str, BaseConnector] = {}
        self._connector_types: Dict[str, Type[BaseConnector]] = {}
        self._initialization_time = datetime.utcnow().isoformat()
        self._context_tag = f"registry_{hashlib.sha256(self._initialization_time.encode()).hexdigest()[:8]}"

    def register_connector_type(self, connector_type: str, connector_class: Type[BaseConnector]) -> bool:
        """
        Register a connector type for later instantiation.

        Args:
            connector_type: Unique type identifier
            connector_class: Connector class implementing BaseConnector

        Returns:
            bool: True if registration successful
        """
        if not issubclass(connector_class, BaseConnector):
            raise ValueError(f"Connector class must inherit from BaseConnector")

        if connector_type in self._connector_types:
            return False  # Already registered

        self._connector_types[connector_type] = connector_class
        return True

    def register_connector(self, connector: BaseConnector) -> bool:
        """
        Register an instantiated connector.

        Args:
            connector: Connector instance to register

        Returns:
            bool: True if registration successful
        """
        if connector.connection_id in self._connectors:
            return False  # Already registered

        self._connectors[connector.connection_id] = connector
        return True

    def unregister_connector(self, connector_id: str) -> bool:
        """
        Unregister a connector.

        Args:
            connector_id: Connector ID to unregister

        Returns:
            bool: True if unregistration successful
        """
        if connector_id not in self._connectors:
            return False

        del self._connectors[connector_id]
        return True

    def get_connector(self, connector_id: str) -> Optional[BaseConnector]:
        """
        Retrieve a connector by ID.

        Args:
            connector_id: Connector ID to retrieve

        Returns:
            BaseConnector instance or None if not found
        """
        return self._connectors.get(connector_id)

    def get_connectors_by_type(self, connector_type: str) -> List[BaseConnector]:
        """
        Get all connectors of a specific type.

        Args:
            connector_type: Type of connectors to retrieve

        Returns:
            List of matching connectors
        """
        return [
            conn for conn in self._connectors.values()
            if conn.config.connector_type == connector_type
        ]

    def get_all_connectors(self) -> Dict[str, BaseConnector]:
        """
        Get all registered connectors.

        Returns:
            Dict mapping connector IDs to connector instances
        """
        return self._connectors.copy()

    async def create_connector(self, connector_type: str, config: ConnectorConfig) -> Optional[BaseConnector]:
        """
        Create and register a new connector instance.

        Args:
            connector_type: Type of connector to create
            config: Configuration for the connector

        Returns:
            Newly created connector or None if type not registered
        """
        if connector_type not in self._connector_types:
            return None

        connector_class = self._connector_types[connector_type]
        connector = connector_class(config)
        self.register_connector(connector)
        return connector

    def discover_connectors(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Discover available connectors with optional filtering.

        Args:
            filters: Optional filters (status, type, etc.)

        Returns:
            List of connector metadata dicts
        """
        connectors = []
        for connector in self._connectors.values():
            metadata = connector.get_capabilities()

            # Apply filters if provided
            if filters:
                if "status" in filters and connector.status.value != filters["status"]:
                    continue
                if "type" in filters and connector.config.connector_type != filters["type"]:
                    continue

            connectors.append(metadata)

        return connectors

    def get_registry_status(self) -> Dict[str, Any]:
        """
        Get registry status and statistics.

        Returns:
            Dict containing registry status information
        """
        status_counts = {}
        for connector in self._connectors.values():
            status = connector.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        type_counts = {}
        for connector in self._connectors.values():
            conn_type = connector.config.connector_type
            type_counts[conn_type] = type_counts.get(conn_type, 0) + 1

        return {
            "context_tag": self._context_tag,
            "initialization_time": self._initialization_time,
            "total_connectors": len(self._connectors),
            "total_connector_types": len(self._connector_types),
            "registered_types": list(self._connector_types.keys()),
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "timestamp": datetime.utcnow().isoformat(),
            "dlp_level": "DLP_L1_OK",
        }


# Global connector registry instance
connector_registry = ConnectorRegistry()
