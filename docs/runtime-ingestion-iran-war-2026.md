# Iran War 2026 — Runtime Ingestion Contract

## Purpose

This document specifies the runtime ingestion contract for the Iran War 2026 package within Orion Station / QGIA. It defines how schema files, actor cards, probability ledgers, and scenario catalogs from the Knowledge Spine and Library should be loaded, validated, and registered for use in OSIQP simulations, ABCP updates, and QSFE scenario runs.

---

## Source Document Map

| Document | Source Repo | Path | Ingestion Role |
|---|---|---|---|
| Scenario taxonomy | `qgia-knowledge-spine` | `frameworks/iran-war-scenario-taxonomy.md` | Scenario ID registry |
| Actor card schema | `qgia-knowledge-spine` | `schemas/actor-card-schema.md` | Validation schema |
| Ledger schema | `qgia-knowledge-spine` | `schemas/probability-ledger-schema.md` | Ledger validation |
| Dirichlet template | `qgia-knowledge-spine` | `methods/iran-regime-dirichlet-template.md` | Prior initialization |
| Baseline ledger | `qgia-knowledge-library` | `regions/middle-east/iran/iran-war-2026/baseline-ledger.md` | Initial state load |
| Actor cards | `qgia-knowledge-library` | `regions/middle-east/iran/iran-war-2026/actor-cards.md` | Actor node initialization |
| Scenario catalog | `qgia-knowledge-library` | `regions/middle-east/iran/iran-war-2026/scenario-catalog.md` | Scenario tree construction |

---

## Ingestion Sequence

1. **Load and validate scenario taxonomy** — Register all canonical `scenario_id` values into the active scenario registry. Reject any downstream document referencing undefined IDs.

2. **Load actor card schema** — Store validation rules for required fields, utility encoding constraints, and trigger rule delta bounds.

3. **Load and validate actor cards** — Validate each card against the schema. Initialize actor nodes in the ABCP simulation graph with utility weights, hard constraints, and trigger rules active.

4. **Load ledger schema** — Register column definitions, distribution type vocabulary, and update threshold rules.

5. **Load and validate baseline ledger** — Initialize probability state for all scenarios. Load Dirichlet prior Dir(4.0, 2.0, 1.8, 1.2) for the regime trajectory family. Validate that `dirichlet_component` rows sum to 1.00 within their scenario family and window.

6. **Load scenario catalog** — Construct the scenario tier index. Register Tier I scenarios as primary tracking targets for all QGIA deliverables.

7. **Register package node** — Emit a `qgia.knowledge.updated` event that conforms to the shared Constellation event schema, including `source_node` and a `payload` object with package registration metadata for CONSTELLATION-PRIME and AURORA-RUNTIME consumers.

---

## Validation Rules

| Check | Condition | Action on Failure |
|---|---|---|
| Scenario ID integrity | All `scenario_id` values in ledger and actor cards exist in taxonomy | Reject document, log error |
| Actor card required fields | All required fields present and typed correctly | Reject card, log error |
| Utility range | All utility values are integers 1–5 | Reject card |
| Trigger delta bounds | All `delta` values in trigger rules are 0.01–0.15 | Warn; do not reject |
| Dirichlet sum | Regime trajectory probabilities sum to 1.00 ± 0.001 | Reject ledger section |
| Confidence range | All confidence scores are 0.00–1.00 | Reject row |
| Timestamp format | ISO-8601 required | Reject row |

---

## Configuration Contract

```yaml
package_id: qgia.iran-war-2026
baseline_timestamp: "2026-04-19T00:00:00Z"
theater: Iran
status: active

scenario_families:
  - family_id: regime_trajectory
    distribution: dirichlet
    alpha: [4.0, 2.0, 1.8, 1.2]
    members:
      - IRN_REGIME_H1_HARDLINE_SURVIVAL
      - IRN_REGIME_H2_MANAGED_TRANSITION
      - IRN_REGIME_H3_REVOLUTIONARY_COLLAPSE
      - IRN_REGIME_H4_FRAGMENTED_AUTHORITY

  - family_id: war_outcomes
    distribution: independent_beta
    members:
      - IRN_WAR_CEASEFIRE_0_60D
      - IRN_WAR_PROTRACTED_AIR_CAMPAIGN_60_180D
      - IRN_WAR_HORMUZ_CLOSURE_GE_60D
      - IRN_WAR_CARRIER_COMBAT_LOSS
      - IRN_WAR_REGION_WIDE_CONFLICT_GE_6_STATES
      - IRN_WAR_NUCLEAR_DECISION_WITHIN_12M

actor_nodes:
  - IRGC_QF
  - ISR_NETANYAHU_COALITION
  - US_EXECUTIVE_TRUMP

update_thresholds:
  min_delta_to_log: 0.03
  dirichlet_concentration_alert: 0.70
  instability_signal_threshold: 0.45  # H3 + H4 combined

confidence_floor:
  warn_below: 0.60
  reject_below: 0.40
```

---

## Episode Step Reference

A minimal episode step for OSIQP simulation:

```yaml
episode_id: iran-war-2026-ep001
package_id: qgia.iran-war-2026
step: 1
timestamp: "2026-04-19T00:00:00Z"
active_scenarios:
  - IRN_WAR_PROTRACTED_AIR_CAMPAIGN_60_180D
  - IRN_WAR_REGION_WIDE_CONFLICT_GE_6_STATES
  - IRN_WAR_HORMUZ_CLOSURE_GE_60D
observations: []
actor_mode_overrides: {}
ledger_snapshot: baseline
```

---

## Versioning

| Field | Value |
|---|---|
| Version | 0.1.0 |
| Status | Draft |
| Owner | Orion Station / QGIA Runtime |
| Review cycle | On schema or package structural change |
