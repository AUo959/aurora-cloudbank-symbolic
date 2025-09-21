# Lint refactor tracking (src/modules)

Track staged lint refactors in legacy code areas (src/ and modules/). CI lint is currently scoped to tools/*; this issue coordinates incremental cleanups and the gradual expansion of CI lint coverage as areas are cleaned.

References:

- Owners: docs/operational/owners/LINT_REFACTOR_OWNERS.md
- CI (scoped): .github/workflows/lint-core.yml
- Plan: docs/operational/guides/LINT_REFACTOR_PLAN.md

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

Ownership

- [ ] Confirm owners for areas above (see Owners doc)

Stage 1 – whitespace/formatting

- [ ] modules/opal2 (W293/E303/E302)
- [ ] modules/cask (W293/E303/E302)
- [ ] src/core (W293/E303/E302)
- [ ] src/bridges (W293/E303/E302)
- [ ] src/servers (W293/E303/E302)

Stage 2 – imports/collisions

- [ ] modules/opal2 (F401/F811)
- [ ] modules/cask (F401/F811)
- [ ] src/core (F401/F811)
- [ ] src/bridges (F401/F811)
- [ ] src/servers (F401/F811)

Stage 3 – undefined names/logic nits

- [ ] modules/opal2 (F821/E999)
- [ ] modules/cask (F821/E999)
- [ ] src/core (F821/E999)
- [ ] src/bridges (F821/E999)
- [ ] src/servers (F821/E999)

Stage 4 – line lengths/wrapping

- [ ] modules/opal2 (E501)
- [ ] modules/cask (E501)
- [ ] src/core (E501)
- [ ] src/bridges (E501)
- [ ] src/servers (E501)

Stage 5 – CI lint expansion

- [ ] Expand CI lint to include modules/opal2
- [ ] Expand CI lint to include modules/cask
- [ ] Expand CI lint to include src/core
- [ ] Expand CI lint to include src/bridges
- [ ] Expand CI lint to include src/servers

## Notes

- Keep PRs small and focused per area/stage; avoid behavior changes.
- Use pre-commit locally; match CI flake8 settings for consistency.
- As areas clear Stage 1–3, begin enabling E501 gradually with structured wrappers.
