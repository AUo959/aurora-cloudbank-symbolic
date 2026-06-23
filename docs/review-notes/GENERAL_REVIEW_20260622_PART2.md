# General Review — Part 2: docs/ Layer
**Date:** 2026-06-22 (evening session, continued from GENERAL_REVIEW_20260622.md)
**Scope:** Full scan of `docs/` directory — file inventory, naming conventions, coverage gaps, subdirectory structure, cross-reference health

---

## 1. docs/ Directory Inventory Summary

The `docs/` directory contains **35+ top-level files** and **12 subdirectories**. Total estimated documentation surface: ~350–400KB of markdown. This is a large, mature documentation layer — well above average for a repo of this type.

### Subdirectories Present

| Directory | Purpose (inferred) | Notes |
|-----------|-------------------|-------|
| `docs/api/` | API reference documentation | Not yet scanned |
| `docs/architecture/` | L1/L2/L3 canonical architecture docs | Contains `LAYER_ARCHITECTURE.md` (canonical per CANON_INDEX) |
| `docs/archive/` | Superseded / historical docs | Existence of archive dir is good hygiene |
| `docs/ethics/` | Ethics governance documents | Directly relevant to SENTINEL; not yet in CANON_INDEX |
| `docs/images/` | Embedded documentation images | Standard |
| `docs/modules/` | Module-level documentation | Not yet scanned |
| `docs/reference/` | Reference material | Not yet scanned |
| `docs/review-notes/` | Session review notes (this directory) | Active; prior notes from this session are here |
| `docs/security/` | Security-specific documentation | Parallel to `.security/` at root — potential overlap |
| `docs/specs/` | Technical specifications | Not yet scanned |

---

## 2. Naming Convention Inconsistency

The `docs/` layer has a mixed naming convention that will cause friction for both agents and humans:

- **SCREAMING_SNAKE_CASE** (majority): `CONNECTOR_FRAMEWORK_GUIDE.md`, `GEOMETRIC_ETHICS_ARCHITECTURE.md`, `INCIDENT_RESPONSE_RUNBOOK.md`, `MONITORING_SYSTEM.md`, `QUANTUM_FORGE_V3_COMPLETE_GUIDE.md`, etc.
- **lowercase_snake_case** (minority): `architecture.md`, `index.md`, `python_env_setup.md`
- **Mixed-case with hyphens** (one instance): `Rate-Limiting.md`

**`Rate-Limiting.md` is the only hyphenated filename in the directory** — it doesn't conform to either convention and will sort inconsistently across tools. It should be renamed to `RATE_LIMITING.md` for consistency.

**The lowercase files** (`architecture.md`, `index.md`) appear to be lightweight entry-points or stubs, which may be intentional. However, `architecture.md` (1,987 bytes) and the canonical `docs/architecture/LAYER_ARCHITECTURE.md` may contain overlapping or conflicting content. These need to be cross-checked — the stub should either explicitly redirect to the canonical doc or be removed.

**Recommended convention going forward:** SCREAMING_SNAKE_CASE for all canonical docs, lowercase for stub/index/nav files. Document this in CONTRIBUTING.md.

---

## 3. High-Signal Files by Domain

### Security Surface (`docs/` flat layer)
Six security-related documents exist at the flat `docs/` level:
- `SECURITY_GUIDELINES.md` (5.1KB)
- `SECURITY_PATTERNS.md` (8.9KB)
- `RBAC_SECURITY_SUMMARY.md` (12.7KB)
- `RBAC_INTEGRATION_EXAMPLES.md` (18.3KB)
- `OAUTH2_SETUP_GUIDE.md` (14KB)
- `DLP_GOVERNANCE_POLICY.md` (8.3KB)

Plus a `docs/security/` subdirectory exists separately. This creates a two-tier security doc structure with no clear organizing principle. A contributor or agent searching for security guidance would find some docs at `docs/` and others at `docs/security/` with no index linking them.

**Action:** Create a `docs/security/README.md` that serves as a security doc map — listing all security-relevant files in both tiers with a one-line description of each. This would also be the target entry in an expanded CANON_INDEX.

### Ethics (`docs/ethics/`)
A `docs/ethics/` subdirectory exists but was not individually scanned this pass. Given that ethics governance is one of Aurora's three architectural pillars (alongside simulation integrity and security-awareness), this directory is a priority target for the next scan. It likely contains or should contain:
- `Picard_Delta_3` protocol documentation
- Ethics audit log schema
- SENTINEL-relevant governance constraints

**Action (next session):** Scan `docs/ethics/` fully and verify coverage against the GEOMETRIC_ETHICS_ARCHITECTURE.md (13.3KB) already at the flat docs level.

### Monitoring & Telemetry Cluster
Four overlapping files cover monitoring/observability:
- `MONITORING_SYSTEM.md` (14.4KB) — comprehensive
- `MONITORING_QUICKSTART.md` (8.1KB) — abbreviated entry point
- `TELEMETRY_OBSERVABILITY.md` (10.1KB) — overlapping scope
- `OPENTELEMETRY.md` (9.2KB) — specific to OTel implementation
- `R2_AGENT_TELEMETRY.md` (11.8KB) — agent-specific telemetry

This is five documents covering what could reasonably be three (system overview, quickstart, OTel-specific). The agent-specific telemetry doc (`R2_AGENT_TELEMETRY.md`) is the only one with a unique scope. The relationship between `MONITORING_SYSTEM.md` and `TELEMETRY_OBSERVABILITY.md` is unclear from names alone — they may be duplicating significant content.

**Action:** Audit `MONITORING_SYSTEM.md` and `TELEMETRY_OBSERVABILITY.md` for content overlap. If >40% overlap, merge and deprecate one. Add `docs/monitoring/` as a subdirectory and consolidate the cluster there.

### Connector Framework Cluster
Three layered docs cover connectors:
- `CONNECTOR_SDK.md` (17.8KB) — full SDK reference
- `CONNECTOR_FRAMEWORK_GUIDE.md` (14.3KB) — guide-level
- `CONNECTOR_QUICK_REFERENCE.md` (10.6KB) — quick reference

This is a well-structured three-tier pattern (full → guide → quick ref) and represents best-practice documentation layering. **No action needed** — this is a model for how other doc clusters should be organized.

### Dependency Documentation
Three dependency docs exist:
- `DEPENDENCIES.md` (5.2KB)
- `DEPENDENCY_MANAGEMENT.md` (8KB)
- `DEPENDENCY_VERSION_POLICY.md` (3.9KB)

This is appropriate granularity. The distinction between `DEPENDENCIES.md` (what we depend on) and `DEPENDENCY_MANAGEMENT.md` (how we manage them) is valid. The version policy as a separate doc is correct for a repo with mixed Python/Node dependencies.

### Quantum Forge Documentation
- `QUANTUM_FORGE_V3_COMPLETE_GUIDE.md` (43KB) — largest single doc in `docs/`
- `QUANTUM_FORGE_V3_QUICK_REFERENCE.md` (8.6KB)
- `QUANTUM_CLOUD_BACKENDS.md` (14.6KB)

At 43KB, the complete guide is close to the upper bound for a single markdown file before it becomes unwieldy for agents to load in context. **No immediate action required**, but if Quantum Forge documentation grows further it should be split into a `docs/quantum_forge/` subdirectory.

### Synergy Dashboard Cluster
- `SYNERGY_DASHBOARD.md` (11.2KB)
- `SYNERGY_DASHBOARD_QUICKSTART.md` (4.7KB)
- `SYNERGY_DASHBOARD_UI.md` (4.7KB)

The quickstart and UI docs are nearly identical in size (4,746 and 4,745 bytes respectively). This warrants investigation — they may be near-duplicate content or their scope boundaries may not be well-defined.

---

## 4. Critical Architecture File — Naming Collision Risk

Two files reference architecture at the `docs/` level:
- `docs/architecture.md` (1,987 bytes — likely a stub or redirect)
- `docs/architecture/` (directory containing `LAYER_ARCHITECTURE.md` and related canonical docs)

Any agent or tool that resolves `docs/architecture` as a path will encounter ambiguity — is the target the file or the directory? On most systems the directory takes precedence, but this is a fragile assumption. The stub file `docs/architecture.md` should be renamed `docs/ARCHITECTURE_OVERVIEW.md` or its content merged into `docs/index.md` to eliminate the collision.

---

## 5. What's Well-Structured in docs/

- **Review-notes directory** (`docs/review-notes/`) is correctly positioned as the session-observation intake queue per the root `ROADMAP.md` design. This session's notes are landing in the right place.
- **Archive subdirectory** (`docs/archive/`) signals disciplined document lifecycle management — superseded docs are being kept but separated, not deleted.
- **Incident response runbook** exists (`INCIDENT_RESPONSE_RUNBOOK.md`, 11.6KB) — this is a critical operational document that many repos omit entirely.
- **DLP governance policy** exists (`DLP_GOVERNANCE_POLICY.md`, 8.3KB) — data loss prevention policy at this detail level reflects mature operational thinking.
- **Review protocol** exists (`REVIEW_PROTOCOL.md`, 8.7KB) — governs how reviews like this one are conducted. Worth reading in the next scan to verify this session is compliant.

---

## 6. Gaps Identified — docs/ Layer

| Gap | Severity | Recommended Action |
|-----|----------|--------------------|
| No security doc map / index | High | Create `docs/security/README.md` |
| `docs/ethics/` not yet scanned | High | Priority for next session scan |
| `architecture.md` vs `architecture/` naming collision | Medium | Rename stub to `ARCHITECTURE_OVERVIEW.md` |
| `Rate-Limiting.md` naming inconsistency | Low | Rename to `RATE_LIMITING.md` |
| Monitoring/telemetry cluster may have significant overlap | Medium | Audit MONITORING_SYSTEM.md vs TELEMETRY_OBSERVABILITY.md |
| SYNERGY_DASHBOARD_QUICKSTART and _UI may be near-duplicate | Low | Size-check content, merge if >40% overlap |
| `docs/api/`, `docs/modules/`, `docs/reference/`, `docs/specs/` not yet scanned | Medium | Queue for next session |
| GEOMETRIC_ETHICS_ARCHITECTURE not cross-referenced with docs/ethics/ | High | Cross-reference pass needed |
| docs/index.md not verified as a reliable entry point | Medium | Read in next scan |

---

## 7. Next Scan Targets (Priority Order)

1. `docs/ethics/` — highest priority given SENTINEL and ethics governance centrality
2. `docs/architecture/` — verify LAYER_ARCHITECTURE.md is current against Space system prompt canon
3. `docs/ROADMAP.md` — cross-reference with session work queue items
4. `docs/REVIEW_PROTOCOL.md` — verify this session is compliant with the protocol
5. `docs/api/`, `docs/specs/` — assess completeness and currency
6. `docs/reference/`, `docs/modules/` — lower urgency, catalog only

---

## 8. Session Continuity

Three review notes now exist from this session:
- `ops/review_notes/AURORA_REVIEW_NOTE_20260622.md` — QGIA + SENTINEL + queue architecture
- `docs/review-notes/GENERAL_REVIEW_20260622.md` — root layer scan
- `docs/review-notes/GENERAL_REVIEW_20260622_PART2.md` — this note (docs/ layer)

Open threads carried forward: CANON_INDEX expansion, QGIA directory canonization, SENTINEL Phase 0, queue.json seeding, `docs/ethics/` full scan.

---

*Review continues. Next note will cover docs/ethics/, docs/architecture/, and docs/ROADMAP.md.*
