"""
Tests for retention TTL on monitoring subsystems (issue #809).

Verifies that violations, drift alerts, interventions, and cooldown maps
are bounded by the retention window and purged on demand.
"""

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.monitoring.drift_detector import DriftDetector, DriftAlert, DriftLevel, DriftMethod
from src.monitoring.ethics_engine import EthicsEngine, EthicsViolation, ViolationSeverity, RuleCategory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _old_ts(hours: int = 200) -> str:
    """ISO timestamp older than 168 h (default retention)."""
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _fresh_ts() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# DriftDetector
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_drift_detector_accepts_retention_hours():
    """DriftDetector can be initialised with a custom retention_hours."""
    dd = DriftDetector(retention_hours=48)
    assert dd.retention_hours == 48


@pytest.mark.unit
def test_purge_old_alerts_removes_expired(tmp_path):
    """purge_old_alerts drops alerts older than retention_hours."""
    dd = DriftDetector(retention_hours=168, alerts_path=tmp_path / "alerts.jsonl")

    # Plant two synthetic alerts: one old, one fresh
    old_alert = DriftAlert(
        timestamp=_old_ts(200),
        agent_id="a1", metric_name="m",
        level=DriftLevel.CRITICAL, method=DriftMethod.Z_SCORE,
        current_value=5.0, baseline_value=1.0, deviation=4.0,
        description="old alert",
    )
    fresh_alert = DriftAlert(
        timestamp=_fresh_ts(),
        agent_id="a1", metric_name="m",
        level=DriftLevel.INFO, method=DriftMethod.Z_SCORE,
        current_value=1.1, baseline_value=1.0, deviation=0.1,
        description="fresh alert",
    )
    dd.alerts = [old_alert, fresh_alert]

    removed = dd.purge_old_alerts()

    assert removed == 1
    assert len(dd.alerts) == 1
    assert dd.alerts[0].level == DriftLevel.INFO


@pytest.mark.unit
def test_purge_old_alerts_noop_when_all_fresh(tmp_path):
    """purge_old_alerts does nothing when all alerts are within retention window."""
    dd = DriftDetector(retention_hours=168, alerts_path=tmp_path / "alerts.jsonl")
    fresh_alert = DriftAlert(
        timestamp=_fresh_ts(),
        agent_id="a1", metric_name="m",
        level=DriftLevel.INFO, method=DriftMethod.Z_SCORE,
        current_value=1.1, baseline_value=1.0, deviation=0.1,
        description="fresh alert",
    )
    dd.alerts = [fresh_alert]

    removed = dd.purge_old_alerts()

    assert removed == 0
    assert len(dd.alerts) == 1


# ---------------------------------------------------------------------------
# EthicsEngine
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_ethics_engine_accepts_retention_hours():
    """EthicsEngine can be initialised with a custom retention_hours."""
    ee = EthicsEngine(retention_hours=24)
    assert ee.retention_hours == 24


@pytest.mark.unit
def test_purge_old_violations_removes_expired(tmp_path):
    """purge_old_violations drops violations older than retention_hours."""
    ee = EthicsEngine(
        violations_path=tmp_path / "violations.jsonl",
        retention_hours=168,
    )

    old_v = EthicsViolation(
        timestamp=_old_ts(200),
        agent_id="a1",
        rule_id="r1", rule_name="Test Rule",
        severity=ViolationSeverity.CRITICAL, category=RuleCategory.SAFETY,
        description="old violation", blocked=False, context={},
    )
    fresh_v = EthicsViolation(
        timestamp=_fresh_ts(),
        agent_id="a1",
        rule_id="r2", rule_name="Other Rule",
        severity=ViolationSeverity.LOW, category=RuleCategory.SAFETY,
        description="fresh violation", blocked=False, context={},
    )
    ee.violations = [old_v, fresh_v]

    removed = ee.purge_old_violations()

    assert removed == 1
    assert len(ee.violations) == 1
    assert ee.violations[0].rule_id == "r2"


# ---------------------------------------------------------------------------
# MonitoringSystem
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_monitoring_system_accepts_retention_hours(tmp_path):
    """MonitoringSystem propagates retention_hours to subsystems."""
    import os
    with patch.dict(os.environ, {"MONITORING_SIGNING_KEY": "a" * 64}):
        from src.monitoring.monitoring_system import MonitoringSystem
        ms = MonitoringSystem(storage_dir=tmp_path, retention_hours=48)
        assert ms.retention_hours == 48
        assert ms.drift_detector.retention_hours == 48
        assert ms.ethics_engine.retention_hours == 48


@pytest.mark.unit
def test_purge_old_interventions_removes_stale(tmp_path):
    """purge_old_interventions trims old entries from interventions and cooldown map."""
    import os
    from src.monitoring.monitoring_system import MonitoringSystem, Intervention, InterventionType

    with patch.dict(os.environ, {"MONITORING_SIGNING_KEY": "a" * 64}):
        ms = MonitoringSystem(storage_dir=tmp_path, retention_hours=168)

    old_iv = Intervention(
        timestamp=_old_ts(200),
        agent_id="agent-old",
        type=InterventionType.NOTIFY_OPERATOR,
        reason="old",
        context={},
        success=True,
    )
    fresh_iv = Intervention(
        timestamp=_fresh_ts(),
        agent_id="agent-new",
        type=InterventionType.NOTIFY_OPERATOR,
        reason="fresh",
        context={},
        success=True,
    )
    ms.interventions = [old_iv, fresh_iv]
    cutoff = datetime.now(timezone.utc) - timedelta(hours=200)
    ms.last_intervention_time = {
        "agent-old": cutoff - timedelta(hours=1),
        "agent-new": datetime.now(timezone.utc),
    }

    removed = ms.purge_old_interventions()

    assert removed == 1
    assert len(ms.interventions) == 1
    assert ms.interventions[0].agent_id == "agent-new"
    assert "agent-old" not in ms.last_intervention_time
    assert "agent-new" in ms.last_intervention_time


@pytest.mark.unit
def test_run_retention_cleanup_calls_all_subsystems(tmp_path):
    """run_retention_cleanup delegates to all three purge methods."""
    import os
    from unittest.mock import MagicMock
    from src.monitoring.monitoring_system import MonitoringSystem

    with patch.dict(os.environ, {"MONITORING_SIGNING_KEY": "a" * 64}):
        ms = MonitoringSystem(storage_dir=tmp_path, retention_hours=168)

    ms.drift_detector.purge_old_alerts = MagicMock(return_value=0)
    ms.ethics_engine.purge_old_violations = MagicMock(return_value=0)
    ms.purge_old_interventions = MagicMock(return_value=0)

    ms.run_retention_cleanup()

    ms.drift_detector.purge_old_alerts.assert_called_once()
    ms.ethics_engine.purge_old_violations.assert_called_once()
    ms.purge_old_interventions.assert_called_once()
