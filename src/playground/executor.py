"""Execution queue abstraction supporting RQ or inline async workers."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from typing import Optional

from fastapi import BackgroundTasks

from .metrics import execution_counter, execution_errors, execution_latency
from .models import ExecutionLanguage, ExecutionResult, ExecutionStatusResponse
from .pii import redact
from .sandbox import SandboxDockerRunner
from .storage import SessionStore

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from rq import Queue
except Exception:  # pragma: no cover
    Queue = None


class ExecutionQueue:
    """Dispatch execution requests to a queue backend or local worker."""

    def __init__(self, store: SessionStore):
        self.store = store
        self.runner = SandboxDockerRunner()
        self.queue: Optional[Queue] = None
        if Queue and store.redis:
            try:
                self.queue = Queue("playground-executor", connection=store.redis)
                logger.info("✅ Playground RQ queue configured")
            except Exception as exc:  # pragma: no cover
                logger.warning("⚠️ Unable to initialise RQ queue: %s", exc)
                self.queue = None

    def _record_metrics(self, language: ExecutionLanguage, duration: float, success: bool):
        execution_counter.labels(language=language.value).inc()
        execution_latency.labels(language=language.value).observe(duration)
        if not success:
            execution_errors.labels(language=language.value).inc()

    async def _execute_inline(
        self, session_id: str, code: str, language: ExecutionLanguage, stdin: Optional[str]
    ) -> ExecutionResult:
        started = time.time()
        result = await self.runner.run(language, code, stdin)
        result.started_at = started
        result.completed_at = time.time()
        result.duration_ms = (result.completed_at - started) * 1000
        result.session_id = session_id
        result.redacted_output = redact(result.output)
        self._record_metrics(language, result.duration_ms / 1000, result.status == "completed")
        return result

    async def enqueue(
        self,
        session_id: str,
        code: str,
        language: ExecutionLanguage,
        stdin: Optional[str],
        background_tasks: BackgroundTasks,
    ) -> str:
        task_id = str(uuid.uuid4())
        if self.queue:
            try:
                job = self.queue.enqueue(
                    "src.playground.sandbox.run_sandbox",
                    language.value,
                    code,
                    stdin,
                    job_timeout=35,
                )
                return job.id
            except Exception as exc:  # pragma: no cover
                logger.warning("RQ enqueue failed, falling back to inline: %s", exc)

        async def runner_task():
            result = await self._execute_inline(session_id, code, language, stdin)
            self.store.save_result(session_id, result.dict())
            await self.store.publish_event(
                session_id,
                {
                    "event": "completed",
                    "session_id": session_id,
                    "task_id": task_id,
                    "payload": result.dict(),
                },
            )

        background_tasks.add_task(asyncio.create_task, runner_task())
        return task_id

    def get_status(self, session_id: str, task_id: str) -> ExecutionStatusResponse:
        stored = self.store.get_result(session_id)
        if stored and stored.get("task_id") == task_id:
            return ExecutionStatusResponse(
                task_id=task_id,
                session_id=session_id,
                status=stored.get("status", "pending"),
                result=ExecutionResult(**stored),
            )
        return ExecutionStatusResponse(task_id=task_id, session_id=session_id, status="pending")
