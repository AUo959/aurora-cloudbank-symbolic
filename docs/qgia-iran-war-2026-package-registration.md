# QGIA Iran War 2026 — Constellation Package Registration

## Purpose

This document registers the Iran War 2026 documentation package with CONSTELLATION-PRIME (aurora-cloudbank-symbolic) and provides knowledge-index integration notes, cross-repo node manifests, and event-contract references.

---

## Package Node Registration

| Field | Value |
|---|---|
| Package ID | `qgia.iran-war-2026` |
| Package type | Theater assessment bundle |
| Primary repo | `qgia-knowledge-library` |
| Path | `regions/middle-east/iran/iran-war-2026/` |
| Schema repo | `qgia-knowledge-spine` |
| Schema path | `frameworks/`, `schemas/`, `methods/` |
| Runtime repo | `Orion-Station-QGIA` |
| Runtime path | `docs/runtime-ingestion-iran-war-2026.md` |
| Baseline date | 2026-04-19T00:00:00Z |
| Status | Active — kinetic conflict in progress |

---

## Cross-Repo Node Manifest

```json
{
  "node_id": "qgia.iran-war-2026",
  "node_type": "theater_assessment_bundle",
  "status": "active",
  "baseline_timestamp": "2026-04-19T00:00:00Z",
  "repos": {
    "schema": {
      "repo": "qgia-knowledge-spine",
      "paths": [
        "frameworks/iran-war-scenario-taxonomy.md",
        "schemas/actor-card-schema.md",
        "schemas/probability-ledger-schema.md",
        "methods/iran-regime-dirichlet-template.md"
      ]
    },
    "corpus": {
      "repo": "qgia-knowledge-library",
      "paths": [
        "regions/middle-east/iran/iran-war-2026/README.md",
        "regions/middle-east/iran/iran-war-2026/baseline-ledger.md",
        "regions/middle-east/iran/iran-war-2026/actor-cards.md",
        "regions/middle-east/iran/iran-war-2026/scenario-catalog.md"
      ]
    },
    "runtime": {
      "repo": "Orion-Station-QGIA",
      "paths": [
        "docs/runtime-ingestion-iran-war-2026.md",
        "docs/config-contracts.md"
      ]
    }
  },
  "upstream_links": [
    "qgia.spine",
    "qgia.corpus"
  ],
  "downstream_consumers": [
    "qgia.space-node",
    "qgia.orion-runtime"
  ]
}
```

---

## Knowledge-Index Integration Notes

### Index Entry Requirements

When updating `.aurora/knowledge-index.json`, the Iran War 2026 package should be indexed with the following metadata:

```json
{
  "id": "qgia.iran-war-2026",
  "title": "Iran War 2026 Theater Assessment Bundle",
  "theater": "Middle East / Iran",
  "type": "theater_assessment",
  "status": "active",
  "baseline": "2026-04-19T00:00:00Z",
  "documents": [
    { "id": "iran-war-scenario-taxonomy", "repo": "qgia-knowledge-spine", "type": "framework" },
    { "id": "actor-card-schema", "repo": "qgia-knowledge-spine", "type": "schema" },
    { "id": "probability-ledger-schema", "repo": "qgia-knowledge-spine", "type": "schema" },
    { "id": "iran-regime-dirichlet-template", "repo": "qgia-knowledge-spine", "type": "method" },
    { "id": "iran-war-2026-readme", "repo": "qgia-knowledge-library", "type": "theater_readme" },
    { "id": "iran-war-2026-baseline-ledger", "repo": "qgia-knowledge-library", "type": "ledger" },
    { "id": "iran-war-2026-actor-cards", "repo": "qgia-knowledge-library", "type": "actor_cards" },
    { "id": "iran-war-2026-scenario-catalog", "repo": "qgia-knowledge-library", "type": "scenario_catalog" }
  ],
  "key_scenarios": [
    "IRN_WAR_PROTRACTED_AIR_CAMPAIGN_60_180D",
    "IRN_WAR_REGION_WIDE_CONFLICT_GE_6_STATES",
    "IRN_REGIME_H1_HARDLINE_SURVIVAL",
    "IRN_WAR_HORMUZ_CLOSURE_GE_60D",
    "IRN_WAR_NUCLEAR_DECISION_WITHIN_12M"
  ]
}
```

### Auto-Index Trigger

Once both `qgia-knowledge-spine` PR #2 and `qgia-knowledge-library` PR #3 are merged, the auto-index pipeline should be triggered to:
1. Pull updated manifests from both repos
2. Register the `qgia.iran-war-2026` node in `.aurora/knowledge-index.json`
3. Emit a `KNOWLEDGE_NODE_REGISTERED` event to downstream consumers
4. Notify `qgia.space-node` and `qgia.orion-runtime` of the new package availability

---

## Event Contracts

### `KNOWLEDGE_NODE_REGISTERED`

```json
{
  "event_type": "KNOWLEDGE_NODE_REGISTERED",
  "node_id": "qgia.iran-war-2026",
  "timestamp": "<merge_timestamp>",
  "triggering_repos": ["qgia-knowledge-spine", "qgia-knowledge-library"],
  "consumers": ["qgia.space-node", "qgia.orion-runtime"]
}
```

### `LEDGER_BASELINE_COMMITTED`

```json
{
  "event_type": "LEDGER_BASELINE_COMMITTED",
  "package_id": "qgia.iran-war-2026",
  "timestamp": "2026-04-19T00:00:00Z",
  "scenario_count": 9,
  "tier_1_count": 5,
  "tier_2_count": 4,
  "composite_confidence": 0.74
}
```

---

## Maintenance

- Registration document should be updated when package structure changes materially.
- Knowledge-index entries must be updated when new theater documents are added.
- Event contracts should be versioned alongside the schema repo.

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Status | Draft |
| Owner | CONSTELLATION-PRIME / aurora-cloudbank-symbolic |
| Review cycle | On package structural change |
