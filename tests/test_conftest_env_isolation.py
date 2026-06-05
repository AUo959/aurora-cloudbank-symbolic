"""
Tests that verify conftest.py env-var fixture scoping (issue #794).

Ensures:
- Core security variables (CSRF_SECRET_KEY etc.) are available during the session.
- AURORA_ALLOW_DEV_AUTH_FIXTURE is NOT set unless dev_auth_fixture_env is requested.
- dev_auth_fixture_env injects and cleans up the dev-auth variables correctly.
"""
import os

import pytest


@pytest.mark.unit
def test_csrf_secret_key_is_set():
    """CSRF_SECRET_KEY must be present for every test (security middleware relies on it)."""
    assert os.environ.get("CSRF_SECRET_KEY") is not None, (
        "CSRF_SECRET_KEY should be set by the test_env_vars session fixture"
    )


@pytest.mark.unit
def test_ws_auth_secret_is_set():
    """WS_AUTH_SECRET must be present for every test."""
    assert os.environ.get("WS_AUTH_SECRET") is not None, (
        "WS_AUTH_SECRET should be set by the test_env_vars session fixture"
    )


@pytest.mark.unit
def test_jwt_secret_key_is_set():
    """JWT_SECRET_KEY must be present for every test."""
    assert os.environ.get("JWT_SECRET_KEY") is not None, (
        "JWT_SECRET_KEY should be set by the test_env_vars session fixture"
    )


@pytest.mark.unit
def test_dev_auth_fixture_env_not_set_by_default():
    """AURORA_ALLOW_DEV_AUTH_FIXTURE must NOT be set unless dev_auth_fixture_env is requested.

    This is the core regression check for issue #794: the dev-auth bypass must not
    bleed into tests that do not explicitly request it.
    """
    assert os.environ.get("AURORA_ALLOW_DEV_AUTH_FIXTURE") is None, (
        "AURORA_ALLOW_DEV_AUTH_FIXTURE should only be set when dev_auth_fixture_env "
        "is explicitly requested by a test — it must not leak into other tests."
    )


@pytest.mark.unit
def test_dev_auth_passwords_not_set_by_default():
    """Dev password variables must NOT be set unless dev_auth_fixture_env is requested."""
    for var in (
        "AURORA_DEV_ADMIN_PASSWORD",
        "AURORA_DEV_OPERATOR_PASSWORD",
        "AURORA_DEV_OBSERVER_PASSWORD",
    ):
        assert os.environ.get(var) is None, (
            f"{var} should only be present when dev_auth_fixture_env is active"
        )


@pytest.mark.unit
def test_dev_auth_fixture_env_sets_vars(dev_auth_fixture_env):  # noqa: ARG001
    """When dev_auth_fixture_env is requested the bypass variables are present."""
    assert os.environ.get("AURORA_ALLOW_DEV_AUTH_FIXTURE") == "true"
    assert os.environ.get("AURORA_DEV_ADMIN_PASSWORD") is not None
    assert os.environ.get("AURORA_DEV_OPERATOR_PASSWORD") is not None
    assert os.environ.get("AURORA_DEV_OBSERVER_PASSWORD") is not None


@pytest.mark.unit
def test_dev_auth_fixture_env_cleaned_up_after_use():
    """After a test that used dev_auth_fixture_env the variables must be absent again.

    This test intentionally does NOT request dev_auth_fixture_env.  Because pytest
    runs tests in declaration order within a module, this test runs after
    test_dev_auth_fixture_env_sets_vars, proving that monkeypatch cleaned up.
    """
    assert os.environ.get("AURORA_ALLOW_DEV_AUTH_FIXTURE") is None, (
        "AURORA_ALLOW_DEV_AUTH_FIXTURE leaked from a prior test — monkeypatch "
        "teardown did not run correctly."
    )
