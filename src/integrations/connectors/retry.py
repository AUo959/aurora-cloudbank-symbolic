"""
Retry Logic with Exponential Backoff

Provides resilient retry mechanisms for external service calls
with Aurora's DLP tracking and error handling patterns.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Type


class RetryPolicy:
    """
    Retry policy with exponential backoff.

    Implements resilient retry logic for transient failures
    while maintaining Aurora's observability standards.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retriable_exceptions: Optional[tuple] = None,
        name: str = "retry_policy"
    ):
        """
        Initialize retry policy.

        Args:
            max_attempts: Maximum retry attempts
            base_delay: Initial delay between retries (seconds)
            max_delay: Maximum delay between retries (seconds)
            backoff_factor: Exponential backoff multiplier
            jitter: Add random jitter to prevent thundering herd
            retriable_exceptions: Tuple of exception types to retry
            name: Policy identifier
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retriable_exceptions = retriable_exceptions or (Exception,)
        self.name = name

        # Tracking metrics
        self._total_attempts = 0
        self._successful_retries = 0
        self._failed_retries = 0
        self._context_tag = f"retry_{name}"

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = min(self.base_delay * (self.backoff_factor ** attempt), self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            delay = delay * (0.5 + random.random())

        return delay

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func

        Raises:
            Exception: If all retry attempts fail
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            self._total_attempts += 1

            try:
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Success
                if attempt > 0:
                    self._successful_retries += 1
                return result

            except self.retriable_exceptions as e:
                last_exception = e

                # If this was the last attempt, raise the exception
                if attempt == self.max_attempts - 1:
                    self._failed_retries += 1
                    raise e

                # Calculate delay and wait before retry
                delay = self._calculate_delay(attempt)
                await asyncio.sleep(delay)

        # Should not reach here, but raise last exception if we do
        if last_exception:
            raise last_exception
        raise Exception("Retry logic failed without exception")

    def get_status(self) -> Dict[str, Any]:
        """
        Get retry policy status.

        Returns:
            Dict containing status and metrics
        """
        return {
            "context_tag": self._context_tag,
            "name": self.name,
            "max_attempts": self.max_attempts,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "backoff_factor": self.backoff_factor,
            "jitter_enabled": self.jitter,
            "total_attempts": self._total_attempts,
            "successful_retries": self._successful_retries,
            "failed_retries": self._failed_retries,
            "retry_success_rate": (
                self._successful_retries / max(1, self._successful_retries + self._failed_retries)
            ),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dlp_level": "DLP_L1_OK",
        }

    def reset(self):
        """Reset retry metrics"""
        self._total_attempts = 0
        self._successful_retries = 0
        self._failed_retries = 0


def create_retry_policy(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    **kwargs
) -> RetryPolicy:
    """
    Factory function to create retry policy.

    Args:
        max_attempts: Maximum retry attempts
        base_delay: Initial delay between retries
        **kwargs: Additional retry policy parameters

    Returns:
        RetryPolicy instance
    """
    return RetryPolicy(max_attempts=max_attempts, base_delay=base_delay, **kwargs)
