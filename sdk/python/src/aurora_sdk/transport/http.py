"""HTTP transport layer for Aurora SDK."""

import asyncio
from typing import Any, Optional

import httpx

from aurora_sdk.__version__ import __version__
from aurora_sdk.config import Config
from aurora_sdk.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
    TimeoutError,
    ValidationError,
)


class HTTPTransport:
    """HTTP client with retry and error handling.

    Handles all HTTP communication with the Aurora API, including:
    - Authentication
    - Retry logic with exponential backoff
    - Error handling and exception mapping
    - Request/response validation
    """

    def __init__(self, config: Config) -> None:
        """Initialize HTTP transport.

        Args:
            config: SDK configuration
        """
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build request headers.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": f"aurora-sdk-python/{__version__}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """GET request with retry.

        Args:
            path: URL path
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            AuroraError: On API errors
        """
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """POST request with retry.

        Args:
            path: URL path
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            AuroraError: On API errors
        """
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """PUT request with retry.

        Args:
            path: URL path
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            AuroraError: On API errors
        """
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """DELETE request with retry.

        Args:
            path: URL path
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            AuroraError: On API errors
        """
        return await self._request("DELETE", path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """Execute request with retry and error handling.

        Args:
            method: HTTP method
            path: URL path
            **kwargs: Additional request parameters

        Returns:
            Response JSON data

        Raises:
            AuroraError: On API errors
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.client.request(method, path, **kwargs)

                # Handle errors
                if response.status_code >= 400:
                    self._handle_error(response)

                # Return JSON data
                return response.json()

            except httpx.TimeoutException as e:
                last_exception = TimeoutError(f"Request timeout after {self.config.timeout}s")

            except httpx.NetworkError as e:
                last_exception = NetworkError(f"Network error: {str(e)}")

            except Exception as e:
                # Don't retry on client errors (4xx except 429)
                if isinstance(last_exception, (AuthenticationError, AuthorizationError,
                                              ValidationError, ResourceNotFoundError)):
                    raise

                last_exception = e

            # Exponential backoff for retries
            if attempt < self.config.max_retries:
                delay = min(2 ** attempt, 60)  # Max 60 seconds
                await asyncio.sleep(delay)

        # All retries exhausted
        if last_exception:
            raise last_exception

        raise ServerError("Request failed after all retries")

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle HTTP errors.

        Args:
            response: HTTP response

        Raises:
            AuroraError: Appropriate exception based on status code
        """
        status = response.status_code

        try:
            error_data = response.json()
            message = error_data.get("detail", response.text)
        except Exception:
            message = response.text

        # Map status codes to exceptions
        if status == 401:
            raise AuthenticationError(
                f"Authentication failed: {message}. "
                "Check your API key at https://dashboard.aurora.dev"
            )
        elif status == 403:
            raise AuthorizationError(f"Authorization failed: {message}")
        elif status == 404:
            raise ResourceNotFoundError(f"Resource not found: {message}")
        elif status == 422:
            # Validation error with details
            details = error_data.get("errors", {}) if isinstance(error_data, dict) else {}
            raise ValidationError(f"Validation failed: {message}", details=details)
        elif status == 429:
            # Rate limit with retry-after header
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                f"Rate limit exceeded: {message}",
                retry_after=retry_after
            )
        elif status >= 500:
            raise ServerError(f"Server error ({status}): {message}")
        else:
            raise ServerError(f"HTTP error ({status}): {message}")

    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        await self.client.aclose()

    async def __aenter__(self) -> "HTTPTransport":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
