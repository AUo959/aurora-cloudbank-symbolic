"""
Concurrency tests for write-lock guards on persistence classes.

Verifies that AuditLogger, DriftDetector, EthicsEngine, and MonitoringSystem
can handle concurrent writes from multiple threads without raising exceptions
and that the final on-disk state is consistent (not partial/corrupted).
"""

import json
import os
import threading

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SIGNING_KEY = "test-write-lock-signing-key-00000000"
_N_THREADS = 10


def _run_threads(target, args_list):
    """Launch threads concurrently and join them all."""
    errors = []

    def safe_target(*args, **kwargs):
        try:
            target(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=safe_target, args=a) for a in args_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return errors


# ---------------------------------------------------------------------------
# AuditLogger
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_audit_logger_concurrent_writes_no_exception(tmp_path):
    """Multiple threads appending audit entries must not raise."""
    from src.monitoring.audit_logger import AuditLogger

    storage = tmp_path / "audit.jsonl"
    logger = AuditLogger(storage_path=storage, signing_key=_SIGNING_KEY)

    def write_entry(i):
        logger.log_manual_override(
            agent_id=f"agent-{i}",
            operator="tester",
            action="approve",
            justification=f"thread {i}",
        )

    errors = _run_threads(write_entry, [(i,) for i in range(_N_THREADS)])
    assert errors == [], f"Concurrent writes raised: {errors}"


@pytest.mark.unit
def test_audit_logger_concurrent_writes_consistent_state(tmp_path):
    """All audit entries written concurrently must appear on disk."""
    from src.monitoring.audit_logger import AuditLogger

    storage = tmp_path / "audit.jsonl"
    logger = AuditLogger(storage_path=storage, signing_key=_SIGNING_KEY)

    errors = _run_threads(
        lambda i: logger.log_manual_override(
            agent_id=f"agent-{i}",
            operator="tester",
            action="approve",
            justification=f"thread {i}",
        ),
        [(i,) for i in range(_N_THREADS)],
    )
    assert errors == []

    lines = [l for l in storage.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == _N_THREADS, (
        f"Expected {_N_THREADS} entries on disk, got {len(lines)}"
    )
    # Every line must be valid JSON
    for line in lines:
        entry = json.loads(line)
        assert "event_type" in entry


# ---------------------------------------------------------------------------
# DriftDetector
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_drift_detector_concurrent_persist_no_exception(tmp_path):
    """Multiple threads persisting drift alerts must not raise."""
    from src.monitoring.drift_detector import DriftDetector, DriftLevel, DriftMethod, DriftAlert
    from datetime import datetime, timezone

    alerts_path = tmp_path / "alerts.jsonl"
    detector = DriftDetector(alerts_path=alerts_path)

    # Pre-populate a baseline so detect_drift works
    detector.establish_baseline("agent-0", "cpu", [0.5] * 20)

    def write_alert(i):
        alert = DriftAlert(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=f"agent-{i}",
            metric_name="cpu",
            level=DriftLevel.WARNING,
            method=DriftMethod.THRESHOLD,
            current_value=0.9,
            baseline_value=0.5,
            deviation=0.8,
            description=f"thread {i}",
        )
        detector._persist_alert(alert)

    errors = _run_threads(write_alert, [(i,) for i in range(_N_THREADS)])
    assert errors == [], f"Concurrent writes raised: {errors}"


@pytest.mark.unit
def test_drift_detector_concurrent_persist_consistent_state(tmp_path):
    """All drift alerts written concurrently must appear on disk."""
    from src.monitoring.drift_detector import DriftDetector, DriftLevel, DriftMethod, DriftAlert
    from datetime import datetime, timezone

    alerts_path = tmp_path / "alerts.jsonl"
    detector = DriftDetector(alerts_path=alerts_path)

    def write_alert(i):
        alert = DriftAlert(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=f"agent-{i}",
            metric_name="cpu",
            level=DriftLevel.INFO,
            method=DriftMethod.THRESHOLD,
            current_value=0.7,
            baseline_value=0.5,
            deviation=0.4,
            description=f"thread {i}",
        )
        detector._persist_alert(alert)

    errors = _run_threads(write_alert, [(i,) for i in range(_N_THREADS)])
    assert errors == []

    lines = [l for l in alerts_path.read_text().splitlines() if l.strip()]
    assert len(lines) == _N_THREADS, (
        f"Expected {_N_THREADS} alert lines, got {len(lines)}"
    )
    for line in lines:
        entry = json.loads(line)
        assert "agent_id" in entry


# ---------------------------------------------------------------------------
# EthicsEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_ethics_engine_concurrent_persist_no_exception(tmp_path):
    """Multiple threads persisting ethics violations must not raise."""
    from src.monitoring.ethics_engine import (
        EthicsEngine,
        EthicsViolation,
        ViolationSeverity,
        RuleCategory,
    )
    from src.core.time_utils import utc_iso

    violations_path = tmp_path / "violations.jsonl"
    engine = EthicsEngine(violations_path=violations_path)

    def write_violation(i):
        violation = EthicsViolation(
            timestamp=utc_iso(),
            agent_id=f"agent-{i}",
            rule_id="TEST_001",
            rule_name="Test Rule",
            severity=ViolationSeverity.LOW,
            category=RuleCategory.AI_ETHICS,
            description=f"thread {i}",
            blocked=False,
            context={},
        )
        engine._persist_violation(violation)

    errors = _run_threads(write_violation, [(i,) for i in range(_N_THREADS)])
    assert errors == [], f"Concurrent writes raised: {errors}"


@pytest.mark.unit
def test_ethics_engine_concurrent_persist_consistent_state(tmp_path):
    """All ethics violations written concurrently must appear on disk."""
    from src.monitoring.ethics_engine import (
        EthicsEngine,
        EthicsViolation,
        ViolationSeverity,
        RuleCategory,
    )
    from src.core.time_utils import utc_iso

    violations_path = tmp_path / "violations.jsonl"
    engine = EthicsEngine(violations_path=violations_path)

    def write_violation(i):
        violation = EthicsViolation(
            timestamp=utc_iso(),
            agent_id=f"agent-{i}",
            rule_id="TEST_001",
            rule_name="Test Rule",
            severity=ViolationSeverity.LOW,
            category=RuleCategory.AI_ETHICS,
            description=f"thread {i}",
            blocked=False,
            context={},
        )
        engine._persist_violation(violation)

    errors = _run_threads(write_violation, [(i,) for i in range(_N_THREADS)])
    assert errors == []

    lines = [l for l in violations_path.read_text().splitlines() if l.strip()]
    assert len(lines) == _N_THREADS, (
        f"Expected {_N_THREADS} violation lines, got {len(lines)}"
    )
    for line in lines:
        entry = json.loads(line)
        assert "rule_id" in entry


# ---------------------------------------------------------------------------
# MonitoringSystem
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_monitoring_system_concurrent_persist_no_exception(tmp_path, monkeypatch):
    """Multiple threads calling _persist_state must not raise."""
    monkeypatch.setenv("MONITORING_SIGNING_KEY", _SIGNING_KEY)

    from src.monitoring.monitoring_system import MonitoringSystem

    system = MonitoringSystem(storage_dir=tmp_path / "monitoring")

    errors = _run_threads(
        lambda: system._persist_state(),
        [() for _ in range(_N_THREADS)],
    )
    assert errors == [], f"Concurrent writes raised: {errors}"


@pytest.mark.unit
def test_monitoring_system_concurrent_persist_consistent_state(tmp_path, monkeypatch):
    """State file written concurrently must remain valid JSON."""
    monkeypatch.setenv("MONITORING_SIGNING_KEY", _SIGNING_KEY)

    from src.monitoring.monitoring_system import MonitoringSystem

    state_dir = tmp_path / "monitoring"
    system = MonitoringSystem(storage_dir=state_dir)

    errors = _run_threads(
        lambda: system._persist_state(),
        [() for _ in range(_N_THREADS)],
    )
    assert errors == []

    state_file = state_dir / "monitoring_state.json"
    assert state_file.exists(), "State file must exist after persist"
    data = json.loads(state_file.read_text())
    assert "interventions" in data
    assert "last_intervention_time" in data


# ---------------------------------------------------------------------------
# InsightLedger (already locked — regression guard)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_insight_ledger_already_has_write_lock():
    """InsightLedger._lock must be a threading.Lock (regression guard)."""
    import threading
    from modules.insight_ledger.ledger_core import InsightLedger

    ledger = InsightLedger(storage_path="/tmp/test_lock_ledger_regression")
    assert hasattr(ledger, "_lock"), "InsightLedger must have a _lock attribute"
    assert isinstance(ledger._lock, type(threading.Lock())), (
        "InsightLedger._lock must be a threading.Lock instance"
    )
