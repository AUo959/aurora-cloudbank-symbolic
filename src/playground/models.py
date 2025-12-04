"""Pydantic schemas and domain types for the Playground backend."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ExecutionLanguage(str, Enum):
    """Supported sandbox languages."""

    python = "python"
    javascript = "javascript"


class SessionCreateRequest(BaseModel):
    language: ExecutionLanguage = Field(..., description="Preferred execution language")
    seed_code: Optional[str] = Field(None, description="Optional starter snippet")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionCreateResponse(BaseModel):
    session_id: str
    expires_at: float


class ExecuteRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Existing session identifier")
    code: str
    language: ExecutionLanguage
    stdin: Optional[str] = None


class ExecutionResult(BaseModel):
    task_id: str
    session_id: str
    status: str
    output: str = ""
    errors: List[str] = Field(default_factory=list)
    started_at: float
    completed_at: Optional[float] = None
    duration_ms: Optional[float] = None
    redacted_output: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionStatusResponse(BaseModel):
    task_id: str
    session_id: str
    status: str
    result: Optional[ExecutionResult] = None


class ShareRequest(BaseModel):
    session_id: str
    code: str
    language: ExecutionLanguage


class ShareResponse(BaseModel):
    short_code: str
    session_id: str
    url: HttpUrl
    embed_html: str


class StreamMessage(BaseModel):
    event: str
    session_id: str
    task_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class QueueSummary(BaseModel):
    executor: str
    backend_available: bool
    queue_name: str
    sandbox_ready: bool


class PlaygroundHealth(BaseModel):
    sessions_backend: str
    queue: QueueSummary
    redis_connected: bool
    ttl_seconds: int
