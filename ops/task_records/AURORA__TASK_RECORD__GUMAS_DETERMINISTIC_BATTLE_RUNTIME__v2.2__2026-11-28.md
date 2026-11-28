# Aurora Durable Task Execution Record

**Task ID:** `TASK-20260812-gumas-deterministic-battle-runtime`
**Version:** `v2.2`
**Supersedes:** `ops/task_records/AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v2.1__2026-08-15.md`
**Created:** `2026-11-28`
**Status:** `active`
**Owner / active worker:** `Aurora / Claude Code`
**Repository:** `AUo959/aurora-cloudbank-symbolic`
**Branch:** `claude/project-thread-t3tl0t` (continues `agent/gumas-flash-rebellion-battle-baseline`)
**PR:** `#1506` lineage
**Current phase:** `Phase 11: authority granted; Run 0 and controls executed on the engaging engine`
**Owner direction (2026-11-28):** Asked whether to finish or park #1506, the owner answered "finish it, obviously" and "our goal is to get everything functional." That is direction to finish the work. It is not yet the explicit, committed Phase-11 execution authority record that §5 of the Phase-11 contract requires. That record is requested from the owner separately.

---

## 1. What changed since v2.1

1. **Main integrated.** The branch now merges current `main`, including the GUMAS Unified P0–P6 stack (#1735), the P0 validator split (#1730), and the cargo-arrival fix (#1736). The merge was clean. The accepted Phase-9 one-step ledger entry `e5fbf153…` and the Phase-10 public normalized report `a2de14d9…` still reproduced byte for byte on the merged tree, before the source changes below.
2. **Phase-9 defect fixed: no run could pass macrostep 1.** The prior-checkpoint validator compared the state's retained Phase-6 identity (semantic-normalized, the identity Phase 7 consumes) against the raw receipt hash. Every real run failed at macrostep 2. Fixed and covered by regression tests. See Phase-11 spec §2.1.
3. **Phase-4 gap closed: polity input reached no engine variable.** The CanonRec authority doctrine vector is now bound into the run identity and conditions commander attributes through a fixed coefficient table. See Phase-11 spec §2.2.
4. **Phase-11 harness implemented.** The `simulation/runtime/gumas_battle_controls/` package covers authority preflight, variant derivation with a machine-checked allowed-delta matrix, a run driver, Phase-10 export, Control A/B/C comparison, and sealed evidence with byte-identical regeneration.
   - Normative contract: `simulation/specs/GUMAS__SPEC__DETERMINISM_SUBSTITUTION_CONTROLS_RUN0__v1.0__2026-11-28.md`
   - Tests: `tests/test_gumas_battle_controls.py`
   - Workflow: `.github/workflows/gumas-battle-controls.yml`

5. **Owner authority granted 2026-11-28** (decision card). The authority record is committed. The first full execution passed Controls A/B/C, but every run was a non-engagement with zero weapon attempts.
6. **Phase-5/9 gap fixed: no navigation intent closed range.** `POSITION_FOR_ADVANTAGE` now steers to a weapon-range standoff against the side-local contact track. `EVASIVE_VECTOR` without a contact falls back to the tangent instead of aborting. See Phase-11 spec §2.3 and the movement-spec amendment.
7. **Phase-2 role fix folded in** (from #1740): resolver 1.1.0, derivation v1.2, control manifest `9e4a1844…`, T0 `05634f70…`.
8. The evidence was re-generated on the fixed engine. Two workers are used because four parallel full runs exceed 16 GB.

Accepted source identities for Phases 2, 4, 5, 9 and 10 change because their sources changed. Historical Phase 1–10 receipts remain unchanged as records of what was accepted on their heads.

## 2. Phase status

- **Phases 0–10:** PASS (Phase 4, Phase 9 and the Phase-10 validator amended as above).
- **Phase 11 harness, preflight, and contract tests:** IMPLEMENTED. Synthetic and pinned-CanonRec input-resolution tests pass. No full battle has been committed.
- **Control A/B/C execution and Run 0:** EXECUTED. The evidence is committed and CI regenerates it byte for byte.

## 3. Exact next action

1. Once the owner grants authority, commit `simulation/authority/GUMAS__EXECUTION_AUTHORITY__RUN0_AND_CONTROLS__v1.0__2026-11-28.json`, citing the owner's decision.
2. Run `python simulation/runtime/gumas_battle_controls/controls_cli.py execute --canonrec-root <pinned checkout> --authority <record> --as-of <date> --out simulation/runs/gumas/GUMAS__EVIDENCE__RUN0_AND_CONTROLS__v1.0__2026-11-28.json`.
3. Commit the evidence. The `GUMAS Battle Controls` workflow must regenerate it byte for byte.

## 4. Follow-ups recorded, not done here

- SonarCloud and Codacy advisory statuses carried over from v2.1.

**Outputs remain non-canon. No battle result is claimed in this record.**
