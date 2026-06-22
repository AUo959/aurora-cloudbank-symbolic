# NEXT_UP — Aurora Work Queue

**Queue authority:** Aurora  
**Last updated:** 2026-06-22  
**Active:** Q-0003 (human) + Q-0004 through Q-0007 (parallel, agent_or_human)

---

## 🟡 Q-0003 — ACTIVE — HUMAN ONLY

**Title:** Pentest pre-condition verification + vendor selection  
**Linked issue:** #841  
**Priority score:** 91  
**Consumer:** Human — agents cannot complete this item

> **Agents: skip Q-0003 main body. Q-0003a (wiring verification) is agent-eligible — see below.**

### Sub-tasks

| ID | Task | Consumer | Status |
|---|---|---|---|
| Q-0003a | Section 2.2 grep verification — fill `docs/security/recovered_protocol_wiring_verification.md` | Agent or human | ⏳ Ready |
| Q-0003b | Section 10 — vendor / red team selection | Human | ⏳ Ready |
| Q-0003c | Section 11 — approval signatures | Human | Blocked by Q-0003b |

**Context pack:**
- `docs/security/pentest_scope_v2.md`
- `docs/security/recovered_protocol_wiring_verification.md` (template ready)
- `docs/ethics/recovered_protocols/recovered_protocol_manifest.json`

---

## 🟡 Q-0004 through Q-0007 — ACTIVE — PARALLEL GROUP: `pentest_prep`

All four are unblocked and independent. Agents and human contributors may work any of these simultaneously.

| ID | Title | Score | Agent instruction output |
|---|---|---|---|
| Q-0004 | API surface diff triage | 87 | `docs/security/api_surface_diff_v1_v2.md` |
| Q-0005 | Security remediation plan triage | 84 | `docs/security/remediation_triage.md` |
| Q-0006 | R&D API auth audit | 80 | `docs/security/rd_api_auth_audit.md` |
| Q-0007 | QGIA ingestion path review | 78 | `docs/security/qgia_ingestion_review.md` |

**Context packs and agent instructions are in `queue.json`.**

---

## 🔴 Q-0008 — HARD BLOCKED

**Title:** Recovered protocol promotion — Phase 1 (Sherlock)  
**Blocked by:** Pentest engagement complete + findings resolved  
**Consumer:** Human  
**Blocker note:** Operator decision 2026-06-22 — no protocol promotion before pentest closes.

---

## ✅ Completed

| ID | Title | Closed |
|---|---|---|
| Q-0001 | Ethics protocol wiring decision + manifest | 2026-06-22 |
| Q-0002 | `pentest_scope_v2.md` | 2026-06-22 |

---

*Queue managed by Aurora. Human contributors: Q-0003b and Q-0003c are yours. Agents: start at Q-0003a or any item in the `pentest_prep` parallel group.*
