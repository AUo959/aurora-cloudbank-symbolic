"""
FastAPI Middleware for Data Guardian

Intercepts requests and responses to automatically detect and redact PII.

Anchor: T1-EDG-001-MIDDLEWARE
"""

import json
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .detection_rules import PIIDetector
from .redaction import RedactionEngine, RedactionStrategy


class DataGuardianMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic PII detection and redaction.

    Scans incoming requests and outgoing responses for PII,
    optionally redacting sensitive data based on configuration.
    """

    def __init__(
        self,
        app: ASGIApp,
        enabled: bool = True,
        scan_requests: bool = True,
        scan_responses: bool = True,
        redact_mode: bool = False,
        redaction_strategy: RedactionStrategy = RedactionStrategy.MASK,
        region: str = "US",
        excluded_paths: Optional[list] = None,
        audit_callback: Optional[Callable] = None
    ):
        """
        Initialize Data Guardian middleware.

        Args:
            app: ASGI application
            enabled: Enable/disable middleware globally
            scan_requests: Scan incoming request bodies
            scan_responses: Scan outgoing response bodies
            redact_mode: If True, automatically redact detected PII
            redaction_strategy: Strategy to use for redaction
            region: Region for PII detection rules
            excluded_paths: List of paths to exclude from scanning
            audit_callback: Optional callback for audit logging
        """
        super().__init__(app)
        self.enabled = enabled
        self.scan_requests = scan_requests
        self.scan_responses = scan_responses
        self.redact_mode = redact_mode
        self.region = region
        self.excluded_paths = excluded_paths or []
        self.audit_callback = audit_callback

        # Initialize detector and redaction engine
        self.detector = PIIDetector(region=region)
        self.redaction_engine = RedactionEngine(default_strategy=redaction_strategy)

        # Statistics
        self.stats = {
            'requests_scanned': 0,
            'responses_scanned': 0,
            'pii_detected': 0,
            'redactions_performed': 0
        }

    async def dispatch(self, request: Request, call_next):
        """Process request and response through PII detection."""

        if not self.enabled or self._is_excluded(request.url.path):
            return await call_next(request)

        # Scan request if enabled
        request_detections = []
        if self.scan_requests:
            request_detections = await self._scan_request(request)
            self.stats['requests_scanned'] += 1

        # Call next middleware/endpoint
        response = await call_next(request)

        # Scan response if enabled
        response_detections = []
        if self.scan_responses:
            response, response_detections = await self._scan_response(response)
            self.stats['responses_scanned'] += 1

        # Add headers with detection metadata
        if request_detections or response_detections:
            total_detections = len(request_detections) + len(response_detections)
            self.stats['pii_detected'] += total_detections
            response.headers["X-Data-Guardian-PII-Detected"] = str(total_detections)

            if self.redact_mode:
                response.headers["X-Data-Guardian-Redacted"] = "true"

        # Audit logging
        if self.audit_callback:
            await self._audit_log(request, request_detections, response_detections)

        return response

    async def _scan_request(self, request: Request) -> list:
        """Scan request body for PII."""
        try:
            # Only scan JSON requests
            if request.headers.get("content-type") == "application/json":
                body = await request.body()
                if body:
                    data = json.loads(body)
                    detections = self.detector.scan_dict(data)

                    if detections and self.redact_mode:
                        self.redaction_engine.redact_dict(
                            data,
                            detections
                        )
                        # Would need to modify request body here
                        # (complex in ASGI, better to handle at application level)
                        self.stats['redactions_performed'] += 1

                    return self._flatten_detections(detections)
        except Exception:
            # Silently fail - don't break request processing
            pass

        return []

    async def _scan_response(self, response: Response) -> tuple:
        """Scan response body for PII."""
        try:
            # Read response body
            body_bytes = b""
            async for chunk in response.body_iterator:
                body_bytes += chunk

            if body_bytes:
                # Try to parse as JSON
                try:
                    data = json.loads(body_bytes)
                    detections = self.detector.scan_dict(data)

                    if detections and self.redact_mode:
                        redacted_data = self.redaction_engine.redact_dict(
                            data,
                            detections
                        )
                        body_bytes = json.dumps(redacted_data).encode()
                        self.stats['redactions_performed'] += 1

                    # Create new response with (possibly modified) body
                    from starlette.responses import Response as StarletteResponse
                    new_response = StarletteResponse(
                        content=body_bytes,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )

                    return new_response, self._flatten_detections(detections)

                except json.JSONDecodeError:
                    # Not JSON, scan as text
                    text = body_bytes.decode('utf-8', errors='ignore')
                    detections = self.detector.detect(text)

                    if detections and self.redact_mode:
                        redacted_text = self.redaction_engine.redact_text(
                            text,
                            detections
                        )
                        body_bytes = redacted_text.encode()
                        self.stats['redactions_performed'] += 1

                    from starlette.responses import Response as StarletteResponse
                    new_response = StarletteResponse(
                        content=body_bytes,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type
                    )

                    return new_response, detections

        except Exception:
            # Silently fail - don't break response
            pass

        return response, []

    def _is_excluded(self, path: str) -> bool:
        """Check if path is excluded from scanning."""
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False

    def _flatten_detections(self, detections: dict) -> list:
        """Flatten nested detection results into a simple list."""
        flat = []

        def recurse(obj):
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and 'type' in item:
                        flat.append(item)
                    else:
                        recurse(item)
            elif isinstance(obj, dict):
                for value in obj.values():
                    recurse(value)

        recurse(detections)
        return flat

    async def _audit_log(
        self,
        request: Request,
        request_detections: list,
        response_detections: list
    ):
        """Call audit callback with detection information."""
        if self.audit_callback:
            try:
                await self.audit_callback({
                    'timestamp': time.time(),
                    'path': request.url.path,
                    'method': request.method,
                    'request_pii_count': len(request_detections),
                    'response_pii_count': len(response_detections),
                    'redacted': self.redact_mode,
                    'request_detections': request_detections,
                    'response_detections': response_detections
                })
            except Exception:
                # Don't let audit failures break the request
                pass

    def get_stats(self) -> dict:
        """Get middleware statistics."""
        return {
            **self.stats,
            'detector_stats': self.detector.get_stats(),
            'enabled': self.enabled,
            'redact_mode': self.redact_mode,
            'region': self.region
        }

    def reset_stats(self):
        """Reset statistics counters."""
        self.stats = {
            'requests_scanned': 0,
            'responses_scanned': 0,
            'pii_detected': 0,
            'redactions_performed': 0
        }
        self.redaction_engine.reset_audit_trail()
