# Peer Review Report — Current Stub and Integration Evidence

**Date:** 2026-06-12  
**Status:** Peer review candidate — current-evidence refresh  
**Historical source audit:** `.aurora/STUB_AND_INTEGRATION_AUDIT.md`  
**Review mode:** Documentation / planning only  
**Runtime impact:** None  

---

## 1. Purpose

This report replaces the stale-audit summary with a current-evidence peer review report.

The historical `.aurora/STUB_AND_INTEGRATION_AUDIT.md` is dated November 14, 2025. It is useful as a lead list, but it is too old to treat as current truth. This report therefore separates:

- historical audit claims,
- current evidence checked against `main`,
- stale or likely-resolved findings,
- confirmed current risks,
- existing issues/PRs that already track the work,
- follow-up items that still need direct verification.

This PR does not implement fixes.

---

## 2. Executive Finding

The historical audit is materially stale. At least two major claims require correction:

1. Mixed-state quantum measurement, entropy, and fidelity support now exist in `modules/quantum_simulator/quantum_state.py`.
2. Opal2 does have an API surface in `modules/opal2/api/opal2_api.py`; the old `routes.py` absence is not enough to conclude there is no API implementation.

Direct current inspection still confirms real recovery targets:

- HR routes still contain silent mock fallback behavior for missing `StaffingAnalyzer`, `CharacterGenerator`, and `OrganizationalIntelligence` imports.
- Open issue #761 already tracks HR mock fallback and `OrganizationalIntelligence`; do not open a duplicate.
- Repository search for HR recovery work found no matching branches and no commits for the searched class/module names.
- Opal2 appears to be implemented as a standalone FastAPI app in `modules/opal2/api/opal2_api.py`, with health/render/generate/plugins/cache/WebSocket/demo surfaces.
- Closed issue #765 and merged PR #935 already repaired malformed Opal2 route decorators and added route smoke tests.
- The remaining Opal2 question is likely main-app integration and lint/CI coverage, not missing API code.
- `src/improvement/engine.py` still has a base `ImprovementPattern.detect()` that raises `NotImplementedError`, while concrete default patterns are implemented.

The peer review pipeline should therefore use this report as a current triage artifact, not as acceptance of the old audit wholesale.

---

## 3. Current Evidence Ledger

| Finding | Label | Current Evidence | Peer Review Action |
|---|---|---|---|
| Historical audit is stale | Observed | Historical source audit is dated November 14, 2025 | Do not open implementation issues from it without current verification |
| HR route mock fallback remains present | Observed | `modules/hr_system/api/hr_routes.py` catches `ImportError` and returns mock data for staffing, character generation, and organizational intelligence | Track through existing issue #761; do not duplicate |
| Existing HR issue already tracks this work | Observed | Issue #761: "Replace or explicitly gate HR mock fallbacks and implement OrganizationalIntelligence" | Use #761 as the coordination surface for HR recovery |
| HR recovery search found no matching active branch or commit | Observed / Blocked | Branch search for `hr` returned no results; commit search for HR class/module names returned no results | Treat as unresolved until local/full-tree evidence finds completed work elsewhere |
| HR core classes were not found by repository search | Observed / Blocked | Search for `class StaffingAnalyzer`, `class CharacterGenerator`, and `class OrganizationalIntelligence` returned only `hr_routes.py` | Verify with local tree or broader code search before implementation |
| Quantum mixed-state `NotImplementedError` claim appears resolved/stale | Observed | Current `quantum_state.py` implements density-matrix creation, mixed-state measurement, entropy, and fidelity paths | Do not open mixed-state implementation issue from old audit; consider tests/docs review only |
| Opal2 `routes.py` is absent, but Opal2 API code exists under `opal2_api.py` | Observed | `modules/opal2/api/opal2_api.py` defines a FastAPI app with `/health`, `/render`, `/generate`, `/plugins`, `/cache/stats`, `/cache/clear`, `/ws`, and `/demo` | Do not classify as missing API implementation solely because `routes.py` is absent |
| Existing Opal2 issue/PR already repaired route decorator breakage | Observed | Issue #765 is closed; PR #935 merged decorator fixes and route smoke tests | Do not reopen decorator issue unless regression is observed |
| Remaining Opal2 risk is likely integration/classification/CI coverage | Derived | Search for `opal2_api` main-app inclusion did not find current integration evidence; old issues note Opal2 CI exclusions | Verify whether Opal2 is standalone service, mounted app, or intentionally excluded from main API |
| Improvement Engine base class still raises `NotImplementedError`, but concrete default patterns are implemented | Observed / Derived | `ImprovementPattern.detect()` raises `NotImplementedError`; `ComplexityPattern`, `DuplicateCodePattern`, `LongFunctionPattern`, `MagicNumberPattern`, and `ErrorHandlingPattern` implement detection | Classify as abstract base behavior unless production code instantiates base pattern directly |
| Flight Control integration status not yet re-verified in this pass | Blocked | Not inspected directly in this refresh | Do not create issue yet; verify first |
| Continuity API status not yet re-verified in this pass | Blocked | Not inspected directly in this refresh | Do not create issue yet; verify first |
| Security TODOs from old audit not yet re-verified in this pass | Blocked | Not inspected directly in this refresh | Run focused security TODO search before creating issues |

---

## 4. Current-Evidence Detail

### 4.1 HR System Mock Fallback — Confirmed Current Risk, Existing Issue Found

Current route behavior imports implementation classes inside request handlers and returns plausible mock data if imports fail.

Confirmed fallback sites:

- `analyze_staffing_needs()` imports `StaffingAnalyzer`; on `ImportError`, it logs a warning and returns mock staffing numbers.
- `generate_character()` imports `CharacterGenerator`; on `ImportError`, it logs a warning and returns generated placeholder profile data.
- `get_organizational_intelligence()` imports `OrganizationalIntelligence`; on `ImportError`, it logs a warning and returns placeholder organizational data.

Existing coordination surface:

- Issue #761 already tracks this exact area: "Replace or explicitly gate HR mock fallbacks and implement OrganizationalIntelligence."

Recovery search performed:

- PR search for HR class/module names did not surface a specific HR recovery PR.
- Branch search for `hr` returned no matching branches.
- Commit search for `StaffingAnalyzer`, `CharacterGenerator`, `OrganizationalIntelligence`, and `hr_system` returned no results.

Risk:

- API consumers may receive plausible but non-real HR analysis.
- Import failure is degraded to mock content instead of explicit unavailable/demo-mode behavior.
- This can blur implementation truth and runtime capability.

Recommended follow-up:

- Do not open a duplicate issue.
- Use #761 for HR recovery work.
- Before implementation, perform a local/full-tree search to determine whether completed HR core work exists under another name or branch outside indexed GitHub search.
- If no implementation exists, update #761 with the current evidence and proceed with a focused implementation PR.

### 4.2 Quantum Mixed-State Operations — Historical Claim Appears Resolved

The old audit claimed mixed-state `measure`, `entropy`, and `fidelity` raised `NotImplementedError`.

Current evidence shows:

- `QuantumState.from_density_matrix()` exists.
- `QuantumState.from_pure_ensemble()` exists.
- `density_matrix` property supports stored density matrix and pure-state conversion.
- `measure()` handles mixed states via diagonal density-matrix probabilities.
- `entropy()` computes Von Neumann entropy from density-matrix eigenvalues.
- `fidelity_with()` handles pure/mixed and mixed/mixed state fidelity using matrix square roots.

Recommended follow-up:

- Do not open an implementation issue from the old audit.
- Optional: verify test coverage for mixed-state measurement, entropy, and fidelity.
- Optional: update or annotate the historical audit as stale if repo convention allows.

### 4.3 Opal2 API Surface — Historical Claim Needs Correction

The old audit focused on absence of `modules/opal2/api/routes.py`. Current evidence shows this is too narrow.

Current Opal2 API evidence:

- `modules/opal2/api/opal2_api.py` exists.
- It defines a standalone FastAPI `app`.
- It exposes `/`, `/health`, `/render`, `/generate`, `/plugins`, `/cache/stats`, `/cache/clear`, `/ws`, and `/demo` surfaces.
- Closed issue #765 and merged PR #935 already fixed malformed decorators for `/render` and `/generate` and added route smoke tests.

Remaining question:

- Is Opal2 intended to run as a standalone FastAPI app, be mounted into the main Aurora API, or remain excluded from main runtime pathways?
- Is Opal2 still excluded from broad lint/CI, and if so, is the narrower smoke coverage sufficient?

Recommended follow-up:

- Do not create an issue saying Opal2 has no API implementation.
- Create or locate a focused issue only for Opal2 runtime classification/main-app integration/CI coverage if that gap remains.
- If Opal2 is intentionally standalone, document that status instead of wiring it into `aurora_api.py` by default.

### 4.4 Improvement Engine — Partially Stale / Needs Classification

The base class still raises `NotImplementedError`, but current file also includes concrete pattern implementations and a registered default pattern set.

Current concrete implementations include:

- `ComplexityPattern`
- `DuplicateCodePattern`
- `LongFunctionPattern`
- `MagicNumberPattern`
- `ErrorHandlingPattern`

Risk:

- This may be normal abstract/base-class behavior rather than an incomplete implementation.
- The real question is whether base `ImprovementPattern` is ever instantiated directly or whether production claims overstate the engine's capability.

Recommended follow-up:

- Do not classify this as an implementation bug yet.
- Verify usage sites and tests.
- If needed, convert base class to `abc.ABC` / `@abstractmethod` or document extension contract.

---

## 5. Recommended Follow-Up Work

### Existing Issue — HR System Mock Fallback and OrganizationalIntelligence

**Priority:** High  
**Type:** Implementation / safety  
**Status:** Existing issue #761 should remain the coordination surface.

Scope:

- Verify current `modules/hr_system/core/` tree locally or via full file listing.
- Confirm whether concrete `StaffingAnalyzer`, `CharacterGenerator`, and `OrganizationalIntelligence` implementations exist under another name or in unrecovered branches.
- Remove silent production mock fallback, gate it behind explicit demo mode, or return structured unavailable errors.
- Add tests for success and missing-backend behavior.

Acceptance criteria:

- No production route silently returns plausible mock data because imports failed.
- Missing backend behavior is explicit and test-covered.
- Logs do not expose sensitive implementation details.

### Issue Candidate — Opal2 Runtime Classification / Main-App Integration / CI Coverage

**Priority:** Medium  
**Type:** Architecture / integration  
**Status:** Current evidence supports a focused classification issue if no duplicate exists.

Scope:

- Confirm intended status of Opal2: standalone FastAPI app, mounted main API sub-app, internal library, or deprecated module.
- If standalone, document launch path and required smoke coverage.
- If mounted, design minimal integration route/mount and tests.
- If internal-only, document that status clearly.
- Confirm whether Opal2 remains excluded from broad lint/CI and whether targeted tests are sufficient.

### Issue Candidate — Mixed-State Quantum Test Coverage Review

**Priority:** Low-Medium  
**Type:** Test/documentation review  
**Status:** Historical implementation claim appears stale; do not create implementation issue without new evidence.

Scope:

- Verify tests for mixed-state measurement, entropy, and fidelity.
- Add tests/docs only if coverage or public API documentation is weak.

### Issue Candidate — Improvement Engine Contract Review

**Priority:** Low  
**Type:** Design/documentation  
**Status:** Needs usage verification.

Scope:

- Verify whether `ImprovementPattern` is intentionally abstract.
- Check if base class is directly instantiated anywhere.
- Consider `abc.ABC` / `@abstractmethod` cleanup or documentation.

### Audit Continuation — Remaining Historical Claims

**Priority:** Medium  
**Type:** Audit continuation  
**Status:** Blocked until direct inspection.

Scope:

- Flight Control integration boundary.
- Continuity API status.
- Empty exception handlers.
- Security TODOs.
- Agents, instance_bridge, memory_retrieval, vector_gen module status.

---

## 6. State Classification

| Item | Classification |
|---|---|
| Historical audit file | Historical State / Lead List |
| This report | Current Review Artifact / Peer Review Candidate |
| HR mock fallback finding | Current Canon Evidence / Existing Issue #761 |
| Quantum mixed-state implementation-gap claim | Historical State / Likely Resolved |
| Opal2 `routes.py` absence | Historical State / Misleading Narrow Claim |
| Opal2 `opal2_api.py` API surface | Current Canon Evidence |
| Opal2 main-app integration question | Current Evidence Gap / Architecture Classification Needed |
| Improvement base `NotImplementedError` | Current Canon Evidence / Needs Design Classification |
| Follow-up work list | Recommended Planning Artifact |
| Any implementation fixes | Not canon until committed through PR |

---

## 7. Review Constraints

Do not use the November 2025 audit as direct proof of current defects.

Do not implement all findings in one umbrella PR.

Do not create duplicate issues for work already tracked by #761 or resolved by #765/#935.

Do not create implementation issues for stale or unverified claims.

Do not treat library/API exposure questions as implementation bugs until intended surface is confirmed.

Security TODOs require a separate current-evidence pass before issue creation.

---

## 8. Recommended Peer Review Outcome

Recommended outcome for this PR:

- Accept this report as a corrected current-evidence triage artifact.
- Route HR recovery work through existing issue #761.
- Treat Opal2 as partially recovered: API exists, decorator bug fixed, remaining question is classification/integration/CI coverage.
- Create focused follow-up issues only for findings verified against current `main` and not already tracked.
- Treat mixed-state quantum implementation as likely resolved unless tests/docs prove a remaining gap.
- Continue evidence refresh for the remaining historical audit categories.

---

## 9. Validation

Documentation-only change.

Suggested local check:

```bash
python - <<'PY'
from pathlib import Path
p = Path('.aurora/peer_review/STUB_AND_INTEGRATION_AUDIT_PEER_REVIEW_REPORT.md')
text = p.read_text()
assert 'Current Evidence Ledger' in text
assert 'Existing issue #761' in text
assert 'Opal2 `opal2_api.py` API surface' in text
assert 'Historical State / Lead List' in text
assert 'Likely Resolved' in text
PY
```

No runtime code changed.
