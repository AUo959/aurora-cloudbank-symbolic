"""Tests for keeping the dependency-light SlowAPI stub out of real limiter coverage."""

from contextlib import contextmanager
import sys
from types import SimpleNamespace
import unittest

import pytest

from tests import _slowapi_stub


SLOWAPI_MODULE_NAMES = ("slowapi", "slowapi.errors", "slowapi.middleware", "slowapi.util")


@contextmanager
def preserved_slowapi_modules():
    saved_modules = {name: sys.modules.get(name) for name in SLOWAPI_MODULE_NAMES}
    for name in SLOWAPI_MODULE_NAMES:
        sys.modules.pop(name, None)
    try:
        yield
    finally:
        for name in SLOWAPI_MODULE_NAMES:
            sys.modules.pop(name, None)
        for name, module in saved_modules.items():
            if module is not None:
                sys.modules[name] = module


def test_install_stub_returns_when_real_slowapi_is_discoverable(monkeypatch):
    checks = unittest.TestCase()

    def fake_find_spec(name):
        if name == "slowapi":
            return SimpleNamespace(origin="/venv/site-packages/slowapi/__init__.py")
        return None

    monkeypatch.setattr(_slowapi_stub.importlib.util, "find_spec", fake_find_spec)

    with preserved_slowapi_modules():
        _slowapi_stub.install_slowapi_stub()

        for name in SLOWAPI_MODULE_NAMES:
            checks.assertNotIn(name, sys.modules)


def test_install_stub_marks_modules_when_real_slowapi_is_missing(monkeypatch):
    checks = unittest.TestCase()
    monkeypatch.setattr(_slowapi_stub.importlib.util, "find_spec", lambda name: None)

    with preserved_slowapi_modules():
        _slowapi_stub.install_slowapi_stub()

        for name in SLOWAPI_MODULE_NAMES:
            checks.assertIs(
                getattr(sys.modules[name], _slowapi_stub.SLOWAPI_TEST_STUB_MARKER),
                True,
            )

        from slowapi import Limiter

        limited = Limiter().limit("1/minute")(lambda: "ok")
        checks.assertEqual(limited(), "ok")


def test_assert_real_slowapi_loaded_rejects_installed_stub(monkeypatch):
    monkeypatch.setattr(_slowapi_stub.importlib.util, "find_spec", lambda name: None)

    with preserved_slowapi_modules():
        _slowapi_stub.install_slowapi_stub()

        with pytest.raises(AssertionError, match="real SlowAPI coverage is not active"):
            _slowapi_stub.assert_real_slowapi_loaded()
