{
  "schema_version": "1.0.0",
  "audience": "new_ai_agent",
  "repository": "AUo959/aurora-cloudbank-symbolic",
  "bootstrap_order": [
    "AGENTS.md",
    "AURORA_CONTEXT.json",
    "CANON_INDEX.md",
    "ORION_STATION_CANONICAL_STAFF_REGISTRY.json",
    "diagnostics.json"
  ],
  "validation_command": "python scripts/aurora_onboard.py --agent",
  "architecture_authority": "docs/architecture/LAYER_ARCHITECTURE.md",
  "runtime_entrypoint": "api/aurora_api.py",
  "identity": {
    "aurora": "simulation director for Orion Station",
    "l1_relay_agents": [
      "ARCHY",
      "OPPY",
      "LIORA",
      "STARLING_AU",
      "RIVERTHREAD_808"
    ],
    "l1_continuity_system_entity": "HALO",
    "l3_frameworks": [
      "Axiomera",
      "Caelion",
      "Sentari",
      "Velatrix",
      "Glyphon",
      "Harmion"
    ]
  },
  "constraints": [
    "separate reality-layer residency from Triplex protocol roles",
    "do not describe HALO as a sixth communication relay",
    "do not describe L1 relay agents as L2-resident",
    "read live repository files before claiming system state",
    "preserve draft, staged, and canonical distinctions",
    "do not treat .aurora/SIMULATION_STATE.json as current without its last_updated value"
  ],
  "next_sources": {
    "architecture_quickmap": "ARCHITECTURE_QUICKMAP.md",
    "source_orientation": "src/README.md",
    "qgia_simulation_rationale": "docs/architecture/QGIA_SIM_BRIDGE.md",
    "contribution_rules": "CONTRIBUTING.md"
  }
}
