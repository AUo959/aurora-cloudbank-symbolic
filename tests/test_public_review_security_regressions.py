"""Regression tests for public-review security hardening on PR #1327."""

import asyncio
import inspect
import re
from pathlib import Path

import pytest

from modules.insight_ledger import api as ledger_api
from src.improvement import api as improvement_api
from src.middleware import error_helpers


@pytest.mark.unit
@pytest.mark.security
def test_improvement_path_resolver_returns_trusted_enumerated_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """A valid lookup key resolves to a path enumerated from the safe root."""
    safe_root = tmp_path / "safe"
    target = safe_root / "pkg" / "target.py"
    target.parent.mkdir(parents=True)
    target.write_text("print('inside')\n", encoding="utf-8")
    monkeypatch.setattr(improvement_api, "_safe_root", lambda: safe_root.resolve())

    resolved = improvement_api._resolve_request_path("pkg/target.py")

    assert resolved == target.resolve()


@pytest.mark.unit
@pytest.mark.security
def test_improvement_path_resolver_rejects_absolute_sibling(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """An absolute lookup key beside the configured root must fail closed."""
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
def test_improvement_path_resolver_rejects_parent_traversal(
    tmp_path: Path,
    monkeypatch,
) -> None:
    safe_root = tmp_path / "safe"
    safe_root.mkdir()
    monkeypatch.setattr(improvement_api, "_safe_root", lambda: safe_root.resolve())

    with pytest.raises(improvement_api.HTTPException) as exc_info:
        improvement_api._resolve_request_path("../outside.py")

    assert exc_info.value.status_code == 400


@pytest.mark.unit
@pytest.mark.security
def test_improvement_path_resolver_rejects_symlink_escape(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """A trusted enumeration result is still rejected if its link escapes."""
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
        improvement_api._resolve_request_path("inside.py")

    assert exc_info.value.status_code == 403


@pytest.mark.unit
@pytest.mark.security
def test_improvement_path_resolver_reports_missing_key(
    tmp_path: Path,
    monkeypatch,
) -> None:
    safe_root = tmp_path / "safe"
    safe_root.mkdir()
    monkeypatch.setattr(improvement_api, "_safe_root", lambda: safe_root.resolve())

    with pytest.raises(improvement_api.HTTPException) as exc_info:
        improvement_api._resolve_request_path("missing.py")

    assert exc_info.value.status_code == 404


@pytest.mark.unit
@pytest.mark.security
def test_improvement_root_rejects_filesystem_root(monkeypatch) -> None:
    root = Path(Path.cwd().anchor)
    monkeypatch.setenv("AURORA_IMPROVEMENT_ROOT", str(root))

    with pytest.raises(RuntimeError, match="filesystem root"):
        improvement_api._safe_root()


@pytest.mark.unit
@pytest.mark.security
def test_ledger_http_export_has_no_caller_path_parameter(monkeypatch) -> None:
    """The HTTP surface generates the filename and accepts no path input."""
    calls = []

    class _Ledger:
        def export_ledger(self, output_path: str, include_genesis: bool = True) -> int:
            calls.append((output_path, include_genesis))
            return 7

    monkeypatch.setattr(ledger_api, "get_ledger", lambda: _Ledger())

    assert "output_path" not in inspect.signature(ledger_api.export_ledger).parameters
    response = asyncio.run(ledger_api.export_ledger(include_genesis=False))

    assert response.success is True
    assert response.entries_exported == 7
    assert response.export_path == calls[0][0]
    assert calls[0][1] is False
    assert Path(response.export_path).name == response.export_path
    assert re.fullmatch(r"ledger-export-\d{8}T\d{12}Z-[0-9a-f]{32}\.json", response.export_path)


@pytest.mark.unit
def test_http_error_logs_client_type_without_private_message(monkeypatch) -> None:
    """Routine 4xx logs exclude raw exception messages and tracebacks."""
    warning_calls = []
    error_calls = []
    monkeypatch.setattr(
        error_helpers.logger,
        "warning",
        lambda *args, **kwargs: warning_calls.append((args, kwargs)),
    )
    monkeypatch.setattr(
        error_helpers.logger,
        "error",
        lambda *args, **kwargs: error_calls.append((args, kwargs)),
    )

    result = error_helpers.http_error(
        409,
        "Consent state conflict.",
        ValueError("private detail"),
    )

    assert result.status_code == 409
    assert result.detail == "Consent state conflict."
    assert len(warning_calls) == 1
    assert error_calls == []
    rendered = repr(warning_calls)
    assert "ValueError" in rendered
    assert "private detail" not in rendered
    assert "exc_info" not in warning_calls[0][1]


@pytest.mark.unit
def test_http_error_supplies_explicit_traceback_for_server_errors(monkeypatch) -> None:
    """A provided 5xx exception carries explicit exc_info outside except blocks."""
    error_calls = []
    monkeypatch.setattr(
        error_helpers.logger,
        "error",
        lambda *args, **kwargs: error_calls.append((args, kwargs)),
    )

    exc = RuntimeError("boom")
    result = error_helpers.http_error(500, "Internal server error.", exc)

    assert result.status_code == 500
    assert result.detail == "Internal server error."
    assert len(error_calls) == 1
    assert error_calls[0][1]["exc_info"] == (RuntimeError, exc, exc.__traceback__)
