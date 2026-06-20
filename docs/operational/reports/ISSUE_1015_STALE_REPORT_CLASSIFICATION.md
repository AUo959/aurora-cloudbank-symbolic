# Issue 1015 - Stale Report Classification And Recovery Clues

Status: issue triage report. This file classifies historical implementation
claims against current `main`; it does not promote historical reports into
implementation truth.

Source issue: [AUo959/aurora-cloudbank-symbolic#1015](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1015)
Worktree base: `origin/main` at `3494e5ac` (`deps: bump esbuild (#1017)`)
Created by: Codex
Created date: 2026-06-13

## Summary

The first pass focused on the HR cluster requested by issue #1015, then checked
the extra Opal2, memory retrieval, vector generation, and instance bridge clues
from issue comments. The second pass classified the remaining stale reports
listed in the issue body.

Key results:

- HR historical reports are useful lead material, but they mix current code,
  stale deployment state, and proposed phases.
- `modules/hr/` is current code evidence for HR Helios v3.0 and quantum HR
  enhancement.
- `modules/hr_system/` is current code evidence for staffing analysis,
  character generation, and a mounted `/hr_system` router.
- Issue #761 can be narrowed: `StaffingAnalyzer` and `CharacterGenerator` now
  exist, while `OrganizationalIntelligence` is still missing and
  `/hr_system/organizational_intel` currently degrades to mock data.
- The Opal2 plugin clue is current evidence: `modules/opal2/plugin_system.py`
  defines `PluginSystem` multiple times, so the later simplified class likely
  shadows the fuller plugin system.
- `memory_retrieval`, `vector_gen`, and `instance_bridge` all exist in current
  `main`; only their wiring and test coverage differ.
- Subroutine, thread transfer, cross-repo collaboration, command-chain, code
  quality, resilience sentinel, insight ledger, HALO/PAS continuity, and
  flight-control claims mostly resolve to current surfaces.
- Several older reports overstate production readiness or cite stale route
  names. Treat them as lead material, not validation truth.

## Classification Legend

| Classification | Meaning |
| --- | --- |
| Current Canon Evidence | Verified against committed current files. |
| Historical State | Useful statement about a past branch, PR, or snapshot; not current proof. |
| Recovered / Renamed | Current implementation exists under a different path/name. |
| Unverified Lead | Search clue requiring deeper runtime or history verification. |
| Contradicted / Stale | Current evidence conflicts with the historical claim. |
| Proposed Design | Described intent or future phase, not implemented evidence. |
| Existing Issue / Do Not Duplicate | Already tracked by a live issue or PR. |

## HR Cluster

| Source document | Main claims | Current evidence | Classification | Follow-up |
| --- | --- | --- | --- | --- |
| `.aurora/HR_SYSTEM_VALIDATION.md` | `modules/hr_system/` has `CharacterGenerator`; generated HR candidate artifacts; API integration opportunities remain. | `modules/hr_system/core/character_generator.py` exists. `api/aurora_api.py` now includes `modules.hr_system.api.hr_routes`; the document's future integration language is stale. | Mixed: Current Canon Evidence + Historical State. | Keep as lead material; current route topology should use `api/aurora_api.py` and `docs/architecture/RUNTIME_PATH_DRIFT_LEDGER.md`. |
| `.aurora/HR_SYSTEM_IMPLEMENTATION_SUMMARY.md` | `CharacterGenerator` complete; `staffing_analyzer.py`, `organizational_intelligence.py`, and API routes listed as future phases. | `CharacterGenerator`, `StaffingAnalyzer`, and `hr_routes.py` now exist. `organizational_intelligence.py` is still absent. | Recovered / Renamed for staffing/API; Proposed Design for organizational intelligence. | Narrow #761 to missing organizational intelligence and explicit mock/degraded behavior. |
| `modules/hr/DEPLOYMENT_SUMMARY.md` | HR Helios v3.0 deployed to branch `feature/hr-module-v3-helios-T20251111`, PR #337, with core module, docs, config, and tests. | `modules/hr/aurora_hr_module_advanced_v3.py`, `modules/hr/quantum_hr_enhancement.py`, `modules/hr/__init__.py`, docs, and `tests/hr/test_hr_module.py` exist on current main. | Current Canon Evidence for files; Historical State for branch/PR workflow status. | Do not rely on the old PR status. Validate current code with tests. |
| `modules/hr/CODE_REVIEW_COMPLETE.md` | AI review approved HR module and quantum enhancement; 8 tests passing; minor lint warnings. | Current test file still has 8 tests; module exports `AuroraHRModule` and optional quantum exports. Review claims are historical. | Historical State with current supporting evidence. | Use current CI/test runs, not the review document, as validation truth. |
| `modules/hr/QUANTUM_INTEGRATION_COMPLETE.md` | Quantum HR enhancement with L1 character profiles, VSA encoding, team dynamics, and `QuantumHRIntegration`. | `modules/hr/quantum_hr_enhancement.py` defines `QuantumCharacterDatabase` and `QuantumHRIntegration`; `modules/hr/__init__.py` conditionally exports quantum classes. | Current Canon Evidence for code presence; Historical State for performance/production claims. | If behavior matters, add focused tests around quantum HR integration rather than relying on summary metrics. |

## Issue #761 Mapping

Issue #761 originally names three HR concerns:

| Concern | Current evidence | Classification | Recommended action |
| --- | --- | --- | --- |
| `StaffingAnalyzer` import fallback | `modules/hr_system/core/staffing_analyzer.py` defines `StaffingAnalyzer`; `hr_routes.py` imports it for `/hr_system/analyze_staffing`. | Current Canon Evidence. | Do not keep treating this as missing. Add route-level behavior coverage if needed. |
| `CharacterGenerator` import fallback | `modules/hr_system/core/character_generator.py` defines `CharacterGenerator`, but route code calls `generate_profile(...)` while the class defines `generate_character(...)`. | Current code exists, but route behavior needs verification. | Add a targeted test for `POST /hr_system/generate_character`; fix method mismatch if reproduced. |
| `OrganizationalIntelligence` missing | No `modules/hr_system/core/organizational_intelligence.py` exists. `hr_routes.py` imports it and returns mock data on `ImportError`. | Missing Current Surface / Existing Issue. | Implement or explicitly gate `/hr_system/organizational_intel` as degraded. This is the remaining hard #761 gap. |

## Runtime And API Evidence

| Claim | Current evidence | Classification | Follow-up |
| --- | --- | --- | --- |
| `/hr_system` API is not integrated | `api/aurora_api.py` imports `modules.hr_system.api.hr_routes` and calls `app.include_router(hr_system_router)`. | Contradicted / Stale. | Use `api/aurora_api.py` and API inventory docs as current authority. |
| HR split is duplicate/conflicting | `docs/architecture/RUNTIME_PATH_DRIFT_LEDGER.md` records `modules/hr/rd_api.py` and `modules/hr_system/api/hr_routes.py` as a canonical split: `/rd` and `/hr_system`. | Current Canon Evidence. | Keep both. Do not collapse `hr/` and `hr_system/` based on old reports. |
| API catalog is current truth | `docs/api/API_CATALOG.json` and `docs/api/api_schema.json` are generated snapshots; drift ledger warns snapshots may lag current routers. | Historical/generated snapshot. | Regenerate in a separate issue when route schema detail matters. |

## Additional Clues From Issue Comments

| Reference | Current target found? | Evidence | Classification | Follow-up |
| --- | --- | --- | --- | --- |
| Opal2 `PluginSystem` duplicate definitions | Yes. | `modules/opal2/plugin_system.py` defines a full `PluginSystem` near the top and simplified `PluginSystem` definitions later in the same file. | Current Canon Evidence / likely merge artifact. | Open or claim a focused cleanup issue/PR. Add import/behavior tests proving which class loads and preserving built-in plugin behavior. |
| `memory_retrieval` | Yes. | `modules/memory_retrieval/` contains API, core, config, store, and cache. Tests exist: `tests/test_memory_retrieval_full.py`, `tests/test_memory_retrieval_api.py`, and `tests/test_memory_retrieval_cap.py`. | Current Canon Evidence. | Do not open a missing-module issue. If needed, verify router mount behavior separately. |
| `vector_gen` | Yes. | `modules/vector_gen/vector_gen_v2.py` and `tests/test_vector_gen_v2.py` exist. Version consolidation docs mark v2 as canonical. | Current Canon Evidence. | No missing-module action needed. |
| `instance_bridge` | Yes. | `modules/instance_bridge/bridge_server.py`, `bridge_client.py`, and `__init__.py` exist. This scoped scan did not find matching tests. | Unverified Lead / current surface with unclear coverage. | Audit runtime role and add tests or deprecate only after impact review. |

## Second Pass Report Classification

The remaining reports from the issue body are now classified against current
`main`:

| Source document | Current evidence | Classification | Follow-up |
| --- | --- | --- | --- |
| `.aurora/STUB_AND_INTEGRATION_AUDIT.md` | Mixed audit. HR missing-core claims are now partly stale because `StaffingAnalyzer` and `CharacterGenerator` exist; `OrganizationalIntelligence` is still absent. Quantum mixed-state `NotImplementedError` claims are stale because `modules/quantum_simulator/quantum_state.py` now supports density matrices, mixed-state measurement, entropy, and fidelity. `src/improvement/engine.py` still has an abstract `ImprovementPattern.detect()`. Flight Control remains JavaScript-first but is documented and tested. Opal2 has `modules/opal2/api/opal2_api.py`, not `api/routes.py`; it is a standalone FastAPI app and is not listed as a main `aurora_api.py` mounted router. HALO/PAS now has `/continuity/halo_pas/status`. Resilience Sentinel is mounted at `/sentinel`. | Mixed: Current Canon Evidence + Contradicted / Stale + Existing Issue. | Use draft PR #1014 as the peer-review surface for audit cleanup. Do not reopen broad "missing module" issues; split only the surviving gaps. |
| `.aurora/SUBROUTINE_INTEGRATION_STATUS.md` | `src/subroutines/api.py` and `src/subroutines/api_enhanced.py` both exist with `/subroutines` routers; `api/aurora_api.py` includes both. Tests exist in `tests/test_subroutines.py`, `tests/test_subroutines_quick.py`, and `tests/test_subroutines_integration.py`. | Current Canon Evidence for files/routes; Historical State for old test counts and production-ready language. | Keep as deployment history. Current validation should run the current tests, not rely on the November status report. |
| `docs/operational/reports/FEATURE_ROADMAP_STATUS.md` | Many listed surfaces exist: thread transfer bridge v1/v2, Data Guardian, AuMemManager, ethics field, quantum simulator, memory retrieval, resilience sentinel, insight ledger, and Opal2. Some route claims are stale: current Quantum Simulator router is `/simulate`, not legacy `/quantum`; Opal2 is a standalone app rather than a main mounted router. | Lead list with mixed current evidence and stale route/status claims. | Use `docs/architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md` and `docs/api/api_surface_inventory.json` for current runtime topology. |
| `docs/SYSTEM_VALIDATION_REPORT_20251021.md` | Historical CI/test snapshot. Current repo has far more tests and different checks; the report's workflow counts, test counts, and syntax-error counts are not current authority. | Historical State. | Do not use for current readiness. Use live PR checks and targeted test runs. |
| `docs/operational/reports/VALIDATION_REPORT.md` | Issue #258 code-quality analyzer files exist: `src/core/code_quality_analyzer.py`, `src/core/code_quality_issue_creator.py`, `.github/workflows/code-quality.yml`, `docs/CODE_QUALITY_SYSTEM.md`, and `tests/test_code_quality_analyzer.py`. | Current Canon Evidence for delivered files; Historical State for merge approval and scan results. | No missing-module issue needed. Re-run `tests/test_code_quality_analyzer.py` when touching this area. |
| `docs/operational/reports/IMPLEMENTATION_SUMMARY.md` | Cross-repo collaboration exists under `src/collab/`; `api/aurora_api.py` includes `src.collab.api_routes`; API inventory lists `/collab`; tests include `tests/test_collab_capsule.py` and `tests/test_collab_workflow_trigger.py`. | Current Canon Evidence for collab surface; Historical State for old phase checklist. | Keep as implementation history. Use current tests before modifying collab behavior. |
| `docs/operational/reports/PR_RESOLUTION_SUCCESS_REPORT.md` | Report cites old PR/branch state and production counts. The mentioned surfaces mostly exist, but PR state must be verified live. Current issue/PR routing should use GitHub, not this report. | Historical State. | Do not use as closure evidence for any current issue. Use it only as a pointer to AuMemManager, security, and Opal2 lineage. |
| `docs/operational/reports/THREAD_TRANSFER_BRIDGE_INTEGRATION_SUCCESS.md` | `modules/reflective_autonomy/thread_transfer/` exists with v1 and v2 artifacts. `api/aurora_api.py` exposes `/api/thread-bridge/status`, `/handshake`, `/validate`, `/companions`, and `/transfer`; API schema/catalog contain these routes. Tests exist for bridge v2 and cross-repo bridge behavior. | Current Canon Evidence for code/routes; Historical State for old "all tests passing" and deployment claims. | Treat v1/v2 as current surfaces, but validate with current tests before behavior changes. |
| `docs/operational/archived/OPAL2_EXPANSION_PROGRESS.md` | `modules/opal2/api/opal2_api.py` exists with `/health`, `/render`, `/generate`, `/plugins`, `/cache/stats`, `/cache/clear`, `/ws`, and `/demo`. Tests cover route registration. Current runtime topology does not list Opal2 as a main `aurora_api.py` mount, and `PluginSystem` duplicate definitions remain a likely shadowing bug. | Current Canon Evidence for standalone Opal2 app; Historical State for PR-readiness language; Current gap for plugin shadowing/main-app exposure. | Open or claim focused Opal2 cleanup: preserve intended plugin behavior, decide whether standalone app should stay separate or be mounted, and add regression tests. |
| `docs/operational/reports/COMMAND_CHAIN_IMPLEMENTATION_SUMMARY.md` | `tools/command_chain/parser.py`, CLI/executor modules, reference docs, and `tools/command_chain/tests/test_parser.py` exist. `tests/test_command_chain_entrypoints.py` covers local commit/sync behaviors. | Current Canon Evidence for parser/tooling; Historical State for old PR-ready status. | Keep command grammar as validation/context unless a separate explicit execution approval path is present. |

## Missing Reference Ledger Seed

Issue #1015 also asks for a missing-reference ledger. This pass identifies the
first seed rows for that future control-plane scan:

| Reference | Referenced from | Current target found? | Classification | Follow-up |
| --- | --- | --- | --- | --- |
| `OrganizationalIntelligence` | HR reports and `modules/hr_system/api/hr_routes.py` | No. | Missing Current Surface / Existing Issue. | Resolve in #761 by implementation or explicit degraded-mode contract. |
| `CharacterGenerator.generate_profile` | `modules/hr_system/api/hr_routes.py` | No; class exposes `generate_character`. | Docs-Runtime / Code-Runtime Mismatch. | Add route-level test, then align method name or route call. |
| Opal2 `api/routes.py` | `.aurora/STUB_AND_INTEGRATION_AUDIT.md` | No; current app is `modules/opal2/api/opal2_api.py`. | Recovered / Renamed. | Stop searching for `routes.py`; decide mount strategy for `opal2_api.py`. |
| Opal2 `PluginSystem` full implementation | Issue #1015 comments and Opal2 reports | Yes, but likely shadowed by duplicate later class definitions. | Current Canon Evidence / likely merge artifact. | Focused cleanup PR with import/behavior regression tests. |
| `/quantum/*` route family | Older roadmap/module docs | No for current topology; current router is `/simulate/*`. | Historical Name / Stale Reference. | Prefer `/simulate` in current docs and generated inventory. |
| `/continuity/halo_pas/status` | Issue #1015 comment and continuity docs | Yes. | Current Canon Evidence. | No missing-route issue needed. Add behavior tests only if changing HALO/PAS. |
| `instance_bridge` tests | Issue #1015 comments and `modules/README.md` | Module exists; no scoped tests found. | Current Surface With Coverage Gap. | Audit runtime owner and add tests or deprecation note. |

## Recommended Follow-ups

1. Keep #1015 open until PR #1019 lands; then close it or convert remaining
   implementation work into focused follow-up issues.
2. Update #761 scope instead of opening a duplicate HR issue:
   - preserve real `StaffingAnalyzer` and `CharacterGenerator` evidence;
   - verify/fix `generate_profile` vs `generate_character`;
   - implement or explicitly gate `OrganizationalIntelligence`.
3. Open or claim a focused Opal2 cleanup after #1015 records the duplicate
   `PluginSystem` evidence and the standalone-vs-mounted API distinction.
4. Treat `memory_retrieval` and `vector_gen` as current modules, not missing
   recovery targets.
5. Treat subroutines, thread transfer, command chain, collab, code-quality,
   resilience sentinel, insight ledger, and HALO/PAS as current surfaces unless
   a fresh test run proves otherwise.
6. Audit `instance_bridge` separately for runtime role and test coverage.

## Verification Performed

Commands run in this worktree:

| Command | Result |
| --- | --- |
| `python3 -m pytest -q tests/test_api_surface_inventory.py` | Passed: 2 tests. |
| `python3 -m pytest -q tests/test_memory_retrieval_api.py tests/test_vector_gen_v2.py` | Passed: 42 tests. |
| `python3 -m pytest -q tests/test_opal2_api_routes.py` | Passed: 3 tests, 1 skipped because optional `slowapi` was not installed in the system Python environment. |
| `python3 -m pytest -q tools/command_chain/tests/test_parser.py tests/test_command_chain_entrypoints.py` | Passed: 41 tests. |
| `python3 -m pytest -q tests/test_flight_control_infrastructure.py` | Passed: 10 tests. |
| `/Users/travisstreets/.local/bin/python3.11 -c "from modules.hr_system.core.character_generator import CharacterGenerator; g=CharacterGenerator(); print('generate_profile', hasattr(g, 'generate_profile')); print('generate_character', hasattr(g, 'generate_character'))"` | Confirmed `generate_profile False`, `generate_character True`. |
| `python3 -m pytest -q tests/hr/test_hr_module.py` | Not completed in the system Python 3.9 environment: missing `numpy`; current package metadata requires Python `>=3.11`. |
| `/Users/travisstreets/.local/bin/python3.11 -m pytest -q tests/hr/test_hr_module.py` | Not completed: the local Python 3.11 interpreter does not have `pytest` installed. |
| `python3 -m pytest -q tests/test_subroutines_quick.py` | Not completed in the system Python 3.9 environment: current subroutine code imports `datetime.UTC` and current package metadata requires Python `>=3.11`; async tests also need an async pytest plugin. |
| `/Users/travisstreets/.local/bin/python3.11 -m pytest -q tests/test_subroutines_quick.py` | Not completed: the local Python 3.11 interpreter does not have `pytest` installed. |
| `/Users/travisstreets/.local/bin/python3.12 -m pytest -q tests/test_subroutines_quick.py` | Not completed: the local Python 3.12 interpreter does not have `pytest` installed. |
| `python3 -m pytest -q tests/test_code_quality_analyzer.py` | Not completed in the system Python 3.9 environment: current code imports `datetime.UTC`; package metadata requires Python `>=3.11`. |
| `python3 -m pytest -q tests/test_bridge_v2_basic.py tests/test_cross_repo_bridge_thread_transfer.py` | Not completed in this local pytest stack: async tests require an async pytest plugin that is not active here. |
| `git diff --check` | Passed. |

Recommended follow-up commands in a provisioned Python `>=3.11` environment:

```bash
python3.11 -m pytest -q tests/hr/test_hr_module.py
python3.11 -m pytest -q tests/test_subroutines_quick.py
python3.11 -m pytest -q tests/test_code_quality_analyzer.py
python3.11 -m pytest -q tests/test_bridge_v2_basic.py tests/test_cross_repo_bridge_thread_transfer.py
python3.11 -m pytest -q tests/test_api_surface_inventory.py
python3.11 -m pytest -q tests/test_memory_retrieval_api.py tests/test_vector_gen_v2.py
python3.11 -m pytest -q tests/test_opal2_api_routes.py
python3.11 -m pytest -q tools/command_chain/tests/test_parser.py tests/test_command_chain_entrypoints.py
python3.11 -m pytest -q tests/test_flight_control_infrastructure.py
git diff --check
```
