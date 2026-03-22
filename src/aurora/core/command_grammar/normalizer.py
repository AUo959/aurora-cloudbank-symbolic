from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Tuple

from .ast import ParseWarning, WarningCode

_EXECUTION_PATTERN = re.compile(r"//\.(?:[A-Za-z0-9_-]+)?\s*$")


@dataclass(frozen=True)
class NormalizationResult:
    text: str
    warnings: Tuple[ParseWarning, ...] = field(default_factory=tuple)


def normalize_command_text(text: str) -> NormalizationResult:
    normalized = text.strip()
    warnings = []

    if not normalized:
        return NormalizationResult(text=normalized)

    if normalized.startswith("+"):
        normalized = normalized[1:].lstrip()
        warnings.append(
            ParseWarning(
                code=WarningCode.LEGACY_PLUS_PREFIX,
                message="Removed legacy leading '+' chain prefix.",
            )
        )

    if _EXECUTION_PATTERN.search(normalized):
        return NormalizationResult(text=normalized, warnings=tuple(warnings))

    if normalized.endswith("//"):
        normalized = normalized[:-2].rstrip() + "//."
        warnings.append(
            ParseWarning(
                code=WarningCode.LEGACY_PARTIAL_TERMINATOR,
                message="Normalized legacy trailing '//' terminator to '//.'.",
            )
        )
        return NormalizationResult(text=normalized, warnings=tuple(warnings))

    normalized = normalized + "//."
    warnings.append(
        ParseWarning(
            code=WarningCode.MISSING_EXECUTION_SIGIL,
            message="Added missing execution sigil '//.' to normalize the invocation.",
        )
    )
    return NormalizationResult(text=normalized, warnings=tuple(warnings))
