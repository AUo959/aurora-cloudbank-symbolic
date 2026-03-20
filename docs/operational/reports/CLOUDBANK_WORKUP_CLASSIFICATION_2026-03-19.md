# CloudBank Workup Classification

Baseline:
- Clean workup branch: `main` at `42e0b9fb`
- Evidence checkout: dirty `main` worktree plus `codex/reconcile-origin-main-2026-03-13`
- Date: `2026-03-19`

## Ignore / Local Runtime State

These paths are machine-local or continuously mutating and should not drive repo churn:
- `.aurora/audit_trail.json`
- `.aurora/branch_config.json`
- `.aurora/gpg/**`
- `.aurora/index/**`
- `.aurora/quicksaves/**`
- `.aurora/seals/**`
- `.aurora/SIMULATION_STATE*.json`
- `runtime/mesh/*.db`
- `runtime/mesh/transcripts/*.jsonl`
- `.env.mesh`

## Stabilize / Promote As Source

These are durable operator-facing sources worth tracking on the workup branch:
- `config/mesh/runtime.env.example`
- `deployment/launchd/com.aurora.mesh-runtime.plist.template`
- `scripts/mesh-runtime-launch.sh`
- `scripts/install_mesh_runtime_launch_agent.sh`
- `scripts/uninstall_mesh_runtime_launch_agent.sh`
- `scripts/run_pre_commit.sh`
- `.husky/pre-commit`
- `scripts/git-hooks/pre-commit`
- `scripts/install_git_hooks.sh`
- `package.json` pre-commit entry
- `.pre-commit-config.yaml` local hook entry

## Restore / Keep Tracked

These existing tracked files remain part of the stable source surface:
- `runtime/mesh/.gitignore`
- `runtime/mesh/transcripts/.gitignore`
- `scripts/auto_selective_ingest_gate.py`
- `smart-devops`
- `scripts/git_pre_commit_hook.py`

## Defer

These evidence-only additions are intentionally not promoted in this workup because they need separate product or canon review:
- `.aurora/README.md`
- `.aurora/build_canonical_state.py`
- `.aurora/load_simulation.py`
- `.aurora/canonical/**`
- `.aurora` narrative/session markdowns
- `config/mesh/memory/Alex Thorne.md`
- `mesh_cli.py`
- `src/mesh/live_agents.py`

## Notes

- The dirty evidence checkout deleted many tracked files from `main`; those deletions were treated as suspicious and not copied forward blindly.
- The untracked launchd plist from the evidence checkout was not promoted as-is because its hardcoded working directory was incorrect for the actual nested repo path.
