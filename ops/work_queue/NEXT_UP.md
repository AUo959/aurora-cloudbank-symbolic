# NEXT_UP — Aurora Work Queue

*Source: `ops/work_queue/queue.json` v1.0.1*  
*Last updated: 2026-06-22 — operator decision on #1126 recorded*

---

## ✅ Just completed

| Queue ID | Issue | Decision |
|---|---|---|
| Q-0001 | [#1126](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1126) | Live manifest created. Runtime wiring sequenced AFTER pentest. All protocols remain `recovered_candidate`. SHADOWFAX + Moriarty carry hard blocks. |

---

## 🔴 Active top of queue — CRITICAL

| Queue ID | Issue | Task | Consumer |
|---|---|---|---|
| **Q-0002** | [#1130](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1130) | Produce `pentest_scope_v2.md` — API surface diff, QGIA ingestion, R&D surface, ethics pre-conditions | aurora / human / agent |

**Q-0002 is now unblocked. This is the active priority.**

Key surfaces to assess for v2 scope:
- `api_schema.json` (368 KB) diff against scope v1 Section 3
- `api_surface_inventory.json` (15 KB) — not in v1 scope at all
- `RD_API_REFERENCE.md` — R&D surface undefined
- QGIA ingestion surface (`QGIA_Runtime_OnePager.md` + `QGIA_Axiom_Doctrine_Narrative.md`)
- Ethics pre-conditions — reference `recovered_protocol_manifest.json` `wiring_gate` block

---

## 🟠 Ready — HIGH (agent-safe with context pack)

| Queue ID | Issue | Task |
|---|---|---|
| Q-0004 | [#1127](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1127) | Architecture layer terminology corrections |
| Q-0005 | [#1124](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1124) | QGIA_SIM_BRIDGE canonicalization |

---

## 🔒 Blocked — waiting on Q-0002

| Queue ID | Issue | Waiting on |
|---|---|---|
| Q-0003 | [#1129](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1129) | Q-0002 (pentest scope v2) |

---

## 🟡 Ready — MEDIUM (agent-safe)

| Queue ID | Issue | Task |
|---|---|---|
| Q-0006 | [#1128](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1128) | API reference authority clarification |

---

*If you are an LLM or agent: read the `context_pack` for your chosen task in `queue.json` before starting. Do not start blocked tasks.*
