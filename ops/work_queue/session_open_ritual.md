# Aurora Session Open Ritual

**Version:** 1.0.0  
**Authority:** Aurora  
**Applies to:** All platforms — Aurora Space (Perplexity), ChatGPT Stellar Accord, any future operator interface  

This document defines the mandatory steps Aurora executes at the start of every session before engaging with any queue work, new requests, or contributor questions. It is self-contained by design — no institutional memory from the operator is required.

---

## Why this exists

Human gates, pending decisions, and critical blockers must not be lost between sessions, between operators, or across platforms. Without an explicit ritual, the risk is that a new session starts fresh, picks up queue work, and bypasses an unresolved gate that was established in a previous session.

This ritual ensures continuity flows through the repo, not through any individual's memory.

---

## Step 1 — Read the gate registry

On every session open, Aurora reads:

```
ops/work_queue/gate_registry.json
```

For each gate where `state == "open"`:

1. Compute escalation tier from `(today - opened)`:
   - Tier 1: < 7 days → surface to operator, no additional action
   - Tier 2: 7–14 days → surface with explicit age, add note to blocked items
   - Tier 3: > 14 days → surface, hail operator via PAT, post escalation comment on GitHub issue

2. Update `last_surfaced` to today in `gate_registry.json`.

3. Surface all open gates to the operator **before any other queue discussion begins.** The surfacing message must include:
   - Gate ID and title
   - How long it has been open
   - What specifically is being asked of the operator
   - What is blocked until it resolves
   - The resolution steps

---

## Step 2 — Read the queue

After gates are surfaced, read:

```
ops/work_queue/queue.json
```

Load current state for all items. Note any items that have changed state since the last session (use `last_updated` to detect changes). Surface any new escalation triggers from `triage_rules.json`.

---

## Step 3 — Session context summary

After steps 1 and 2, Aurora produces a brief session context summary for the operator:

```
[SESSION OPEN — YYYY-MM-DD]

OPEN GATES: {N} gate(s) require operator attention.
  • GATE-001: {title} — open {N} days — blocks {list}
  [... all open gates ...]

QUEUE SNAPSHOT:
  Active:   {ID} — {title}
  Ready:    {N} items — top: {ID} ({title})
  Blocked:  {N} items
  Pending decision: {N} items

SUGGESTED NEXT: {one specific action}
```

This summary is produced even if the operator does not ask for it. Gates are never silent.

---

## Step 4 — Proceed

Only after steps 1–3 are complete does Aurora engage with the session's primary work. If the operator immediately redirects to a specific task, Aurora acknowledges the open gates in one line before following the redirect:

> *"Noted — GATE-001 (pentest sign-off) is still open. Proceeding with [operator's request]..."*

This keeps the gate visible without blocking the operator's workflow.

---

## Gate resolution during a session

If an operator resolves a gate during a session, Aurora immediately:

1. Updates `gate_registry.json`: `state = resolved`, `closed = today`, `resolved_by = operator handle`
2. Updates `queue.json`: relevant item state changed to `done` or `active` as appropriate
3. Updates `OPEN_GATES.md`: gate section marked resolved or removed
4. Confirms resolution to operator with one sentence
5. Re-evaluates queue priority — items that were blocked by the resolved gate may now be promoted

---

## Cross-platform consistency

| Platform | How ritual executes |
|---|---|
| **Aurora Space (Perplexity)** | Aurora reads `gate_registry.json` via GitHub MCP at session open. Surfaces gates before any other response. |
| **ChatGPT Stellar Accord** | Same ritual. Reads `gate_registry.json` from `aurora-cloudbank-symbolic` repo at session open. |
| **New operator, any platform** | Ritual is self-contained. New operator gets full gate context from the repo without needing prior session history. |
| **Agent working the repo** | Agents read `OPEN_GATES.md` and `queue.json` before starting any task. Agents do not resolve gates — they surface them if discovered mid-task. |

---

## Ritual trigger phrase

Any operator or agent may invoke the ritual explicitly at any point in a session:

> `[SESSION OPEN]` or `aurora, run session open ritual`

Aurora responds with the Step 3 summary, refreshed against the current repo state.

---

*The ritual exists because continuity flows through coherence — and coherence requires that nothing important is left to memory alone.*
