# Staged Lint Refactor Plan

Use this plan to coordinate lint cleanup across legacy areas.

- Owners: see [LINT_REFACTOR_OWNERS.md](../owners/LINT_REFACTOR_OWNERS.md)
- Usage Guide: see [LINT_REFACTOR_USAGE.md](LINT_REFACTOR_USAGE.md)
- Open tracking issue: use the template at
  <https://github.com/AUo959/aurora-cloudbank-symbolic/issues/new?template=lint-refactor-tracking.md&title=Staged+lint+refactors+tracking>

Stages:

1. Whitespace/formatting (W293/E303/E302) - **Automated with scripts/stage1_lint_fixer.py**
2. Imports (F401/F811) and rename collisions - Semi-automated
3. Undefined names and syntax (F821/E999) - Manual review required
4. Line length and wrapping (E501) - Semi-automated
5. Expand CI lint coverage for cleaned areas - Manual process

## Quick Start

```bash
# Initialize tracking system
python3 scripts/lint_refactor_manager.py init

# Check current status
python3 scripts/lint_refactor_manager.py quick-status

# Apply Stage 1 fixes to an area
python3 scripts/lint_refactor_manager.py fix-stage1 src/core

# Mark stage complete
python3 scripts/lint_refactor_manager.py complete-stage src/core 1
```

Scope policy:

- CI flake8 currently scopes to tools/*; expand per area after Stage 1/2 land.
- Use pre-commit locally for broader checks.
- Track progress with the automated tracking system.
