# Local Sync Diagnosis

Date: 2026-03-23
Scope: `aurora-cloudbank-symbolic-main`
Status: upstream linkage repaired; local history divergence unresolved
Authority: local diagnostic receipt only

## Key Finding

The CloudDocs worktree at the authoritative nested repo path is not a normal behind-ahead clone of the public GitHub repo. It is a divergent local history with no merge base against fetched `origin/main`.

## Public Source Of Truth

- Remote: `git@github-aurora:AUo959/aurora-cloudbank-symbolic.git`
- Fetched `origin/main` on 2026-03-23
- Public head after fetch: `4d779518f959cec839e3ddf7f51994189fec961e`
- Public head subject: `Auto-update: Synergy Dashboard Module (Issue #260)`

## Local Worktree State

- Local repo path:
  - `/Users/travisstreets/Library/Mobile Documents/com~apple~CloudDocs/Aurora_ORIONCORE_Directory_Main/GUMAS_SIM_2.5/Aurora_Sim_Architecture/aurora-cloudbank-symbolic-main`
- Local `main` head:
  - `42e0b9fb9f1e0e10a9091d595cf2811f2c14eacf`
- Local `main` subject:
  - `Add mesh router runtime and chamber integration`
- Local worktree counts at time of diagnosis:
  - `modified=9`
  - `deleted=427`
  - `untracked=37`

## History Diagnosis

- `git merge-base main origin/main` returned no merge base
- Local root commit:
  - `f517fcbecb4159e1f33cf44c6660cf05360f1f3b`
  - `2026-02-28 22:41:47 -0500`
  - `Fix pytest collection issues and remove test warnings`
- Public root commit:
  - `4fb2678fdf4ba2c66381643df2b1266826cc997d`
  - `2025-04-09 12:52:00 -0400`
  - `Initial commit`

This means the CloudDocs `main` branch is not descended from the current public repo history.

## Upstream Repair Applied

Local `main` previously had no upstream tracking config. That hid the public divergence in normal status output.

Applied local config repair:

```bash
git branch --set-upstream-to=origin/main main
```

Result:

- `git status --short --branch` now reports:
  - `## main...origin/main [ahead 10, behind 1747]`
- This change is config-only. It does not alter commits, index state, or worktree files.

## Deletion Set Vs Public Main

The local worktree has `427` tracked deletions relative to local `HEAD`.

Direct tree checks against fetched `origin/main` show:

- `23` deleted tracked paths still exist in public `origin/main`
- `404` deleted tracked paths do not exist in public `origin/main`

Public-still-present deleted paths include:

- `src/aurora/core/command_grammar/__init__.py`
- `src/aurora/core/command_grammar/ast.py`
- `src/aurora/core/command_grammar/catalog.py`
- `src/aurora/core/command_grammar/normalizer.py`
- `src/aurora/core/command_grammar/parser.py`
- `src/aurora/core/command_grammar/validator.py`
- `src/aurora_fusion/__init__.py`
- `src/aurora_fusion/engine.py`
- `src/aurora_fusion/memory.py`
- `src/aurora_fusion/module_map.py`
- `src/aurora_fusion/profiles.py`
- `tests/test_aurora_command_grammar.py`
- `tests/test_aurora_fusion_engine.py`
- `tests/test_aurora_memory_optimizer.py`
- `tests/test_mesh_router_v1.py`
- `scripts/auto_selective_ingest_gate.py`
- `docs/AURORA_FUSION_META_ANALYSIS.md`
- `manifests/selective_integration/Aurora_SelectiveIntegrationProtocol_v2.5_VIEW.json`
- `manifests/selective_integration/modules_manifest.json`
- `manifests/selective_integration/source.json`
- `manifests/selective_integration/triage_overrides.json`

Interpretation:

- The local deletion set is mixed.
- Much of it is local-only history that is absent from the public repo.
- Part of it conflicts with current public source truth and should not be treated as safe deletion.

## Runtime Repair Carried Forward

Prior to this sync diagnosis, the local `.venv` wrappers were repaired from the stale root-style path to the authoritative nested repo path. This restored local execution for:

- `./.venv/bin/pytest`
- `./.venv/bin/uvicorn`

Focused validation still passes locally:

- `./.venv/bin/pytest tests/test_mesh_runtime_surface.py tests/test_mesh_runtime_api_surface.py -q`
- `cd <repo> && ./.venv/bin/python -c 'from pathlib import Path; from src.mesh.runtime import MeshRuntime; ...'`

## Non-Destructive Limits

No destructive reconciliation was performed.

The following were intentionally not done:

- no `git reset --hard`
- no mass restore from public history
- no overwrite of local deleted paths
- no replacement of the current CloudDocs worktree

## Immediate Next Safe Options

1. Treat fetched `origin/main` as the public source of truth for CloudBank.
2. Do not use the current CloudDocs `main` branch as an authoritative publication baseline.
3. If a clean local public-platform checkout is needed, create a fresh clone or worktree from `origin/main` after resolving local `git-lfs` checkout support.
4. Reconcile the `23` deleted paths that still exist in public `origin/main` before trusting the current CloudDocs worktree for development or publication.
5. Preserve the current divergent CloudDocs worktree until the user decides whether to archive it, replace it, or salvage selected local commits.
