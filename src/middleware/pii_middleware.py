"""PII detection middleware — scans request/response JSON bodies for PII indicators.

Uses modules.data_guardian PIIDetector (regex-based) and optionally RedactionEngine
to redact outbound responses when AURORA_PII_REDACT_RESPONSES=true.

Anchor: T1-EDG-MIDDLEWARE-001
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Endpoints where PII is expected/required and scanning would add noise or
# break functionality (auth, user-profile, health, docs).
_PII_EXEMPT_PATHS = frozenset({
    "/api/auth/token",
    "/api/auth/register",
    "/api/users/me",
    "/health",
    "/metrics",
    "/docs",
    "/openapi.json",
    "/redoc",
})

# 64 KB default — skip scanning very large bodies to limit latency impact.
_MAX_BODY_SCAN_BYTES = int(os.environ.get("AURORA_PII_MAX_BODY_BYTES", str(64 * 1024)))

# Set AURORA_PII_REDACT_RESPONSES=true to enable automatic response redaction.
_PII_REDACT_RESPONSES = (
    os.environ.get("AURORA_PII_REDACT_RESPONSES", "false").lower() == "true"
)


class PIIMiddleware(BaseHTTPMiddleware):
    """Middleware that scans request/response JSON bodies for PII.

    On detection:
    - Logs a WARNING with the path and which PII types were found (never
      logs the actual PII values).
    - If AURORA_PII_REDACT_RESPONSES=true, redacts the response body before
      sending it to the client.
    - Never blocks or modifies request bodies (audit-only on inbound traffic).

    Configuration via environment variables:
        AURORA_PII_MAX_BODY_BYTES  Max bytes to scan (default: 65536 / 64 KB)
        AURORA_PII_REDACT_RESPONSES  Enable response redaction (default: false)
    """

    def __init__(self, app: ASGIApp, *, exempt_paths=None) -> None:
        super().__init__(app)
        self._exempt = frozenset(exempt_paths if exempt_paths is not None else _PII_EXEMPT_PATHS)

        try:
            from modules.data_guardian.detection_rules import PIIDetector
            self._detector = PIIDetector()
            logger.info("PIIMiddleware: PII scanning enabled (data_guardian available)")
        except ImportError:  # pragma: no cover - optional dependency path
            self._detector = None
            logger.warning("PIIMiddleware: data_guardian not available — PII scanning disabled")

    # ------------------------------------------------------------------
    # Core dispatch
    # ------------------------------------------------------------------

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._detector is None or request.url.path in self._exempt:
            return await call_next(request)

        # Scan request body (audit-only; inbound bodies are never modified).
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            body = await request.body()
            if body and len(body) <= _MAX_BODY_SCAN_BYTES:
                try:
                    data = json.loads(body)
                    self._scan_and_log(data, request.url.path, direction="request")
                except Exception:
                    pass  # Never break request processing due to scanning errors

        response = await call_next(request)

        # Optionally redact outgoing JSON responses.
        if _PII_REDACT_RESPONSES and "application/json" in response.headers.get("content-type", ""):
            response = await self._maybe_redact_response(response, request.url.path)

        return response

    # ------------------------------------------------------------------
    # Scanning helpers
    # ------------------------------------------------------------------

    def _scan_and_log(self, data: Any, path: str, direction: str) -> None:
        """Walk the data tree, collect unique PII type names, and log if any found.

        PII values are never included in log output.
        """
        findings: List[str] = []
        self._walk(data, findings)
        if findings:
            logger.warning(
                "PII detected in %s body for %s: %s",
                direction,
                path,
                ", ".join(findings),
                extra={"pii_types": findings, "path": path},
            )

    def _walk(self, data: Any, findings: List[str], depth: int = 0) -> None:
        """Recursively walk data and collect PII type names into *findings*."""
        if depth > 10:
            return

        if isinstance(data, str):
            try:
                # PIIDetector.detect() returns a list of dicts:
                # [{'start': int, 'end': int, 'match': str, 'type': str,
                #   'confidence': float, 'region': str|None}, ...]
                matches = self._detector.detect(data)
                for match in matches:
                    pii_type = match.get("type", "unknown")
                    if pii_type not in findings:
                        findings.append(pii_type)
            except Exception:
                pass

        elif isinstance(data, dict):
            for v in data.values():
                self._walk(v, findings, depth + 1)

        elif isinstance(data, (list, tuple)):
            for item in data:
                self._walk(item, findings, depth + 1)

    # ------------------------------------------------------------------
    # Response redaction
    # ------------------------------------------------------------------

    async def _maybe_redact_response(self, response: Response, path: str) -> Response:
        """Consume the response body, redact any PII, and return a new Response."""
        try:
            body_bytes = b""
            async for chunk in response.body_iterator:
                body_bytes += chunk

            if len(body_bytes) > _MAX_BODY_SCAN_BYTES:
                # Body too large to redact — pass through unchanged.
                return Response(
                    content=body_bytes,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

            data = json.loads(body_bytes)

            from modules.data_guardian.detection_rules import PIIDetector
            from modules.data_guardian.redaction import RedactionEngine

            detector = PIIDetector()
            engine = RedactionEngine()

            scan_results = detector.scan_dict(data)
            if scan_results:
                pii_types = self._collect_types_from_scan(scan_results)
                logger.warning(
                    "PII detected in response body for %s — redacting: %s",
                    path,
                    ", ".join(pii_types),
                    extra={"pii_types": pii_types, "path": path},
                )
                data = engine.redact_dict(data, scan_results)

            return Response(
                content=json.dumps(data),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json",
            )

        except Exception as exc:
            logger.debug("PIIMiddleware: response redaction skipped: %s", exc)
            return response

    @staticmethod
    def _collect_types_from_scan(scan_results: Dict) -> List[str]:
        """Flatten nested scan_dict results to a unique list of PII type strings."""
        types: List[str] = []

        def recurse(obj: Any) -> None:
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and "type" in item:
                        t = item["type"]
                        if t not in types:
                            types.append(t)
                    else:
                        recurse(item)
            elif isinstance(obj, dict):
                if "type" in obj and "start" in obj:
                    t = obj["type"]
                    if t not in types:
                        types.append(t)
                else:
                    for v in obj.values():
                        recurse(v)

        recurse(scan_results)
        return types
