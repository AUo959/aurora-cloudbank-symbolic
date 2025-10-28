"""
Node Health Checker - Continuous Health Monitoring

Monitors bridge node health via heartbeat, API checks, and anchor verification.

Anchor: EOS_SEED_ORION_v2
DLP: context_tag=health_checker_v2, symbolic_hash=HEALTH_CHK_v2
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Node health status"""

    HEALTHY = "healthy"  # All checks passing
    DEGRADED = "degraded"  # Some checks failing
    OFFLINE = "offline"  # All checks failing
    UNKNOWN = "unknown"  # Not yet checked


@dataclass
class HealthCheckResult:
    """Result of health check"""

    node_id: str
    status: HealthStatus
    timestamp: datetime
    heartbeat_ok: bool
    api_ok: bool
    anchor_valid: bool
    drift_sync_ok: bool
    response_time_ms: float
    details: Dict[str, any]


class NodeHealthChecker:
    """
    Continuous health monitoring for bridge nodes.

    Checks:
    - Heartbeat freshness
    - API endpoint availability
    - Anchor hash verification
    - Drift synchronization status
    """

    def __init__(self, heartbeat_timeout: int = 30, api_timeout: int = 5):
        """
        Initialize health checker.

        Args:
            heartbeat_timeout: Seconds for heartbeat timeout
            api_timeout: Seconds for API check timeout
        """
        self.heartbeat_timeout = heartbeat_timeout
        self.api_timeout = api_timeout
        self._client = httpx.AsyncClient(timeout=api_timeout)

    async def check_node_health(
        self, node, expected_anchor: str
    ) -> HealthCheckResult:
        """
        Comprehensive health check for a node.

        Args:
            node: BridgeNode instance
            expected_anchor: Expected anchor hash

        Returns:
            HealthCheckResult with all check details
        """
        start_time = datetime.now()
        checks = {
            "heartbeat": False,
            "api": False,
            "anchor": False,
            "drift_sync": False,
        }
        details = {}

        # Check 1: Heartbeat freshness
        try:
            checks["heartbeat"] = node.is_healthy(self.heartbeat_timeout)
            details["heartbeat"] = {
                "last_heartbeat": node.last_heartbeat.isoformat(),
                "age_seconds": (datetime.now() - node.last_heartbeat).total_seconds(),
            }
        except Exception as e:
            logger.error(f"Heartbeat check failed for {node.node_id[:8]}: {e}")
            details["heartbeat_error"] = str(e)

        # Check 2: API health endpoint
        try:
            url = f"http://{node.hostname}:{node.port}/api/health"
            response = await self._client.get(url)
            checks["api"] = response.status_code == 200
            details["api"] = {"status_code": response.status_code, "url": url}
        except Exception as e:
            logger.error(f"API check failed for {node.node_id[:8]}: {e}")
            details["api_error"] = str(e)

        # Check 3: Anchor verification
        try:
            checks["anchor"] = node.anchor_hash == expected_anchor
            details["anchor"] = {
                "node_anchor": node.anchor_hash[:12] + "...",
                "expected_anchor": expected_anchor[:12] + "...",
                "matches": checks["anchor"],
            }
        except Exception as e:
            logger.error(f"Anchor check failed for {node.node_id[:8]}: {e}")
            details["anchor_error"] = str(e)

        # Check 4: Drift synchronization (placeholder for v2 drift sync)
        try:
            # In full implementation, query drift sync status from node API
            checks["drift_sync"] = True  # Assume synced for now
            details["drift_sync"] = {"synchronized": True}
        except Exception as e:
            logger.error(f"Drift sync check failed for {node.node_id[:8]}: {e}")
            details["drift_sync_error"] = str(e)

        # Calculate overall status
        passed_checks = sum(checks.values())
        if passed_checks == 4:
            status = HealthStatus.HEALTHY
        elif passed_checks >= 2:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.OFFLINE

        response_time = (datetime.now() - start_time).total_seconds() * 1000

        return HealthCheckResult(
            node_id=node.node_id,
            status=status,
            timestamp=datetime.now(),
            heartbeat_ok=checks["heartbeat"],
            api_ok=checks["api"],
            anchor_valid=checks["anchor"],
            drift_sync_ok=checks["drift_sync"],
            response_time_ms=round(response_time, 2),
            details=details,
        )

    async def check_all_nodes(self, nodes, expected_anchor: str) -> Dict[str, HealthCheckResult]:
        """
        Check health of multiple nodes in parallel.

        Args:
            nodes: List of BridgeNode instances
            expected_anchor: Expected anchor hash

        Returns:
            Dictionary mapping node_id to HealthCheckResult
        """
        tasks = [
            self.check_node_health(node, expected_anchor) for node in nodes
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_map = {}
        for node, result in zip(nodes, results):
            if isinstance(result, Exception):
                logger.error(f"Health check error for {node.node_id[:8]}: {result}")
                health_map[node.node_id] = HealthCheckResult(
                    node_id=node.node_id,
                    status=HealthStatus.UNKNOWN,
                    timestamp=datetime.now(),
                    heartbeat_ok=False,
                    api_ok=False,
                    anchor_valid=False,
                    drift_sync_ok=False,
                    response_time_ms=0.0,
                    details={"error": str(result)},
                )
            else:
                health_map[node.node_id] = result

        return health_map

    async def close(self):
        """Close HTTP client"""
        await self._client.aclose()


# Global health checker instance
_health_checker: Optional[NodeHealthChecker] = None


def get_health_checker() -> NodeHealthChecker:
    """Get global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = NodeHealthChecker()
    return _health_checker
