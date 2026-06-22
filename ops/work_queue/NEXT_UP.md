# NEXT_UP — Aurora Work Queue

**Queue authority:** Aurora  
**Schema version:** 1.1.0  
**Last updated:** 2026-06-22  
**Active:** Q-0003 (human-gated) + parallel group `pentest_prep` (Q-0004–Q-0007)

---

## 🟡 Q-0003 — ACTIVE — HUMAN GATE

**Title:** Pentest pre-condition verification + vendor selection  
**Issue:** [#841](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/841)  
**Priority:** CRITICAL (91) · `decision_required` · `consumer_fit: [aurora, human]`

**Agents: skip Q-0003 main body. Q-0003a (wiring verification) is agent-eligible.**

| Sub-task | Consumer | Status | Output |
|---|---|---|---|
| Q-0003a — Section 2.2 grep verification | Agent or human | ⏳ Ready | `docs/security/recovered_protocol_wiring_verification.md` |
| Q-0003b — Section 10 vendor selection | Human | ⏳ Ready | `docs/security/pentest_scope_v2.md` Section 10 |
| Q-0003c — Section 11 signatures | Human | Blocked by Q-0003b | `docs/security/pentest_scope_v2.md` Section 11 |

---

## 🟡 PARALLEL GROUP — `pentest_prep` — ALL READY

All four items are independent. Agents and contributors may work any simultaneously.

| ID | Title | Priority | Output |
|---|---|---|---|
| Q-0004 | API surface diff triage | CRITICAL (87) | `docs/security/api_surface_diff_v1_v2.md` |
| Q-0005 | Security remediation plan triage | CRITICAL (84) | `docs/security/remediation_triage.md` |
| Q-0006 | R&D API surface review + auth audit | CRITICAL (80) | `docs/security/rd_api_auth_audit.md` |
| Q-0007 | QGIA ingestion path implementation review | HIGH (78) | `docs/security/qgia_ingestion_review.md` |

**Context packs and `aurora_notes` for each item are in `queue.json`.**

---

## 🔴 HARD BLOCKED

| ID | Title | Blocked by | Hard gate |
|---|---|---|---|
| Q-0008 | Recovered protocol promotion — Phase 1 (Sherlock) | Q-0003 (pentest) | Operator decision 2026-06-22, issue #1126 |

---

## ✅ Completed

| ID | Title | Closed |
|---|---|---|
| Q-0001 | Ethics protocol wiring decision + manifest | 2026-06-22 |
| Q-0002 | `pentest_scope_v2.md` | 2026-06-22 |

---

*Agents: start from `queue.json`, read `context_pack` first, honour `consumer_fit`.  
Humans: start here, then follow links in the relevant item's `context_pack`.*
