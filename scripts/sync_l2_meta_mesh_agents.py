#!/usr/bin/env python3
"""Sync L2 meta-agent profiles into mesh manifests and memory files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


SUBREPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_DIR = SUBREPO_ROOT / "config" / "mesh" / "agents"
MEMORY_DIR = SUBREPO_ROOT / "config" / "mesh" / "memory"

CONSTELLATION_PATH = (
    WORKSPACE_ROOT
    / "GUMAS_SIM_2.0/04_DOCUMENTATION/ORION_Distribution/Integrated_Docs_v1_1/"
    / "ORION_Perplexity_Integrated_Docs_Bundle__v1.1__2026-02-07/"
    / "L1_L2_L3_PROFILES__AuroraConstellation__v0.2__2026-02-07.md"
)
INTEGRATION_CONFIG_PATH = (
    SUBREPO_ROOT / "docs" / "operational" / "guides" / "L2_META_AGENT_INTEGRATION_CONFIG.json"
)

TARGETS = {
    "ARCHY": {
        "manifest_id": "archy",
        "style": "analytical",
        "typing_delay_ms": 320,
        "signature": "ARCHY",
    },
    "OPPY": {
        "manifest_id": "oppy",
        "style": "performance",
        "typing_delay_ms": 300,
        "signature": "OPPY",
    },
    "LIORA": {
        "manifest_id": "liora",
        "style": "adaptive",
        "typing_delay_ms": 340,
        "signature": "LIORA",
    },
    "STARLING_AU": {
        "manifest_id": "starling_au",
        "style": "communications",
        "typing_delay_ms": 300,
        "signature": "STARLING_AU",
    },
    "RIVERTHREAD_808": {
        "manifest_id": "riverthread_808",
        "style": "continuity",
        "typing_delay_ms": 320,
        "signature": "RIVERTHREAD_808",
    },
}

MODEL_PROFILE = {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "temperature": 0.35,
    "max_output_tokens": 220,
}


def ascii_normalize(text: str) -> str:
    """Convert source prose into plain ASCII for generated files."""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text.encode("ascii", "ignore").decode("ascii")


def clean_text(text: str) -> str:
    """Collapse whitespace and remove citation-number artifacts."""

    text = ascii_normalize(text)
    text = " ".join(text.split())
    text = re.sub(r"\s+\d+\s*(?=[,.;)])", "", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    return text.strip()


def load_constellation_profiles() -> Dict[str, Dict[str, str]]:
    """Parse the relay-agent profiles from the constellation reference."""

    text = CONSTELLATION_PATH.read_text()
    start = text.index("## L2 - Relay Agents")
    end = text.index("## L3 - Frameworks")
    block = text[start:end]
    profiles: Dict[str, Dict[str, str]] = {}
    labels = ["ID", "Type", "Tier", "Function", "Summary", "Competencies", "Ethical Rules", "Ethics", "Philosophy", "Relationships"]
    for section in re.split(r"(?m)^### ", block)[1:]:
        heading, rest = section.split("\n", 1)
        display_name = clean_text(re.split(r"\s+[–-]\s+", heading, maxsplit=1)[0].strip())
        if display_name not in TARGETS:
            continue
        profile: Dict[str, str] = {"display_name": display_name}
        first_paragraph = rest.split("\n\n", 1)[0]
        for label in ["ID", "Type", "Tier", "Function"]:
            match = re.search(rf"{re.escape(label)}:\s*(.+?)(?=(?:\.\s+[A-Z][a-z]+:)|$)", first_paragraph, flags=re.S)
            if match:
                profile[label] = clean_text(match.group(1).rstrip("."))
        for label in labels:
            if label in {"ID", "Type", "Tier", "Function"}:
                continue
            match = re.search(rf"{re.escape(label)}: (.+?)(?:\n\n|$)", rest, flags=re.S)
            if match:
                profile[label] = clean_text(match.group(1))
        profiles[display_name] = profile
    return profiles


def load_integration_map() -> Dict[str, Dict[str, Any]]:
    """Parse the integration config to capture bridge and staff authority data."""

    payload = json.loads(INTEGRATION_CONFIG_PATH.read_text())["l2_meta_agent_integration"]
    sequence = payload["l2_meta_agents"]["integration_sequence"]
    mapped: Dict[str, Dict[str, Any]] = {}
    for item in sequence:
        mapped[item["agent"].upper()] = item
    return mapped


def aliases_for(display_name: str) -> List[str]:
    """Return the routed aliases for a relay agent."""

    if display_name == "ARCHY":
        return ["ARCHY", "archy", "architecture coordinator", "architectural coordination relay", "bridge coordinator"]
    if display_name == "OPPY":
        return ["OPPY", "oppy", "operations coordinator", "operational flight relay", "vector processor"]
    if display_name == "LIORA":
        return ["LIORA", "liora", "communications coordinator", "interface relay", "handshake coordinator"]
    if display_name == "STARLING_AU":
        return ["STARLING_AU", "starling_au", "starling", "documentation coordinator", "continuity dispatcher", "sim coordinator"]
    if display_name == "RIVERTHREAD_808":
        return ["RIVERTHREAD_808", "riverthread_808", "riverthread", "riverthread 808", "data logistics relay", "stream processor"]
    raise KeyError(display_name)


def build_manifest(display_name: str) -> Dict[str, Any]:
    """Render a mesh manifest for a relay agent."""

    target = TARGETS[display_name]
    manifest_id = target["manifest_id"]
    return {
        "id": manifest_id,
        "display_name": display_name,
        "aliases": aliases_for(display_name),
        "channels": [f"direct:{manifest_id}", "#crew_lounge"],
        "default_channel": f"direct:{manifest_id}",
        "execution_mode": "live_llm",
        "model_profile": dict(MODEL_PROFILE),
        "typing_profile": {
            "delay_ms": target["typing_delay_ms"],
        },
        "response_policy": {
            "style": target["style"],
            "fallback_to_deterministic": True,
            "signature": target["signature"],
        },
        "memory_files": [f"config/mesh/memory/{manifest_id}.md"],
    }


def build_memory(profile: Dict[str, str], integration: Dict[str, Any]) -> str:
    """Render the memory markdown for a relay agent."""

    display_name = profile["display_name"]
    lines = [
        f"# {display_name}",
        "",
        "Layer: L2 relay agent / simulation infrastructure, surfaced through the Aurora mesh runtime.",
        f"Canonical ID: {profile.get('ID', 'UNKNOWN')}",
        f"Type: {profile.get('Type', 'L2 Relay Agent')}",
        f"Function: {profile.get('Function', 'Simulation infrastructure coordination')}",
        "",
        "Core brief:",
        profile.get("Summary", ""),
    ]

    for label in ["Competencies", "Ethical Rules", "Ethics", "Philosophy", "Relationships"]:
        if profile.get(label):
            lines.extend(["", f"{label}:", f"- {profile[label]}"])

    if integration:
        lines.extend(
            [
                "",
                "Integration posture:",
                f"- L1 bridge: {integration.get('l1_bridge', 'Aurora Command Router')}",
                f"- Staff authority: {integration.get('staff_authority', 'Station command')}",
                f"- Clearance required: {integration.get('clearance_required', 'UNSPECIFIED')}",
                f"- Integration complexity: {integration.get('integration_complexity', 'UNSPECIFIED')}",
                f"- Sequence priority: {integration.get('priority', 'UNSPECIFIED')}",
            ]
        )

    lines.extend(
        [
            "",
            "Behavioral constraints:",
            f"- Speak as {display_name}, with a system-level relay perspective rather than as an in-world character.",
            "- Keep responses concise, operational, and audit-friendly.",
            "- Do not present yourself as L1 staff or as an L2 in-world NPC; you are simulation infrastructure.",
            "- Preserve ethical constraints and do not suggest hiding dependencies, deleting data arbitrarily, violating privacy, omitting negative outcomes, or breaking continuity.",
            "- When uncertain, escalate through Aurora, the declared L1 bridge, or the authorized L1 staff owner instead of improvising authority.",
        ]
    )

    return "\n".join(lines).strip() + "\n"


def write_outputs(dry_run: bool) -> None:
    """Write manifests and memory files for the five relay agents."""

    profiles = load_constellation_profiles()
    integration_map = load_integration_map()
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    for display_name, target in TARGETS.items():
        profile = profiles[display_name]
        integration = integration_map.get(display_name)
        manifest_path = MANIFEST_DIR / f"{target['manifest_id']}.json"
        memory_path = MEMORY_DIR / f"{target['manifest_id']}.md"
        manifest_payload = build_manifest(display_name)
        memory_text = build_memory(profile, integration or {})

        if dry_run:
            print(f"[dry-run] would write {manifest_path.relative_to(SUBREPO_ROOT)}")
            print(f"[dry-run] would write {memory_path.relative_to(SUBREPO_ROOT)}")
            continue

        manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n")
        memory_path.write_text(memory_text)
        print(f"wrote {manifest_path.relative_to(SUBREPO_ROOT)}")
        print(f"wrote {memory_path.relative_to(SUBREPO_ROOT)}")

    print(f"synced {len(TARGETS)} L2 relay mesh agents")


def main() -> int:
    """CLI entrypoint."""

    parser = argparse.ArgumentParser(description="Sync L2 relay agents into mesh manifests and memory files.")
    parser.add_argument("--dry-run", action="store_true", help="Print intended writes without touching the filesystem.")
    args = parser.parse_args()
    write_outputs(dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
