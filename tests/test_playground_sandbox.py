"""Playground isolation failures must never execute submitted code on the host."""

import subprocess
from unittest.mock import Mock

import pytest

from tests._slowapi_stub import install_slowapi_stub

install_slowapi_stub()

from src.playground import sandbox  # noqa: E402
from src.playground.models import ExecutionLanguage  # noqa: E402

pytestmark = [pytest.mark.unit, pytest.mark.security, pytest.mark.regression]


@pytest.fixture(autouse=True)
def host_execution(monkeypatch):
    host_run = Mock(side_effect=AssertionError("Submitted code reached the host"))
    monkeypatch.setattr(subprocess, "run", host_run)
    yield host_run
    host_run.assert_not_called()


@pytest.mark.parametrize("language", list(ExecutionLanguage))
@pytest.mark.parametrize("failure", ["sdk_missing", "client_unavailable"])
async def test_unavailable_sandbox_refuses_execution(monkeypatch, language, failure):
    docker = None
    if failure == "client_unavailable":
        docker = Mock()
        docker.from_env.side_effect = RuntimeError("Docker daemon unavailable")
    monkeypatch.setattr(sandbox, "docker", docker)

    result = await sandbox.run_sandbox(language.value, "submitted code")

    assert result.status == "failed"
    assert result.errors == ["sandbox_unavailable"]
    assert result.output == ""
    assert result.task_id


@pytest.mark.parametrize("language", list(ExecutionLanguage))
async def test_container_start_failure_never_uses_host(monkeypatch, language):
    client = Mock()
    client.containers.run.side_effect = RuntimeError("Docker unavailable at execution")
    monkeypatch.setattr(sandbox, "docker", Mock(from_env=Mock(return_value=client)))

    result = await sandbox.run_sandbox(language.value, "submitted code")

    assert result.status == "failed"
    assert result.errors == ["Docker unavailable at execution"]
    assert result.output == ""
    client.containers.run.assert_called_once()


@pytest.mark.parametrize("language", list(ExecutionLanguage))
async def test_available_sandbox_uses_container(monkeypatch, language):
    container = Mock()
    container.logs.return_value = b"container output"
    client = Mock()
    client.containers.run.return_value = container
    monkeypatch.setattr(sandbox, "docker", Mock(from_env=Mock(return_value=client)))

    result = await sandbox.run_sandbox(language.value, "submitted code")

    assert result.status == "completed"
    assert result.output == "container output"
    assert result.errors == []
    client.containers.run.assert_called_once_with(
        sandbox.PYTHON_IMAGE if language == ExecutionLanguage.python else sandbox.NODE_IMAGE,
        ["python", "-c", "submitted code"] if language == ExecutionLanguage.python
        else ["node", "-e", "submitted code"],
        mem_limit=sandbox.DOCKER_LIMITS["mem_limit"],
        network_disabled=True,
        cpu_period=sandbox.DOCKER_LIMITS["cpu_period"],
        cpu_quota=sandbox.DOCKER_LIMITS["cpu_quota"],
        stdin_open=True,
        tty=False,
        remove=True,
        environment={"PYTHONUNBUFFERED": "1"},
        working_dir="/sandbox",
    )
    container.remove.assert_called_once_with(force=True)
