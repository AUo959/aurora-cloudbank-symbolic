"""
Log Sanitizer — data_guardian sub-module

Provides sanitize_log_output() and SanitizingLogFilter to prevent log injection.

Log injection occurs when user-controlled input containing newline or carriage-
return characters is written to a log file: the injected characters split the
line, letting an attacker forge arbitrary log entries that appear to come from
the application itself.

sanitize_log_output():
  - Replaces \\n / \\r with the literal escape sequences so the meaning is
    preserved but the log line stays intact.
  - Strips other C0/C1 control characters (except ordinary \\t) that have no
    printable representation and serve no purpose in a log message.
  - Truncates to MAX_LOG_MSG_LENGTH characters to guard against DoS from
    giant payloads.

SanitizingLogFilter:
  - A logging.Filter subclass that applies sanitize_log_output to every
    LogRecord's msg and args so the protection is transparent to all loggers
    in the process once the filter is installed on the root logger or a handler.
"""

import logging
import re
from typing import Any

# C0/C1 control characters except \\t (0x09) — printable tab is acceptable.
# Covers 0x00–0x08, 0x0A–0x1F, 0x7F–0x9F.
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")

# Maximum length before truncation; keeps individual log lines bounded.
MAX_LOG_MSG_LENGTH = 4096


def sanitize_log_output(text: Any) -> str:
    """
    Sanitize a value before it is written to a log record.

    Args:
        text: Any value — typically a str, but may be anything that a logger
              receives as a message or argument.  Non-string values are cast
              to str first.

    Returns:
        A sanitized string safe to write to log output.
    """
    if not isinstance(text, str):
        text = str(text)

    # Replace newlines/carriage-returns with their visible escape sequences.
    text = text.replace("\r\n", "\\r\\n").replace("\n", "\\n").replace("\r", "\\r")

    # Strip remaining control characters that have no printable representation.
    text = _CONTROL_CHARS_RE.sub("", text)

    # Truncate to prevent DoS via extremely long log messages.
    if len(text) > MAX_LOG_MSG_LENGTH:
        text = text[:MAX_LOG_MSG_LENGTH] + " [truncated]"

    return text


class SanitizingLogFilter(logging.Filter):
    """
    logging.Filter that sanitizes LogRecord.msg and LogRecord.args in-place.

    Install on the root logger (or any handler) to automatically protect all
    log output in the process:

        logging.getLogger().addFilter(SanitizingLogFilter())
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = sanitize_log_output(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: sanitize_log_output(v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(sanitize_log_output(a) for a in record.args)
        return True
