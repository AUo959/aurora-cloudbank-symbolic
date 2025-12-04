"""Lightweight PII redaction hooks for console output."""
from __future__ import annotations

import re
from typing import Optional


PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[redacted-email]"),
    (re.compile(r"\b\+?\d[\d\-\s]{8,}\d\b"), "[redacted-phone]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[redacted-ssn]"),
]


def redact(text: Optional[str]) -> Optional[str]:
    if not text:
        return text
    scrubbed = text
    for pattern, replacement in PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed
