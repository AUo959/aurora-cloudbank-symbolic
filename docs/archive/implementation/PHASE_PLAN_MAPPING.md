# Phase Plan Mapping

| Item | Title | Phase | Rationale | Acceptance Signal |
|------|-------|-------|-----------|-------------------|
| PR #372 | fix: resolve syntax errors blocking coverage generation | Phase 1 (CI Stabilization) | Unblocks coverage & CI; low-risk syntactic corrections | All checks green; coverage job succeeds |
| PR #375 | Fix formatting issues in markdown files | Phase 1 (CI Stabilization) | Straightforward formatting; reduces lint noise | Lint jobs clean; no markdown warnings |
| PR #376 | Write a CLAUDE.md | Phase 2 (Quality & Modernization) | Documentation artifact; not blocking CI stability | File present; passes docs lint; linked from README |
| PR #378 | Fix CI failures: flake8 W293, ES module syntax, and Vercel config conflicts | Phase 1 (CI Stabilization) | Directly targets failing CI categories | Post-rebase CI passes; Vercel success |
| PR #379 | Reduce system complexity and enhance functionality | Phase 2 (Quality & Modernization) | Refactoring; should land after stable baseline | Refactor merged; tests unchanged or improved |
| PR #388 | Integrate OPPY v2.1, HR Module v3.0, and Quantum Forge into MCP FastAPI | Phase 3 (Symbolic & MCP Integration) | Adds multi-module integration complexity | New endpoints live; integration tests pass |
| PR #389 | [WIP] Consolidate MCP bridge logic into a single configuration | Phase 3 (Symbolic & MCP Integration) | Centralizes config logic dependency | Single config file; no duplicate bridge logic |
| Issue #380 | Integrate OPPY v2.1, HR Module v3.0 and Quantum Forge into the MCP FastAPI | Phase 3 | Mirrors PR #388 scope | Same as PR #388 signals |
| Issue #381 | Consolidate ThreadCore Payloads and Unify State Management | Phase 2 (Quality & Modernization) | Internal cohesion improvement | Unified state module; reduced payload duplication |
| Issue #382 | Consolidate MCP Bridge Logic into a Single Configuration | Phase 3 | Mirrors PR #389 objective | One config; removed legacy paths |
| Issue #383 | Add RBAC and OAuth2 Authentication | Phase 4 (Security & Observability) | Security layer after stable integrations | Auth endpoints; security tests pass |
| Issue #384 | Activate Telemetry and Observability | Phase 4 | Monitoring after auth foundation | Metrics endpoints active; dashboard ingestion OK |
| Issue #385 | Implement Kubernetes CI Deployment Pipeline | Phase 5 (Performance & Optimization) | Infrastructure scaling optimization | K8s pipeline green; deploy time improved |
| Issue #387 | Provide a Developer Deployment Guide | Phase 6 (Documentation & Release) | Final documentation consolidation | Guide published; referenced in README |

> Note: Issue numbering skipped #386 (not listed in open issues query). If #386 appears later, categorize based on content: likely Phase 4 (security/observability) or Phase 5 (optimization) depending on domain.

## Phase Sequencing Integrity
- Phase 1: Only minimal-risk CI & syntax/config stabilization (PRs #372, #375, #378)
- Phase 2: Documentation & refactors (PR #376, #379, Issue #381)
- Phase 3: Multi-module integration (PR #388, #389, Issues #380, #382)
- Phase 4: Security & telemetry layers (Issues #383, #384)
- Phase 5: Deployment pipeline optimization (Issue #385)
- Phase 6: Final developer-facing documentation (Issue #387) and release packaging

## Dependencies Graph (Simplified)
```
Phase1 --> Phase2 --> Phase3 --> Phase4 --> Phase5 --> Phase6
          \          \        \         \         \
           (Docs)     (Integration)  (Security)   (Perf)   (Docs Final)
```

## Risk Notes
- Do not merge integration PRs (#388/#389) before CI baseline is fully green.
- Security implementation (RBAC/OAuth2) should not start before MCP consolidation to avoid duplicative policy wiring.
- Kubernetes pipeline depends on stable integration + security context for environment variables.

## Transition Criteria
| From | To | Required Conditions |
|------|----|---------------------|
| Phase 1 → 2 | All Phase 1 PRs merged; CI green for 3 consecutive runs |
| Phase 2 → 3 | Documentation artifacts merged; refactor tests stable |
| Phase 3 → 4 | Integration tests >90% pass; no critical errors |
| Phase 4 → 5 | Auth + telemetry endpoints stable; security tests passing |
| Phase 5 → 6 | Pipeline deploy success rate >95%; perf baseline captured |
| Phase 6 → Release | All docs updated; CHANGELOG complete; tag prepared |

---
Anchor: PHASE-PLAN-MAPPING
Created: 2025-11-17
