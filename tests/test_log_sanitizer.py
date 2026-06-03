"""Tests for modules/data_guardian/log_sanitizer.py (Issue #781)."""

import logging

import pytest

from modules.data_guardian.log_sanitizer import (
    MAX_LOG_MSG_LENGTH,
    SanitizingLogFilter,
    sanitize_log_output,
)


@pytest.mark.unit
class TestSanitizeLogOutput:
    """sanitize_log_output strips injection vectors from arbitrary input."""

    def test_clean_string_unchanged(self):
        assert sanitize_log_output("hello world") == "hello world"

    def test_newline_escaped(self):
        result = sanitize_log_output("line1\nline2")
        assert "\n" not in result
        assert "\\n" in result

    def test_carriage_return_escaped(self):
        result = sanitize_log_output("line1\rline2")
        assert "\r" not in result
        assert "\\r" in result

    def test_crlf_escaped(self):
        result = sanitize_log_output("line1\r\nline2")
        assert "\r\n" not in result
        assert "\\r\\n" in result

    def test_control_chars_stripped(self):
        # NUL, BEL, ESC should all disappear
        result = sanitize_log_output("a\x00b\x07c\x1bc")
        assert "\x00" not in result
        assert "\x07" not in result
        assert "\x1b" not in result
        assert "abc" in result

    def test_tab_preserved(self):
        # Tabs are printable and should NOT be stripped
        assert "\t" in sanitize_log_output("col1\tcol2")

    def test_long_string_truncated(self):
        long_msg = "x" * (MAX_LOG_MSG_LENGTH + 100)
        result = sanitize_log_output(long_msg)
        assert len(result) <= MAX_LOG_MSG_LENGTH + len(" [truncated]")
        assert result.endswith("[truncated]")

    def test_non_string_cast(self):
        assert sanitize_log_output(42) == "42"
        assert sanitize_log_output(None) == "None"
        assert sanitize_log_output(["a", "b"]) == "['a', 'b']"

    def test_injection_attempt(self):
        payload = "normal\n[CRITICAL] forged entry"
        result = sanitize_log_output(payload)
        # The forged entry is still there as text but not on its own line
        assert "\n" not in result
        assert "forged entry" in result


@pytest.mark.unit
class TestSanitizingLogFilter:
    """SanitizingLogFilter sanitizes record.msg and record.args in-place."""

    def _make_record(self, msg, *args) -> logging.LogRecord:
        return logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0,
            msg=msg, args=args, exc_info=None,
        )

    def test_filter_returns_true(self):
        f = SanitizingLogFilter()
        record = self._make_record("hello")
        assert f.filter(record) is True

    def test_msg_sanitized(self):
        f = SanitizingLogFilter()
        record = self._make_record("user said: \ninjected")
        f.filter(record)
        assert "\n" not in record.msg

    def test_tuple_args_sanitized(self):
        f = SanitizingLogFilter()
        record = self._make_record("val=%s", "evil\nvalue")
        f.filter(record)
        assert isinstance(record.args, tuple)
        assert "\n" not in record.args[0]

    def test_dict_args_sanitized(self):
        f = SanitizingLogFilter()
        # Construct the record and set args directly to avoid LogRecord
        # constructor's internal validation of the args/msg combo.
        record = self._make_record("val=%(k)s")
        record.args = {"k": "bad\nval"}
        f.filter(record)
        assert isinstance(record.args, dict)
        assert "\n" not in record.args["k"]

    def test_no_args_unchanged(self):
        f = SanitizingLogFilter()
        record = self._make_record("plain message")
        record.args = None
        f.filter(record)
        assert record.msg == "plain message"
        assert record.args is None
