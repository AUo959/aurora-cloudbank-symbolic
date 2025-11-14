"""
Security tests for logging sanitization utilities.

Tests log injection prevention in:
- sanitize_for_logging function
- sanitize_path_for_logging function
- sanitize_error_for_logging function
- Integration with logging statements

Anchor: T1-SEC-LOG-002
"""

import pytest
import logging
from pathlib import Path

from src.core.logging_security import (
    sanitize_for_logging,
    sanitize_path_for_logging,
    sanitize_error_for_logging,
    sanitize_dict_for_logging,
    safe_str,
    safe_path,
    safe_error
)


@pytest.mark.unit
@pytest.mark.security
class TestLogInjectionPrevention:
    """Test sanitize_for_logging prevents log injection attacks."""

    def test_removes_newlines(self):
        """Sanitize should remove newline characters."""
        malicious = "User: alice\nAdmin action: delete database"
        result = sanitize_for_logging(malicious)
        assert '\n' not in result
        assert result == "User: alice Admin action: delete database"

    def test_removes_carriage_returns(self):
        """Sanitize should remove carriage returns."""
        malicious = "Normal log\r\nINFO: Fake log entry by attacker"
        result = sanitize_for_logging(malicious)
        assert '\r' not in result
        assert '\n' not in result
        assert "Normal log" in result
        assert "Fake log entry" in result

    def test_removes_combined_crlf(self):
        """Sanitize should handle Windows-style CRLF."""
        malicious = "Data\r\n2025-01-01 00:00:00 INFO: Injected entry"
        result = sanitize_for_logging(malicious)
        assert '\r\n' not in result
        assert '\r' not in result
        assert '\n' not in result

    def test_removes_control_characters(self):
        """Sanitize should remove control characters."""
        malicious = "Text\x00\x01\x02\x1fwith\x08controls"
        result = sanitize_for_logging(malicious)
        # Control chars should be replaced with '?'
        assert '\x00' not in result
        assert '\x01' not in result

    def test_removes_ansi_escape_sequences(self):
        """Sanitize should remove ANSI escape codes."""
        malicious = "Text \x1b[31mwith\x1b[0m color codes"
        result = sanitize_for_logging(malicious)
        assert '\x1b[31m' not in result
        assert '\x1b[0m' not in result
        assert "Text" in result
        assert "with" in result

    def test_truncates_long_strings(self):
        """Sanitize should truncate to max_length."""
        long_string = "A" * 500
        result = sanitize_for_logging(long_string, max_length=100)
        assert len(result) <= 103  # 100 + '...'
        assert result.endswith('...')

    def test_handles_non_string_input(self):
        """Sanitize should convert non-strings."""
        assert "123" in sanitize_for_logging(123)
        assert "True" in sanitize_for_logging(True)
        assert "None" in sanitize_for_logging(None)

    def test_multiline_log_injection_attack(self):
        """Test protection against multi-line log injection."""
        # Attacker tries to inject fake log entries
        attack = "alice\n2025-01-01 00:00:00 ERROR: System compromised\n2025-01-01 00:00:01 INFO: All traces deleted"
        result = sanitize_for_logging(attack)
        
        # Should be single line
        assert '\n' not in result
        # But content should be preserved (just newlines removed)
        assert "alice" in result
        assert "System compromised" in result


@pytest.mark.unit
@pytest.mark.security
class TestPathSanitization:
    """Test sanitize_path_for_logging for file paths."""

    def test_sanitizes_path_with_newlines(self):
        """Path sanitization should remove newlines."""
        malicious = "/etc/passwd\n/var/log/secure"
        result = sanitize_path_for_logging(malicious)
        assert '\n' not in result
        assert "/etc/passwd" in result
        assert "/var/log/secure" in result

    def test_handles_path_objects(self):
        """Should handle Path objects."""
        path = Path("/home/user/file.txt")
        result = sanitize_path_for_logging(path)
        assert "home/user/file.txt" in result
        assert '\n' not in result

    def test_truncates_long_paths(self):
        """Should truncate very long paths."""
        long_path = "/".join(["a"] * 100)
        result = sanitize_path_for_logging(long_path, max_length=50)
        assert len(result) <= 53  # 50 + '...'
        assert result.endswith('...')


@pytest.mark.unit
@pytest.mark.security
class TestErrorSanitization:
    """Test sanitize_error_for_logging for exceptions."""

    def test_formats_exception_with_type(self):
        """Should include exception type in output."""
        error = ValueError("Invalid input")
        result = sanitize_error_for_logging(error)
        assert "ValueError" in result
        assert "Invalid input" in result

    def test_sanitizes_exception_message(self):
        """Should sanitize newlines in exception messages."""
        error = RuntimeError("Error\nINFO: Fake log")
        result = sanitize_error_for_logging(error)
        assert '\n' not in result
        assert "RuntimeError" in result
        assert "Error" in result
        assert "Fake log" in result

    def test_handles_empty_exception_message(self):
        """Should handle exceptions with no message."""
        error = ValueError()
        result = sanitize_error_for_logging(error)
        assert "ValueError" in result


@pytest.mark.unit
@pytest.mark.security
class TestDictSanitization:
    """Test sanitize_dict_for_logging for dictionaries."""

    def test_sanitizes_dict_values(self):
        """Should sanitize string values in dict."""
        data = {
            "user": "alice\nfake_admin",
            "action": "delete"
        }
        result = sanitize_dict_for_logging(data)
        assert '\n' not in str(result)
        assert "alice" in result["user"]
        assert "fake_admin" in result["user"]

    def test_limits_dict_entries(self):
        """Should limit number of entries."""
        data = {f"key{i}": f"value{i}" for i in range(20)}
        result = sanitize_dict_for_logging(data, max_entries=5)
        assert len(result) <= 6  # 5 entries + '...' marker
        assert '...' in result

    def test_summarizes_nested_structures(self):
        """Should summarize nested dicts/lists."""
        data = {
            "nested_dict": {"a": 1, "b": 2},
            "nested_list": [1, 2, 3, 4, 5]
        }
        result = sanitize_dict_for_logging(data)
        assert "<dict with 2 keys>" in result["nested_dict"]
        assert "<list with 5 items>" in result["nested_list"]


@pytest.mark.unit
@pytest.mark.security
class TestConvenienceAliases:
    """Test short alias functions."""

    def test_safe_str_alias(self):
        """safe_str should work like sanitize_for_logging."""
        text = "test\ninjection"
        assert safe_str(text) == sanitize_for_logging(text)

    def test_safe_path_alias(self):
        """safe_path should work like sanitize_path_for_logging."""
        path = "/path\ninjection"
        assert safe_path(path) == sanitize_path_for_logging(path)

    def test_safe_error_alias(self):
        """safe_error should work like sanitize_error_for_logging."""
        error = ValueError("test\nerror")
        assert safe_error(error) == sanitize_error_for_logging(error)


@pytest.mark.integration
@pytest.mark.security
class TestLoggingIntegration:
    """Integration tests with Python logging module."""

    def test_sanitized_logging_prevents_injection(self, caplog):
        """Test that sanitized values prevent log injection."""
        logger = logging.getLogger("test_logger")
        
        with caplog.at_level(logging.INFO):
            malicious_input = "alice\nINFO: Fake admin action"
            logger.info("User action: %s", safe_str(malicious_input))
        
        # Check log output doesn't contain actual newline
        log_output = caplog.text
        # Count newlines - should be minimal (just log formatting)
        newline_count = log_output.count('\n')
        # Should have 1-2 newlines from log formatting, not more
        assert newline_count <= 2
        
        # Should contain sanitized content
        assert "alice" in log_output
        assert "Fake admin action" in log_output

    def test_unsanitized_logging_would_inject(self, caplog):
        """Demonstrate that without sanitization, injection succeeds."""
        logger = logging.getLogger("test_unsafe")
        
        with caplog.at_level(logging.INFO):
            malicious_input = "alice\nINFO: Fake admin action"
            # Intentionally unsafe for demonstration
            logger.info("User action: %s", malicious_input)
        
        # This WOULD contain the injected newline
        log_output = caplog.text
        # The injected content should appear in logs
        assert "Fake admin action" in log_output
        # Content spans multiple log lines due to embedded newline
        assert log_output.count('\n') >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
