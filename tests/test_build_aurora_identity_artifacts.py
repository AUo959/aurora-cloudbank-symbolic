"""Tests for Aurora identity artifact generation helpers."""

from __future__ import annotations

import os
import sys


sys.path.insert(0, os.path.abspath("."))

from scripts.build_aurora_identity_artifacts import build_aurora_manifest, build_identity_precedence


def test_build_aurora_manifest_uses_runtime_tool_bindings() -> None:
    runtime_profile = {
        "capabilities": {
            "tool_bindings": [
                "aurora_command_grammar",
                "system_status",
                "symbolic_processing",
            ]
        }
    }

    manifest = build_aurora_manifest(runtime_profile)

    assert manifest["id"] == "aurora"
    assert manifest["default_channel"] == "direct:aurora"
    assert manifest["instruction_profile_file"] == "config/mesh/profiles/aurora_instruction_profile.json"
    assert manifest["continuity_log_file"] == "config/mesh/continuity/aurora.jsonl"
    assert manifest["tool_bindings"] == runtime_profile["capabilities"]["tool_bindings"]
    assert "Aurora Core" not in manifest["aliases"]


def test_build_identity_precedence_resolves_aurora_core_to_reference_only() -> None:
    precedence = build_identity_precedence(
        {
            "name": "Aurora",
            "shorthand": "AU",
        }
    )

    assert precedence["canonical_name"] == "Aurora"
    assert precedence["canonical_shorthand"] == "AU"
    assert precedence["reference_only_labels"] == ["Aurora Core"]
    assert precedence["resolution_status"] == "resolved_by_primary_precedence"
