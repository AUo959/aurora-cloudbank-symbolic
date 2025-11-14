"""Configuration management for Aurora SDK."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration for Aurora SDK.

    Attributes:
        api_key: API key for authentication
        base_url: Base URL for API
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        cache_ttl: Cache TTL in seconds (0 = disabled)
        log_level: Logging level

    Example:
        >>> config = Config(api_key="sk_test_...", base_url="http://localhost:8000")
        >>> client = AuroraClient(config=config)
    """

    api_key: str
    base_url: str = "http://localhost:8000"
    timeout: float = 30.0
    max_retries: int = 3
    cache_ttl: int = 0
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables.

        Environment variables:
            AURORA_API_KEY: API key
            AURORA_BASE_URL: Base URL
            AURORA_TIMEOUT: Request timeout
            AURORA_MAX_RETRIES: Max retries
            AURORA_CACHE_TTL: Cache TTL
            AURORA_LOG_LEVEL: Log level

        Args:
            env_file: Optional path to .env file

        Returns:
            Config instance

        Raises:
            ValueError: If AURORA_API_KEY is not set

        Example:
            >>> config = Config.from_env()
            >>> config = Config.from_env(env_file=Path(".env"))
        """
        # Load .env file if provided
        if env_file:
            load_dotenv(env_file)

        # Get API key (required)
        api_key = os.getenv("AURORA_API_KEY")
        if not api_key:
            raise ValueError(
                "AURORA_API_KEY environment variable is required. "
                "Get your API key at https://dashboard.aurora.dev"
            )

        # Get other config values with defaults
        return cls(
            api_key=api_key,
            base_url=os.getenv("AURORA_BASE_URL", "http://localhost:8000"),
            timeout=float(os.getenv("AURORA_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("AURORA_MAX_RETRIES", "3")),
            cache_ttl=int(os.getenv("AURORA_CACHE_TTL", "0")),
            log_level=os.getenv("AURORA_LOG_LEVEL", "INFO"),
        )

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.api_key:
            raise ValueError("api_key is required")

        if not self.base_url:
            raise ValueError("base_url is required")

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        if self.cache_ttl < 0:
            raise ValueError("cache_ttl must be non-negative")

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self.validate()
