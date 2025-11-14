"""Aurora CloudBank Symbolic Python SDK.

This package provides a pythonic interface to the Aurora CloudBank Symbolic API,
enabling developers to interact with quantum simulations, memory management,
thread transfer bridges, and decision intelligence tools.

Example:
    >>> from aurora_sdk import AuroraClient
    >>> client = AuroraClient(api_key="sk_test_...")
    >>> result = await client.quantum.run_scenario("supply_chain", num_suppliers=5)
    >>> print(result.optimal_state)
"""

from aurora_sdk.__version__ import __version__
from aurora_sdk.client import AuroraClient
from aurora_sdk.config import Config
from aurora_sdk.exceptions import (
    AuroraError,
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
    TimeoutError,
    ValidationError,
)

__all__ = [
    "__version__",
    "AuroraClient",
    "Config",
    "AuroraError",
    "AuthenticationError",
    "AuthorizationError",
    "NetworkError",
    "RateLimitError",
    "ResourceNotFoundError",
    "ServerError",
    "TimeoutError",
    "ValidationError",
]
