"""
Rate Limiter and Connection Pool Management

Provides rate limiting and connection pooling for external service calls
with Aurora's DLP tracking and resource management protocols.
"""

import asyncio
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Optional


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Implements rate limiting to respect external service constraints
    while maintaining Aurora's observability standards.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        burst_size: Optional[int] = None,
        name: str = "rate_limiter"
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to rpm)
            name: Identifier for tracking
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.name = name

        # Token bucket implementation
        self._tokens = float(self.burst_size)
        self._last_update = time.time()
        self._lock = asyncio.Lock()

        # Tracking metrics
        self._total_requests = 0
        self._throttled_requests = 0
        self._context_tag = f"ratelimit_{name}"

    async def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens for making requests.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            bool: True if tokens acquired, False if rate limited
        """
        async with self._lock:
            self._total_requests += 1
            self._refill_tokens()

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            else:
                self._throttled_requests += 1
                return False

    async def wait_for_token(self, tokens: int = 1):
        """
        Wait until tokens are available.

        Args:
            tokens: Number of tokens needed
        """
        while not await self.acquire(tokens):
            await asyncio.sleep(0.1)

    def _refill_tokens(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self._last_update

        # Calculate tokens to add based on rate
        tokens_to_add = elapsed * (self.requests_per_minute / 60.0)
        self._tokens = min(self.burst_size, self._tokens + tokens_to_add)
        self._last_update = now

    def get_status(self) -> Dict[str, Any]:
        """
        Get rate limiter status.

        Returns:
            Dict containing status and metrics
        """
        self._refill_tokens()
        return {
            "context_tag": self._context_tag,
            "name": self.name,
            "requests_per_minute": self.requests_per_minute,
            "burst_size": self.burst_size,
            "available_tokens": self._tokens,
            "total_requests": self._total_requests,
            "throttled_requests": self._throttled_requests,
            "throttle_rate": (
                self._throttled_requests / self._total_requests
                if self._total_requests > 0 else 0
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dlp_level": "DLP_L1_OK",
        }

    def reset(self):
        """Reset rate limiter state"""
        self._tokens = float(self.burst_size)
        self._last_update = time.time()
        self._total_requests = 0
        self._throttled_requests = 0


class ConnectionPool:
    """
    Connection pool manager for external services.

    Manages connection pooling and reuse with Aurora's
    resource management and tracking protocols.
    """

    def __init__(
        self,
        max_connections: int = 10,
        min_connections: int = 2,
        max_idle_time: int = 300,
        name: str = "connection_pool"
    ):
        """
        Initialize connection pool.

        Args:
            max_connections: Maximum concurrent connections
            min_connections: Minimum maintained connections
            max_idle_time: Maximum idle time before closing (seconds)
            name: Pool identifier
        """
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.max_idle_time = max_idle_time
        self.name = name

        # Connection tracking
        self._active_connections: Dict[str, Any] = {}
        self._idle_connections: Deque[Dict[str, Any]] = deque()
        self._connection_count = 0
        self._lock = asyncio.Lock()

        # Metrics
        self._total_acquired = 0
        self._total_released = 0
        self._total_created = 0
        self._total_closed = 0
        self._context_tag = f"pool_{name}"

    async def acquire(self) -> Optional[str]:
        """
        Acquire a connection from the pool.

        Returns:
            Connection ID or None if pool exhausted
        """
        async with self._lock:
            self._total_acquired += 1

            # Try to reuse idle connection
            while self._idle_connections:
                conn = self._idle_connections.popleft()
                conn_id = conn["id"]

                # Check if connection is still valid
                if self._is_connection_valid(conn):
                    self._active_connections[conn_id] = conn
                    conn["acquired_at"] = datetime.now(timezone.utc)
                    return conn_id
                else:
                    # Connection expired, close it
                    self._total_closed += 1
                    self._connection_count -= 1

            # Create new connection if under limit
            if self._connection_count < self.max_connections:
                conn_id = await self._create_connection()
                return conn_id

            # Pool exhausted
            return None

    async def release(self, connection_id: str):
        """
        Release a connection back to the pool.

        Args:
            connection_id: ID of connection to release
        """
        async with self._lock:
            self._total_released += 1

            if connection_id not in self._active_connections:
                return

            conn = self._active_connections.pop(connection_id)
            conn["released_at"] = datetime.now(timezone.utc)

            # Return to idle pool if under max idle
            if len(self._idle_connections) < self.max_connections:
                self._idle_connections.append(conn)
            else:
                # Close connection if too many idle
                self._total_closed += 1
                self._connection_count -= 1

    async def _create_connection(self) -> str:
        """
        Create a new connection.

        Returns:
            Connection ID
        """
        conn_id = f"conn_{self._connection_count}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        conn = {
            "id": conn_id,
            "created_at": datetime.now(timezone.utc),
            "acquired_at": datetime.now(timezone.utc),
            "released_at": None,
        }

        self._active_connections[conn_id] = conn
        self._connection_count += 1
        self._total_created += 1

        return conn_id

    def _is_connection_valid(self, conn: Dict[str, Any]) -> bool:
        """
        Check if connection is still valid.

        Args:
            conn: Connection metadata

        Returns:
            bool: True if connection is valid
        """
        if not conn.get("released_at"):
            return True

        # Check idle time
        released_at = conn["released_at"]
        if isinstance(released_at, str):
            released_at = datetime.fromisoformat(released_at)

        idle_seconds = (datetime.now(timezone.utc) - released_at).total_seconds()
        return idle_seconds < self.max_idle_time

    def get_status(self) -> Dict[str, Any]:
        """
        Get connection pool status.

        Returns:
            Dict containing status and metrics
        """
        return {
            "context_tag": self._context_tag,
            "name": self.name,
            "max_connections": self.max_connections,
            "min_connections": self.min_connections,
            "total_connections": self._connection_count,
            "active_connections": len(self._active_connections),
            "idle_connections": len(self._idle_connections),
            "total_acquired": self._total_acquired,
            "total_released": self._total_released,
            "total_created": self._total_created,
            "total_closed": self._total_closed,
            "utilization": (
                len(self._active_connections) / self.max_connections
                if self.max_connections > 0 else 0
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dlp_level": "DLP_L1_OK",
        }

    async def close_all(self):
        """Close all connections in the pool"""
        async with self._lock:
            self._active_connections.clear()
            self._idle_connections.clear()
            self._total_closed += self._connection_count
            self._connection_count = 0
