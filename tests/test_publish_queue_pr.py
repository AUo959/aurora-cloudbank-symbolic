"""Queue PR lifecycle regressions; all GitHub commands are mocked."""

import json

import pytest

from scripts import publish_queue_pr as publisher


REPO = "AUo959/aurora-cloudbank-symbolic"
SHA = "a" * 40


def proposal(number=1626, kind="ingestion"):
    prefix = "auto-ingest" if kind == "ingestion" else "escalation-surfaced"
    return {
        "number": number,
        "state": "open",
        "base": {"ref": "main"},
        "user": {"login": "github-actions[bot]"},
        "head": {
            "ref": f"queue/{prefix}-20261005-0634",
            "sha": SHA,
            "repo": {"full_name": REPO},
        },
    }


def test_latest_pending_generation_is_reused():
    other = proposal(1627, "escalation")
    assert publisher.select_pending([proposal(1611), other, proposal()], "ingestion", REPO)["number"] == 1626


def test_unrelated_prs_do_not_block_generation():
    pr = proposal()
    pr["head"]["ref"] = "codex/queue-repair"
    assert publisher.select_pending([pr], "ingestion", REPO) is None


@pytest.mark.parametrize("field,value", [
    ("author", "owner"), ("repo", "fork/aurora-cloudbank-symbolic"),
    ("repo", None), ("base", "develop"), ("state", "closed"), ("sha", "not-a-sha"),
])
def test_unsafe_matching_proposal_stops_publication(field, value):
    pr = proposal()
    if field == "author":
        pr["user"]["login"] = value
    elif field == "repo":
        pr["head"]["repo"] = {"full_name": value} if value else None
    elif field == "base":
        pr["base"]["ref"] = value
    elif field == "sha":
        pr["head"]["sha"] = value
    else:
        pr[field] = value
    with pytest.raises(ValueError, match="Untrusted"):
        publisher.select_pending([pr], "ingestion", REPO)


@pytest.mark.parametrize("files", [
    [], [{"filename": ".github/workflows/aurora-ci-minimal.yml", "status": "modified"}],
    [{"filename": "ops/work_queue/queue.json", "status": "removed"}],
    [{"filename": "ops/work_queue/queue.json", "status": "renamed"}],
])
def test_dispatch_refuses_empty_or_unexpected_diff(files):
    with pytest.raises(ValueError, match="scope"):
        publisher.validate_files(files, "ingestion")


def test_generated_view_scope_is_supported():
    publisher.validate_files([
        {"filename": "ops/work_queue/gate_registry.json", "status": "modified"},
        {"filename": "ops/work_queue/OPEN_GATES.md", "status": "modified"},
    ], "escalation")


def test_paginated_pr_lists_are_not_truncated(monkeypatch):
    monkeypatch.setattr(publisher, "gh", lambda *args: json.dumps([[proposal(1611)], [proposal()]]))
    assert len(publisher.pages("endpoint")) == 2


def test_missing_checks_dispatch_both_existing_workflows_on_pr_branch(monkeypatch):
    calls = []

    def gh(*args):
        calls.append(args)
        return json.dumps([{"workflow_runs": []}]) if args[0] == "api" else ""

    monkeypatch.setattr(publisher, "gh", gh)
    publisher.dispatch_checks(REPO, proposal())
    dispatched = [c for c in calls if c[0] == "workflow"]
    assert dispatched == [
        ("workflow", "run", w, "--repo", REPO, "--ref", proposal()["head"]["ref"])
        for w in publisher.WORKFLOWS
    ]


@pytest.mark.parametrize("status,conclusion", [
    ("queued", None), ("in_progress", None), ("completed", "success"),
    ("completed", "failure"), ("completed", "cancelled"),
])
def test_existing_dispatch_never_creates_weekly_rerun_churn(monkeypatch, status, conclusion):
    def gh(*args):
        assert args[0] == "api"
        return json.dumps([{"workflow_runs": [{
            "id": 10, "head_sha": SHA, "event": "workflow_dispatch",
            "status": status, "conclusion": conclusion,
        }]}])

    monkeypatch.setattr(publisher, "gh", gh)
    publisher.dispatch_checks(REPO, proposal())


def test_other_head_or_approval_required_pr_run_does_not_hide_missing_dispatch(monkeypatch):
    calls = []

    def gh(*args):
        calls.append(args)
        if args[0] != "api":
            return ""
        return json.dumps([{"workflow_runs": [
            {"id": 10, "head_sha": "b" * 40, "event": "workflow_dispatch"},
            {"id": 11, "head_sha": SHA, "event": "pull_request"},
        ]}])

    monkeypatch.setattr(publisher, "gh", gh)
    publisher.dispatch_checks(REPO, proposal())
    assert len([c for c in calls if c[0] == "workflow"]) == 2


@pytest.mark.parametrize("pending", [False, True])
def test_workflow_output_stops_new_generation_only_for_pending_proposal(monkeypatch, tmp_path, pending):
    output = tmp_path / "outputs"
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr("sys.argv", ["publish_queue_pr.py", "--kind", "ingestion"])

    def pages(endpoint):
        if "/files?" in endpoint:
            return [{"filename": "ops/work_queue/queue.json", "status": "modified"}]
        return [proposal()] if pending else []

    dispatches = []
    monkeypatch.setattr(publisher, "pages", pages)
    monkeypatch.setattr(publisher, "dispatch_checks", lambda *args: dispatches.append(args))
    assert publisher.main() == 0
    assert output.read_text() == f"pending={str(pending).lower()}\n"
    assert len(dispatches) == int(pending)


def test_api_failure_does_not_fall_through_to_new_pr(monkeypatch, tmp_path):
    output = tmp_path / "outputs"
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr("sys.argv", ["publish_queue_pr.py", "--kind", "ingestion"])

    def pages(endpoint):
        raise RuntimeError("GitHub unavailable")

    monkeypatch.setattr(publisher, "pages", pages)
    with pytest.raises(RuntimeError, match="unavailable"):
        publisher.main()
    assert not output.exists()


def test_diff_rejection_does_not_dispatch_or_allow_generation(monkeypatch, tmp_path):
    output = tmp_path / "outputs"
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setattr("sys.argv", ["publish_queue_pr.py", "--kind", "ingestion"])
    monkeypatch.setattr(publisher, "pages", lambda endpoint: [proposal()] if "/files?" not in endpoint else [
        {"filename": "src/runtime.py", "status": "modified"},
    ])
    monkeypatch.setattr(publisher, "dispatch_checks", lambda *args: pytest.fail("unsafe dispatch"))
    with pytest.raises(ValueError, match="scope"):
        publisher.main()
    assert not output.exists()
