"""Exceptions for Aurora SDK."""

from typing import Any


class AuroraError(Exception):
    """Base exception for Aurora SDK.

    All Aurora SDK exceptions inherit from this class.
    """

    def __init__(self, message: str, **kwargs: Any) -> None:
        """Initialize exception.

        Args:
            message: Error message
            **kwargs: Additional error context
        """
        super().__init__(message)
        self.message = message
        self.kwargs = kwargs

    def __str__(self) -> str:
        """String representation."""
        return self.message


class AuthenticationError(AuroraError):
    """Authentication failed.

    Raised when API key is invalid or missing.
    """

    pass


class AuthorizationError(AuroraError):
    """Authorization failed.

    Raised when authenticated user lacks permissions for the requested operation.
    """

    pass


class RateLimitError(AuroraError):
    """Rate limit exceeded.

    Raised when too many requests are made in a given time period.
    """

    def __init__(self, message: str, retry_after: int) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds until rate limit resets
        """
        super().__init__(message)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """String representation."""
        return f"{self.message} (retry after {self.retry_after}s)"


class ValidationError(AuroraError):
    """Request validation failed.

    Raised when request parameters are invalid.
    """

    def __init__(self, message: str, details: dict[str, Any]) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            details: Validation error details
        """
        super().__init__(message)
        self.details = details

    def __str__(self) -> str:
        """String representation."""
        errors = "\n".join(f"  - {k}: {v}" for k, v in self.details.items())
        return f"{self.message}\n{errors}"


class ResourceNotFoundError(AuroraError):
    """Resource not found (404).

    Raised when requested resource does not exist.
    """

    pass


class ServerError(AuroraError):
    """Server error (5xx).

    Raised when server encounters an internal error.
    """

    pass


class NetworkError(AuroraError):
    """Network/connection error.

    Raised when network connection fails or is interrupted.
    """

    pass


class TimeoutError(AuroraError):
    """Request timeout.

    Raised when request exceeds timeout limit.
    """

    pass
