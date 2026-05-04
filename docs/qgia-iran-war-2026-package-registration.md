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
    "QGIA-SPINE",
    "QGIA-CORPUS"
  ],
  "downstream_consumers": [
    "CONSTELLATION-PRIME",
    "AURORA-RUNTIME"
  ]
}
```

---

## Knowledge-Index Integration Notes

### Index Entry Requirements

When updating `.aurora/knowledge-index.json`, represent the Iran War 2026 package through schema-compliant `documents[]` entries in the source repo's top-level knowledge index. Package-level metadata such as status, baseline date, key scenarios, and dependency state belongs in this registration document or a dedicated package manifest unless `constellation-contracts/schemas/knowledge-index.schema.json` is extended.

Example `qgia-knowledge-spine/.aurora/knowledge-index.json` structure:

```json
{
  "version": "1.0.0",
  "source_repo": "qgia-knowledge-spine",
  "generated_at": "2026-04-19T00:00:00Z",
  "documents": [
    {
      "id": "iran-war-scenario-taxonomy",
      "title": "Iran War Scenario Taxonomy",
      "domain": "framework",
      "path": "frameworks/iran-war-scenario-taxonomy.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    },
    {
      "id": "actor-card-schema",
      "title": "Actor Card Schema",
      "domain": "schema",
      "path": "schemas/actor-card-schema.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    },
    {
      "id": "probability-ledger-schema",
      "title": "Probability Ledger Schema",
      "domain": "schema",
      "path": "schemas/probability-ledger-schema.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    },
    {
      "id": "iran-regime-dirichlet-template",
      "title": "Iran Regime Dirichlet Template",
      "domain": "method",
      "path": "methods/iran-regime-dirichlet-template.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    }
  ]
}
```

Example `qgia-knowledge-library/.aurora/knowledge-index.json` structure:

```json
{
  "version": "1.0.0",
  "source_repo": "qgia-knowledge-library",
  "generated_at": "2026-04-19T00:00:00Z",
  "documents": [
    {
      "id": "iran-war-2026-readme",
      "title": "Iran War 2026 Package README",
      "domain": "theater_readme",
      "path": "regions/middle-east/iran/iran-war-2026/README.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    },
    {
      "id": "iran-war-2026-baseline-ledger",
      "title": "Iran War 2026 Baseline Ledger",
      "domain": "ledger",
      "path": "regions/middle-east/iran/iran-war-2026/baseline-ledger.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    },
    {
      "id": "iran-war-2026-actor-cards",
      "title": "Iran War 2026 Actor Cards",
      "domain": "actor_cards",
      "path": "regions/middle-east/iran/iran-war-2026/actor-cards.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    },
    {
      "id": "iran-war-2026-scenario-catalog",
      "title": "Iran War 2026 Scenario Catalog",
      "domain": "scenario_catalog",
      "path": "regions/middle-east/iran/iran-war-2026/scenario-catalog.md",
      "checksum": "REPLACE_WITH_ACTUAL_SHA256"
    }
  ]
}
```

### Auto-Index Trigger

Once both `qgia-knowledge-spine` PR #2 and `qgia-knowledge-library` PR #3 are merged, the auto-index pipeline should be triggered to:
1. Pull updated manifests from both repos
2. Regenerate and validate the schema-compliant `.aurora/knowledge-index.json` files
3. Emit `qgia.knowledge.updated` events from `QGIA-SPINE` and `QGIA-CORPUS`
4. Notify `CONSTELLATION-PRIME` and `AURORA-RUNTIME` of the new package availability through the event payload

---

## Event Contracts

### Package schema registration

```json
{
  "event_type": "qgia.knowledge.updated",
  "source_node": "QGIA-SPINE",
  "timestamp": "2026-04-19T00:00:00Z",
  "payload": {
    "action": "package_schema_registered",
    "package_id": "qgia.iran-war-2026",
    "triggering_repos": ["qgia-knowledge-spine", "qgia-knowledge-library"],
    "documents": [
      "frameworks/iran-war-scenario-taxonomy.md",
      "schemas/actor-card-schema.md",
      "schemas/probability-ledger-schema.md",
      "methods/iran-regime-dirichlet-template.md"
    ],
    "consumers": ["CONSTELLATION-PRIME", "AURORA-RUNTIME"]
  }
}
```

### Ledger baseline committed

```json
{
  "event_type": "qgia.knowledge.updated",
  "source_node": "QGIA-CORPUS",
  "timestamp": "2026-04-19T00:00:00Z",
  "payload": {
    "action": "ledger_baseline_committed",
    "package_id": "qgia.iran-war-2026",
    "scenario_count": 9,
    "tier_1_count": 5,
    "tier_2_count": 4,
    "composite_confidence": 0.74
  }
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
