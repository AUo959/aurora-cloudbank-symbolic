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

import os
import logging
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

log = logging.getLogger("aurora.connector.bridge")

DEFAULT_TIMEOUT = 10.0  # seconds


class BridgeError(Exception):
    """Raised when the Aurora API returns an error or is unreachable."""


class CloudbankBridge:
    """
    Thin async HTTP client wrapping the Aurora API.

    Reads configuration from environment:
      AURORA_API_BASE_URL   -- base URL of aurora_api_server.py
      AURORA_CONNECTOR_TOKEN -- Bearer token for auth
    """

    def __init__(self) -> None:
        if httpx is None:
            raise ImportError("httpx is required: pip install httpx")

        self.base_url = os.getenv("AURORA_API_BASE_URL", "http://localhost:8000").rstrip("/")
        self.token = os.getenv("AURORA_CONNECTOR_TOKEN", "")

        if not self.token:
            log.warning(
                "AURORA_CONNECTOR_TOKEN not set. Requests will be unauthenticated."
            )

    @property
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get(self, path: str, params: dict | None = None) -> Any:
        """
        Perform a GET request against the Aurora API.

        Args:
            path: API path (e.g. "/state", "/agents")
            params: Optional query parameters

        Returns:
            Parsed JSON response body

        Raises:
            BridgeError: On HTTP error or connection failure
        """
        url = f"{self.base_url}{path}"
        log.debug("GET %s params=%s", url, params)

        # TODO: Map Aurora API endpoint paths to match aurora_api_server.py routes.
        # Current aurora_api.py endpoints need audit to confirm exact path names.
        # See api/aurora_api_server.py for route definitions.

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            try:
                response = await client.get(url, headers=self._headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                raise BridgeError(
                    f"Aurora API returned {exc.response.status_code} for GET {path}: "
                    f"{exc.response.text[:200]}"
                ) from exc
            except httpx.RequestError as exc:
                raise BridgeError(
                    f"Cannot reach Aurora API at {self.base_url}: {exc}"
                ) from exc

    async def post(self, path: str, payload: dict | None = None) -> Any:
        """
        Perform a POST request against the Aurora API.

        Args:
            path: API path (e.g. "/memory/node", "/anomaly/flag")
            payload: Request body (will be JSON-encoded)

        Returns:
            Parsed JSON response body

        Raises:
            BridgeError: On HTTP error or connection failure
        """
        url = f"{self.base_url}{path}"
        log.debug("POST %s payload=%s", url, payload)

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            try:
                response = await client.post(url, headers=self._headers, json=payload or {})
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                raise BridgeError(
                    f"Aurora API returned {exc.response.status_code} for POST {path}: "
                    f"{exc.response.text[:200]}"
                ) from exc
            except httpx.RequestError as exc:
                raise BridgeError(
                    f"Cannot reach Aurora API at {self.base_url}: {exc}"
                ) from exc
