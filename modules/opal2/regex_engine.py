"""Simplified Regex Generation Engine.

This component provides a tiny rule based system for converting short
text descriptions into regular expressions.  The implementation is not
intended to be comprehensive but demonstrates how a component can
encapsulate specialised functionality for use within :class:`Opal2Core`.
"""
from __future__ import annotations

import re
from typing import Any, Dict

from .base_component import Opal2Component


PATTERN_LIBRARY: Dict[str, str] = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "number": r"\d+",
    "digits": r"\d+",
    "letters": r"[A-Za-z]+",
    "alphanumeric": r"[A-Za-z0-9]+",
    "whitespace": r"\s+",
    "word": r"\w+",
    "uuid": r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    "date": r"\d{4}-\d{2}-\d{2}",
    "time": r"\d{2}:\d{2}(?::\d{2})?",
    "ipv4": r"(?:\d{1,3}\.){3}\d{1,3}",
    "url": r"https?://[^\s]+",
}


class RegexGenerationEngine(Opal2Component):
    """Generate regexes from simple descriptions."""

    name = "regex"
    description = "Generate regular expressions from text instructions"
    capabilities = ["generate_regex"]

    def __init__(self) -> None:
        super().__init__()
        self._examples: list[str] | None = None

    def process(self, data: Any) -> str:
        """Return a regex string based on ``data``."""
        if isinstance(data, str):
            desc = data.lower().strip()
            pattern = PATTERN_LIBRARY.get(desc)
            if pattern:
                return pattern

            result = self.parse_count_based_pattern(desc, "exactly ", " digits", r"\d{{{count}}}")
            if result:
                return result

            result = self.parse_count_based_pattern(desc, "sequence of ", " digits", r"\d{{{count}}}")
            if result:
                return result

            result = self.parse_count_based_pattern(desc, "at least ", " digits", r"\d{{{count},}}")
            if result:
                return result

            if desc.endswith(" digit number") and desc[0].isdigit():
                count = desc.split()[0]
                if count.isdigit():
                    return rf"\d{{{count}}}"

            result = self.parse_count_based_pattern(desc, "exactly ", " letters", r"[A-Za-z]{{{count}}}")
            if result:
                return result

            result = self.parse_count_based_pattern(desc, "at least ", " letters", r"[A-Za-z]{{{count},}}")
            if result:
                return result

        if isinstance(data, dict) and "examples" in data:
            examples = [str(e) for e in data["examples"] if e]
            if not examples:
                raise ValueError("No examples provided")
            self._examples = examples
            prefix = examples[0]
            suffix = examples[0]
            for ex in examples[1:]:
                # common prefix
                i = 0
                while i < len(prefix) and i < len(ex) and prefix[i] == ex[i]:
                    i += 1
                prefix = prefix[:i]

                # common suffix
                i = 0
                while i < len(suffix) and i < len(ex) and suffix[-i - 1] == ex[-i - 1]:
                    i += 1
                suffix = suffix[len(suffix) - i :]

            core = r".*"
            if prefix and suffix:
                return rf"{re.escape(prefix)}{core}{re.escape(suffix)}"
            if prefix:
                return rf"{re.escape(prefix)}{core}"
            if suffix:
                return rf"{core}{re.escape(suffix)}"

        raise ValueError("Description too complex for automatic regex generation")

    def validate(self, output: Any) -> bool:
        """Ensure the produced regex compiles."""
        try:
            pattern = re.compile(str(output))
        except re.error:
            return False

        if self._examples:
            if not all(pattern.search(ex) for ex in self._examples):
                return False

        return True
