"""
PII Redaction Utilities for Persistence

Provides helper functions that redact personally identifiable information (PII)
from dicts and lists before they are written to any persistent store (ledger,
monitoring files, audit logs, etc.).

Anchor: T1-EDG-001-PERSIST
"""

import copy
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Attempt to import data_guardian redaction components.
# Graceful degradation: if the module is unavailable, redaction is skipped and
# a warning is emitted so that callers keep working without crashing.
try:
    from modules.data_guardian.detection_rules import PIIDetector
    from modules.data_guardian.redaction import RedactionEngine, RedactionStrategy

    _DETECTOR = PIIDetector()
    _REDACTOR = RedactionEngine(default_strategy=RedactionStrategy.MASK)
    _DATA_GUARDIAN_AVAILABLE = True
except ImportError:  # pragma: no cover – tested via monkeypatch
    _DATA_GUARDIAN_AVAILABLE = False
    logger.warning(
        "data_guardian module not available; PII redaction before persistence is disabled."
    )


def _redact_value(value: str) -> str:
    """Redact PII from a single string value.

    Returns the redacted string.  If data_guardian is not available the
    original string is returned unchanged.
    """
    if not _DATA_GUARDIAN_AVAILABLE:
        return value

    detections = _DETECTOR.detect(value)
    if not detections:
        return value

    # Use a fresh engine instance per call to avoid cross-call token counter
    # bleed while still leveraging the module-level detector for efficiency.
    engine = RedactionEngine(default_strategy=RedactionStrategy.MASK)
    return engine.redact_text(value, detections)


def _redact_dict_recursive(data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a deep copy of *data* with PII strings redacted recursively."""
    redacted: Dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            redacted[key] = _redact_value(value)
        elif isinstance(value, dict):
            redacted[key] = _redact_dict_recursive(value)
        elif isinstance(value, list):
            redacted[key] = _redact_list_items(value)
        else:
            # ints, floats, bools, None – pass through unchanged
            redacted[key] = value
    return redacted


def _redact_list_items(items: list) -> list:
    """Redact PII from each item in a list (strings or nested dicts)."""
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(_redact_value(item))
        elif isinstance(item, dict):
            result.append(_redact_dict_recursive(item))
        elif isinstance(item, list):
            result.append(_redact_list_items(item))
        else:
            result.append(item)
    return result


def redact_for_persistence(data: Dict[str, Any], context_tag: str = "") -> Dict[str, Any]:
    """Redact PII from *data* dict before it is written to any persistent store.

    Performs a recursive scan of all string values in the dict and replaces
    detected PII (email, phone, SSN, credit-card number, IP address, etc.)
    with masked representations using the ``data_guardian`` module.

    If ``data_guardian`` is not importable (graceful degradation) the original
    dict is returned **unchanged** and a warning is logged.

    Args:
        data:        Dictionary to redact.  Must not be ``None``.
        context_tag: Optional DLP context tag for audit traceability.

    Returns:
        A new dictionary that is safe to write to disk.  The original *data*
        argument is never mutated.
    """
    if not isinstance(data, dict):
        logger.warning(
            "redact_for_persistence received non-dict value (type=%s); returning as-is. "
            "context_tag=%s",
            type(data).__name__,
            context_tag,
        )
        return data  # type: ignore[return-value]

    if not data:
        return {}

    if not _DATA_GUARDIAN_AVAILABLE:
        logger.warning(
            "PII redaction skipped (data_guardian unavailable). context_tag=%s",
            context_tag,
        )
        return copy.deepcopy(data)

    try:
        redacted = _redact_dict_recursive(data)
        logger.debug("PII redaction applied before persistence. context_tag=%s", context_tag)
        return redacted
    except Exception as exc:
        # Never crash a write path — log and return original data.
        logger.error(
            "PII redaction failed (%s); returning original data. context_tag=%s",
            exc,
            context_tag,
        )
        return copy.deepcopy(data)


def redact_list_for_persistence(
    records: List[Dict[str, Any]], context_tag: str = ""
) -> List[Dict[str, Any]]:
    """Apply :func:`redact_for_persistence` to every item in *records*.

    Args:
        records:     List of dicts to redact.
        context_tag: Optional DLP context tag for audit traceability.

    Returns:
        A new list where each dict has been redacted.
    """
    return [redact_for_persistence(record, context_tag=context_tag) for record in records]
