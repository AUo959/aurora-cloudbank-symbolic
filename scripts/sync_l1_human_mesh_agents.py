#!/usr/bin/env python3
"""Sync Orion L1 human roster entries into mesh agent manifests."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


SUBREPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_DIR = SUBREPO_ROOT / "config" / "mesh" / "agents"
MEMORY_DIR = SUBREPO_ROOT / "config" / "mesh" / "memory"

ROSTER_PATH = (
    WORKSPACE_ROOT
    / "GUMAS_SIM_2.0/04_DOCUMENTATION/ORION_Distribution/Integrated_Docs_v1_1/"
    / "ORION_Perplexity_Integrated_Docs_Bundle__v1.1__2026-02-07/"
    / "L1_PERSONNEL__OrionStation_HumanRosterWithBios__v1.2__2026-02-07.txt"
)
REGISTRY_PATH = (
    WORKSPACE_ROOT
    / "GUMAS_SIM_2.0/04_DOCUMENTATION/ORION_Distribution/Integrated_Docs_v1_1/"
    / "ORION_Perplexity_Integrated_Docs_Bundle__v1.1__2026-02-07/"
    / "ORION__ENTITY_REGISTRY__v1.0.txt"
)
CONSTELLATION_PATH = (
    WORKSPACE_ROOT
    / "GUMAS_SIM_2.0/04_DOCUMENTATION/ORION_Distribution/Integrated_Docs_v1_1/"
    / "ORION_Perplexity_Integrated_Docs_Bundle__v1.1__2026-02-07/"
    / "L1_L2_L3_PROFILES__AuroraConstellation__v0.2__2026-02-07.md"
)

TITLE_PREFIXES = (
    "Commander ",
    "Lt. Commander ",
    "Lt. ",
    "Dr. ",
    "Prof. ",
    "Cadet ",
    "Chief Engineer ",
    "Chief ",
)

STYLE_BY_DIVISION = {
    "Command & Ethics": "strategic",
    "Science & Simulation Oversight": "analytical",
    "Operations & Security": "strategic",
    "Operations": "communications",
    "Operations & Engineering": "analytical",
    "Medical": "adaptive",
    "Systems & Infrastructure": "analytical",
    "Simulation & Cognitive Systems": "adaptive",
    "Interface & Aesthetics": "communications",
    "Operations & QA": "continuity",
    "Training": "adaptive",
}

DELAY_BY_STYLE = {
    "strategic": 620,
    "analytical": 520,
    "performance": 470,
    "adaptive": 500,
    "communications": 430,
    "continuity": 460,
    "general": 450,
}

MODEL_PROFILE = {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "temperature": 0.4,
    "max_output_tokens": 220,
}


def ascii_normalize(text: str) -> str:
    """Convert source prose into plain ASCII for generated artifacts."""

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
    """Collapse whitespace and strip citation noise from extracted text."""

    text = ascii_normalize(text)
    text = " ".join(text.split())
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = re.sub(r"\s+\d+\s*(?=[,.;)])", "", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    return text.strip()


def normalize_lookup(value: str) -> str:
    """Normalize a name/alias to a lookup key."""

    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def strip_title(name: str) -> str:
    """Remove leading honorifics when the roster provides a full name."""

    stripped = name
    for prefix in TITLE_PREFIXES:
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped


def has_given_name(name: str) -> bool:
    """Return True when the canonical name includes more than one token."""

    return len(strip_title(name).split()) > 1


def display_name_for(name: str) -> str:
    """Use title-stripped display names for full names, preserve titled surnames."""

    stripped = strip_title(name)
    return stripped if has_given_name(name) else name


def manifest_id_for(name: str) -> str:
    """Build a stable manifest id for a human character."""

    if name == "Commander Alex Thorne":
        return "alex_thorne"
    base = display_name_for(name)
    if not has_given_name(name):
        base = name
    return normalize_lookup(base)


def unique_first_names(entries: Iterable[Dict[str, Any]]) -> set[str]:
    """Return only first names that are unique across the roster."""

    first_names = [display_name_for(entry["name"]).split()[0].lower() for entry in entries if has_given_name(entry["name"])]
    counts = Counter(first_names)
    return {name for name, count in counts.items() if count == 1}


def parse_roster_table(roster_text: str) -> List[Dict[str, str]]:
    """Extract the primary roster table rows."""

    rows: List[Dict[str, str]] = []
    in_table = False
    for line in roster_text.splitlines():
        if line.startswith("| Name |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            parts = [part.strip() for part in line.strip().strip("|").split("|")]
            if parts[0] == "---":
                continue
            rows.append(
                {
                    "name": parts[0],
                    "role": parts[1],
                    "division": parts[2],
                    "status": parts[3],
                    "certainty": parts[4],
                }
            )
    return rows


def parse_roster_detail(roster_text: str) -> Dict[str, Dict[str, Any]]:
    """Extract longform roster bio details keyed by normalized name."""

    details: Dict[str, Dict[str, Any]] = {}
    for section in re.split(r"(?m)^### ", roster_text)[1:]:
        name, rest = section.split("\n", 1)
        detail: Dict[str, Any] = {"name": name.strip()}
        for label in ["Role", "Division", "Status", "Certainty"]:
            match = re.search(rf"\*\*{re.escape(label)}:\*\* (.+)", rest)
            detail[label.lower()] = clean_text(match.group(1)) if match else ""

        body = rest
        match = re.search(r"\*\*Certainty:\*\* .+?\n\n", rest, flags=re.S)
        if match:
            body = rest[match.end() :].strip()

        paragraphs = [paragraph.strip() for paragraph in body.split("\n\n") if paragraph.strip()]
        detail["primary_summary"] = clean_text(paragraphs[0]) if paragraphs else ""
        addenda: Dict[str, str] = {}
        for paragraph in paragraphs[1:]:
            match = re.match(r"\*\*(.+?):\*\*\s*(.+)$", paragraph, flags=re.S)
            if match:
                addenda[clean_text(match.group(1))] = clean_text(match.group(2))
        detail["primary_additional"] = addenda
        details[normalize_lookup(name)] = detail
    return details


def parse_registry(registry_text: str) -> Dict[str, Dict[str, str]]:
    """Extract entity ids and authority metadata from the registry."""

    registry: Dict[str, Dict[str, str]] = {}
    in_table = False
    for line in registry_text.splitlines():
        if line.startswith("| Entity ID |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            parts = [part.strip() for part in line.strip().strip("|").split("|")]
            if parts[0] == "---":
                continue
            registry[normalize_lookup(parts[1])] = {
                "entity_id": parts[0],
                "preferred_name": parts[1],
                "layer": parts[2],
                "type": parts[3],
                "primary_role": parts[4],
                "authority": parts[5],
                "sources": parts[6],
            }
    return registry


def parse_constellation(constellation_text: str) -> Dict[str, Dict[str, str]]:
    """Extract L1 human addenda from the constellation reference."""

    start = constellation_text.index("## L1 - Human Staff")
    end = constellation_text.index("## L1/L0 - Aurora Core AI")
    human_block = constellation_text[start:end]
    labels = [
        "Role",
        "Layers/Nodes",
        "Responsibilities & Projects",
        "Responsibilities",
        "Personality & Beliefs",
        "Traits",
        "Background",
        "Relationships",
        "Allies & Rivalries",
        "Related Manifests/Capsules",
        "Capsules/Docs",
        "Related Documents",
        "Allies",
    ]
    constellation: Dict[str, Dict[str, str]] = {}
    for section in re.split(r"(?m)^### ", human_block)[1:]:
        name, rest = section.split("\n", 1)
        canonical_name = clean_text(name)
        entry: Dict[str, str] = {"name": canonical_name}
        for label in labels:
            match = re.search(rf"{re.escape(label)}: (.+?)(?:\n\n|$)", rest, flags=re.S)
            if match:
                entry[label] = clean_text(match.group(1))
        keys = {
            normalize_lookup(canonical_name),
            normalize_lookup(strip_title(canonical_name)),
        }
        for key in keys:
            if key:
                constellation[key] = entry
    return constellation


def build_aliases(entry: Dict[str, Any], unique_firsts: set[str]) -> List[str]:
    """Generate safe, non-colliding aliases for a manifest."""

    name = entry["name"]
    manifest_id = entry["manifest_id"]
    display_name = entry["display_name"]

    if manifest_id == "alex_thorne":
        return ["alex", "alex thorne", "alex.thorne", "captain alex line"]

    aliases = [name.lower(), display_name.lower()]
    stripped = strip_title(name)
    if stripped != name:
        aliases.append(stripped.lower())
    if has_given_name(name):
        aliases.append(display_name.lower().replace(" ", "."))
        first_name = display_name.split()[0].lower()
        if first_name in unique_firsts:
            aliases.append(first_name)
    else:
        aliases.append(strip_title(name).lower())
        aliases.append(name.lower().replace(" ", "."))

    deduped: List[str] = []
    seen = set()
    for alias in aliases:
        normalized = normalize_lookup(alias)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(alias)
    return deduped


def response_style_for(entry: Dict[str, Any]) -> str:
    """Choose the fallback response style from role/division."""

    role = entry["role"].lower()
    if "performance" in role:
        return "performance"
    if "observability" in role or "continuity" in role or "drift" in role:
        return "continuity"
    return STYLE_BY_DIVISION.get(entry["division"], "general")


def channel_config_for(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Return routing channels for a human agent."""

    if entry["manifest_id"] == "alex_thorne":
        return {
            "channels": ["private:captain:alex", "#crew_lounge"],
            "default_channel": "private:captain:alex",
        }
    private_channel = f"private:crew:{entry['manifest_id']}"
    return {
        "channels": [private_channel, "#crew_lounge"],
        "default_channel": private_channel,
    }


def build_memory_text(entry: Dict[str, Any]) -> str:
    """Render the memory file contents for a human agent."""

    lines = [
        f"# {entry['display_name']}",
        "",
        "Layer: L1 Orion Station human crew agent.",
        f"Entity ID: {entry['entity_id']}",
        f"Canonical name: {entry['name']}",
        f"Role: {entry['role']}",
        f"Division: {entry['division']}",
        f"Status: {entry['status']}",
        f"Certainty: {entry['certainty']}",
        "",
        "Core brief:",
        entry["primary_summary"],
    ]

    addenda = entry["primary_additional"]
    if addenda:
        lines.extend(["", "Primary addenda:"])
        for key, value in addenda.items():
            lines.append(f"- {key}: {value}")

    constellation = entry["constellation"]
    reference_lines = []
    for key in [
        "Responsibilities & Projects",
        "Responsibilities",
        "Background",
        "Relationships",
        "Allies & Rivalries",
        "Allies",
        "Personality & Beliefs",
        "Traits",
    ]:
        if key in constellation:
            reference_lines.append(f"- {key}: {constellation[key]}")
    if reference_lines:
        lines.extend(["", "Reference addenda (staging/reference):", *reference_lines])
        if any("Aurora Core" in value for value in constellation.values()):
            lines.extend(
                [
                    "",
                    "Canonical routing note:",
                    "- Reference addenda may mention 'Aurora Core'; current routed control-plane identity is Aurora (AU).",
                ]
            )

    lines.extend(
        [
            "",
            "Behavioral constraints:",
            f"- Speak as {entry['display_name']}, grounded in Orion Station L1 operations.",
            "- Respond concisely, operationally, and continuity-safe.",
            "- Do not claim L2 or L3 embodiment; treat relay and glyph systems as external collaborators or oversight layers.",
            "- Preserve role boundaries and authority lines from the roster.",
            "- Mark uncertainty explicitly, especially when the source status is STAGING or details are provisional.",
        ]
    )

    return "\n".join(lines).strip() + "\n"


def build_manifest(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Render the mesh manifest payload for a human agent."""

    style = response_style_for(entry)
    channels = channel_config_for(entry)
    return {
        "id": entry["manifest_id"],
        "display_name": entry["display_name"],
        "aliases": entry["aliases"],
        "channels": channels["channels"],
        "default_channel": channels["default_channel"],
        "execution_mode": "live_llm",
        "model_profile": dict(MODEL_PROFILE),
        "typing_profile": {
            "delay_ms": DELAY_BY_STYLE.get(style, 450),
        },
        "response_policy": {
            "style": style,
            "fallback_to_deterministic": True,
            "signature": entry["display_name"],
        },
        "memory_files": [f"config/mesh/memory/{entry['manifest_id']}.md"],
    }


def load_human_entries() -> List[Dict[str, Any]]:
    """Load and reconcile the current L1 human roster into agent-ready entries."""

    roster_text = ROSTER_PATH.read_text()
    registry_text = REGISTRY_PATH.read_text()
    constellation_text = CONSTELLATION_PATH.read_text()

    roster_rows = parse_roster_table(roster_text)
    roster_detail = parse_roster_detail(roster_text)
    registry = parse_registry(registry_text)
    constellation = parse_constellation(constellation_text)

    entries: List[Dict[str, Any]] = []
    for row in roster_rows:
        key = normalize_lookup(row["name"])
        detail = roster_detail[key]
        reg = registry[key]
        constellation_entry = constellation.get(key) or constellation.get(normalize_lookup(strip_title(row["name"])))
        entries.append(
            {
                "name": row["name"],
                "display_name": display_name_for(row["name"]),
                "manifest_id": manifest_id_for(row["name"]),
                "entity_id": reg["entity_id"],
                "role": clean_text(row["role"]),
                "division": clean_text(row["division"]),
                "status": clean_text(row["status"]),
                "certainty": clean_text(row["certainty"]),
                "primary_summary": detail["primary_summary"],
                "primary_additional": detail["primary_additional"],
                "constellation": constellation_entry or {},
            }
        )

    unique_firsts = unique_first_names(entries)
    alias_claims: Counter[str] = Counter()
    alias_lists: Dict[str, List[str]] = {}
    for entry in entries:
        aliases = build_aliases(entry, unique_firsts)
        alias_lists[entry["manifest_id"]] = aliases
        alias_claims.update(normalize_lookup(alias) for alias in aliases)

    for entry in entries:
        filtered_aliases: List[str] = []
        for alias in alias_lists[entry["manifest_id"]]:
            normalized = normalize_lookup(alias)
            if normalized and alias_claims[normalized] == 1:
                filtered_aliases.append(alias)
        entry["aliases"] = filtered_aliases

    return entries


def write_outputs(entries: List[Dict[str, Any]], dry_run: bool) -> None:
    """Write manifests and memory files for all human agents."""

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        manifest_path = MANIFEST_DIR / f"{entry['manifest_id']}.json"
        memory_path = MEMORY_DIR / f"{entry['manifest_id']}.md"
        manifest_payload = build_manifest(entry)
        memory_text = build_memory_text(entry)

        if dry_run:
            print(f"[dry-run] would write {manifest_path.relative_to(SUBREPO_ROOT)}")
            print(f"[dry-run] would write {memory_path.relative_to(SUBREPO_ROOT)}")
            continue

        manifest_path.write_text(json.dumps(manifest_payload, indent=2) + "\n")
        memory_path.write_text(memory_text)
        print(f"wrote {manifest_path.relative_to(SUBREPO_ROOT)}")
        print(f"wrote {memory_path.relative_to(SUBREPO_ROOT)}")


def main() -> int:
    """Run the sync."""

    parser = argparse.ArgumentParser(description="Sync L1 human roster entries into mesh agent manifests.")
    parser.add_argument("--dry-run", action="store_true", help="Print intended writes without touching the filesystem.")
    args = parser.parse_args()

    entries = load_human_entries()
    write_outputs(entries, dry_run=args.dry_run)
    print(f"synced {len(entries)} L1 human mesh agents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
