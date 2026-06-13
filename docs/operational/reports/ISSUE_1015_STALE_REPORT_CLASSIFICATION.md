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
from issue comments.

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

## Candidate Documents Still To Classify

The HR cluster is now classified. Remaining documents from the issue body should
be processed in a second pass:

| Source document | Initial route |
| --- | --- |
| `.aurora/STUB_AND_INTEGRATION_AUDIT.md` | Covered by draft PR #1014; use that PR report as current peer-review surface. |
| `.aurora/SUBROUTINE_INTEGRATION_STATUS.md` | Compare against current `src/subroutines/` and mounted routers. |
| `docs/operational/reports/FEATURE_ROADMAP_STATUS.md` | Treat as lead list; verify each module path. |
| `docs/SYSTEM_VALIDATION_REPORT_20251021.md` | Historical validation snapshot; classify claims only after current file checks. |
| `docs/operational/reports/VALIDATION_REPORT.md` | Historical validation snapshot; classify claims only after current file checks. |
| `docs/operational/reports/IMPLEMENTATION_SUMMARY.md` | Historical implementation summary; extract file/class/API claims. |
| `docs/operational/reports/PR_RESOLUTION_SUCCESS_REPORT.md` | Historical PR state; verify against current GitHub only. |
| `docs/operational/reports/THREAD_TRANSFER_BRIDGE_INTEGRATION_SUCCESS.md` | Compare against current `modules/reflective_autonomy/thread_transfer/`. |
| `docs/operational/archived/OPAL2_EXPANSION_PROGRESS.md` | Use for the Opal2 duplicate-class cleanup trail. |
| `docs/operational/reports/COMMAND_CHAIN_IMPLEMENTATION_SUMMARY.md` | Compare against current command-chain modules and router exposure. |

## Recommended Follow-ups

1. Keep #1015 open until the non-HR reports above are classified.
2. Update #761 scope instead of opening a duplicate HR issue:
   - preserve real `StaffingAnalyzer` and `CharacterGenerator` evidence;
   - verify/fix `generate_profile` vs `generate_character`;
   - implement or explicitly gate `OrganizationalIntelligence`.
3. Open or claim a focused Opal2 cleanup after #1015 records the duplicate
   `PluginSystem` evidence.
4. Treat `memory_retrieval` and `vector_gen` as current modules, not missing
   recovery targets.
5. Audit `instance_bridge` separately for runtime role and test coverage.

## Verification Performed

Commands run in this worktree:

| Command | Result |
| --- | --- |
| `python3 -m pytest -q tests/test_api_surface_inventory.py` | Passed: 2 tests. |
| `python3 -m pytest -q tests/test_memory_retrieval_api.py tests/test_vector_gen_v2.py` | Passed: 42 tests. |
| `/Users/travisstreets/.local/bin/python3.11 -c "from modules.hr_system.core.character_generator import CharacterGenerator; g=CharacterGenerator(); print('generate_profile', hasattr(g, 'generate_profile')); print('generate_character', hasattr(g, 'generate_character'))"` | Confirmed `generate_profile False`, `generate_character True`. |
| `python3 -m pytest -q tests/hr/test_hr_module.py` | Not completed in the system Python 3.9 environment: missing `numpy`; current package metadata requires Python `>=3.11`. |
| `/Users/travisstreets/.local/bin/python3.11 -m pytest -q tests/hr/test_hr_module.py` | Not completed: the local Python 3.11 interpreter does not have `pytest` installed. |
| `git diff --check` | Passed. |

Recommended follow-up commands in a provisioned Python `>=3.11` environment:

```bash
python3.11 -m pytest -q tests/hr/test_hr_module.py
python3.11 -m pytest -q tests/test_api_surface_inventory.py
python3.11 -m pytest -q tests/test_memory_retrieval_api.py tests/test_vector_gen_v2.py
git diff --check
```
