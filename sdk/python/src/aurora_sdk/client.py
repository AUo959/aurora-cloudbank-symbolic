"""Main Aurora SDK client."""

from typing import Any, Optional

from aurora_sdk.config import Config
from aurora_sdk.exceptions import AuthenticationError
from aurora_sdk.resources.memory import MemoryResource
from aurora_sdk.resources.quantum import QuantumResource
from aurora_sdk.transport.http import HTTPTransport


class AuroraClient:
    """Main client for Aurora CloudBank Symbolic API.

    This is the primary entry point for the Aurora SDK. It provides access to
    all Aurora API resources including quantum simulations, memory management,
    thread transfer bridges, and decision intelligence tools.

    Attributes:
        quantum: Quantum simulation operations
        memory: Memory management operations

    Example:
        >>> from aurora_sdk import AuroraClient
        >>>
        >>> # Initialize with API key
        >>> client = AuroraClient(api_key="sk_test_...")
        >>>
        >>> # Run quantum scenario
        >>> result = await client.quantum.run_scenario(
        ...     "supply_chain_optimization",
        ...     num_suppliers=5
        ... )
        >>> print(result.optimal_state)
        >>>
        >>> # Create memory
        >>> memory = await client.memory.create(
        ...     "Important note",
        ...     tier="active",
        ...     tags=["note"]
        ... )

    Example with context manager:
        >>> async with AuroraClient(api_key="sk_test_...") as client:
        ...     result = await client.quantum.run_scenario("supply_chain")
        ...     print(result.optimal_state)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        max_retries: int = 3,
        config: Optional[Config] = None
    ) -> None:
        """Initialize Aurora client.

        Args:
            api_key: API key for authentication. If not provided, reads from
                AURORA_API_KEY environment variable.
            base_url: Base URL for API. Defaults to localhost.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            config: Custom configuration object. If provided, other params ignored.

        Raises:
            AuthenticationError: If no API key provided or found.

        Example:
            >>> # With API key
            >>> client = AuroraClient(api_key="sk_test_...")
            >>>
            >>> # From environment
            >>> import os
            >>> os.environ["AURORA_API_KEY"] = "sk_test_..."
            >>> client = AuroraClient()
            >>>
            >>> # With custom config
            >>> from aurora_sdk import Config
            >>> config = Config(
            ...     api_key="sk_test_...",
            ...     base_url="https://api.aurora.dev",
            ...     timeout=60.0
            ... )
            >>> client = AuroraClient(config=config)
        """
        # Use provided config or create from parameters
        if config is not None:
            self._config = config
        else:
            # Try to get API key from parameter or environment
            if api_key is None:
                try:
                    self._config = Config.from_env()
                except ValueError:
                    raise AuthenticationError(
                        "API key is required. Provide via api_key parameter or "
                        "AURORA_API_KEY environment variable. "
                        "Get your API key at https://dashboard.aurora.dev"
                    )
            else:
                self._config = Config(
                    api_key=api_key,
                    base_url=base_url,
                    timeout=timeout,
                    max_retries=max_retries
                )

        # Initialize transport
        self._transport = HTTPTransport(self._config)

        # Initialize resources
        self._quantum: Optional[QuantumResource] = None
        self._memory: Optional[MemoryResource] = None

    @property
    def quantum(self) -> QuantumResource:
        """Access quantum simulation operations.

        Returns:
            QuantumResource instance

        Example:
            >>> result = await client.quantum.run_scenario("supply_chain")
        """
        if self._quantum is None:
            self._quantum = QuantumResource(self._transport)
        return self._quantum

    @property
    def memory(self) -> MemoryResource:
        """Access memory management operations.

        Returns:
            MemoryResource instance

        Example:
            >>> memory = await client.memory.create("Important note")
        """
        if self._memory is None:
            self._memory = MemoryResource(self._transport)
        return self._memory

    async def close(self) -> None:
        """Close client and cleanup resources.

        This should be called when you're done using the client to properly
        close HTTP connections.

        Example:
            >>> client = AuroraClient(api_key="sk_test_...")
            >>> # ... use client ...
            >>> await client.close()
        """
        await self._transport.close()

    async def __aenter__(self) -> "AuroraClient":
        """Async context manager entry.

        Returns:
            AuroraClient instance

        Example:
            >>> async with AuroraClient(api_key="sk_test_...") as client:
            ...     result = await client.quantum.run_scenario("supply_chain")
        """
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit.

        Automatically closes the client when exiting the context.

        Args:
            *args: Exception information (if any)
        """
        await self.close()
