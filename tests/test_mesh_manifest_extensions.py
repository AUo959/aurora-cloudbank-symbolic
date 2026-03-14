"""Tests for extended mesh manifest fields."""

from __future__ import annotations

from src.mesh.models import AgentManifest


def test_agent_manifest_round_trips_optional_aurora_fields() -> None:
    manifest = AgentManifest.from_dict(
        {
            "id": "aurora",
            "display_name": "Aurora",
            "aliases": ["Aurora", "AU"],
            "channels": ["direct:aurora"],
            "default_channel": "direct:aurora",
            "execution_mode": "live_llm",
            "model_profile": {"model": "gpt-4.1-mini"},
            "typing_profile": {"delay_ms": 250},
            "response_policy": {"style": "aurora_control_plane", "fallback_to_deterministic": True, "signature": "AURORA"},
            "memory_files": ["config/mesh/memory/aurora.md"],
            "instruction_profile_file": "config/mesh/profiles/aurora_instruction_profile.json",
            "tool_bindings": ["aurora_command_grammar", "system_status"],
            "continuity_log_file": "config/mesh/continuity/aurora.jsonl",
        }
    )

    payload = manifest.to_dict()
    assert payload["instruction_profile_file"] == "config/mesh/profiles/aurora_instruction_profile.json"
    assert payload["tool_bindings"] == ["aurora_command_grammar", "system_status"]
    assert payload["continuity_log_file"] == "config/mesh/continuity/aurora.jsonl"
