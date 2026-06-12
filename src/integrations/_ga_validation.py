"""Shared geometric-algebra expression validation utilities."""

import re

GA_EXPR_WHITELIST: re.Pattern[str] = re.compile(r"^[0-9a-zA-Z_.+\-*/^() \t]+$")
GA_EXPR_BLACKLIST: re.Pattern[str] = re.compile(r"(__|\bimport\b|\beval\b|\bexec\b|os\.|sys\.)")


def validate_ga_expression(name: str, expr: str) -> None:
    """Validate a geometric-algebra expression string."""
    if not expr:
        raise ValueError(f"'{name}' must not be empty")

    if GA_EXPR_BLACKLIST.search(expr):
        raise ValueError(f"'{name}' contains a disallowed token")

    if not GA_EXPR_WHITELIST.match(expr):
        raise ValueError(
            f"'{name}' contains characters not permitted in a geometric-algebra expression"
        )
