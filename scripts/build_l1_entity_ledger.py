#!/usr/bin/env python3
"""Build a canon-first L1 Orion Station entity ledger."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from sync_l1_human_mesh_agents import REGISTRY_PATH, clean_text, load_human_entries, normalize_lookup, parse_registry


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
REPORTS_DIR = WORKSPACE_ROOT / "reports" / "analysis"

OPS_ROOT = WORKSPACE_ROOT / "GUMAS_SIM_2.0/01_OPERATIONS/ORION_Operational_Library_v2_0/LATEST"
STATION_OVERVIEW_PATH = OPS_ROOT / "ORION__L1_STATION_OVERVIEW__v1.1.md"
COMMAND_STRUCTURE_PATH = OPS_ROOT / "ORION__L1_COMMAND_STRUCTURE__v1.1.md"
SYSTEMS_BIBLE_PATH = OPS_ROOT / "ORION__L1_SYSTEMS_BIBLE__v1.1.md"
RUNBOOK_PATH = OPS_ROOT / "ORION__L1_OPERATIONS_RUNBOOK__v1.1.md"
DISPATCH_PATH = OPS_ROOT / "ORION__L1_DISPATCH_PROTOCOL__v1.1.md"
EMERGENCY_PATH = OPS_ROOT / "ORION__L1_EMERGENCY_PROTOCOLS__v1.1.md"
LEGACY_PARTIAL_ROSTER_PATH = (
    WORKSPACE_ROOT
    / "GUMAS_SIM_2.0/02_DEVELOPMENT/Project_Main/Project_Files_GUMAS2_0"
    / "L1_HUMAN_CREW_ROSTER__PARTIAL__v0.1__2026-02-07.json"
)
LEGACY_TECH_READOUT_PATH = (
    WORKSPACE_ROOT / "Aurora_New_11_9/01_OPERATIONS/Station_Infrastructure/orion_station_full_technical_readout.md"
)
LEGACY_LIFE_INFRA_PATH = (
    WORKSPACE_ROOT / "Aurora_New_11_9/01_OPERATIONS/Station_Infrastructure/orion_station_life_infrastructure.md"
)

SOURCE_POLICY = {
    "primary": [
        "ORION.ENT.L1ROSTER.0001",
        "ORION.ENT.REGISTRY.0001",
        "ORION.L1.OPS.COMMAND.0002",
        "ORION.L1.STATION.OVERVIEW.0002",
        "ORION.L1.SYSTEMS.BIBLE.0002",
        "ORION.L1.OPS.RUNBOOK.0002",
        "ORION.L1.DISPATCH.PROTOCOL.0002",
        "ORION.L1.OPS.EMERGENCY.0002",
        "ORION.ARCH.CONTRACT.0001",
    ],
    "reference": [
        "ORION.ENT.CONSTELLATION.0001",
        "ORION.L1.CANVAS.0001",
        "ORION.L1.STATE.0001",
        "DATA__OrionStationPhysicalSpace__v1.0__2026-02-15.md",
    ],
    "legacy": [
        "L1_HUMAN_CREW_ROSTER__PARTIAL__v0.1__2026-02-07.json",
        "orion_station_full_technical_readout.md",
        "orion_station_life_infrastructure.md",
    ],
}

VESSEL_CREW_LINKS = {
    "ORS-05 Lacewing": ["Samantha Gray", "Ren Takahashi"],
    "Guardian Sentinel": ["Lt. Nakamura"],
    "Logistics Alpha": ["Lt. Hassan"],
    "Repair Tender Beta": ["Chief Thomson"],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_bullet_values(path: Path, prefix: str = "- ") -> List[str]:
    values: List[str] = []
    body = read_text(path).split("---\n", 2)[-1]
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            values.append(clean_text(stripped[len(prefix) :]))
    return values


def first_paragraph_after_heading(path: Path) -> str:
    text = read_text(path)
    body = text.split("---\n", 2)[-1]
    paragraphs = [clean_text(part) for part in body.split("\n\n") if part.strip()]
    for paragraph in paragraphs:
        if not paragraph.startswith("#"):
            return paragraph
    return ""


def load_legacy_lookup() -> Dict[str, Dict[str, Any]]:
    payload = json.loads(LEGACY_PARTIAL_ROSTER_PATH.read_text(encoding="utf-8"))
    lookup: Dict[str, Dict[str, Any]] = {}
    for item in payload:
        keys = {normalize_lookup(item["name"])}
        for variant in item.get("name_variants", []):
            keys.add(normalize_lookup(variant))
        for key in keys:
            lookup[key] = item
    return lookup


def legacy_for(entry: Dict[str, Any], legacy_lookup: Dict[str, Dict[str, Any]]) -> Dict[str, Any] | None:
    for candidate in [entry["display_name"], entry["name"]]:
        match = legacy_lookup.get(normalize_lookup(candidate))
        if match:
            return match
    return None


def related_assets_for(entry: Dict[str, Any]) -> List[str]:
    joined = " ".join(
        [
            entry.get("primary_summary", ""),
            " ".join(f"{key}: {value}" for key, value in entry.get("primary_additional", {}).items()),
            " ".join(f"{key}: {value}" for key, value in entry.get("constellation", {}).items()),
        ]
    )
    candidates = [
        "Orion Station",
        "Aurora",
        "Aurora Core",
        "Guardian Sentinel",
        "Logistics Alpha",
        "Repair Tender Beta",
        "Lacewing",
        "ARCHY",
        "OPPY",
        "LIORA",
        "STARLING",
        "RIVERTHREAD",
        "HALO",
    ]
    return [name for name in candidates if name in joined]


def parse_system_blocks() -> List[Dict[str, str]]:
    summaries = {
        "SYS-100 Power": "Primary station energy generation and distribution, anchored by fusion generation with solar and battery reserves.",
        "SYS-110 Thermal": "Thermal management across the rotating habitat and non-rotating core, using radiator panels and heat-pipe regulation.",
        "SYS-120 Attitude / Orbit Control": "Attitude control, orbital adjustments, and maneuvering safeguards needed to keep the L1 frame physically plausible.",
        "SYS-130 Life Support": "Atmosphere, water recycling, food reserves, and environmental stability for a closed-habitat crew.",
        "SYS-140 Communications & Data": "Station comms, HALO-linked data exchange, run-log integrity, and dispatch routing surfaces.",
        "SYS-150 Cyber Defense": "Security monitoring, access control, and cyber-defense posture coordinated with station security.",
        "SYS-160 Defensive Drones (recon + non-lethal deterrence)": "Recon and non-lethal defensive drone layer, including Gamma Swarm support patterns.",
        "SYS-170 Emergency Protocols": "Emergency response system envelope for announce, isolate, stabilize, triage, and audit sequences.",
    }
    return [{"name": item, "summary": summaries.get(item, item)} for item in parse_bullet_values(SYSTEMS_BIBLE_PATH)]


def parse_protocol_entities() -> List[Dict[str, Any]]:
    state_summary = "Current template captures mode, system health, open incidents, and planned activities. As of 2026-02-07 the snapshot is a fillable shell rather than a populated operational record."
    return [
        {
            "name": "L1 Command Structure",
            "authority": "primary",
            "summary": "Chain of command is Commander -> Executive Officer -> Division Chiefs -> Watch Officers -> Specialists. Divisions named in canon: Operations, Engineering, Science, Medical, Security, Comms/Data.",
            "sources": ["ORION.L1.OPS.COMMAND.0002"],
        },
        {
            "name": "L1 Operations Runbook",
            "authority": "primary (staging scaffold)",
            "summary": clean_text(first_paragraph_after_heading(RUNBOOK_PATH) + " Handoff minimum: station mode, system health, open incidents, comms windows, crew alerts. Escalation: safety risk -> emergency protocol + notify command + log."),
            "sources": ["ORION.L1.OPS.RUNBOOK.0002"],
        },
        {
            "name": "L1 Dispatch Protocol",
            "authority": "primary",
            "summary": clean_text(first_paragraph_after_heading(DISPATCH_PATH) + " Dispatch fields: timestamp, objective, constraints, resources, risk notes, completion criteria. Every dispatch creates a run-log entry and an incident report if safety-critical."),
            "sources": ["ORION.L1.DISPATCH.PROTOCOL.0002"],
        },
        {
            "name": "L1 Emergency Protocols",
            "authority": "primary (staging scaffold)",
            "summary": clean_text(first_paragraph_after_heading(EMERGENCY_PATH) + " Triggers: fire, depressurization, radiation, critical cyber breach, mass casualty. Standard steps: announce -> isolate -> stabilize -> triage -> audit."),
            "sources": ["ORION.L1.OPS.EMERGENCY.0002"],
        },
        {
            "name": "L1 State Snapshot",
            "authority": "run_output scaffold",
            "summary": state_summary,
            "sources": ["ORION.L1.STATE.0001"],
        },
    ]


def parse_station_spaces() -> List[Dict[str, Any]]:
    overview_summary = first_paragraph_after_heading(STATION_OVERVIEW_PATH)
    return [
        {
            "name": "Orion Station",
            "authority": "primary + canonical",
            "summary": clean_text(
                overview_summary
                + " Continuity/identity seed is EOS_SEED_ORION with L1 anchor L1_ANCHOR_ORIONSTATION."
            ),
            "sources": ["ORION.L1.STATION.OVERVIEW.0002", "ORION.ARCH.CONTRACT.0001"],
        },
        {
            "name": "The Observatory",
            "authority": "primary",
            "summary": "Named as Orion Station's command/simulation chamber used to operate L2. Dispatch protocol is explicitly framed as The Observatory workflow.",
            "sources": ["ORION.L1.STATION.OVERVIEW.0002", "ORION.L1.DISPATCH.PROTOCOL.0002"],
        },
        {
            "name": "Habitat Ring",
            "authority": "legacy/reference",
            "summary": "Rotating habitat ring providing 0.3g artificial gravity and most crew living/working space.",
            "sources": ["orion_station_life_infrastructure.md", "orion_station_full_technical_readout.md"],
        },
        {
            "name": "Non-rotating Core",
            "authority": "legacy/reference",
            "summary": "Central station core containing docking bays, zero-g research labs, and the major communications array.",
            "sources": ["orion_station_life_infrastructure.md", "orion_station_full_technical_readout.md"],
        },
        {
            "name": "Observation Lounge (The Dome)",
            "authority": "legacy/reference",
            "summary": "Deck 4 observation lounge with wide viewing windows; treated as an informal crew social hub during off-hours.",
            "sources": ["orion_station_life_infrastructure.md"],
        },
        {
            "name": "Docking Bay Network",
            "authority": "legacy/reference",
            "summary": "Four primary docking bays plus eight auxiliary ports handling large vessels, shuttles, and supply runs.",
            "sources": ["orion_station_life_infrastructure.md", "orion_station_full_technical_readout.md"],
        },
    ]


def normalize_vessel_name(raw_heading: str) -> str:
    heading = clean_text(raw_heading)
    mapping = {
        "ORF-01 CONSTANCY": "ORF-01 Constancy",
        "ORS-01 HELIOS": "ORS-01 Helios",
        "ORS-02 LIORA": "ORS-02 Liora",
        "ORS-03 ARCHIMEDES": "ORS-03 Archimedes",
        "ORS-04 PIONEER": "ORS-04 Pioneer",
        "ORS-05 LACEWING": "ORS-05 Lacewing",
        "GUARDIAN SENTINEL": "Guardian Sentinel",
        "LOGISTICS ALPHA": "Logistics Alpha",
        "REPAIR TENDER BETA": "Repair Tender Beta",
    }
    for key, value in mapping.items():
        if heading.startswith(key):
            return value
    return heading.title()


def parse_detail_lines(block: str) -> Dict[str, str]:
    details: Dict[str, str] = {}
    for match in re.finditer(r"- \*\*(.+?)\*\*:\s*(.+)", block):
        details[clean_text(match.group(1))] = clean_text(match.group(2))
    return details


def parse_vessels() -> List[Dict[str, Any]]:
    text = read_text(LEGACY_TECH_READOUT_PATH)
    fleet_block_match = re.search(r"## III\. FLEET MANIFEST(.*?)(?=\n## IV\.)", text, flags=re.S)
    if not fleet_block_match:
        return []
    fleet_block = fleet_block_match.group(1)
    vessels: List[Dict[str, Any]] = []
    for match in re.finditer(r"^#### (.+?)\n(.*?)(?=^#### |\Z)", fleet_block, flags=re.M | re.S):
        name = normalize_vessel_name(match.group(1))
        details = parse_detail_lines(match.group(2))
        mission = details.get("Mission", "")
        status = details.get("Status", "")
        vessel_class = details.get("Class", "")
        crew = details.get("Crew", "")
        equipment = details.get("Equipment", "")
        summary_parts = [part for part in [vessel_class, mission, status] if part]
        if crew:
            summary_parts.append(f"Crew: {crew}")
        if equipment:
            summary_parts.append(f"Equipment: {equipment}")
        crew_links = VESSEL_CREW_LINKS.get(name, [])
        if crew_links:
            summary_parts.append("Linked crew: " + ", ".join(crew_links))
        vessels.append(
            {
                "name": name,
                "authority": "legacy technical reference"
                if not crew_links
                else "staging crew roster + older technical reference",
                "summary": clean_text(". ".join(summary_parts) + "."),
                "sources": ["orion_station_full_technical_readout.md"],
            }
        )
    return vessels


def build_human_entries() -> List[Dict[str, Any]]:
    entries = load_human_entries()
    registry = parse_registry(REGISTRY_PATH.read_text(encoding="utf-8"))
    legacy_lookup = load_legacy_lookup()
    results: List[Dict[str, Any]] = []
    for entry in entries:
        key = normalize_lookup(entry["name"])
        legacy = legacy_for(entry, legacy_lookup)
        record = {
            "entity_id": registry[key]["entity_id"],
            "name": entry["name"],
            "display_name": entry["display_name"],
            "role": entry["role"],
            "division": entry["division"],
            "status": entry["status"],
            "certainty": entry["certainty"],
            "registry_authority": registry[key]["authority"],
            "primary_summary": entry["primary_summary"],
            "primary_additional": entry["primary_additional"],
            "constellation": entry["constellation"],
            "related_assets": related_assets_for(entry),
            "legacy_drift": legacy,
        }
        results.append(record)
    return results


def build_summary(entries: List[Dict[str, Any]], divisions: List[str], systems: List[Dict[str, Any]], protocols: List[Dict[str, Any]], spaces: List[Dict[str, Any]], vessels: List[Dict[str, Any]]) -> Dict[str, Any]:
    canon_count = sum(1 for entry in entries if entry["certainty"] == "CANON")
    staging_count = sum(1 for entry in entries if entry["certainty"] != "CANON")
    constellation_count = sum(1 for entry in entries if entry["constellation"])
    legacy_count = sum(1 for entry in entries if entry["legacy_drift"])
    return {
        "primary_l1_humans": len(entries),
        "certainty_breakdown": {"CANON": canon_count, "STAGING": staging_count},
        "with_constellation_addenda": constellation_count,
        "with_legacy_drift_traces": legacy_count,
        "adjacent_entity_surfaces": {
            "divisions": len(divisions),
            "system_blocks": len(systems),
            "protocols_and_runbooks": len([item for item in protocols if item["name"] != "L1 State Snapshot"]),
            "named_vessels_and_craft": len(vessels),
            "named_station_spaces_and_features": len(spaces),
        },
    }


def build_conflicts() -> List[str]:
    return [
        "The primary entity registry contains only L1 humans for the L1 portion of the registry; vessels, named spaces, and most physical systems remain outside the promoted registry and survive only in operational or legacy documents.",
        "Aurora naming is now resolved by precedence: the primary 2026-02-11 identity schematics bundle and current runtime define Aurora / AU as the routed control-plane identity, while 'Aurora Core' remains reference-only legacy phrasing from lower-precedence materials.",
        "Reference constellation prose is useful for relationships and personality, but it must not silently override the roster and registry on titles, division placement, or certainty.",
        "Named vessel commanders Lt. Nakamura, Lt. Hassan, Chief Thomson, Samantha Gray, Ren Takahashi, and Cadet Mira Chen remain STAGING until promoted beyond the roster/reference set.",
    ]


def build_recommendations() -> List[str]:
    return [
        "Use the 2026-02-07 human roster and the entity registry as the personnel source of truth for L1.",
        "If named vessels or station spaces need canon promotion, promote them into the entity registry instead of leaving them in legacy technical references.",
        "Preserve any 'Aurora Core' references as labeled legacy/reference wording rather than merging them into the routed Aurora / AU identity.",
        "Regenerate mesh human agents from the same roster inputs to keep memory files aligned with the ledger.",
    ]


def build_json_payload() -> Dict[str, Any]:
    entries = build_human_entries()
    divisions = list(dict.fromkeys(entry["division"] for entry in entries))
    systems = parse_system_blocks()
    protocols = parse_protocol_entities()
    spaces = parse_station_spaces()
    vessels = parse_vessels()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return {
        "title": "L1 Entity Ledger - Orion Station",
        "generated_at_utc": generated_at,
        "purpose": "Source-prioritized ledger of currently known L1 entities, with emphasis on human crew/staff and the L1 environment they operate inside.",
        "source_policy": SOURCE_POLICY,
        "summary": build_summary(entries, divisions, systems, protocols, spaces, vessels),
        "humans": entries,
        "divisions": divisions,
        "system_blocks": systems,
        "protocol_entities": protocols,
        "station_spaces": spaces,
        "vessels": vessels,
        "conflicts": build_conflicts(),
        "recommendations": build_recommendations(),
    }


def format_reference_addenda(entry: Dict[str, Any]) -> str | None:
    if not entry["constellation"]:
        return None
    ordered_keys = [
        "Responsibilities & Projects",
        "Responsibilities",
        "Background",
        "Relationships",
        "Allies & Rivalries",
        "Allies",
        "Personality & Beliefs",
        "Traits",
    ]
    parts = [f"{key}: {entry['constellation'][key]}" for key in ordered_keys if key in entry["constellation"]]
    return " | ".join(parts) if parts else None


def render_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# L1 Entity Ledger - Orion Station",
        "",
        f"Generated: {payload['generated_at_utc']}",
        "",
        "Purpose: source-prioritized ledger of all currently known L1 entities, with emphasis on human crew/staff and the L1 environment they operate inside.",
        "",
        "## Authority Stack",
        "",
        "1. Primary/canonical-or-primary L1 sources used first: `" + "`, `".join(payload["source_policy"]["primary"]) + "`.",
        "2. Reference/staging supplements used only as labeled addenda: `" + "`, `".join(payload["source_policy"]["reference"]) + "`.",
        "3. Older/conflicting materials were not silently merged; they are preserved as legacy drift notes: `" + "`, `".join(payload["source_policy"]["legacy"]) + "`.",
        "",
        "## Summary",
        "",
        f"- Primary L1 human entities in the current roster/registry: {payload['summary']['primary_l1_humans']}.",
        f"- Certainty split: {payload['summary']['certainty_breakdown']['CANON']} CANON, {payload['summary']['certainty_breakdown']['STAGING']} STAGING.",
        f"- {payload['summary']['with_constellation_addenda']} of the {payload['summary']['primary_l1_humans']} people also have constellation addenda with staging/reference background material.",
        f"- {payload['summary']['with_legacy_drift_traces']} people have explicit legacy/conflict traces in the partial development roster extract.",
        (
            "- Additional L1-adjacent entity surfaces identified: "
            f"{payload['summary']['adjacent_entity_surfaces']['divisions']} roster divisions, "
            f"{payload['summary']['adjacent_entity_surfaces']['system_blocks']} system blocks, "
            f"{payload['summary']['adjacent_entity_surfaces']['protocols_and_runbooks']} protocols/runbooks, "
            f"{payload['summary']['adjacent_entity_surfaces']['named_vessels_and_craft']} named vessels/craft, and "
            f"{payload['summary']['adjacent_entity_surfaces']['named_station_spaces_and_features']} named station spaces/features."
        ),
        "",
        "## Primary Human Ledger",
        "",
        "| Entity ID | Name | Role | Division | Certainty | Registry Authority |",
        "|---|---|---|---|---|---|",
    ]
    for entry in payload["humans"]:
        lines.append(
            f"| {entry['entity_id']} | {entry['name']} | {entry['role']} | {entry['division']} | {entry['certainty']} | {entry['registry_authority']} |"
        )

    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for entry in payload["humans"]:
        grouped[entry["division"]].append(entry)

    for division in payload["divisions"]:
        members = grouped.get(division, [])
        if not members:
            continue
        lines.extend(["", f"### {division} ({len(members)})", ""])
        for entry in members:
            lines.append(f"#### {entry['name']} - {entry['entity_id']}")
            lines.append("")
            lines.append(
                f"- Primary canon status: `{entry['status']}` / `{entry['certainty']}` / registry authority `{entry['registry_authority']}`."
            )
            lines.append(f"- Primary role: {entry['role']}.")
            lines.append(f"- Primary summary: {entry['primary_summary']}")
            if entry["related_assets"]:
                lines.append(f"- Related L1 assets mentioned in current/secondary material: {', '.join(entry['related_assets'])}.")
            reference_addenda = format_reference_addenda(entry)
            if reference_addenda:
                lines.append(f"- Constellation addenda (reference/staging): {reference_addenda}")
            if entry["primary_additional"]:
                rendered = " | ".join(f"{key}: {value}" for key, value in entry["primary_additional"].items())
                lines.append(f"- Primary addenda: {rendered}")
            legacy = entry["legacy_drift"]
            if legacy:
                lines.append(
                    "- Legacy drift: certainty `{}`; older roles/mentions `{}`; sources `{}`; notes `{}`.".format(
                        legacy.get("certainty", "UNKNOWN"),
                        ", ".join(legacy.get("roles", [])) or "none",
                        ", ".join(legacy.get("sources", [])) or "none",
                        ", ".join(legacy.get("notes", [])) or "none",
                    )
                )
            lines.append("")

    lines.extend(["## L1 Environment And Assets", ""])
    lines.append("### Divisions")
    lines.append("")
    for division in payload["divisions"]:
        lines.append(f"- **{division}**")

    lines.extend(["", "### System Blocks", ""])
    for system in payload["system_blocks"]:
        lines.append(f"- **{system['name']}**: {system['summary']}")

    lines.extend(["", "### Protocols, Runbooks, State", ""])
    for item in payload["protocol_entities"]:
        source_list = ", ".join(item["sources"])
        lines.append(f"- **{item['name']}** (authority `{item['authority']}`): {item['summary']} Sources: {source_list}.")

    lines.extend(["", "### Named Station Spaces / Features", ""])
    for item in payload["station_spaces"]:
        source_list = ", ".join(item["sources"])
        lines.append(f"- **{item['name']}** (authority `{item['authority']}`): {item['summary']} Sources: {source_list}.")

    lines.extend(["", "### Named Vessels / Craft", ""])
    for item in payload["vessels"]:
        source_list = ", ".join(item["sources"])
        lines.append(f"- **{item['name']}** (authority `{item['authority']}`): {item['summary']} Sources: {source_list}.")

    lines.extend(["", "## Reconciliation Notes", ""])
    for item in payload["conflicts"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Recommended Next Steps", ""])
    for item in payload["recommendations"]:
        lines.append(f"- {item}")

    stamp = datetime.now(timezone.utc).date().isoformat()
    lines.extend(
        [
            "",
            "## Output References",
            "",
            f"- Markdown ledger: `reports/analysis/L1_ENTITY_LEDGER__{stamp}.md`",
            f"- Machine-readable ledger: `reports/analysis/L1_ENTITY_LEDGER__{stamp}.json`",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs() -> None:
    payload = build_json_payload()
    markdown = render_markdown(payload)
    stamp = datetime.now(timezone.utc).date().isoformat()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = REPORTS_DIR / f"L1_ENTITY_LEDGER__{stamp}.md"
    json_path = REPORTS_DIR / f"L1_ENTITY_LEDGER__{stamp}.json"
    md_path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {json_path}")


def main() -> int:
    write_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
