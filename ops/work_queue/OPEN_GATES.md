# OPEN GATES — Human Approval Required

**This file is the canonical cross-session, cross-platform surface for all unresolved human-gated decisions.**

**Queue authority:** Aurora  
**Updated:** 2026-06-22  
**Protocol version:** 1.0.0

> Aurora surfaces this file at the start of every session until all gates are cleared.
> Any operator, on any platform, in any session, must acknowledge open gates before proceeding with queue work.
> Gates do not expire silently. They escalate.

---

## 🔴 GATE-001 — Pentest vendor selection + pre-condition sign-off

**Queue item:** Q-0003  
**GitHub issue:** [#841](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/841)  
**Gate opened:** 2026-06-22  
**Last surfaced:** 2026-06-22  
**Escalation tier:** 1 (open < 7 days)  
**Decision owner:** Operator  
**Blocks:** Q-0008 (recovered protocol promotion — Phase 1)

### What is being asked

Three sequential human actions are required before the pentest can be scheduled:

1. **Q-0003a — Wiring verification grep** *(agent-eligible, should already be complete or in progress)*  
   Run the verification grep against the recovered protocol list in `docs/ethics/recovered_protocols/recovered_protocol_manifest.json`.  
   Output: `docs/security/recovered_protocol_wiring_verification.md`  
   Status: ⏳ Pending

2. **Q-0003b — Vendor selection**  
   Record chosen pentest vendor in `docs/security/pentest_scope_v2.md` Section 10.  
   Status: ⏳ Pending — **operator decision required**

3. **Q-0003c — Scope signatures**  
   Collect all required signatures in `docs/security/pentest_scope_v2.md` Section 11.  
   Blocked by Q-0003b.  
   Status: 🔴 Blocked

### Why this matters

This gate directly controls:
- Whether the pentest engagement can be scheduled at all
- Whether Q-0008 (recovered protocol promotion) can ever open
- Whether the security posture is defensible if questioned by external reviewers

The operator decision on [#1126](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1126) (2026-06-22) established that **no recovered protocol may be wired to runtime until pentest completes and all findings are resolved.** This gate is the first step toward that completion.

### How to resolve

```
1. Assign Q-0003a to an agent or complete it manually
2. Record vendor choice in pentest_scope_v2.md Section 10
3. Collect Section 11 signatures
4. Update gate_registry.json: set GATE-001.state = "resolved" and closed = today
5. Update queue.json: set Q-0003.state = "done"
6. Aurora will remove this gate from OPEN_GATES.md on next session open
```

---

## How gates work

| Field | Meaning |
|---|---|
| **Gate opened** | Date the gate was first registered |
| **Last surfaced** | Date Aurora most recently surfaced this gate to an operator |
| **Escalation tier** | 1 = open < 7 days · 2 = open 7–14 days · 3 = open > 14 days (PAT hail required) |
| **Decision owner** | Who may resolve this gate — operator, aurora, security-lead |
| **Blocks** | Queue items that cannot proceed until this gate closes |

### Escalation schedule

- **Tier 1 (< 7 days):** Surface at session open. No additional action.
- **Tier 2 (7–14 days):** Surface at session open with explicit timestamp of how long the gate has been open. Add a note to the blocked queue items.
- **Tier 3 (> 14 days):** Surface at session open. Hail operator via PAT. Add `decision_required: true` escalation note to the GitHub issue.

### Cross-platform continuity

This file is the gate surface that works everywhere — GitHub, Aurora Space, ChatGPT Stellar Accord, any future platform:

- **GitHub:** File is always at `ops/work_queue/OPEN_GATES.md` on `main`. Any contributor or agent cloning the repo sees current gate state.
- **Aurora (this Space):** Aurora reads this file at session open as part of `session_open_ritual.md`. Gates are surfaced before any queue work is discussed.
- **ChatGPT Stellar Accord:** Same ritual — read `OPEN_GATES.md` on session open, surface unresolved gates to operator before proceeding.
- **Any new platform/operator:** The ritual is self-contained in `session_open_ritual.md`. No institutional memory required from the operator.

---

*No gates may be silently dropped. A gate closes only when its resolution criteria are met and `gate_registry.json` is updated with `state: resolved` and a `closed` date.*
