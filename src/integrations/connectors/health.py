"""
Health Monitor for External Tool Connectors

Provides comprehensive health monitoring and status tracking for
connectors with Aurora's DLP tracking and symbolic governance.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .base import BaseConnector, ConnectorStatus


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthMonitor:
    """
    Monitor health and performance of external tool connectors.

    Tracks connector status, performance metrics, and provides
    health checks following Aurora's observability patterns.
    """

    def __init__(self):
        self._health_records: Dict[str, List[Dict[str, Any]]] = {}
        self._current_status: Dict[str, HealthStatus] = {}
        self._context_tag = f"health_monitor_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    async def check_connector_health(self, connector: BaseConnector) -> Dict[str, Any]:
        """
        Perform health check on a connector.

        Args:
            connector: Connector to check

        Returns:
            Dict containing health status and metrics
        """
        try:
            # Get connector's own health check
            connector_health = await connector.health_check()

            # Determine overall health status
            health_status = self._determine_health_status(connector, connector_health)

            # Record health check
            health_record = {
                "connector_id": connector.connection_id,
                "connector_name": connector.config.name,
                "connector_type": connector.config.connector_type,
                "status": connector.status.value,
                "health_status": health_status.value,
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": connector_health,
                "dlp_level": "DLP_L1_OK",
            }

            # Store record
            if connector.connection_id not in self._health_records:
                self._health_records[connector.connection_id] = []
            self._health_records[connector.connection_id].append(health_record)

            # Update current status
            self._current_status[connector.connection_id] = health_status

            return health_record

        except Exception as e:
            return {
                "connector_id": connector.connection_id,
                "connector_name": connector.config.name,
                "status": "error",
                "health_status": HealthStatus.UNHEALTHY.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "dlp_level": "DLP_L1_OK",
            }

    def _determine_health_status(
        self,
        connector: BaseConnector,
        health_data: Dict[str, Any]
    ) -> HealthStatus:
        """
        Determine health status based on connector state and metrics.

        Args:
            connector: Connector instance
            health_data: Health check data from connector

        Returns:
            HealthStatus enum value
        """
        # Check connector status
        if connector.status == ConnectorStatus.ERROR:
            return HealthStatus.UNHEALTHY
        elif connector.status == ConnectorStatus.DISCONNECTED:
            return HealthStatus.UNHEALTHY
        elif connector.status == ConnectorStatus.SUSPENDED:
            return HealthStatus.DEGRADED

        # Check health data indicators
        if health_data.get("status") == "error":
            return HealthStatus.UNHEALTHY
        elif health_data.get("status") == "degraded":
            return HealthStatus.DEGRADED

        # Default to healthy if connected/ready
        if connector.status in [ConnectorStatus.CONNECTED, ConnectorStatus.READY]:
            return HealthStatus.HEALTHY

        return HealthStatus.UNKNOWN

    def get_connector_health(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """
        Get latest health status for a connector.

        Args:
            connector_id: ID of connector

        Returns:
            Latest health record or None
        """
        records = self._health_records.get(connector_id, [])
        return records[-1] if records else None

    def get_connector_health_history(
        self,
        connector_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get health history for a connector.

        Args:
            connector_id: ID of connector
            limit: Maximum number of records to return

        Returns:
            List of health records
        """
        records = self._health_records.get(connector_id, [])
        return records[-limit:]

    def get_all_health_status(self) -> Dict[str, Any]:
        """
        Get health status for all monitored connectors.

        Returns:
            Dict containing overall health status
        """
        status_counts = {
            HealthStatus.HEALTHY.value: 0,
            HealthStatus.DEGRADED.value: 0,
            HealthStatus.UNHEALTHY.value: 0,
            HealthStatus.UNKNOWN.value: 0,
        }

        for status in self._current_status.values():
            status_counts[status.value] += 1

        # Determine overall system health
        if status_counts[HealthStatus.UNHEALTHY.value] > 0:
            overall_status = HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED.value] > 0:
            overall_status = HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY.value] > 0:
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.UNKNOWN

        return {
            "context_tag": self._context_tag,
            "overall_health": overall_status.value,
            "total_connectors": len(self._current_status),
            "status_distribution": status_counts,
            "connector_statuses": {
                conn_id: status.value
                for conn_id, status in self._current_status.items()
            },
            "timestamp": datetime.utcnow().isoformat(),
            "dlp_level": "DLP_L1_OK",
        }

    def clear_history(self, connector_id: Optional[str] = None):
        """
        Clear health check history.

        Args:
            connector_id: Optional connector ID to clear. If None, clear all.
        """
        if connector_id:
            self._health_records.pop(connector_id, None)
            self._current_status.pop(connector_id, None)
        else:
            self._health_records.clear()
            self._current_status.clear()
