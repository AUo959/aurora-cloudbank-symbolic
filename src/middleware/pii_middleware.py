"""PII detection middleware — scans request/response JSON bodies for PII indicators.

Uses modules.data_guardian PIIDetector (regex-based) and optionally RedactionEngine
to redact outbound responses when AURORA_PII_REDACT_RESPONSES=true.

Anchor: T1-EDG-MIDDLEWARE-001
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

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
                except Exception as exc:
                    # Never break request processing due to scanning errors, but
                    # do not fail silently either: a scan that always throws
                    # looks identical to a scan that finds nothing.
                    self._log_failure(request.url.path, "request-scan", exc)

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
        failures: List[str] = []
        self._walk(data, findings, failures=failures)
        if failures:
            # Aggregated to one line per scan: _walk runs per string value, so
            # logging each failure would flood the log on a large payload while
            # telling you nothing more than the class and the count.
            logger.warning(
                "PIIMiddleware: detector failed on %d value(s) in %s body for %s (%s) "
                "— those values were not scanned",
                len(failures),
                direction,
                path,
                ", ".join(sorted(set(failures))),
                extra={"path": path, "direction": direction, "error_classes": sorted(set(failures))},
            )
        if findings:
            logger.warning(
                "PII detected in %s body for %s: %s",
                direction,
                path,
                ", ".join(findings),
                extra={"pii_types": findings, "path": path},
            )

    def _walk(
        self,
        data: Any,
        findings: List[str],
        depth: int = 0,
        failures: Optional[List[str]] = None,
    ) -> None:
        """Recursively walk data and collect PII type names into *findings*.

        Detector failures are appended to *failures* as exception class names
        so the caller can report them once, rather than being swallowed.
        """
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
            except Exception as exc:
                # Scanning must never break the request; record the class only
                # (never the value, which is the PII itself) and continue.
                if failures is not None:
                    failures.append(type(exc).__name__)

        elif isinstance(data, dict):
            for v in data.values():
                self._walk(v, findings, depth + 1, failures=failures)

        elif isinstance(data, (list, tuple)):
            for item in data:
                self._walk(item, findings, depth + 1, failures=failures)

    # ------------------------------------------------------------------
    # Response redaction
    # ------------------------------------------------------------------

    def _log_failure(self, path: str, stage: str, exc: BaseException) -> None:
        """Record a scan/redaction failure without ever logging PII values.

        Only the route, the stage, and the exception *class* are emitted. The
        exception message is deliberately omitted: detector and JSON errors
        routinely quote the offending input, which is precisely the data this
        middleware exists to keep out of logs.
        """
        logger.warning(
            "PIIMiddleware: %s failed for %s (%s) — protection degraded for this response",
            stage,
            path,
            type(exc).__name__,
            extra={"pii_stage": stage, "path": path, "error_class": type(exc).__name__},
        )

    @staticmethod
    def _rebuild(
        response: Response,
        body: bytes,
        *,
        media_type: Optional[str],
        body_changed: bool,
    ) -> Response:
        """Reconstruct a response from buffered bytes.

        Once ``body_iterator`` has been drained the original response object is
        unusable — returning it hands the client an empty or partial body under
        the original status and headers. Every exit from redaction therefore
        goes through here.

        When the body changed, ``content-length`` is dropped so Starlette
        recomputes it; copying the pre-redaction value would describe bytes that
        are no longer being sent.
        """
        headers = dict(response.headers)
        if body_changed:
            for key in [k for k in headers if k.lower() == "content-length"]:
                headers.pop(key)
        return Response(
            content=body,
            status_code=response.status_code,
            headers=headers,
            media_type=media_type,
        )

    async def _maybe_redact_response(self, response: Response, path: str) -> Response:
        """Consume the response body, redact any PII, and return a new Response."""
        # Buffer first, and keep the bytes for every subsequent exit path.
        body_bytes = b""
        try:
            async for chunk in response.body_iterator:
                body_bytes += chunk
        except Exception as exc:
            # The iterator is now partially drained and cannot be replayed;
            # emit whatever was buffered rather than an exhausted response.
            self._log_failure(path, "response-buffer", exc)
            return self._rebuild(
                response, body_bytes, media_type=response.media_type, body_changed=True
            )

        if len(body_bytes) > _MAX_BODY_SCAN_BYTES:
            # Body too large to redact — pass the original bytes through.
            return self._rebuild(
                response, body_bytes, media_type=response.media_type, body_changed=False
            )

        try:
            data = json.loads(body_bytes)

            from modules.data_guardian.detection_rules import PIIDetector
            from modules.data_guardian.redaction import RedactionEngine

            detector = PIIDetector()
            engine = RedactionEngine()

            scan_results = detector.scan_dict(data)
            if not scan_results:
                # Nothing to redact: emit the original bytes verbatim rather
                # than a re-serialised copy, so key order and formatting are
                # preserved exactly.
                return self._rebuild(
                    response, body_bytes, media_type=response.media_type, body_changed=False
                )

            pii_types = self._collect_types_from_scan(scan_results)
            logger.warning(
                "PII detected in response body for %s — redacting: %s",
                path,
                ", ".join(pii_types),
                extra={"pii_types": pii_types, "path": path},
            )
            redacted = json.dumps(engine.redact_dict(data, scan_results)).encode("utf-8")

        except Exception as exc:
            # Parse, detector, or redaction failure. Fall back to the exact
            # bytes the application produced — never a consumed response.
            self._log_failure(path, "response-redaction", exc)
            return self._rebuild(
                response, body_bytes, media_type=response.media_type, body_changed=False
            )

        return self._rebuild(
            response, redacted, media_type="application/json", body_changed=True
        )

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
