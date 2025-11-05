"""
Circuit Breaker Pattern Implementation

Provides fault tolerance for external service calls with automatic
circuit breaking and recovery following Aurora's resilience protocols.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, Optional


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is broken, rejecting calls
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker for fault-tolerant external service calls.

    Implements the circuit breaker pattern to prevent cascading failures
    and allow graceful degradation following Aurora's resilience protocols.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        expected_exception: type = Exception,
        name: str = "circuit_breaker"
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout_seconds: Time to wait before attempting recovery
            expected_exception: Exception type to catch
            name: Circuit breaker identifier
        """
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.expected_exception = expected_exception
        self.name = name

        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._last_failure_time: Optional[datetime] = None
        self._success_count = 0
        self._total_calls = 0
        self._context_tag = f"cb_{name}"

    @property
    def state(self) -> CircuitState:
        """Get current circuit state"""
        return self._state

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        if self._state != CircuitState.OPEN:
            return False

        if self._last_failure_time is None:
            return True

        elapsed = datetime.now(timezone.utc) - self._last_failure_time
        return elapsed > timedelta(seconds=self.timeout_seconds)

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            Exception: If circuit is open or call fails
        """
        self._total_calls += 1

        # Check if we should attempt reset
        if self._should_attempt_reset():
            self._state = CircuitState.HALF_OPEN

        # If circuit is open, reject call immediately
        if self._state == CircuitState.OPEN:
            raise Exception(f"Circuit breaker '{self.name}' is OPEN")

        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Call succeeded - update state
            self._on_success()
            return result

        except self.expected_exception as e:
            # Call failed - update state
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self._success_count += 1
        self._failure_count = 0

        # If we were in half-open state, close the circuit
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call"""
        self._failure_count += 1
        self._last_failure_time = datetime.now(timezone.utc)

        # Open circuit if threshold exceeded
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN

    def reset(self):
        """Manually reset circuit breaker"""
        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._last_failure_time = None

    def get_status(self) -> Dict[str, Any]:
        """
        Get circuit breaker status.

        Returns:
            Dict containing status information
        """
        return {
            "context_tag": self._context_tag,
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_calls": self._total_calls,
            "failure_threshold": self.failure_threshold,
            "timeout_seconds": self.timeout_seconds,
            "last_failure_time": self._last_failure_time.isoformat() if self._last_failure_time else None,
            "can_reset": self._should_attempt_reset(),
            "dlp_level": "DLP_L1_OK",
        }
