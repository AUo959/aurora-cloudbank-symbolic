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


def gate(issue=1558):
    return {
        "gate_id": f"gate-{issue}", "github_issue": issue,
        "opened": "2026-09-01", "last_surfaced": "2026-09-28",
        "days_since_surfaced": 12, "escalation_tier": 1,
    }


def test_partial_notification_failure_retries_only_undelivered_gates(monkeypatch):
    comments, attempts = {}, []
    fail_once = True

    def gh(*args):
        nonlocal fail_once
        if args[0] == "api":
            return json.dumps({"state": "open"})
        issue = int(args[2])
        attempts.append(issue)
        if issue == 1559 and fail_once:
            fail_once = False
            raise RuntimeError("delivery failed")
        comments.setdefault(issue, []).append({
            "user": {"login": "github-actions[bot]"}, "body": args[-1],
        })
        return ""

    monkeypatch.setattr(publisher, "gh", gh)
    monkeypatch.setattr(publisher, "pages", lambda endpoint: comments.get(int(endpoint.split("/")[4]), []))
    report = {"escalations": [gate(), gate(1559)], "threshold_days": 3, "ungated_decisions": []}
    with pytest.raises(RuntimeError, match="delivery failed"):
        publisher.notify_escalations(REPO, report)
    publisher.notify_escalations(REPO, report)
    # Also covers successful delivery followed by failed PR creation: same baseline.
    publisher.notify_escalations(REPO, report)
    assert attempts == [1558, 1559, 1559]


def test_marker_changes_only_when_registry_baseline_changes():
    original = gate()
    retry = {**original, "days_since_surfaced": 19}
    next_cycle = {**original, "last_surfaced": "2026-10-10"}
    assert publisher.escalation_marker(original) == publisher.escalation_marker(retry)
    assert publisher.escalation_marker(original) != publisher.escalation_marker(next_cycle)


def test_non_bot_marker_does_not_suppress_delivery(monkeypatch):
    calls = []
    monkeypatch.setattr(publisher, "gh", lambda *args: calls.append(args) or json.dumps({"state": "open"}))
    monkeypatch.setattr(publisher, "pages", lambda endpoint: [{
        "user": {"login": "owner"}, "body": publisher.escalation_marker(gate()),
    }])
    publisher.notify_gate(REPO, gate(), 3)
    assert calls[-1][:5] == ("issue", "comment", "1558", "--repo", REPO)


def test_comment_lookup_error_prevents_posting(monkeypatch):
    calls = []
    monkeypatch.setattr(publisher, "gh", lambda *args: calls.append(args) or json.dumps({"state": "open"}))

    def fail(endpoint):
        raise RuntimeError("comments unavailable")

    monkeypatch.setattr(publisher, "pages", fail)
    with pytest.raises(RuntimeError, match="comments unavailable"):
        publisher.notify_gate(REPO, gate(), 3)
    assert all(c[0] == "api" for c in calls)


def test_closed_issue_is_not_notified(monkeypatch):
    calls = []
    monkeypatch.setattr(publisher, "gh", lambda *args: calls.append(args) or json.dumps({"state": "closed"}))
    monkeypatch.setattr(publisher, "pages", lambda endpoint: pytest.fail("closed issue comments read"))
    publisher.notify_gate(REPO, gate(), 3)
    assert len(calls) == 1


def test_notification_cli_uses_report_without_pr_dispatch(monkeypatch, tmp_path):
    report = tmp_path / "report.json"
    payload = {"escalations": [], "threshold_days": 3, "ungated_decisions": []}
    report.write_text(json.dumps(payload))
    monkeypatch.setenv("GITHUB_REPOSITORY", REPO)
    monkeypatch.setattr("sys.argv", ["publish_queue_pr.py", "--kind", "escalation",
                                    "--notify-escalations", str(report)])
    calls = []
    monkeypatch.setattr(publisher, "notify_escalations", lambda *args: calls.append(args))
    monkeypatch.setattr(publisher, "pages", lambda endpoint: pytest.fail("PR lookup during notification"))
    assert publisher.main() == 0
    assert calls == [(REPO, payload)]
