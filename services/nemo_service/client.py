"""Shared NEMO service client for CloudHub-side integrations (issue #1061).

One httpx.Client, one fallback contract: every public method returns the
decoded response dict on success and ``None`` on ANY failure — connection
refused, timeout, non-2xx, undecodable body. Callers implement their own
graceful degradation on ``None`` and never see an exception from here.

The client is synchronous because every CloudHub endpoint that calls NEMO
(mcp_route_command, qf_create_agent, oppy_plan_maneuver, hr_*) is a sync
``def`` handler; issue #1061's async-client sketch assumed async handlers.
FastAPI runs sync handlers in the threadpool, so a shared sync client with
a bounded timeout is the equivalent pattern.

Environment:
    NEMO_SERVICE_URL  base URL (default http://aurora-nemo-service:8090,
                      the in-cluster service DNS from k8s/aurora-nemo-service.yaml)
    NEMO_TIMEOUT_S    per-request timeout seconds (default 10 — a sync
                      handler thread blocks for the duration, so this is
                      deliberately tighter than the service's own 30s budget)
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger("nemo_client")

# Pod-to-pod call inside the cluster network: the NEMO service
# (k8s/aurora-nemo-service.yaml) serves plain HTTP on 8090 and there is no
# mesh/mTLS layer in this deployment. Override NEMO_SERVICE_URL with an
# https:// URL if the service ever moves behind TLS.
DEFAULT_BASE_URL = "http://aurora-nemo-service:8090"  # NOSONAR(S5332) in-cluster DNS, deliberate


def _base_url() -> str:
    return os.getenv("NEMO_SERVICE_URL", DEFAULT_BASE_URL)


def _timeout_s() -> float:
    try:
        return float(os.getenv("NEMO_TIMEOUT_S", "10"))
    except ValueError:
        return 10.0


class NemoClient:
    """Thin wrapper over the NEMO inference HTTP surface."""

    def __init__(self, transport: Optional[httpx.BaseTransport] = None) -> None:
        # `transport` is injectable so tests can use httpx.MockTransport
        # without a live service.
        self._client = httpx.Client(
            base_url=_base_url(), timeout=_timeout_s(), transport=transport
        )

    def _post(self, path: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = self._client.post(path, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning("NEMO %s unavailable, falling back: %s", path, exc)
            return None

    def generate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 256,
        temperature: float = 1.0,
    ) -> Optional[Dict[str, Any]]:
        """POST /nemo/generate. Returns GenerateResponse dict or None."""
        return self._post(
            "/nemo/generate",
            {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "context": context,
            },
        )

    def infer(
        self,
        model_type: str,
        text: Optional[str] = None,
        audio_bytes: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """POST /nemo/infer. Returns InferResponse dict or None."""
        payload: Dict[str, Any] = {"model_type": model_type, "context": context}
        if text is not None:
            payload["text"] = text
        if audio_bytes is not None:
            payload["audio_bytes"] = audio_bytes
        return self._post("/nemo/infer", payload)

    def close(self) -> None:
        self._client.close()


_client: Optional[NemoClient] = None
_client_lock = threading.Lock()


def get_nemo_client() -> NemoClient:
    """Process-wide shared client (lazily created, thread-safe)."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = NemoClient()
    return _client


def close_nemo_client() -> None:
    """Close and drop the shared client (app shutdown / test isolation)."""
    global _client
    with _client_lock:
        if _client is not None:
            _client.close()
            _client = None
