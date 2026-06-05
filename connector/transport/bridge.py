"""
Cloudbank Bridge
=================
REST bridge connecting MCP tool handlers to the existing
Aurora FastAPI layer (api/aurora_api_server.py).

All tool handlers call bridge methods instead of making
direct HTTP requests. This centralizes:
  - Base URL configuration
  - Auth header injection
  - Error handling and retries
  - Response parsing

Usage:
    bridge = CloudbankBridge()
    data = await bridge.get("/state")
    data = await bridge.post("/memory/node", payload={...})
"""

import asyncio
import os
import logging
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

log = logging.getLogger("aurora.connector.bridge")

DEFAULT_TIMEOUT = 10.0  # seconds
_CONNECTOR_VERSION = "0.1.0"
_MAX_GET_RETRIES = 3


class BridgeError(Exception):
    """Raised when the Aurora API returns an error or is unreachable."""


class CloudbankBridge:
    """
    Thin async HTTP client wrapping the Aurora API.

    Reads configuration from environment:
      AURORA_API_BASE_URL              -- base URL of aurora_api_server.py
      AURORA_CONNECTOR_TOKEN           -- Bearer token for auth (required; fails closed if absent)
      AURORA_CONNECTOR_TIMEOUT_SECONDS -- per-request timeout in seconds (default 10)
    """

    def __init__(self) -> None:
        if httpx is None:
            raise ImportError("httpx is required: pip install httpx")

        self.base_url = os.getenv("AURORA_API_BASE_URL", "http://localhost:8000").rstrip("/")
        self.token = os.getenv("AURORA_CONNECTOR_TOKEN", "")

        if not self.token:
            raise RuntimeError(
                "AURORA_CONNECTOR_TOKEN is required. "
                "Set it before starting the MCP connector."
            )

        self._timeout = float(
            os.getenv("AURORA_CONNECTOR_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT))
        )

    @property
    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"aurora-mcp-connector/{_CONNECTOR_VERSION}",
            "X-Source-Client": "aurora-mcp-connector",
            "X-Connector-Version": _CONNECTOR_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get(self, path: str, params: dict | None = None) -> Any:
        """
        Perform a GET request against the Aurora API.

        Retries up to _MAX_GET_RETRIES times on connection errors and 5xx responses
        with exponential backoff. Does not retry on 4xx (client errors).

        Args:
            path: API path (e.g. "/state", "/agents")
            params: Optional query parameters

        Returns:
            Parsed JSON response body

        Raises:
            BridgeError: On HTTP error or connection failure after all retries
        """
        url = f"{self.base_url}{path}"
        log.debug("GET %s params=%s", url, params)

        last_exc: Exception | None = None
        for attempt in range(_MAX_GET_RETRIES):
            if attempt:
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                try:
                    response = await client.get(url, headers=self._headers, params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code < 500:
                        raise BridgeError(
                            f"Aurora API returned {exc.response.status_code} for GET {path}"
                        ) from exc
                    last_exc = exc
                except httpx.RequestError as exc:
                    last_exc = exc

        raise BridgeError(
            f"Aurora API unreachable at {self.base_url} after {_MAX_GET_RETRIES} attempts"
        ) from last_exc

    async def post(self, path: str, payload: dict | None = None) -> Any:
        """
        Perform a POST request against the Aurora API.

        No automatic retry (non-idempotent operation).

        Args:
            path: API path (e.g. "/memory/node", "/anomaly/flag")
            payload: Request body (will be JSON-encoded)

        Returns:
            Parsed JSON response body

        Raises:
            BridgeError: On HTTP error or connection failure
        """
        url = f"{self.base_url}{path}"
        log.debug("POST %s", url)

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                response = await client.post(url, headers=self._headers, json=payload or {})
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                raise BridgeError(
                    f"Aurora API returned {exc.response.status_code} for POST {path}"
                ) from exc
            except httpx.RequestError as exc:
                raise BridgeError(
                    f"Cannot reach Aurora API at {self.base_url}"
                ) from exc
