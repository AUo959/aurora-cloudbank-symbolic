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

    if resolve_config_path(workspace_path=str(temp_git_repo)) is not None:
        pytest.fail("Expected workspace config lookup to ignore caller CWD config")


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

    if resolved != workspace_config:
        pytest.fail(f"Expected workspace-scoped config, got {resolved}")


def test_execute_commit_creates_local_commit(temp_git_repo):
    _append_change(temp_git_repo)

    result = execute_commit(workspace_path=str(temp_git_repo))

    if not result.success:
        pytest.fail("Expected execute_commit to succeed")
    if not result.commit_sha:
        pytest.fail("Expected execute_commit to return a commit SHA")
    commit_count = subprocess.run(  # nosec
        ["git", "rev-list", "--count", "HEAD"],
        cwd=temp_git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    if commit_count.stdout.strip() != "2":
        pytest.fail(f"Expected two commits, got {commit_count.stdout.strip()}")


def test_execute_321_preserves_partial_commit_metadata_on_sync_failure(temp_git_repo):
    _append_change(temp_git_repo)

    result = execute_321(workspace_path=str(temp_git_repo))

    if result.success:
        pytest.fail("Expected execute_321 to fail during sync without origin")
    if not result.commit_sha:
        pytest.fail("Expected execute_321 to preserve the local commit SHA")
    if result.files_changed != 1:
        pytest.fail(f"Expected one changed file, got {result.files_changed}")
    if not any(phase.phase_number == 4 and not phase.success for phase in result.phases):
        pytest.fail("Expected execute_321 to preserve the phase 4 sync failure")

    commit_count = subprocess.run(  # nosec
        ["git", "rev-list", "--count", "HEAD"],
        cwd=temp_git_repo,
        check=True,
        capture_output=True,
        text=True,
    )
    if commit_count.stdout.strip() != "2":
        pytest.fail(f"Expected two commits, got {commit_count.stdout.strip()}")


def test_command_executor_imports_under_current_python(temp_git_repo):
    executor = CommandExecutor(str(temp_git_repo))
    if executor is None:
        pytest.fail("Expected CommandExecutor to import and instantiate")


def test_command_executor_treats_continuity_accept_as_success(temp_git_repo):
    result = CommandExecutor(str(temp_git_repo)).execute("#999//.")

    if not result.success:
        pytest.fail("Continuity accept should be treated as a successful command")
    if result.failed_commands != 0:
        pytest.fail(f"Expected no failed commands, got {result.failed_commands}")
    if not result.results[0].success:
        pytest.fail("Continuity accept result should be successful")
    if result.results[0].output["status"] != "sealed":
        pytest.fail(f"Expected sealed status, got {result.results[0].output['status']}")


def test_command_executor_reports_handler_failure_for_sync_workflow(temp_git_repo):
    _append_change(temp_git_repo)

    result = CommandExecutor(str(temp_git_repo)).execute("#321//.")

    if result.success:
        pytest.fail("Expected #321//. sync workflow to fail without origin")
    if result.failed_commands != 1:
        pytest.fail(f"Expected one failed command, got {result.failed_commands}")
    if result.results[0].success:
        pytest.fail("Expected #321//. command result to fail without origin")
    if result.results[0].output["status"] not in {"failed", "partial", "warning"}:
        pytest.fail(f"Expected failure-like status, got {result.results[0].output['status']}")
