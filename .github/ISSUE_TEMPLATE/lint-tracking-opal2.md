---
name: "Lint tracking – opal2 (Stage 3)"
about: Track and stage lint refactors for modules/opal2 and adjacent modules
labels: ["tech-debt", "lint", "quality"]
---

# Lint tracking – opal2 (Stage 3)

## Summary

Stage 3 lint tracking and incremental refactors for `modules/opal2` (plugins, engines, renderers). Goal: keep CI green while expanding coverage and cleaning up legacy issues.

## Scope

- Expand flake8 CI coverage to include `modules/opal2` (done in PR: add workflow update).
- Address lingering lint-only issues across:
  - `modules/opal2/plugins/*`
  - `modules/opal2/engines/*`
  - `modules/opal2/*` (registry, glyph core/cache interactions)
- Maintain backwards compatibility and avoid behavior changes unless covered by tests.

## Owners

- Primary: @AUo959
- Co-owners: @repo-maintainers

## Acceptance criteria

- CI flake8 includes `modules/opal2` and stays green for main.
- No E9/F82/F401/E501 hard errors in `modules/opal2` on main.
- Any refactors include minimal unit tests or smoke coverage when public behavior is touched.

## Task list

- [x] Create minimal clean plugin system (`plugin_system.py`) and base plugin API with lint compliance.
- [x] Fix trailing-blank (W391) and whitespace issues in plugin files.
- [x] Polish `quantum_renderer` and `webgl_renderer` for E304/E501.
- [x] Update CI workflow to lint `modules/opal2`.
- [ ] Sweep `modules/opal2` for any remaining lint warnings and open targeted sub-tasks.
- [ ] Evaluate adding type hints and mypy config for `modules/opal2`.
- [ ] Consider pre-commit hook updates to cover opal2 paths locally.

## References

- Makefile targets: `make check` (lint + tests)
- Workflow: `.github/workflows/lint-core.yml`
- Tests: `pytest -q` (currently 109 passing).

## Notes

- Keep changes small and validate often. If a lint fix implies functional changes, split into a separate PR with tests.
