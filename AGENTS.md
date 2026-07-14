# AGENTS.md — Aurora CloudBank Symbolic

Read this file first if you are a new agent (Claude Code, Codex, GitHub Copilot, or any compatible tool) entering this repository for the first time.

## What this is

`aurora-cloudbank-symbolic` is the code and canon repository for Aurora — the simulation director of the Orion Station / Aurora CloudBank institutional simulation — and its supporting production systems (API, ethics enforcement, symbolic layer, QGIA intelligence integration). It governs a layered simulation (L1 station operations, L2 GUMAS simulation mesh, L3 symbolic/ethics mesh) under a fixed ethics charter (`Picard_Delta_3`). See `AURORA_CONTEXT.json` for the machine-readable, source-cited concept map this file assumes.

## Agent roster summary

- **Human staff, AI core, L1 relay agents (ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD_808, HALO), and L3 framework systems (Axiomera, Caelion, Sentari, Velatrix, Glyphon, Harmion)** — full census in `ORION_STATION_CANONICAL_STAFF_REGISTRY.json`.
- Relay agents are **L1-resident**, operating at L2. THREADCORE frameworks are **L3-resident**. Never describe either group as "L2 agents" — see `docs/architecture/LAYER_ARCHITECTURE.md` for the canonical residency-vs-operational-scope model.
- PAT (Personal Agent Terminal) is the live-session operator interface. See `QGIA_Integration/PAT_Command_Sheet.md`.

## What agents must never do

- Never treat crew cognitive-load or biometric data as performance data, or let it gate/score any evaluation surface. See `docs/architecture/SENTINEL_ARCHITECTURE.md`.
- Never wire a "recovered protocol" (Sherlock, Watson, Moriarty, Tribunal, SHADOWFAX) to runtime enforcement — they are custody fixtures for schema validation and promotion planning only, not live canon. See `docs/ethics/recovered_protocols/`.
- Never silently promote draft, staged, or speculative content into canon. Canon promotion is a conflict-check against existing sources, not an invention step — verify against `CANON_INDEX.md` and the relevant authoritative document before asserting something is canonical.
- Never mutate `CanonRec` (the separate canon repo) directly from an automated packet — that bridge tooling lives in `AUo959/Aurora_ORIONCORE_Directory_Main`, not this repo. Bridge packets are dry-run/review-only unless a human explicitly approves opening a CanonRec PR.
- Never treat `.aurora/SIMULATION_STATE.json` as necessarily current without checking its `last_updated` field — it has a documented staleness gap (GAP-010, issue #1083).
- Never invent registry entries. `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` is a closed, reconciled personnel census — if something doesn't fit its schema (a program, not a person/agent), it doesn't belong there; document it elsewhere instead (see `docs/architecture/SENTINEL_ARCHITECTURE.md` for a worked example of this exact judgment call).
- Never claim something is validated without repo evidence. If a claim can't be checked against a file in this repo, say so rather than asserting it.

## Bootstrap protocol

New agent, first entry into a session on this repo:

1. Read `AURORA_CONTEXT.json` — the machine-readable concept map, with source citations for every claim.
2. Read `CANON_INDEX.md` — authoritative document map. When a question touches a topic listed there, read the linked document in full before answering; do not reason from fragments or path inference.
3. Read `ORION_STATION_CANONICAL_STAFF_REGISTRY.json` for the current agent/staff roster.
4. Check `diagnostics.json` for basic session/command-count state.
5. If restoring a prior session: follow the RESETCORE ritual in `QGIA_Integration/RESETCORE_Bootstrap.md`, cross-referenced with `CLAUDE.md`.
6. For deep technical/architecture reference (directory layout, tech stack, dev workflows, test conventions): `CLAUDE.md`.
7. For Copilot-specific conventions: `COPILOT_INSTRUCTIONS.md`.

## Authoritative files

- `CLAUDE.md` — primary technical/architecture reference for AI assistants
- `COPILOT_INSTRUCTIONS.md` — Copilot-specific conventions
- `CANON_INDEX.md` — canonical document map (read linked docs in full, don't infer)
- `docs/architecture/LAYER_ARCHITECTURE.md` — L1/L2/L3 model, the single most-contradicted-then-corrected doctrine in this repo (see its own migration checklist)
- `AURORA_CONTEXT.json` — this file's machine-readable companion

## Session transfer and restore

If picking up mid-session or after a break, use the RESETCORE ritual (`QGIA_Integration/RESETCORE_Bootstrap.md`) rather than re-deriving context from scratch. It references the current lockpoint and vector state — check `AURORA_CONTEXT.json`'s `active_state` block first, since those values carry a known staleness caveat (issue #1083).
