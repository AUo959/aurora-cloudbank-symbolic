"""
Tests for configurable storage paths via env vars (issue #813).

Covers:
 - MonitoringSystem: AURORA_MONITORING_PATH, AURORA_STATE_ROOT, default fallback
 - InsightLedger:    AURORA_LEDGER_PATH, AURORA_STATE_ROOT, default fallback
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch


# ---------------------------------------------------------------------------
# MonitoringSystem
# ---------------------------------------------------------------------------

_FAKE_SIGNING_KEY = "a" * 64  # valid hex for MONITORING_SIGNING_KEY


@pytest.mark.unit
def test_monitoring_system_respects_aurora_monitoring_path(tmp_path):
    """AURORA_MONITORING_PATH is used as storage_dir when set."""
    monitoring_dir = tmp_path / "custom_monitoring"
    monitoring_dir.mkdir()

    env = {
        "AURORA_MONITORING_PATH": str(monitoring_dir),
        "AURORA_STATE_ROOT": "",
        "MONITORING_SIGNING_KEY": _FAKE_SIGNING_KEY,
    }
    with patch.dict(os.environ, env, clear=False):
        from src.monitoring.monitoring_system import MonitoringSystem
        ms = MonitoringSystem()
        assert ms.storage_dir == monitoring_dir


@pytest.mark.unit
def test_monitoring_system_respects_aurora_state_root(tmp_path):
    """AURORA_STATE_ROOT/monitoring is used when AURORA_MONITORING_PATH is absent."""
    env = {
        "AURORA_MONITORING_PATH": "",
        "AURORA_STATE_ROOT": str(tmp_path),
        "MONITORING_SIGNING_KEY": _FAKE_SIGNING_KEY,
    }
    with patch.dict(os.environ, env, clear=False):
        from src.monitoring.monitoring_system import MonitoringSystem
        ms = MonitoringSystem()
        assert ms.storage_dir == tmp_path / "monitoring"


@pytest.mark.unit
def test_monitoring_system_falls_back_to_cwd_relative(tmp_path, monkeypatch):
    """Without env vars, storage_dir defaults to ./monitoring_data (cwd-relative)."""
    monkeypatch.chdir(tmp_path)
    env = {
        "AURORA_MONITORING_PATH": "",
        "AURORA_STATE_ROOT": "",
        "MONITORING_SIGNING_KEY": _FAKE_SIGNING_KEY,
    }
    with patch.dict(os.environ, env, clear=False):
        from src.monitoring.monitoring_system import MonitoringSystem
        ms = MonitoringSystem()
        assert ms.storage_dir == Path("./monitoring_data")


@pytest.mark.unit
def test_monitoring_system_explicit_storage_dir_overrides_env(tmp_path):
    """Explicitly passed storage_dir takes precedence over all env vars."""
    explicit_dir = tmp_path / "explicit"
    explicit_dir.mkdir()
    env = {
        "AURORA_MONITORING_PATH": str(tmp_path / "env_path"),
        "AURORA_STATE_ROOT": str(tmp_path / "state_root"),
        "MONITORING_SIGNING_KEY": _FAKE_SIGNING_KEY,
    }
    with patch.dict(os.environ, env, clear=False):
        from src.monitoring.monitoring_system import MonitoringSystem
        ms = MonitoringSystem(storage_dir=explicit_dir)
        assert ms.storage_dir == explicit_dir


# ---------------------------------------------------------------------------
# InsightLedger root resolution
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_ledger_root_respects_aurora_ledger_path(tmp_path):
    """AURORA_LEDGER_PATH sets the ledger safe root."""
    ledger_root = tmp_path / "custom_ledgers"
    ledger_root.mkdir()

    env = {
        "AURORA_LEDGER_PATH": str(ledger_root),
        "AURORA_STATE_ROOT": "",
    }
    with patch.dict(os.environ, env, clear=False):
        from modules.insight_ledger.ledger_core import InsightLedger
        ledger = InsightLedger("mystore")
        assert ledger.storage_path.parent == ledger_root
        import shutil
        shutil.rmtree(ledger.storage_path)


@pytest.mark.unit
def test_ledger_root_respects_aurora_state_root(tmp_path):
    """AURORA_STATE_ROOT/ledgers is used when AURORA_LEDGER_PATH is absent."""
    env = {
        "AURORA_LEDGER_PATH": "",
        "AURORA_STATE_ROOT": str(tmp_path),
    }
    with patch.dict(os.environ, env, clear=False):
        from modules.insight_ledger.ledger_core import InsightLedger
        ledger = InsightLedger("mystore")
        assert ledger.storage_path.parent == tmp_path / "ledgers"
        import shutil
        shutil.rmtree(ledger.storage_path)
