"""Playground FastAPI endpoints for sessions, execution, sharing, and streams."""
from __future__ import annotations

import secrets
import time
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .executor import ExecutionQueue
from .limiter import get_rate_limiter
from .metrics import sessions_gauge
from .models import (
    ExecuteRequest,
    ExecutionStatusResponse,
    PlaygroundHealth,
    SessionCreateRequest,
    SessionCreateResponse,
    ShareRequest,
    ShareResponse,
    StreamMessage,
)
from .storage import SessionStore

router = APIRouter(prefix="/playground", tags=["playground"])
store = SessionStore()
rate_limiter = get_rate_limiter(store)
queue = ExecutionQueue(store)


async def _broadcast(session_id: str, payload: Dict[str, Any]):
    await store.publish_event(session_id, payload)


@router.post("/session", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest) -> SessionCreateResponse:
    session_id = secrets.token_urlsafe(12)
    sessions_gauge.inc()
    payload = store.create_session(
        session_id,
        {"language": request.language.value, "metadata": request.metadata, "seed_code": request.seed_code},
    )
    await _broadcast(session_id, {"event": "session_created", "session_id": session_id, "payload": payload})
    return SessionCreateResponse(session_id=session_id, expires_at=payload["expires_at"])


@router.post("/execute", response_model=ExecutionStatusResponse)
async def execute_code(
    request: Request, body: ExecuteRequest, background_tasks: BackgroundTasks
) -> ExecutionStatusResponse:
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.enforce(client_ip)
    session_id = body.session_id or secrets.token_urlsafe(12)
    existing = store.get_session(session_id)
    if not existing:
        store.create_session(session_id, {"language": body.language.value, "metadata": {}, "seed_code": None})
    await _broadcast(session_id, {"event": "started", "session_id": session_id})
    task_id = await queue.enqueue(session_id, body.code, body.language, body.stdin, background_tasks)
    return queue.get_status(session_id, task_id)


@router.get("/results/{session_id}", response_model=ExecutionStatusResponse)
async def get_results(session_id: str, task_id: str) -> ExecutionStatusResponse:
    return queue.get_status(session_id, task_id)


@router.post("/share", response_model=ShareResponse)
async def share_session(body: ShareRequest, request: Request) -> ShareResponse:
    session = store.get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    short_code = secrets.token_urlsafe(6)
    share_payload = {
        "session_id": body.session_id,
        "code": body.code,
        "language": body.language.value,
        "created_at": time.time(),
    }
    store.set_share_code(short_code, share_payload)
    base_url = str(request.base_url).rstrip("/")
    share_url = f"{base_url}/playground/share/{short_code}"
    embed_html = f"<iframe src=\"{share_url}\" title=\"Aurora Playground\" loading=\"lazy\"></iframe>"
    await _broadcast(
        body.session_id,
        {"event": "shared", "session_id": body.session_id, "payload": {"short_code": short_code}},
    )
    return ShareResponse(short_code=short_code, session_id=body.session_id, url=share_url, embed_html=embed_html)


@router.get("/share/{short_code}")
async def fetch_shared(short_code: str):
    payload = store.get_share_code(short_code)
    if not payload:
        raise HTTPException(status_code=404, detail="Shared snippet not found")
    return payload


@router.get("/health", response_model=PlaygroundHealth)
async def healthcheck() -> PlaygroundHealth:
    redis_status = "redis" if store.redis else "memory"
    queue_summary = {
        "executor": "rq" if queue.queue else "inline",
        "backend_available": bool(queue.queue),
        "queue_name": "playground-executor",
        "sandbox_ready": queue.runner is not None,
    }
    return PlaygroundHealth(
        sessions_backend=redis_status,
        queue=queue_summary,
        redis_connected=bool(store.redis),
        ttl_seconds=store.ttl_seconds,
    )


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        async for payload in store.stream_events(session_id):
            message = StreamMessage(**payload)
            await websocket.send_json(message.dict())
    except WebSocketDisconnect:
        # Client disconnected from WebSocket; no action needed.
        pass


@router.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
