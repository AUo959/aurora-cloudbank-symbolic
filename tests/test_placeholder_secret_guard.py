"""
Tests for api/_guard.py — runtime placeholder-secret guard (issue #766).
"""

import os
import pytest
from unittest.mock import patch


def _run_guard(**env_overrides):
    """Import and call assert_no_placeholder_secrets with the given env overrides."""
    import importlib
    import api._guard as guard_module
    importlib.reload(guard_module)  # ensure fresh import after env mutation

    with patch.dict(os.environ, env_overrides, clear=False):
        guard_module.assert_no_placeholder_secrets()


_PLACEHOLDER = "BUILD_PHASE_PLACEHOLDER_" + "0" * 48
_REAL = "a" * 64


@pytest.mark.unit
def test_raises_when_placeholder_present():
    """Guard raises RuntimeError if any secret is a placeholder at runtime."""
    env = {
        "CSRF_SECRET_KEY": _PLACEHOLDER,
        "AURORA_SECRET_KEY": _REAL,
        "WS_AUTH_SECRET": _REAL,
        "AES_KEY_256_HEX": _REAL,
        "AURORA_BUILD_PHASE": "",
    }
    with patch.dict(os.environ, env, clear=False):
        from api._guard import assert_no_placeholder_secrets
        with pytest.raises(RuntimeError, match="CSRF_SECRET_KEY"):
            assert_no_placeholder_secrets()


@pytest.mark.unit
def test_raises_lists_all_offenders():
    """RuntimeError message lists every offending variable."""
    env = {
        "CSRF_SECRET_KEY": _PLACEHOLDER,
        "AURORA_SECRET_KEY": _PLACEHOLDER,
        "WS_AUTH_SECRET": _REAL,
        "AES_KEY_256_HEX": _REAL,
        "AURORA_BUILD_PHASE": "",
    }
    with patch.dict(os.environ, env, clear=False):
        from api._guard import assert_no_placeholder_secrets
        with pytest.raises(RuntimeError) as exc_info:
            assert_no_placeholder_secrets()
        msg = str(exc_info.value)
        assert "CSRF_SECRET_KEY" in msg
        assert "AURORA_SECRET_KEY" in msg


@pytest.mark.unit
def test_build_phase_flag_suppresses_guard():
    """Guard is silent when AURORA_BUILD_PHASE=1, even with placeholder secrets."""
    env = {
        "CSRF_SECRET_KEY": _PLACEHOLDER,
        "AURORA_SECRET_KEY": _PLACEHOLDER,
        "WS_AUTH_SECRET": _PLACEHOLDER,
        "AES_KEY_256_HEX": _PLACEHOLDER,
        "AURORA_BUILD_PHASE": "1",
    }
    with patch.dict(os.environ, env, clear=False):
        from api._guard import assert_no_placeholder_secrets
        assert_no_placeholder_secrets()  # must not raise


@pytest.mark.unit
def test_passes_when_all_real_secrets_configured():
    """Guard is silent when all guarded vars have non-placeholder values."""
    env = {
        "CSRF_SECRET_KEY": _REAL,
        "AURORA_SECRET_KEY": _REAL,
        "WS_AUTH_SECRET": _REAL,
        "AES_KEY_256_HEX": _REAL,
        "AURORA_BUILD_PHASE": "",
    }
    with patch.dict(os.environ, env, clear=False):
        from api._guard import assert_no_placeholder_secrets
        assert_no_placeholder_secrets()  # must not raise


@pytest.mark.unit
def test_missing_env_var_does_not_raise():
    """Absent env vars (empty string) are not placeholders — guard stays silent."""
    env = {
        "CSRF_SECRET_KEY": "",
        "AURORA_SECRET_KEY": "",
        "WS_AUTH_SECRET": "",
        "AES_KEY_256_HEX": "",
        "AURORA_BUILD_PHASE": "",
    }
    with patch.dict(os.environ, env, clear=False):
        from api._guard import assert_no_placeholder_secrets
        # Empty strings do not start with the placeholder prefix
        assert_no_placeholder_secrets()  # must not raise


@pytest.mark.unit
def test_only_exact_prefix_triggers_guard():
    """Strings that merely contain the prefix substring but don't start with it are safe."""
    env = {
        "CSRF_SECRET_KEY": "prefix_BUILD_PHASE_PLACEHOLDER_000",
        "AURORA_SECRET_KEY": _REAL,
        "WS_AUTH_SECRET": _REAL,
        "AES_KEY_256_HEX": _REAL,
        "AURORA_BUILD_PHASE": "",
    }
    with patch.dict(os.environ, env, clear=False):
        from api._guard import assert_no_placeholder_secrets
        assert_no_placeholder_secrets()  # must not raise — prefix is in middle
