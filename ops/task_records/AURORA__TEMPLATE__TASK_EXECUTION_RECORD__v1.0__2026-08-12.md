# Aurora Durable Task Execution Record

**Task ID:** `TASK-YYYYMMDD-<slug>`  
**Version:** `v1.0`  
**Created:** `YYYY-MM-DD`  
**Status:** `planned | active | blocked | waiting_review | completed | aborted | superseded | rolled_back`  
**Owner / active worker:** `<name/agent>`  
**Repository:** `<owner/repo>`  
**Branch:** `<branch>`  
**Queue ID:** `<id or none>`  
**Issue:** `<# or none>`  
**PR:** `<# or none>`  
**Creation commit:** `<sha once committed>`  
**Controlling revision:** `<this file/version + commit>`

---

## 1. Objective

`<What outcome are we trying to achieve?>`

## 2. Acceptance statement

This task is complete when:

- `<testable completion condition>`
- `<testable completion condition>`

## 3. Authority and source inputs

### Independently verified

- `<path / commit / source / artifact>` — `<why authoritative>`

### Externally supplied evidence

- `<source>` — `<status and verification boundary>`

### Owner decisions

- `<decision>` — `<date/context>`

### Assumptions

- `<assumption>` — `<how it will be verified or contained>`

## 4. Scope

### In scope

- `<item>`

### Out of scope

- `<item>`

### Protected / immutable surfaces

- `<item>`

## 5. Current state and known gaps

### Current state

- `<fact>`

### Known gaps / blockers

- `<gap>`

### Contradictions / drift to resolve

- `<item>`

## 6. Planned mutations

| Surface / path | Intended change | Authority / rationale | Risk |
| --- | --- | --- | --- |
| `<path>` | `<change>` | `<why>` | `<low/medium/high>` |

Unexpected mutation surfaces discovered later must be recorded in the plan-delta log before or with the corresponding implementation commit.

## 7. Execution sequence and gates

### Phase 0 — Preflight

Actions:
- `<action>`

Gate to exit:
- `<condition>`

### Phase 1 — `<name>`

Actions:
- `<action>`

Gate to exit:
- `<condition>`

### Phase 2 — `<name>`

Actions:
- `<action>`

Gate to exit:
- `<condition>`

## 8. Invariants and non-negotiables

- `<property that must remain true>`
- `<property that must remain true>`

## 9. Validation and acceptance tests

| ID | Validation | Expected result | Evidence / receipt |
| --- | --- | --- | --- |
| `V-01` | `<test/check>` | `<expected>` | `<pending>` |

## 10. Stop conditions and owner decisions

Stop and request owner/authority input if:

- `<condition>`
- `<condition>`

Do not improvise across these boundaries.

## 11. Rollback and recovery

### Pre-mutation recovery points

- `<backup/hash/commit/witness>`

### Rollback procedure

1. `<step>`
2. `<step>`

## 12. Decision and plan-delta log

| Date / commit | Decision or delta | Evidence / reason | Authority | Consequence |
| --- | --- | --- | --- | --- |
| `YYYY-MM-DD` | Initial plan committed | `<reason>` | `<authority>` | Implementation may begin after preflight gate |

Do not delete earlier material decisions after work has depended on them. Major changes require a new task-record version.

## 13. Evidence and receipts

### Commits

- `<sha>` — `<purpose>`

### Source / artifact hashes

- `<sha256>` — `<artifact>`

### CI / tests / replay / audit

- `<result>`

### Superseded artifacts

- `<artifact>` — superseded by `<artifact>`, retained for lineage

## 14. Current status and next action

**Current phase:** `<phase>`  
**Completed gates:** `<list>`  
**Open blockers:** `<list>`  
**Owner decision required:** `yes/no`  
**Exact next action:** `<single concrete continuation step>`

## 15. Handoff anchor

Any handoff for this task must reference:

- task record: `<repo path>`
- task record version: `<version>`
- controlling commit / PR head: `<sha>`
- current phase: `<phase>`
- exact next action: `<action>`
- unresolved blocker / decision: `<item or none>`

A handoff supplements this record; it does not replace it.

## 16. Completion record

**Final status:** `<pending>`  
**Merge / closing PR:** `<pending>`  
**Final controlling commit:** `<pending>`  
**Validation result:** `<pending>`  
**Residual risks / follow-ups:** `<pending>`  
**Successor task record(s):** `<none/pending>`
