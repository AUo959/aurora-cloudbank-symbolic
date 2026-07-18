"""
Tests for ops/work_queue/ingest_issues.py — the #1131 "Sync script" item.

Pure-function coverage of the ingestion core (no network, no gh): label
filtering, dedup/idempotency, tail-rank placement preserving Aurora's
rank authority, advisory scoring from triage_rules.json, and schema
validity of the resulting queue.

Runs standalone (stdlib + jsonschema only) so queue-validation.yml can
execute it with --noconftest alongside test_work_queue_schema.py.
"""

import json
from pathlib import Path

import jsonschema

from ops.work_queue.ingest_issues import (
    INGEST_LABELS,
    build_entries,
    known_issue_numbers,
    score_issue,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
WORK_QUEUE = REPO_ROOT / "ops" / "work_queue"


def _rules():
    return json.loads((WORK_QUEUE / "triage_rules.json").read_text())["rules"]


def _queue():
    return {
        "_meta": {
            "version": "test",
            "description": "test queue",
            "last_aurora_review": "2026-07-17T00:00:00Z",
            "schema": "ops/work_queue/queue_schema.json",
        },
        "active": [
            {"rank": 1, "id": "security/CVE-audit", "title": "CVE audit", "status": "open"},
            {"rank": 2, "id": "arch/layer-canonization", "title": "Layers (#1234)", "status": "open"},
        ],
        "completed": [
            {"id": "#1126", "title": "Recovered protocols manifest decision",
             "status": "done", "closed": "2026-06-24"},
        ],
    }


def _issue(number, title="Test issue", labels=("blocking",), state="OPEN"):
    return {
        "number": number,
        "title": title,
        "labels": [{"name": name} for name in labels],
        "state": state,
    }


def test_label_filter_only_ingests_roadmap_labels():
    assert INGEST_LABELS == {"blocking", "security"}
    issues = [
        _issue(2001, labels=("blocking",)),
        _issue(2002, labels=("security",)),
        _issue(2003, labels=("enhancement",)),  # not in scope
        _issue(2004, labels=()),                # unlabeled
    ]
    entries = build_entries(issues, _queue(), _rules(), today="2026-07-17")
    assert {e["github_issue"] for e in entries} == {2001, 2002}


def test_dedup_covers_ids_titles_and_github_issue_fields():
    known = known_issue_numbers(_queue())
    # '#1126' completed id and '(#1234)' title reference both count
    assert 1126 in known and 1234 in known

    issues = [_issue(1126), _issue(1234), _issue(2005)]
    entries = build_entries(issues, _queue(), _rules(), today="2026-07-17")
    assert [e["github_issue"] for e in entries] == [2005]


def test_idempotent_rerun_is_a_noop():
    queue = _queue()
    issues = [_issue(2006, labels=("blocking", "security"))]
    first = build_entries(issues, queue, _rules(), today="2026-07-17")
    assert len(first) == 1
    queue["active"] += first
    second = build_entries(issues, queue, _rules(), today="2026-07-17")
    assert second == []


def test_tail_rank_placement_never_touches_existing_order():
    queue = _queue()
    issues = [
        _issue(2007, labels=("security",)),              # score 30
        _issue(2008, labels=("blocking", "security")),   # score 70 — first among new
    ]
    entries = build_entries(issues, queue, _rules(), today="2026-07-17")
    # Existing max rank is 2; new entries take 3 and 4, score-ordered
    assert [(e["rank"], e["github_issue"]) for e in entries] == [(3, 2008), (4, 2007)]
    assert all(e["aurora_authority"] is False for e in entries)
    assert all("awaiting Aurora triage" in e["aurora_note"] for e in entries)


def test_scoring_matches_triage_rules():
    rules = _rules()
    assert score_issue({"blocking"}, rules) == (40, ["TR-01"])
    assert score_issue({"security"}, rules) == (30, ["TR-02"])
    assert score_issue({"pentest"}, rules) == (30, ["TR-02"])
    assert score_issue({"blocking", "security", "architecture"}, rules) == (
        95, ["TR-01", "TR-02", "TR-03"]
    )


def test_closed_issues_are_skipped():
    entries = build_entries(
        [_issue(2009, state="CLOSED")], _queue(), _rules(), today="2026-07-17"
    )
    assert entries == []


def test_ingested_queue_validates_against_schema():
    schema = json.loads((WORK_QUEUE / "queue_schema.json").read_text())
    queue = _queue()
    queue["active"] += build_entries(
        [_issue(2010, labels=("blocking",)), _issue(2011, labels=("security",))],
        queue, _rules(), today="2026-07-17",
    )
    errors = list(jsonschema.Draft7Validator(schema).iter_errors(queue))
    assert errors == [], [e.message for e in errors]


def test_live_queue_plus_ingestion_validates_against_schema():
    """The real queue.json with a synthetic ingestion must stay schema-valid."""
    schema = json.loads((WORK_QUEUE / "queue_schema.json").read_text())
    queue = json.loads((WORK_QUEUE / "queue.json").read_text())
    entries = build_entries(
        [_issue(9999, labels=("blocking",))], queue, _rules(), today="2026-07-17"
    )
    assert len(entries) == 1
    queue["active"] += entries
    errors = list(jsonschema.Draft7Validator(schema).iter_errors(queue))
    assert errors == [], [e.message for e in errors]
