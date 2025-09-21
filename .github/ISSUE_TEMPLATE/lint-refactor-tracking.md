---
name: "Lint refactor tracking (src/modules)"
about: Track staged lint refactors by area and ownership
labels: ["maintenance", "lint", "tech-debt"]
---

# Lint refactor tracking (src/modules)

## Summary

Track lint refactors in legacy code areas (src/ and modules/). CI lint is scoped to tools*, so this issue tracks staged cleanup work.

## Plan (staged)

- Stage 1: whitespace/formatting (W293/E303/E302)
- Stage 2: imports (F401/F811), rename collisions
- Stage 3: undefined names and logic nits (F821, E999)
- Stage 4: line lengths (E501) and structured wrapping
- Stage 5: enable CI lint expansion for the cleaned areas

## Areas and owners

- modules/opal2 (owner: AUo959)
- modules/cask (owner: AUo959)
- src/core (owner: AUo959)
- src/bridges (owner: AUo959)
- src/servers (owner: AUo959)

## Tracking checklist

- [x] Agree owners for areas above
- [ ] Stage 1 complete for modules/opal2
- [ ] Stage 1 complete for modules/cask
- [ ] Stage 1 complete for src/core
- [ ] Stage 1 complete for src/bridges
- [ ] Stage 1 complete for src/servers
- [ ] Stage 2 complete for modules/opal2
- [ ] Stage 2 complete for modules/cask
- [ ] Stage 2 complete for src/core
- [ ] Stage 2 complete for src/bridges
- [ ] Stage 2 complete for src/servers
- [ ] Stage 3 complete for modules/opal2
- [ ] Stage 3 complete for modules/cask
- [ ] Stage 3 complete for src/core
- [ ] Stage 3 complete for src/bridges
- [ ] Stage 3 complete for src/servers
- [ ] Stage 4 complete for modules/opal2
- [ ] Stage 4 complete for modules/cask
- [ ] Stage 4 complete for src/core
- [ ] Stage 4 complete for src/bridges
- [ ] Stage 4 complete for src/servers
- [ ] Stage 5 - Expand CI lint to include cleaned areas

## Notes

- Keep PRs small and focused per area/stage.
- Prefer mechanical fixes first, no behavior changes.
- Use pre-commit locally to enforce ongoing quality.

## Usage

Use the lint refactor tracker script:

```bash
# Analyze current state
python3 scripts/lint_refactor_tracker.py analyze

# Generate progress report
python3 scripts/lint_refactor_tracker.py report

# Mark stage complete
python3 scripts/lint_refactor_tracker.py complete --area modules/opal2 --stage 1

# Generate updated checklist
python3 scripts/lint_refactor_tracker.py checklist
```
