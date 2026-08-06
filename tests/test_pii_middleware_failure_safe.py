"""Failure-safety regression tests for PIIMiddleware response redaction (#1344).

The defect these cover: ``_maybe_redact_response`` drained
``response.body_iterator`` and then, on any exception, returned that same
now-exhausted response object. The client received an empty or partial body
under the original status and headers — a redaction failure turned into
response corruption.

Every test here asserts on bytes the client actually receives, not on internal
state, because "the middleware returned something" was never the problem.
"""

from __future__ import annotations

import json

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.testclient import TestClient

from src.middleware import pii_middleware as pii_mod
from src.middleware.pii_middleware import PIIMiddleware

PAYLOAD = {"user": "alice", "note": "hello world", "n": 1}


@pytest.fixture(autouse=True)
def _enable_response_redaction(monkeypatch: pytest.MonkeyPatch):
    """Response redaction is opt-in via env; these tests exercise it on."""
    monkeypatch.setattr(pii_mod, "_PII_REDACT_RESPONSES", True)


def build_client(payload=None, *, raw: str | None = None) -> TestClient:
    app = FastAPI()

    @app.get("/data")
    async def data():
        if raw is not None:
            return JSONResponse(content={}, media_type="application/json")
        return JSONResponse(content=payload if payload is not None else PAYLOAD)

    app.add_middleware(PIIMiddleware)
    return TestClient(app)


def test_body_is_not_lost_when_redaction_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """A detector explosion must not empty the response body.

    This is the core regression: pre-fix the client got b"" here.
    """
    client = build_client()

    def boom(self, data):  # noqa: ANN001
        raise RuntimeError("detector exploded")

    from modules.data_guardian.detection_rules import PIIDetector

    monkeypatch.setattr(PIIDetector, "scan_dict", boom, raising=False)

    response = client.get("/data")
    assert response.status_code == 200
    assert response.content != b"", "body was lost — the exhausted response was returned"
    assert response.json() == PAYLOAD


def test_invalid_json_body_is_passed_through_verbatim() -> None:
    """A non-JSON body served as application/json must survive untouched."""
    app = FastAPI()

    @app.get("/data")
    async def data():
        from starlette.responses import Response

        return Response(content=b"not json at all", media_type="application/json")

    app.add_middleware(PIIMiddleware)
    client = TestClient(app)

    response = client.get("/data")
    assert response.status_code == 200
    assert response.content == b"not json at all"


def test_content_length_matches_body_on_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fallback responses must not advertise a length they do not send."""
    client = build_client()

    from modules.data_guardian.detection_rules import PIIDetector

    monkeypatch.setattr(
        PIIDetector, "scan_dict", lambda self, d: (_ for _ in ()).throw(ValueError("nope")),
        raising=False,
    )

    response = client.get("/data")
    declared = response.headers.get("content-length")
    assert declared is not None
    assert int(declared) == len(response.content)


def test_content_length_matches_body_after_redaction(monkeypatch: pytest.MonkeyPatch) -> None:
    """A redacted body changes length; the header must follow it."""
    client = build_client({"email": "alice@example.com", "pad": "x" * 50})

    response = client.get("/data")
    declared = response.headers.get("content-length")
    assert declared is not None
    assert int(declared) == len(response.content), (
        "stale Content-Length copied from the pre-redaction body"
    )


def test_status_and_headers_preserved_on_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fallback must not alter status or unrelated headers."""
    app = FastAPI()

    @app.get("/data")
    async def data():
        return JSONResponse(
            content=PAYLOAD, status_code=418, headers={"x-custom": "kept"}
        )

    app.add_middleware(PIIMiddleware)
    client = TestClient(app)

    from modules.data_guardian.detection_rules import PIIDetector

    monkeypatch.setattr(
        PIIDetector, "scan_dict", lambda self, d: (_ for _ in ()).throw(RuntimeError("x")),
        raising=False,
    )

    response = client.get("/data")
    assert response.status_code == 418
    assert response.headers.get("x-custom") == "kept"
    assert response.json() == PAYLOAD


def test_clean_body_is_byte_identical() -> None:
    """With nothing to redact, the original bytes are emitted unchanged."""
    payload = {"b": 2, "a": 1}  # key order matters for this assertion
    client = build_client(payload)

    response = client.get("/data")
    # JSONResponse renders with compact separators; the point of this assertion
    # is that the middleware emits those original bytes rather than a
    # re-serialised copy, which would reorder/reformat for no reason.
    assert response.content == json.dumps(payload, separators=(",", ":")).encode("utf-8")


def test_redaction_failure_is_logged_without_pii(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Failures must be observable, but must not echo the scanned values."""
    secret = "alice@example.com"
    client = build_client({"email": secret})

    from modules.data_guardian.detection_rules import PIIDetector

    monkeypatch.setattr(
        PIIDetector,
        "scan_dict",
        lambda self, d: (_ for _ in ()).throw(RuntimeError(f"failed on {secret}")),
        raising=False,
    )

    with caplog.at_level("WARNING"):
        response = client.get("/data")

    assert response.json() == {"email": secret}
    logged = " ".join(record.getMessage() for record in caplog.records)
    assert "response-redaction" in logged, "failure was not reported at all"
    assert secret not in logged, "exception message leaked the PII value into logs"
