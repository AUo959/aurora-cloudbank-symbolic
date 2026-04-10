#!/usr/bin/env python3
"""
Regression tests for command-chain entrypoints.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

from tools.command_chain.cmd_commit import execute_commit
from tools.command_chain.comprehensive_sync_321 import execute_321, resolve_config_path
from tools.command_chain.executor import CommandExecutor


@pytest.fixture
def temp_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)

        (repo_path / "sample.txt").write_text("alpha\n")
        subprocess.run(["git", "add", "sample.txt"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True, capture_output=True)

        yield repo_path


def _append_change(repo_path: Path):
    with (repo_path / "sample.txt").open("a") as handle:
        handle.write("beta\n")


def test_resolve_config_path_does_not_leak_caller_cwd(monkeypatch, temp_git_repo):
    caller_dir = temp_git_repo / "caller"
    caller_config = caller_dir / ".aurora"
    caller_config.mkdir(parents=True)
    (caller_config / "sync_config.json").write_text('{"default_commit_type": "docs"}')

    monkeypatch.chdir(caller_dir)

    assert resolve_config_path(workspace_path=str(temp_git_repo)) is None


def test_execute_commit_creates_local_commit(temp_git_repo):
    _append_change(temp_git_repo)

    result = execute_commit(workspace_path=str(temp_git_repo))

    assert result.success is True
    assert result.commit_sha
    commit_count = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=temp_git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert commit_count.stdout.strip() == "2"


def test_execute_321_preserves_partial_commit_metadata_on_sync_failure(temp_git_repo):
    _append_change(temp_git_repo)

    result = execute_321(workspace_path=str(temp_git_repo))

    assert result.success is False
    assert result.commit_sha
    assert result.files_changed == 1
    assert any(phase.phase_number == 4 and not phase.success for phase in result.phases)

    commit_count = subprocess.run(
        ["git", "rev-list", "--count", "HEAD"],
        cwd=temp_git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert commit_count.stdout.strip() == "2"


def test_command_executor_imports_under_current_python(temp_git_repo):
    executor = CommandExecutor(str(temp_git_repo))
    assert executor is not None


def test_command_executor_reports_handler_failure_for_sync_workflow(temp_git_repo):
    _append_change(temp_git_repo)

    result = CommandExecutor(str(temp_git_repo)).execute("#321//.")

    assert result.success is False
    assert result.failed_commands == 1
    assert result.results[0].success is False
    assert result.results[0].output["status"] in {"failed", "partial", "warning"}
