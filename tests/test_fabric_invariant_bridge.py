"""Fabric-invariant findings must reach the drift response pipeline.

RULING-FABRIC-WIRING (2026-07-21). The enforcement trace in
`reports/analysis/velar_fabric_pass__2026-07-21.md` §2 found the symbolic layer
enforced **zero** fabric invariants semantically: DriftResponder existed but nothing
fabric-aware fed it. These tests pin the bridge that closes that gap.

Severity mapping is the ruling's: VIOLATION -> alert/escalate, GAP -> log/notify.

The load-bearing test here is `test_fabric_violation_does_not_suspend_or_rebaseline`.
A fabric VIOLATION is CRITICAL, and the stock `critical` runbook suspends the agent and
hard-rebaselines. Doing that because a canon record overstates its map placement would
be useless and disruptive — the fault is in the corpus, not in a running agent. The
ruling names no suspend/throttle/rebaseline action, and that must stay true.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.agents.drift_responder import DriftResponder, ResponseStatus  # noqa: E402
from src.monitoring.drift_detector import DriftAlert, DriftLevel, DriftMethod  # noqa: E402
from src.monitoring.fabric_invariant_bridge import (  # noqa: E402
    RUNBOOK_GAP,
    RUNBOOK_VIOLATION,
    dispatch,
    finding_to_alert,
    findings_to_alerts,
    load_findings,
)

VIOLATION = {
    "invariant": "P1", "severity": "VIOLATION", "subject": "loc_khalrix_3",
    "detail": "Entity claims canonical placement but map row is STAGING.",
}
GAP = {
    "invariant": "C1", "severity": "GAP", "subject": "virex_talvaren",
    "detail": "Character capsule has no location_binding field.",
}
INFO = {
    "invariant": "T3", "severity": "INFO", "subject": "somebody",
    "detail": "recent_actions undated.",
}


def test_violation_maps_to_critical_with_its_own_runbook():
    alert = finding_to_alert(VIOLATION)
    assert alert is not None
    assert alert.level is DriftLevel.CRITICAL
    assert alert.metadata["runbook"] == RUNBOOK_VIOLATION


def test_gap_maps_to_warning_with_its_own_runbook():
    alert = finding_to_alert(GAP)
    assert alert is not None
    assert alert.level is DriftLevel.WARNING
    assert alert.metadata["runbook"] == RUNBOOK_GAP


def test_info_findings_are_not_actionable():
    """An INFO finding records an answered question — it warrants no response."""
    assert finding_to_alert(INFO) is None
    assert findings_to_alerts([VIOLATION, GAP, INFO]) != []
    assert len(findings_to_alerts([VIOLATION, GAP, INFO])) == 2


def test_unknown_severity_is_skipped_not_crashed():
    assert finding_to_alert({"severity": "BANANA", "invariant": "X", "subject": "y"}) is None


def test_alert_carries_provenance_back_to_the_finding():
    alert = finding_to_alert(VIOLATION)
    assert alert.metadata["invariant"] == "P1"
    assert alert.metadata["subject"] == "loc_khalrix_3"
    assert "fabric_invariants_check" in alert.metadata["source"]
    assert alert.metric_name == "fabric.P1"


def test_numeric_fields_are_meaningful_for_a_categorical_check():
    """Canon is expected to hold zero findings, so baseline 0 / current 1 is honest."""
    alert = finding_to_alert(VIOLATION)
    assert alert.baseline_value == 0.0
    assert alert.current_value == 1.0
    assert alert.deviation == 1.0


def test_responder_honours_the_requested_runbook():
    responder = DriftResponder()
    event = responder.handle_alert(finding_to_alert(VIOLATION))
    assert event.status is ResponseStatus.EXECUTED
    assert "FABRIC" in event.runbook_name.upper()


def test_fabric_violation_does_not_suspend_or_rebaseline():
    """The whole reason fabric findings get their own runbook.

    A canon-integrity finding must not suspend an agent or wipe a baseline.
    """
    import yaml
    runbooks_path = REPO_ROOT / "src" / "aurora" / "drift_runbooks.yaml"
    data = yaml.safe_load(runbooks_path.read_text(encoding="utf-8"))
    fabric = [r for r in data["runbooks"] if str(r["level"]).startswith("fabric_")]
    assert fabric, "fabric runbooks must exist"
    for runbook in fabric:
        types = {action["type"] for action in runbook["actions"]}
        forbidden = types & {"suspend", "throttle", "rebaseline"}
        assert not forbidden, (
            f"{runbook['level']} must not {forbidden}: a fabric finding is a corpus "
            "problem, not a runaway agent"
        )


def test_violation_runbook_alerts_and_escalates_per_the_ruling():
    import yaml
    data = yaml.safe_load(
        (REPO_ROOT / "src" / "aurora" / "drift_runbooks.yaml").read_text(encoding="utf-8")
    )
    book = next(r for r in data["runbooks"] if r["level"] == "fabric_violation")
    types = {a["type"] for a in book["actions"]}
    assert {"alert", "escalate"} <= types, "RULING: VIOLATION -> alert/escalate"


def test_gap_runbook_logs_and_notifies_per_the_ruling():
    import yaml
    data = yaml.safe_load(
        (REPO_ROOT / "src" / "aurora" / "drift_runbooks.yaml").read_text(encoding="utf-8")
    )
    book = next(r for r in data["runbooks"] if r["level"] == "fabric_gap")
    types = {a["type"] for a in book["actions"]}
    assert {"log", "notify"} <= types, "RULING: GAP -> log/notify"


def test_unknown_runbook_key_falls_back_instead_of_swallowing_the_alert():
    responder = DriftResponder()
    alert = DriftAlert(
        timestamp="2026-08-09T00:00:00Z", agent_id="a", metric_name="m",
        level=DriftLevel.WARNING, method=DriftMethod.THRESHOLD,
        current_value=1.0, baseline_value=0.0, deviation=1.0,
        description="d", metadata={"runbook": "does_not_exist"},
    )
    event = responder.handle_alert(alert)
    assert event.status is ResponseStatus.EXECUTED, "must fall back to the level runbook"


def test_alerts_without_metadata_still_use_the_level_default():
    """Regression: the runbook override must not break ordinary statistical drift."""
    responder = DriftResponder()
    alert = DriftAlert(
        timestamp="2026-08-09T00:00:00Z", agent_id="a", metric_name="latency",
        level=DriftLevel.INFO, method=DriftMethod.Z_SCORE,
        current_value=2.0, baseline_value=1.0, deviation=1.0,
        description="ordinary drift",
    )
    event = responder.handle_alert(alert)
    assert event.status is ResponseStatus.EXECUTED


def test_dispatch_runs_every_actionable_finding(tmp_path: Path):
    report = tmp_path / "fabric.json"
    report.write_text(json.dumps({"findings": [VIOLATION, GAP, INFO]}), encoding="utf-8")
    events = dispatch(load_findings(report), DriftResponder())
    assert len(events) == 2, "INFO must not produce a response"
    assert all(e.status is ResponseStatus.EXECUTED for e in events)


def test_load_findings_accepts_both_report_shapes(tmp_path: Path):
    wrapped = tmp_path / "a.json"
    wrapped.write_text(json.dumps({"findings": [GAP], "counts": {}}), encoding="utf-8")
    bare = tmp_path / "b.json"
    bare.write_text(json.dumps([GAP]), encoding="utf-8")
    assert load_findings(wrapped) == load_findings(bare) == [GAP]
