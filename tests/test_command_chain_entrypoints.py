#!/usr/bin/env python3
"""
Regression tests for command-chain entrypoints.
"""

import subprocess  # nosec B404
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

        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)  # nosec
        subprocess.run(  # nosec
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(  # nosec
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        (repo_path / "sample.txt").write_text("alpha\n")
        subprocess.run(["git", "add", "sample.txt"], cwd=repo_path, check=True, capture_output=True)  # nosec
        subprocess.run(  # nosec
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

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

    assert resolve_config_path(workspace_path=str(temp_git_repo)) is None, (  # nosec B101
        "Expected workspace config lookup to ignore caller CWD config"
    )


def test_resolve_config_path_prefers_workspace_relative_config(monkeypatch, temp_git_repo):
    caller_dir = temp_git_repo / "caller"
    caller_config = caller_dir / ".aurora"
    caller_config.mkdir(parents=True)
    (caller_config / "sync_config.json").write_text('{"default_commit_type": "docs"}')

    workspace_dir = temp_git_repo / "workspace"
    workspace_config = workspace_dir / ".aurora" / "sync_config.json"
    workspace_config.parent.mkdir(parents=True)
    workspace_config.write_text('{"default_commit_type": "fix"}')

    monkeypatch.chdir(caller_dir)

    resolved = resolve_config_path(
        config_path=".aurora/sync_config.json",
        workspace_path=str(workspace_dir),
    )

    assert resolved == workspace_config, f"Expected workspace-scoped config, got {resolved}"  # nosec B101


def test_execute_commit_creates_local_commit(temp_git_repo):
    _append_change(temp_git_repo)

    result = execute_commit(workspace_path=str(temp_git_repo))

    assert result.success, "Expected execute_commit to succeed"  # nosec B101
    assert result.commit_sha, "Expected execute_commit to return a commit SHA"  # nosec B101
    commit_count = subprocess.run(  # nosec
        ["git", "rev-list", "--count", "HEAD"],
        cwd=temp_git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert commit_count.stdout.strip() == "2", f"Expected two commits, got {commit_count.stdout.strip()}"  # nosec B101


def test_execute_321_preserves_partial_commit_metadata_on_sync_failure(temp_git_repo):
    _append_change(temp_git_repo)

    result = execute_321(workspace_path=str(temp_git_repo))

    assert not result.success, "Expected execute_321 to fail during sync without origin"  # nosec B101
    assert result.commit_sha, "Expected execute_321 to preserve the local commit SHA"  # nosec B101
    assert result.files_changed == 1, f"Expected one changed file, got {result.files_changed}"  # nosec B101
    assert any(phase.phase_number == 4 and not phase.success for phase in result.phases), (  # nosec B101
        "Expected execute_321 to preserve the phase 4 sync failure"
    )

    commit_count = subprocess.run(  # nosec
        ["git", "rev-list", "--count", "HEAD"],
        cwd=temp_git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    assert commit_count.stdout.strip() == "2", f"Expected two commits, got {commit_count.stdout.strip()}"  # nosec B101


def test_command_executor_imports_under_current_python(temp_git_repo):
    CommandExecutor(str(temp_git_repo))


def test_command_executor_treats_continuity_accept_as_success(temp_git_repo):
    result = CommandExecutor(str(temp_git_repo)).execute("#999//.")

    assert result.success, "Continuity accept should be treated as a successful command"  # nosec B101
    assert result.failed_commands == 0, f"Expected no failed commands, got {result.failed_commands}"  # nosec B101
    assert result.results[0].success, "Continuity accept result should be successful"  # nosec B101
    assert result.results[0].output["status"] == "sealed", (  # nosec B101
        f"Expected sealed status, got {result.results[0].output['status']}"
    )


def test_command_executor_reports_handler_failure_for_sync_workflow(temp_git_repo):
    _append_change(temp_git_repo)

    result = CommandExecutor(str(temp_git_repo)).execute("#321//.")

    assert not result.success, "Expected #321//. sync workflow to fail without origin"  # nosec B101
    assert result.failed_commands == 1, f"Expected one failed command, got {result.failed_commands}"  # nosec B101
    assert not result.results[0].success, "Expected #321//. command result to fail without origin"  # nosec B101
    assert result.results[0].output["status"] in {"failed", "partial", "warning"}, (  # nosec B101
        f"Expected failure-like status, got {result.results[0].output['status']}"
    )
