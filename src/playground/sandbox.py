"""Docker-based sandbox runners for Python and Node execution."""
from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import Dict, Optional

from .models import ExecutionLanguage, ExecutionResult
from .pii import redact

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional docker runtime
    import docker
except Exception:  # pragma: no cover
    docker = None


DOCKER_LIMITS = {
    "mem_limit": os.getenv("PLAYGROUND_MEM_LIMIT", "512m"),
    "cpu_period": 100000,
    "cpu_quota": int(os.getenv("PLAYGROUND_CPU_QUOTA", "100000")),
    "network_disabled": True,
    "stdin_open": True,
    "tty": False,
    "read_only": True,
}

PYTHON_IMAGE = os.getenv("PLAYGROUND_PYTHON_IMAGE", "python:3.11-slim")
NODE_IMAGE = os.getenv("PLAYGROUND_NODE_IMAGE", "node:20-slim")


class SandboxDockerRunner:
    """Execute untrusted code inside a constrained Docker container."""

    def __init__(self):
        self.client = None
        if docker is None:
            logger.warning("Docker SDK unavailable; Playground execution disabled")
        else:
            try:
                self.client = docker.from_env()
            except Exception:
                logger.exception("Docker client unavailable; Playground execution disabled")

    def _container_command(self, language: ExecutionLanguage, code: str, stdin: Optional[str]) -> Dict[str, str]:
        if language == ExecutionLanguage.python:
            entrypoint = ["python", "-c", code]
            input_data = stdin or ""
            image = PYTHON_IMAGE
        else:
            entrypoint = ["node", "-e", code]
            input_data = stdin or ""
            image = NODE_IMAGE
        return {"image": image, "input_data": input_data, "entrypoint": entrypoint}

    def _run_docker(self, language: ExecutionLanguage, code: str, stdin: Optional[str]) -> ExecutionResult:
        task_id = str(uuid.uuid4())
        command = self._container_command(language, code, stdin)
        if not self.client:
            logger.warning("Isolated sandbox unavailable; refusing Playground execution")
            return ExecutionResult(
                task_id=task_id,
                session_id="",
                status="failed",
                output="",
                errors=["sandbox_unavailable"],
                started_at=0.0,
            )

        container = None
        try:
            container = self.client.containers.run(
                command["image"],
                command["entrypoint"],
                mem_limit=DOCKER_LIMITS["mem_limit"],
                network_disabled=DOCKER_LIMITS["network_disabled"],
                cpu_period=DOCKER_LIMITS["cpu_period"],
                cpu_quota=DOCKER_LIMITS["cpu_quota"],
                stdin_open=True,
                tty=False,
                remove=True,
                environment={"PYTHONUNBUFFERED": "1"},
                working_dir="/sandbox",
            )
            if command["input_data"]:
                container.exec_run("/bin/sh", stdin=True, socket=True)
            output = container.logs(stdout=True, stderr=True).decode("utf-8", errors="ignore")
            redacted_output = redact(output)
            return ExecutionResult(
                task_id=task_id,
                session_id="",
                status="completed",
                output=output,
                redacted_output=redacted_output,
                errors=[],
                started_at=0.0,
            )
        except Exception as exc:  # pragma: no cover
            logger.error("Docker execution failed: %s", exc)
            return ExecutionResult(
                task_id=task_id,
                session_id="",
                status="failed",
                output="",
                errors=[str(exc)],
                started_at=0.0,
            )
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass

    async def run(self, language: ExecutionLanguage, code: str, stdin: Optional[str]) -> ExecutionResult:
        return await asyncio.to_thread(self._run_docker, language, code, stdin)


async def run_sandbox(language: str, code: str, stdin: Optional[str] = None) -> ExecutionResult:
    runner = SandboxDockerRunner()
    return await runner.run(ExecutionLanguage(language), code, stdin)
