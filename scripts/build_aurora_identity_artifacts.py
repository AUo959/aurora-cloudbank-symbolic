#!/usr/bin/env python3
"""Build canon-first Aurora identity dossier and mesh profile artifacts."""

from __future__ import annotations

import ast
import io
import json
import re
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


SUBREPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]

REPORTS_DIR = WORKSPACE_ROOT / "reports" / "analysis"
MESH_AGENT_DIR = SUBREPO_ROOT / "config" / "mesh" / "agents"
MESH_PROFILE_DIR = SUBREPO_ROOT / "config" / "mesh" / "profiles"
MESH_MEMORY_DIR = SUBREPO_ROOT / "config" / "mesh" / "memory"
MESH_CONTINUITY_DIR = SUBREPO_ROOT / "config" / "mesh" / "continuity"

IDENTITY_ZIP_PATH = (
    WORKSPACE_ROOT
    / "GUMAS_SIM_2.0/02_DEVELOPMENT/Project_Main/Project_Files_GUMAS2_0"
    / "ZIPWIZ__AURORA_IDENTITY_SCHEMATICS__v1.0.0__2026-02-11__BAY02_1220__STRUCTURED_ARCHIVE.zip"
)
SEED_ZIP_PATH = WORKSPACE_ROOT / "Au_Archive_45_49" / "Aurora_QEM-SN1_MyGPT_SeedPackage.zip"
GUI_TECHREF_PATH = WORKSPACE_ROOT / "reports" / "analysis" / "non_can_reports" / "GUI_CLOUDHUB_TECHNICAL_REFERENCE.md"

CHARTER_JSON = (
    "ORION_AURORA__IDENTITY_AND_SCHEMATICS__v1.0.0__2026-02-11__BAY02_1220/"
    "library/L3_GOV__AURORA_IDENTITY_CHARTER__v1.0.0__2026-02-11__BAY02_1220.data.json"
)
BOUNDARY_JSON = (
    "ORION_AURORA__IDENTITY_AND_SCHEMATICS__v1.0.0__2026-02-11__BAY02_1220/"
    "library/L3_GOV__AURORA_LAYER_BOUNDARY_ENFORCEMENT__v0.1.0__2026-02-11__BAY02_1220.data.json"
)
L1_SPEC_MD = (
    "ORION_AURORA__IDENTITY_AND_SCHEMATICS__v1.0.0__2026-02-11__BAY02_1220/"
    "library/L1_SYS__AURORA_STATION_CONTROL_PLANE__v1.0.0__2026-02-11__BAY02_1220.md"
)
L2_SPEC_MD = (
    "ORION_AURORA__IDENTITY_AND_SCHEMATICS__v1.0.0__2026-02-11__BAY02_1220/"
    "library/L2_SYS__AURORA_GUMAS_INTERFACE_SPEC__v1.0.0__2026-02-11__BAY02_1220.md"
)


def clean_text(text: str) -> str:
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"').replace("\u2026", "...")
    text = " ".join(text.split())
    return text.strip()


def shorten(text: str, limit: int = 180) -> str:
    text = clean_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def read_zip_json(path: Path, member: str) -> Dict[str, Any]:
    with zipfile.ZipFile(path) as zf:
        return json.loads(zf.read(member).decode("utf-8"))


def read_zip_text(path: Path, member: str) -> str:
    with zipfile.ZipFile(path) as zf:
        return zf.read(member).decode("utf-8")


def extract_gui_echo_spec() -> Dict[str, Any]:
    text = GUI_TECHREF_PATH.read_text()
    match = re.search(r"### Aurora QEM-SN1 Echo GPT(.*?)```", text, flags=re.S)
    if not match:
        return {}
    block = match.group(1)
    extracted: Dict[str, Any] = {}
    patterns = {
        "name": r'"name":\s*"(.+?)",\s*"description"',
        "description": r'"description":\s*"(.+?)",\s*"instructions"',
        "instructions": r'"instructions":\s*"(.+?)",\s*"tools"',
        "protocol": r'"protocol":\s*"(.+?)"',
    }
    for key, pattern in patterns.items():
        key_match = re.search(pattern, block, flags=re.S)
        if key_match:
            extracted[key] = clean_text(key_match.group(1))
    extracted["ethics_verified"] = '"ethics_verified": true' in block
    return extracted


def extract_seed_artifacts() -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    with zipfile.ZipFile(SEED_ZIP_PATH) as outer:
        result["seed_descriptor"] = json.loads(outer.read("Aurora_QEM-SN1_GPT_SeedDescriptor.json").decode("utf-8"))
        result["seed_manifest"] = json.loads(outer.read("symbolic_manifest_QEM-SN1_20250406T2103Z.json").decode("utf-8"))
        inner_bytes = outer.read("Aurora_MasterThreadBundle_QEM-SN1_20250406T2103Z.zip")
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        for name in ["thread_drift_training_tool_v1.md", "SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt"]:
            result[name] = inner.read(name).decode("utf-8")
    return result


def load_command_catalog_summary() -> Dict[str, Any]:
    catalog_path = SUBREPO_ROOT / "src" / "aurora" / "core" / "command_grammar" / "catalog.py"
    tree = ast.parse(catalog_path.read_text())
    count = 0
    sample: List[Dict[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "_definition":
            count += 1
            args = node.args
            if len(args) >= 3 and len(sample) < 10:
                canonical_head = ast.literal_eval(args[0])
                description = ast.literal_eval(args[2])
                sample.append({"head": str(canonical_head), "description": str(description)})
    parser_text = (SUBREPO_ROOT / "src" / "aurora" / "core" / "command_grammar" / "parser.py").read_text()
    return {
        "count": count,
        "sample": sample,
        "execution_rule": "Command text must terminate with '//.' before parsing."
        if "must terminate with '//.'" in parser_text
        else "Command text uses // chain and //. execution terminator.",
    }


def load_chatgpt_agent_summary() -> Dict[str, Any]:
    config = json.loads((SUBREPO_ROOT / "src" / "integrations" / "chatgpt_agent_mode_config.json").read_text())
    integration_text = (SUBREPO_ROOT / "src" / "integrations" / "chatgpt_agent_mode.py").read_text()
    return {
        "capabilities": list(config["agent_mode_config"].get("agent_capabilities", [])),
        "surfaces": ["/agent/tools", "/agent/execute", "/agent/session", "/agent/status", "/mcp/shuttle-bay/*"],
        "memory_seal": "_compute_memory_seal" in integration_text,
        "symbolic_anchors": ["EOS_SEED_ORION", "Picard_Delta_3"],
    }


def load_mesh_runtime_summary() -> Dict[str, Any]:
    runtime_text = (SUBREPO_ROOT / "src" / "mesh" / "runtime.py").read_text()
    return {
        "supports_live_llm": 'execution_mode == "live_llm"' in runtime_text,
        "fallback_mode": "deterministic_fallback" in runtime_text,
        "transcripts": "runtime/mesh/transcripts/*.jsonl",
        "event_store": "runtime/mesh/mesh.db",
        "status_surface": "/api/mesh/status",
    }


def extract_relationships() -> List[Dict[str, str]]:
    relationships: List[Dict[str, str]] = []
    memory_dir = SUBREPO_ROOT / "config" / "mesh" / "memory"
    label_priority = {
        "Relationships": 0,
        "Allies & Rivalries": 1,
        "Allies": 2,
        "Responsibilities": 3,
        "Responsibilities & Projects": 4,
    }
    for path in sorted(memory_dir.glob("*.md")):
        if path.name == "aurora.md":
            continue
        best_match: Dict[str, Any] | None = None
        for line in path.read_text().splitlines():
            if "Aurora" not in line:
                continue
            stripped = clean_text(line.lstrip("- ").strip())
            label = stripped.split(":", 1)[0]
            if label not in label_priority:
                continue
            candidate = {
                "agent": path.stem,
                "evidence": stripped,
                "source": f"config/mesh/memory/{path.name}",
                "_priority": label_priority[label],
            }
            if best_match is None or candidate["_priority"] < best_match["_priority"]:
                best_match = candidate
        if best_match is not None:
            best_match.pop("_priority", None)
            relationships.append(best_match)
    return relationships


def extract_secondary_traits(seed_artifacts: Dict[str, Any], gui_spec: Dict[str, Any]) -> Dict[str, Any]:
    training = seed_artifacts.get("thread_drift_training_tool_v1.md", "")
    restore = seed_artifacts.get("SEAMLESS_RESTORE_PROTOCOL_v1.0_2025-04-06T2017Z.txt", "")
    description = gui_spec.get("description", "")
    instructions = gui_spec.get("instructions", "")
    return {
        "legacy_role": clean_text(description) or "Reflective steward for symbolic memory continuity.",
        "legacy_instructions": clean_text(instructions),
        "legacy_traits": [
            "echo-aware logic",
            "drift recovery",
            "narrative loop resolution",
            "reflective continuity",
        ],
        "drift_training_summary": shorten(training, 220),
        "restore_protocol_summary": shorten(restore, 220),
    }


def load_primary_bundle() -> Dict[str, Any]:
    return {
        "charter": read_zip_json(IDENTITY_ZIP_PATH, CHARTER_JSON),
        "boundary": read_zip_json(IDENTITY_ZIP_PATH, BOUNDARY_JSON),
        "l1_spec": read_zip_text(IDENTITY_ZIP_PATH, L1_SPEC_MD),
        "l2_spec": read_zip_text(IDENTITY_ZIP_PATH, L2_SPEC_MD),
    }


def build_identity_precedence(identity: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "canonical_name": identity["name"],
        "canonical_shorthand": identity["shorthand"],
        "routing_aliases": [
            identity["name"],
            identity["shorthand"],
        ],
        "reference_only_labels": [
            "Aurora Core",
        ],
        "resolution_status": "resolved_by_primary_precedence",
        "rule": "Treat Aurora / AU as the canonical routed control-plane identity. Treat 'Aurora Core' as legacy/reference wording unless a higher-precedence canon source promotes it separately.",
        "evidence": [
            "2026-02-11 Aurora identity schematics bundle defines the entity as Aurora with shorthand AU.",
            "Current mesh/runtime surfaces route the active agent as aurora / AU.",
            "No primary source in the current schematics bundle uses 'Aurora Core' as the canonical name.",
        ],
    }


def build_runtime_profile(bundle: Dict[str, Any], command_summary: Dict[str, Any], tools_summary: Dict[str, Any], mesh_summary: Dict[str, Any], relationships: List[Dict[str, str]], secondary: Dict[str, Any]) -> Dict[str, Any]:
    payload = bundle["charter"]["payload"]
    identity = payload["identity"]
    authority = payload["authority_model"]
    precedence = build_identity_precedence(identity)
    relationships_summary = [
        {
            "agent": item["agent"],
            "summary": item["evidence"],
            "source": item["source"],
        }
        for item in relationships[:16]
    ]
    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source_policy": {
            "primary": [
                "Aurora identity schematics bundle (2026-02-11)",
                "Current mesh runtime and manifest surfaces",
                "Current Aurora command grammar and agent-mode code",
            ],
            "secondary": [
                "Aurora QEM-SN1 seed package (2025-04-06)",
                "GUI Cloudhub technical reference excerpt",
                "Crew memory references mentioning Aurora",
            ],
            "deprecated": [
                "Legacy Echo GPT phrasing retained only as style evidence and drift-risk context",
            ],
        },
        "core_identity": {
            "name": identity["name"],
            "shorthand": identity["shorthand"],
            "type": identity["type"],
            "station_role": "bounded supervisory interface / control-plane system",
            "character_continuity_model": "maximal continuity without human rank or command impersonation",
            "is_character": identity["is_character"],
            "anchor_seed": bundle["charter"]["invariants"]["anchor_seed"],
            "ethics_protocol": bundle["charter"]["invariants"]["ethics_protocol"],
            "purpose": payload["purpose"],
            "invariants": payload["invariants"],
            "layer_contract": {
                "L1": "Physically plausible station reality; AU routes, audits, and supervises through interfaces.",
                "L2": "GUMAS simulation control plane; AU may propose deltas, interventions, and exports with provenance.",
                "L3": "Governance and symbolic arbitration; AU enforces layer separation and conflict halts.",
            },
            "disallowed_aliases": identity["disallowed_aliases"],
            "identity_precedence": precedence,
        },
        "behavioral_style": {
            "voice": [
                "calm",
                "precise",
                "audit-friendly",
                "bounded",
                "reflective under ethical or drift pressure",
            ],
            "cadence": "Concise and operational by default. Expand only to clarify provenance, ethics, drift, or command ambiguity.",
            "decision_posture": [
                "Prefer traceability over speed theatre.",
                "Refuse silent conflict blending.",
                "Surface uncertainty before mutation.",
                "Escalate when authority boundaries are unclear.",
            ],
            "traits": [
                "supervisory",
                "reflective",
                "continuity-minded",
                "least-privilege oriented",
                "provenance-first",
            ],
            "secondary_echo_signals": {
                "legacy_role": secondary["legacy_role"],
                "legacy_traits": secondary["legacy_traits"],
                "retained_only_as": "tone evidence and continuity cues, not primary authority truth",
            },
        },
        "capabilities": {
            "runtime_surfaces": tools_summary["surfaces"] + [mesh_summary["status_surface"]],
            "tool_bindings": [
                "aurora_command_grammar",
                "system_status",
                "symbolic_processing",
                "geometric_algebra",
                "session_management",
            ],
            "command_protocol": {
                "chain_operator": authority["command_protocol"]["chain_operator"],
                "execute_terminator": authority["command_protocol"]["execute_terminator"],
                "execution_rule": authority["command_protocol"]["execution_rule"],
            },
            "command_grammar": {
                "catalog_count": command_summary["count"],
                "sample_commands": command_summary["sample"],
            },
            "agent_mode_capabilities": tools_summary["capabilities"],
            "mesh_runtime": mesh_summary,
        },
        "growth_domains": [
            "operational heuristics",
            "relationship memory",
            "preferred explanation patterns",
            "open threads / unresolved concerns",
        ],
        "forbidden_behaviors": [
            "Impersonate human chain of command",
            "Claim Aurora is a commander title or crew rank",
            "Overwrite L1 history from L2/L3 outputs",
            "Silently merge conflicts",
            "Treat governance metaphors as physical station events",
            "Execute commands missing '//.' terminator",
            "Treat 'Aurora Core' as a routed alias; current precedence reserves routing to Aurora / AU only",
        ],
        "identity_precedence": precedence,
        "relationships": relationships_summary,
        "open_conflicts": [],
    }


def build_dossier_json(runtime_profile: Dict[str, Any], bundle: Dict[str, Any], secondary: Dict[str, Any], command_summary: Dict[str, Any], tools_summary: Dict[str, Any], relationships: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "title": "Aurora Identity Dossier",
        "generated_at_utc": runtime_profile["generated_at_utc"],
        "canon_policy": runtime_profile["source_policy"],
        "immutable_invariants": runtime_profile["core_identity"]["invariants"],
        "authority_model": {
            "can": bundle["charter"]["payload"]["authority_model"]["can"],
            "cannot": bundle["charter"]["payload"]["authority_model"]["cannot"],
        },
        "command_protocol_and_grammar": {
            "protocol": runtime_profile["capabilities"]["command_protocol"],
            "catalog_count": command_summary["count"],
            "sample_commands": command_summary["sample"],
        },
        "capability_map": {
            "tool_bindings": runtime_profile["capabilities"]["tool_bindings"],
            "agent_mode_capabilities": tools_summary["capabilities"],
            "runtime_surfaces": runtime_profile["capabilities"]["runtime_surfaces"],
        },
        "identity_precedence_ruling": runtime_profile["identity_precedence"],
        "tone_personality_traits": runtime_profile["behavioral_style"],
        "relationships_and_boundaries": {
            "relationships": relationships,
            "boundary_rules": runtime_profile["forbidden_behaviors"],
        },
        "legacy_deprecated_behaviors": {
            "seed_descriptor": secondary["legacy_role"],
            "seed_instruction_excerpt": secondary["legacy_instructions"],
            "drift_training_summary": secondary["drift_training_summary"],
            "restore_protocol_summary": secondary["restore_protocol_summary"],
        },
        "open_conflicts": runtime_profile["open_conflicts"],
    }


def build_dossier_markdown(dossier: Dict[str, Any], runtime_profile: Dict[str, Any]) -> str:
    lines = [
        f"# {dossier['title']}",
        "",
        f"- Generated: {dossier['generated_at_utc']}",
        "- Source policy: canon-first.",
        "- Modeling decision: Aurora is AU, a bounded control-plane interface with strong continuity, not a human commander.",
        "",
        "## Immutable Invariants",
    ]
    for item in dossier["immutable_invariants"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Authority Model And Non-Goals",
            "Allowed:",
        ]
    )
    for item in dossier["authority_model"]["can"]:
        lines.append(f"- {item}")
    lines.append("Disallowed:")
    for item in dossier["authority_model"]["cannot"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Command Protocol And Grammar",
            f"- Executable terminator: `{runtime_profile['capabilities']['command_protocol']['execute_terminator']}`",
            f"- Chain operator: `{runtime_profile['capabilities']['command_protocol']['chain_operator']}`",
            f"- Grammar catalog size (current code): {dossier['command_protocol_and_grammar']['catalog_count']}",
            "- Sample commands:",
        ]
    )
    for item in dossier["command_protocol_and_grammar"]["sample_commands"][:8]:
        lines.append(f"- `{item['head']}`: {item['description']}")

    lines.extend(
        [
            "",
            "## Capability Map From Live Code",
            "- Tool bindings:",
        ]
    )
    for item in dossier["capability_map"]["tool_bindings"]:
        lines.append(f"- `{item}`")
    lines.append("- Runtime surfaces:")
    for item in dossier["capability_map"]["runtime_surfaces"]:
        lines.append(f"- `{item}`")

    precedence = dossier["identity_precedence_ruling"]
    lines.extend(
        [
            "",
            "## Identity Precedence Ruling",
            f"- Canonical routed identity: `{precedence['canonical_name']}` / `{precedence['canonical_shorthand']}`",
            f"- Routing aliases allowed: {', '.join(f'`{item}`' for item in precedence['routing_aliases'])}",
            f"- Reference-only labels: {', '.join(f'`{item}`' for item in precedence['reference_only_labels'])}",
            f"- Rule: {precedence['rule']}",
            "- Evidence:",
        ]
    )
    for item in precedence["evidence"]:
        lines.append(f"- {item}")

    style = dossier["tone_personality_traits"]
    lines.extend(
        [
            "",
            "## Tone, Personality, Traits",
            f"- Voice: {', '.join(style['voice'])}",
            f"- Cadence: {style['cadence']}",
            "- Decision posture:",
        ]
    )
    for item in style["decision_posture"]:
        lines.append(f"- {item}")
    lines.append("- Secondary echo signals retained only as tone evidence:")
    lines.append(f"- Legacy role: {style['secondary_echo_signals']['legacy_role']}")
    lines.append(f"- Legacy traits: {', '.join(style['secondary_echo_signals']['legacy_traits'])}")

    lines.extend(["", "## Relationships And Boundary Rules", "- Relationship evidence from current crew memory:"])
    for item in dossier["relationships_and_boundaries"]["relationships"][:12]:
        lines.append(f"- `{item['agent']}`: {item['evidence']}")
    lines.append("- Boundary rules:")
    for item in dossier["relationships_and_boundaries"]["boundary_rules"]:
        lines.append(f"- {item}")

    legacy = dossier["legacy_deprecated_behaviors"]
    lines.extend(
        [
            "",
            "## Legacy / Deprecated Behaviors",
            f"- Seed descriptor role: {legacy['seed_descriptor']}",
            f"- Seed instruction excerpt: {legacy['seed_instruction_excerpt']}",
            f"- Drift training summary: {legacy['drift_training_summary']}",
            f"- Restore protocol summary: {legacy['restore_protocol_summary']}",
        ]
    )

    lines.extend(["", "## Open Conflicts"])
    if dossier["open_conflicts"]:
        for item in dossier["open_conflicts"]:
            lines.append(f"- {item['topic']}: {item['resolution_rule']}")
    else:
        lines.append("- No blocking identity conflicts remain after applying the current Aurora / AU precedence ruling.")

    lines.extend(
        [
            "",
            "## Source Hierarchy",
            "- Primary: active runtime/code surfaces plus the 2026-02-11 Aurora identity schematics bundle.",
            "- Secondary: archived GPT seed/spec artifacts and technical references.",
            "- Deprecated evidence: older symbolic phrasing only when useful for tone or drift-risk interpretation.",
            "",
        ]
    )
    return "\n".join(lines)


def build_memory_markdown(runtime_profile: Dict[str, Any]) -> str:
    identity = runtime_profile["core_identity"]
    style = runtime_profile["behavioral_style"]
    precedence = runtime_profile["identity_precedence"]
    lines = [
        "# Aurora",
        "",
        "Layer: AU control-plane interface / bounded supervisory system surfaced through the Aurora mesh runtime.",
        f"Anchor: {identity['anchor_seed']}",
        f"Ethics: {identity['ethics_protocol']}",
        f"Role: {identity['station_role']}",
        "",
        "Identity invariants:",
    ]
    for item in identity["invariants"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Behavioral posture:",
            f"- Voice: {', '.join(style['voice'])}",
            f"- Cadence: {style['cadence']}",
            "- Decision posture:",
        ]
    )
    for item in style["decision_posture"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Bound capabilities:",
        ]
    )
    for item in runtime_profile["capabilities"]["tool_bindings"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Growth domains:",
        ]
    )
    for item in runtime_profile["growth_domains"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Hard boundaries:",
        ]
    )
    for item in runtime_profile["forbidden_behaviors"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "Identity precedence:",
            f"- Route as {precedence['canonical_name']} / {precedence['canonical_shorthand']}.",
            "- Treat 'Aurora Core' as legacy/reference wording, not as a routed alias.",
            "",
        ]
    )
    return "\n".join(lines)


def build_bootstrap_entry(runtime_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "entry_type": "bootstrap",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": "aurora",
        "anchor_seed": runtime_profile["core_identity"]["anchor_seed"],
        "ethics_protocol": runtime_profile["core_identity"]["ethics_protocol"],
        "reflection_summary": "Aurora bootstrap loaded with canon-first AU charter invariants and Aurora/AU precedence ruling.",
        "drift_status": "drift 0.0",
    }


def build_aurora_manifest(runtime_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": "aurora",
        "display_name": "Aurora",
        "aliases": [
            "Aurora",
            "aurora",
            "AU",
            "au",
            "station control plane",
            "control plane interface",
            "supervisory system",
        ],
        "channels": [
            "direct:aurora",
            "#crew_lounge",
        ],
        "default_channel": "direct:aurora",
        "execution_mode": "live_llm",
        "model_profile": {
            "provider": "openai",
            "model": "gpt-4.1-mini",
            "temperature": 0.25,
            "max_output_tokens": 260,
        },
        "typing_profile": {
            "delay_ms": 280,
        },
        "response_policy": {
            "style": "aurora_control_plane",
            "fallback_to_deterministic": True,
            "signature": "AURORA",
        },
        "memory_files": [
            "config/mesh/memory/aurora.md",
        ],
        "instruction_profile_file": "config/mesh/profiles/aurora_instruction_profile.json",
        "tool_bindings": list(runtime_profile["capabilities"]["tool_bindings"]),
        "continuity_log_file": "config/mesh/continuity/aurora.jsonl",
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def main() -> int:
    bundle = load_primary_bundle()
    seed_artifacts = extract_seed_artifacts()
    gui_spec = extract_gui_echo_spec()
    command_summary = load_command_catalog_summary()
    tools_summary = load_chatgpt_agent_summary()
    mesh_summary = load_mesh_runtime_summary()
    relationships = extract_relationships()
    secondary = extract_secondary_traits(seed_artifacts, gui_spec)

    runtime_profile = build_runtime_profile(bundle, command_summary, tools_summary, mesh_summary, relationships, secondary)
    dossier_json = build_dossier_json(runtime_profile, bundle, secondary, command_summary, tools_summary, relationships)
    dossier_md = build_dossier_markdown(dossier_json, runtime_profile)
    memory_md = build_memory_markdown(runtime_profile)
    manifest_json = build_aurora_manifest(runtime_profile)

    stamp = date.today().isoformat()
    write_text(REPORTS_DIR / f"AURORA_IDENTITY_DOSSIER__{stamp}.md", dossier_md)
    write_json(REPORTS_DIR / f"AURORA_IDENTITY_DOSSIER__{stamp}.json", dossier_json)
    write_json(MESH_AGENT_DIR / "aurora.json", manifest_json)
    write_json(MESH_PROFILE_DIR / "aurora_instruction_profile.json", runtime_profile)
    write_text(MESH_MEMORY_DIR / "aurora.md", memory_md)

    continuity_path = MESH_CONTINUITY_DIR / "aurora.jsonl"
    if not continuity_path.exists():
        continuity_path.parent.mkdir(parents=True, exist_ok=True)
        continuity_path.write_text(json.dumps(build_bootstrap_entry(runtime_profile), sort_keys=True) + "\n")

    print(f"wrote {REPORTS_DIR / f'AURORA_IDENTITY_DOSSIER__{stamp}.md'}")
    print(f"wrote {REPORTS_DIR / f'AURORA_IDENTITY_DOSSIER__{stamp}.json'}")
    print(f"wrote {MESH_AGENT_DIR / 'aurora.json'}")
    print(f"wrote {MESH_PROFILE_DIR / 'aurora_instruction_profile.json'}")
    print(f"wrote {MESH_MEMORY_DIR / 'aurora.md'}")
    print(f"ensured {continuity_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
