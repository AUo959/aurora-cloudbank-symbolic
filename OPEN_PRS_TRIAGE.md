# PR Triage – September 23, 2025

This summarizes open PRs and suggests a safe, low-risk merge sequence. Codex branches are parked as requested.

## Ready After CI (Dependabot)
- #146 incremental 24.7.2 — pip dep bump — merge-ok after CI
- #147 mercurial 7.1.1 — pip dep bump — merge-ok after CI
- #149 netaddr 1.3.0 — pip dep bump — merge-ok after CI
- #148 s3transfer 0.14.0 — pip dep bump — merge-ok after CI
- #152 concurrently 9.2.1 — npm dev tool — merge-ok after CI
- #151 helmet 8.1.0 — npm security headers — merge-ok after CI

Recommended merge order: 146 → 147 → 149 → 148 → 152 → 151

Notes:
- All six branches were rebased/updated onto `main`.
- For `helmet`, lockfile was regenerated; verify app/server startup in CI.

## Draft or Parked (Codex – parked)
- #160, #161, #162, #163 — add-import_arc_file-function* — draft; rebased, parked
- #153, #154, #155, #156 — enhance-arc-and-open-pr* — draft; rebased, parked
- #124 — refactor-diagnostics-for-async-file-handling — diverged; needs conflict session (parked)
- #108 — remove-large-binary-files-from-version-control — diverged; parked
- #107 — validate-command-input-in-ethics_layer — diverged; parked
- #97 — design-pqn-modular-architecture-with-orion-integration — diverged; parked
- #159, #158, #157 — numeric/crypto changes targeting PQN base — unstable; parked

## Needs Attention (Non-codex)
- #141 copilot/fix-140 — mergeable_state=dirty — conflict resolution needed (park)
- #138 copilot/fix-137 — mergeable_state=dirty — conflict resolution needed (park)
- #139 copilot/fix-123 — mergeable_state=unstable — rebase + CI re-run (park)
- #145 copilot/fix-144 — mergeable_state=unstable — rebase + CI re-run (park)
- #142 pr-97 — diverged — verify relevance or close (park)
- #117 fix/workflows — diverged — targeted YAML conflict pass later (park)
- #116 docs/aurora-v2.4-integration — diverged — park for doc merge window

## Suggested Next Actions
- Trigger CI for the six Dependabot PRs; merge in the order above once green.
- Label Dependabot PRs with `maintenance`, `dependencies`, `rebased`.
- Keep codex and conflict-heavy PRs parked; schedule a focused conflict session later.

## Quick Links
- Dependabot PRs: #146 #147 #149 #148 #152 #151
- Compare pages: run `OPEN=YES bash scripts/open_dependabot_prs.sh`
