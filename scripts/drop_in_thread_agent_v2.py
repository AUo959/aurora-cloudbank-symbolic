#!/usr/bin/env python3
import argparse
import json
"""Drop-In Thread Context Tagging Agent v2.0

This script classifies thread content using the existing reflective autonomy
classification engine and returns a context dictionary. The output includes
an alias (same as the folder) and optionally a live context directive.
"""

import argparse
import json

from modules.reflective_autonomy.threadcore_tagging import (
    PROJECT_CATEGORIES,
)
from modules.reflective_autonomy.threadcore_tagging import tag_thread_context as base_tag_thread_context

# Live context directive presented when include_directive is True
LIVE_CONTEXT_DIRECTIVE = """
\u26a0\ufe0f LIVE CONTEXT MODE ACTIVE

You are being asked to evaluate the actual content of the thread.
Return a true classification – not an example or template output.

\u2705 Return based on real content
\u2705 DO NOT simulate or placeholder output
\u2705 This is used for routing, sealing, or archive classification
""".strip()

# Default alias mapping uses the category names directly
ALIAS_MAP = {category: category for category in PROJECT_CATEGORIES.keys()}
ALIAS_MAP.setdefault("Unsorted", "Unsorted")


def tag_thread_context(content: str, include_directive: bool = True) -> dict:
    """Classify thread content and return tagging info with alias."""
    base_result = base_tag_thread_context(content)

    alias = ALIAS_MAP.get(base_result["primary_folder"], base_result["primary_folder"])
    result = {        "alias": alias,
        "folder": base_result["primary_folder"],
        "priority": base_result["priority"],
        "reason": base_result["reason"],
    }

    if include_directive:
        result["directive"] = LIVE_CONTEXT_DIRECTIVE

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Drop-In Thread Context Tagging Agent v2.0")
    parser.add_argument("input_file", help="Path to text file to classify")
    parser.add_argument(
        "--no-directive",
        action="store_true",
        help="Omit the live context directive from output",
    )
    args = parser.parse_args()

    with open(args.input_file, "r", encoding="utf-8") as fh:
        content = fh.read()

    _ = tag_thread_context(content, include_directive=not args.no_directive)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
