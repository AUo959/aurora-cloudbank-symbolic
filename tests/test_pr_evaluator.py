"""Tests for tools/pr_evaluator.py (#1342).

#1342 found the evaluator had no tests at all while being made a blocking gate.
These cover the four behaviours that produced false failures on PR #1339:

* evidence scoped to the diff, not the whole repository;
* no duplicate full-suite run under an unmeetable timeout;
* traceability judged on the author's commit, not GitHub's synthetic merge;
* JSON output shape stable enough to act on.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from pr_evaluator import PREvaluator  # noqa: E402


@pytest.fixture
def evaluator(tmp_path: Path) -> PREvaluator:
    return PREvaluator(workspace_root=str(tmp_path))


# ---------------------------------------------------------------- scoping

def test_changed_python_files_only_returns_changed_py(evaluator, tmp_path):
    """Non-Python and untouched files must not become evidence."""
    for rel in ("a.py", "b.txt", "pkg/c.py"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x = 1\n")
    (tmp_path / "untouched.py").write_text("x = 1\n")

    got = evaluator.changed_python_files(["a.py", "b.txt", "pkg/c.py"])
    assert got == ["a.py", "pkg/c.py"]
    assert "untouched.py" not in got


def test_changed_python_files_skips_deleted(evaluator, tmp_path):
    """A deleted .py file is in the diff but cannot be compiled."""
    (tmp_path / "kept.py").write_text("x = 1\n")
    assert evaluator.changed_python_files(["kept.py", "gone.py"]) == ["kept.py"]


def test_changed_python_files_skips_vendored(evaluator, tmp_path):
    """Vendored trees must never be scanned."""
    for rel in (".venv/lib/x.py", "node_modules/y.py", "real.py"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x = 1\n")
    assert evaluator.changed_python_files(
        [".venv/lib/x.py", "node_modules/y.py", "real.py"]
    ) == ["real.py"]


def test_syntax_error_in_changed_file_is_caught(evaluator, tmp_path):
    """The gate must still fail on a real defect in the diff."""
    (tmp_path / "broken.py").write_text("def f(:\n")
    result = evaluator._evaluate_technical_quality(["broken.py"])
    assert result.score < 1.0
    assert any("syntax errors" in f.lower() for f in result.findings)


def test_preexisting_error_outside_diff_is_ignored(evaluator, tmp_path):
    """The regression from #1342: unrelated broken files must not fail a PR."""
    (tmp_path / "preexisting_broken.py").write_text("def f(:\n")
    (tmp_path / "clean.py").write_text("x = 1\n")

    result = evaluator._evaluate_technical_quality(["clean.py"])
    assert result.passed, "a clean PR failed because of a file it never touched"


def test_no_python_changes_scores_clean(evaluator, tmp_path):
    """A docs-only PR must not be penalised for Python evidence."""
    (tmp_path / "README.md").write_text("# hi\n")
    result = evaluator._evaluate_technical_quality(["README.md"])
    assert result.passed
    assert result.score == 1.0


# ------------------------------------------------------------ test running

def test_no_changed_tests_applies_no_penalty(evaluator, tmp_path):
    """Previously the full suite ran and timed out here, costing every PR 0.25."""
    (tmp_path / "src.py").write_text("x = 1\n")
    findings, recs, evidence = [], [], []
    penalty = evaluator._evaluate_changed_tests(["src.py"], evidence, findings, recs)

    assert penalty == 0.0
    signals = {e.signal for e in evidence}
    assert "pytest_changed" in signals
    assert any("aurora-ci-minimal" in e.evidence for e in evidence), (
        "evidence should say where the authoritative gate actually is"
    )


def test_changed_test_file_is_executed(evaluator, tmp_path):
    """A changed test that fails must produce a penalty."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_fails():\n    assert False\n")

    findings, recs, evidence = [], [], []
    penalty = evaluator._evaluate_changed_tests(
        ["tests/test_x.py"], evidence, findings, recs
    )
    assert penalty > 0.0
    assert "Fix failing tests before merge" in recs


def test_changed_passing_test_costs_nothing(evaluator, tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_ok():\n    assert True\n")

    findings, recs, evidence = [], [], []
    penalty = evaluator._evaluate_changed_tests(
        ["tests/test_x.py"], evidence, findings, recs
    )
    assert penalty == 0.0


# ------------------------------------------------------------- traceability

def init_repo(path: Path, message: str) -> None:
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=path, check=True)
    (path / "f.txt").write_text("x")
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=path, check=True)


def test_traceability_uses_head_when_not_synthetic(evaluator, tmp_path):
    init_repo(tmp_path, "fix: something real (#123)")
    assert "fix: something real" in evaluator._traceability_commit_message()


def test_synthetic_merge_message_is_detected(evaluator):
    """The exact shape GitHub generates on pull_request events."""
    assert evaluator._SYNTHETIC_MERGE_RE.match("Merge a1b2c3d4e5f into 9876543210a")
    assert not evaluator._SYNTHETIC_MERGE_RE.match("fix: a real commit (#1)")
    assert not evaluator._SYNTHETIC_MERGE_RE.match("Merge branch 'main' into feature")


def test_traceability_falls_back_past_synthetic_merge(evaluator, tmp_path, monkeypatch):
    """A traceable PR must not be marked untraceable by the merge commit."""
    init_repo(tmp_path, "fix: real work (#42)")
    subprocess.run(["git", "checkout", "-q", "-b", "feature"], cwd=tmp_path, check=True)
    (tmp_path / "g.txt").write_text("y")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "feat: authored change (#42)"], cwd=tmp_path, check=True
    )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(["git", "checkout", "-q", "master"], cwd=tmp_path, check=False)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=tmp_path, check=False)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(
        ["git", "merge", "--no-ff", "-q", "-m", f"Merge {head} into {base}", "feature"],
        cwd=tmp_path, check=True,
    )
    monkeypatch.delenv("GITHUB_HEAD_REF", raising=False)

    message = evaluator._traceability_commit_message()
    assert "authored change" in message, (
        "fell back to the synthetic merge instead of the PR head"
    )


# --------------------------------------------------------------- json shape

def test_evaluate_pr_json_shape(tmp_path, monkeypatch):
    """Consumers parse this; the top-level keys must stay stable."""
    init_repo(tmp_path, "chore: init (#1)")
    monkeypatch.delenv("GITHUB_BASE_REF", raising=False)
    payload = PREvaluator(workspace_root=str(tmp_path)).evaluate_pr()

    for key in (
        "overall_score", "passed", "recommendation", "changed_files",
        "actionable_findings", "results", "score_model",
    ):
        assert key in payload, f"missing top-level key: {key}"
    assert 0.0 <= payload["overall_score"] <= 1.0
    assert isinstance(payload["results"], list) and payload["results"]
    for result in payload["results"]:
        assert {"category", "passed", "score", "weight", "evidence"} <= set(result)
