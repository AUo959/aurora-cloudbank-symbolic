"""Tests for src/config/settings.py."""
import importlib
import sys
import pytest


def _reload_settings():
    """Force-reload settings module to avoid cached validation state."""
    for mod_name in list(sys.modules.keys()):
        if "src.config" in mod_name:
            del sys.modules[mod_name]


@pytest.mark.unit
def test_settings_load_with_critical_vars(monkeypatch):
    monkeypatch.setenv("CSRF_SECRET_KEY", "x" * 32)
    monkeypatch.setenv("AURORA_SECRET_KEY", "y" * 32)
    monkeypatch.setenv("AURORA_BUILD_PHASE", "0")
    _reload_settings()
    from src.config.settings import AuroraSettings
    s = AuroraSettings()
    assert s.csrf_secret_key == "x" * 32


@pytest.mark.unit
def test_settings_fails_without_critical_vars(monkeypatch):
    monkeypatch.delenv("CSRF_SECRET_KEY", raising=False)
    monkeypatch.delenv("AURORA_SECRET_KEY", raising=False)
    monkeypatch.setenv("AURORA_BUILD_PHASE", "0")
    _reload_settings()
    from src.config.settings import AuroraSettings
    with pytest.raises(Exception):
        AuroraSettings()


@pytest.mark.unit
def test_settings_build_phase_suppresses_check(monkeypatch):
    monkeypatch.delenv("CSRF_SECRET_KEY", raising=False)
    monkeypatch.delenv("AURORA_SECRET_KEY", raising=False)
    monkeypatch.setenv("AURORA_BUILD_PHASE", "1")
    _reload_settings()
    from src.config.settings import AuroraSettings
    s = AuroraSettings()  # should not raise
    assert s.aurora_build_phase == "1"


@pytest.mark.unit
def test_load_settings_returns_none_without_exit(monkeypatch):
    monkeypatch.delenv("CSRF_SECRET_KEY", raising=False)
    monkeypatch.delenv("AURORA_SECRET_KEY", raising=False)
    monkeypatch.setenv("AURORA_BUILD_PHASE", "0")
    _reload_settings()
    from src.config.settings import load_settings
    result = load_settings(exit_on_error=False)
    assert result is None
