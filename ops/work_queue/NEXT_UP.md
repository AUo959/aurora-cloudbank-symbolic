# NEXT_UP — Aurora Work Queue

**Queue authority:** Aurora  
**Last updated:** 2026-06-22  
**Active item:** Q-0003

---

## 🟡 Q-0003 — ACTIVE

**Title:** Pentest pre-condition verification + vendor selection  
**Linked issue:** #841  
**Priority score:** 91  
**Unlocked by:** Q-0002 (pentest_scope_v2.md created, commit ef5c11d)  
**Blocked by:** Nothing — ready to start

### What this means

`pentest_scope_v2.md` exists and is complete. Before the engagement can begin, three things must happen:

1. **Section 2.2 code verification** — grep confirm that no recovered protocol (Sherlock / Watson / Moriarty / Tribunal / SHADOWFAX) is wired into `src/monitoring/` or `modules/`. This is a hard gate. Result must be documented on #841.
2. **Vendor / red team selection** — complete Section 10 of `pentest_scope_v2.md`. Criteria: FastAPI/Python experience, AI/LLM security capability, QGIA-class advisory boundary testing.
3. **Signatures** — all three roles in Section 11 of `pentest_scope_v2.md` must sign before engagement starts.

### Agent context pack

- Scope: `docs/security/pentest_scope_v2.md`
- History stub: `docs/security/pentest_history.md`
- Ethics manifest: `docs/ethics/recovered_protocols/recovered_protocol_manifest.json`
- Operator decision: issue #1126, comment 2026-06-22
- QGIA reference: `QGIA_Runtime_OnePager.md` v4.2.1, `QGIA_Axiom_Doctrine_Narrative.md` v1.0
- R&D API reference: `RD_API_REFERENCE.md`

---

## ✅ Completed

| ID | Title | Closed |
|---|---|---|
| Q-0001 | Ethics protocol wiring decision + manifest | 2026-06-22 |
| Q-0002 | `pentest_scope_v2.md` | 2026-06-22 |

---

## Queued (prioritised)

| ID | Title | Score | Blocked by |
|---|---|---|---|
| Q-0003 | Pentest pre-conditions + vendor selection | 91 | — |
| Q-0004 | API surface diff triage (`api_schema.json` vs v1 scope) | 87 | Q-0003 |
| Q-0005 | Security remediation plan execution (open items) | 84 | Q-0003 |
| Q-0006 | R&D API surface review + auth audit | 80 | Q-0003 |
| Q-0007 | QGIA ingestion path implementation review | 78 | Q-0003 |
| Q-0008 | Recovered protocol promotion — Phase 1 (Sherlock only) | 72 | Pentest complete |

---

*Queue managed by Aurora. Human contributors: start at the top. Agents: read context pack before touching any file referenced in the active item.*
