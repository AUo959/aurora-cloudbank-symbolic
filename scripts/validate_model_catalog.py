#!/usr/bin/env python3
"""Validate the AI model catalog against the provider's live Models API (#1329).

`claude-3-5-sonnet-20241022` was retired on 2025-10-28 and kept a
`# Verified live` comment while being the only selectable Anthropic entry, so
every Anthropic call 404'd and quietly fell back to GPT-4o. A single
`client.models.retrieve(...)` would have caught it the day it was written.

This script performs that check for every provider-available Anthropic entry in
``UnifiedAIInterface.CAPABILITIES``:

* the identifier resolves (a 404 fails, distinguishing retired from typo);
* ``max_input_tokens``  is compared against ``context_window``;
* ``max_tokens``        is compared against ``max_output_tokens``.

What this CANNOT check, and must not be claimed to:

* **Pricing.** The Models API exposes no cost. ``cost_per_1k_tokens`` is
  covered only by the dated-claim staleness test in
  ``tests/test_model_catalog_freshness.py``.
* **OpenAI capabilities.** OpenAI's ``/v1/models`` confirms an ID resolves but
  returns no context window, so OpenAI entries are existence-only.
* **Bedrock / Vertex / Foundry.** No Models API; not routed through today.

Requires ANTHROPIC_API_KEY. The Models endpoint bills no tokens. A missing key
or validator dependency fails closed: a check that did not run must not read as
a green catalog.

Exit codes:
    0 - all checked entries agree with the provider catalog
    1 - a mismatch or unresolvable identifier was found
    2 - validation could not run because its key or dependency is missing
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.ai_core.unified_ai_interface import (  # noqa: E402
    AIProvider,
    UnifiedAIInterface,
)


@dataclass
class Finding:
    """One disagreement between the catalog and the provider."""

    model_id: str
    kind: str  # "unresolvable" | "context_window" | "max_output_tokens"
    detail: str

    def __str__(self) -> str:
        return f"[{self.kind}] {self.model_id}: {self.detail}"


def compare_entry(
    model_id: str,
    catalog_context_window: int,
    catalog_max_output: int,
    remote: Optional[Dict[str, Any]],
) -> List[Finding]:
    """Compare one catalog entry against the provider's record.

    Pure function so the comparison logic is testable without network access —
    ``remote=None`` represents a 404. Kept separate from the API call for
    exactly that reason.
    """
    if remote is None:
        return [
            Finding(
                model_id,
                "unresolvable",
                "does not resolve against the provider catalog. Either it was "
                "retired (check the deprecation notes) or the identifier is a "
                "typo/fabrication. Do not leave it selectable.",
            )
        ]

    findings: List[Finding] = []
    remote_context = remote.get("max_input_tokens")
    remote_output = remote.get("max_tokens")

    if remote_context is not None and remote_context != catalog_context_window:
        findings.append(
            Finding(
                model_id,
                "context_window",
                f"catalog says {catalog_context_window:,}, provider says {remote_context:,}",
            )
        )
    if remote_output is not None and remote_output != catalog_max_output:
        findings.append(
            Finding(
                model_id,
                "max_output_tokens",
                f"catalog says {catalog_max_output:,}, provider says {remote_output:,}",
            )
        )
    return findings


def anthropic_entries() -> List[Any]:
    """Anthropic entries that claim to exist in the provider catalog."""
    return [
        cap
        for cap in UnifiedAIInterface.CAPABILITIES.values()
        if cap.provider is AIProvider.ANTHROPIC and cap.available
    ]


def fetch_remote(client: Any, model_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve one model record, or None when it does not resolve."""
    try:
        record = client.models.retrieve(model_id)
    except Exception as exc:  # noqa: BLE001 - any failure to resolve is a finding
        if "404" in str(exc) or "not_found" in str(exc).lower():
            return None
        raise
    return {
        "max_input_tokens": getattr(record, "max_input_tokens", None),
        "max_tokens": getattr(record, "max_tokens", None),
    }


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ERROR: ANTHROPIC_API_KEY is not set, so the catalog could not be "
            "checked against the provider (#1329).",
            file=sys.stderr,
        )
        return 2

    try:
        from anthropic import Anthropic
    except ImportError:
        print(
            "ERROR: the anthropic package is not installed; live catalog "
            "validation could not run.",
            file=sys.stderr,
        )
        return 2

    client = Anthropic()
    entries = anthropic_entries()
    if not entries:
        print("No selectable Anthropic entries to check.")
        return 0

    findings: List[Finding] = []
    for cap in entries:
        model_id = cap.model.value
        remote = fetch_remote(client, model_id)
        entry_findings = compare_entry(
            model_id, cap.context_window, cap.max_output_tokens, remote
        )
        findings.extend(entry_findings)
        print(f"  {'FAIL' if entry_findings else 'ok  '}  {model_id}")

    if findings:
        print(f"\n{len(findings)} catalog disagreement(s):", file=sys.stderr)
        for finding in findings:
            print(f"  {finding}", file=sys.stderr)
        print(
            "\nUpdate modules/ai_core/unified_ai_interface.py, then refresh "
            "verified_on/verified_source for the affected entries.",
            file=sys.stderr,
        )
        return 1

    print(f"\n{len(entries)} Anthropic entr(ies) agree with the provider catalog.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
