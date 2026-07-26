"""Regression tests for public-review security hardening on PR #1327."""

from pathlib import Path

import pytest

from src.improvement import api as improvement_api
from src.middleware import error_helpers


@pytest.mark.unit
@pytest.mark.security
def test_improvement_path_resolver_rejects_absolute_sibling(tmp_path: Path, monkeypatch) -> None:
    """An absolute path beside the configured root must fail closed."""
    safe_root = tmp_path / "safe"
    safe_root.mkdir()
    sibling = tmp_path / "safe-other" / "target.py"
    sibling.parent.mkdir()
    sibling.write_text("print('outside')\n", encoding="utf-8")

    monkeypatch.setattr(improvement_api, "_safe_root", lambda: safe_root.resolve())

    with pytest.raises(improvement_api.HTTPException) as exc_info:
        improvement_api._resolve_request_path(str(sibling))

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access to this path is not allowed."


@pytest.mark.unit
@pytest.mark.security
def test_improvement_path_resolver_rejects_symlink_escape(tmp_path: Path, monkeypatch) -> None:
    """A link inside the root must be judged by its resolved destination."""
    safe_root = tmp_path / "safe"
    safe_root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("print('outside')\n", encoding="utf-8")
    link = safe_root / "inside.py"

    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks are unavailable on this platform")

    monkeypatch.setattr(improvement_api, "_safe_root", lambda: safe_root.resolve())

    with pytest.raises(improvement_api.HTTPException) as exc_info:
        improvement_api._resolve_request_path(str(link))

    assert exc_info.value.status_code == 403


@pytest.mark.unit
def test_http_error_logs_expected_client_errors_without_traceback(monkeypatch) -> None:
    """Routine 4xx responses should warn without exception-level logging."""
    warning_calls = []
    exception_calls = []
    monkeypatch.setattr(error_helpers.logger, "warning", lambda *args: warning_calls.append(args))
    monkeypatch.setattr(error_helpers.logger, "exception", lambda *args: exception_calls.append(args))

    result = error_helpers.http_error(409, "Consent state conflict.", ValueError("private detail"))

    assert result.status_code == 409
    assert result.detail == "Consent state conflict."
    assert len(warning_calls) == 1
    assert exception_calls == []


@pytest.mark.unit
def test_http_error_keeps_traceback_logging_for_server_errors(monkeypatch) -> None:
    """Unexpected 5xx failures must retain exception-level diagnostics.

    The implementation uses ``logger.error(..., exc_info=...)`` rather than
    ``logger.exception()``.  The latter reads from ``sys.exc_info()`` and
    emits a useless ``NoneType: None`` entry when called outside an ``except``
    block — common when constructing an HTTPException in response to an error
    caught elsewhere.  The explicit tuple always carries the right traceback.
    """
    warning_calls = []
    error_calls = []
    monkeypatch.setattr(error_helpers.logger, "warning", lambda *a, **kw: warning_calls.append(a))
    monkeypatch.setattr(error_helpers.logger, "error", lambda *a, **kw: error_calls.append(a))

    result = error_helpers.http_error(500, "Internal server error.", RuntimeError("boom"))

    assert result.status_code == 500
    assert result.detail == "Internal server error."
    assert warning_calls == []
    assert len(error_calls) == 1
