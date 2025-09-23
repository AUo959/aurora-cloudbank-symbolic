# Staged Lint Refactor Plan

Use this plan to coordinate lint cleanup across legacy areas.

- Owners: see [LINT_REFACTOR_OWNERS.md](../owners/LINT_REFACTOR_OWNERS.md)
- Open tracking issue: use the template at
  <https://github.com/AUo959/aurora-cloudbank-symbolic/issues/new?template=lint-refactor-tracking.md&title=Staged+lint+refactors+tracking>

Stages:

1. Whitespace/formatting (W293/E303/E302)
2. Imports (F401/F811) and rename collisions
3. Undefined names and syntax (F821/E999)
4. Line length and wrapping (E501)
5. Expand CI lint coverage for cleaned areas

Scope policy:

- CI flake8 currently scopes to tools/*; expand per area after Stage 1/2 land.
- Use pre-commit locally for broader checks.
