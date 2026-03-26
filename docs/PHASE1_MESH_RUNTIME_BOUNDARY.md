# Phase 1 Mesh Runtime Boundary

Date: 2026-03-21
Scope: `aurora-cloudbank-symbolic-main`
Status: active runtime validated, broad migration still unresolved

## Validated Runtime Surface

The currently validated runtime path is:

- `src/servers/l2_integration_server.py`
- `src/mesh/`
- `src/aurora/cli/mesh_cli.py`
- `config/mesh/agents/*.json`
- `config/mesh/memory/`
- `src/dashboard/agent_constellation.html`
- `src/interfaces/aurora_collaboration_chamber.html`
- `runtime/mesh/`
- `scripts/mesh-runtime-launch.sh`
- `deployment/launchd/com.aurora.mesh-runtime.plist`

## Evidence

### Runtime initialization

This command succeeded in the repo root:

```bash
.venv/bin/python -c 'from pathlib import Path; from src.mesh.runtime import MeshRuntime; rt=MeshRuntime(Path(".")); status=rt.get_status(); print(status["mesh_status"], status["total_agents"], status["event_cursor"])'
```

Observed result on 2026-03-21:

- `mesh_status=operational`
- `total_agents=6`
- `event_cursor=22`

### Compile validation

These files compiled successfully with `py_compile`:

- `src/servers/l2_integration_server.py`
- `src/mesh/runtime.py`
- `src/mesh/live_agents.py`
- `src/aurora/cli/mesh_cli.py`

### Manifest inventory

The current runtime uses `6` agent manifests under `config/mesh/agents/`.

### Test validation

The focused runtime regression tests passed when invoked through the interpreter:

```bash
.venv/bin/python -m pytest tests/test_mesh_runtime_surface.py tests/test_mesh_runtime_api_surface.py -q
```

Note:
- `.venv/bin/pytest` currently points at a stale root-style path and is not reliable in this worktree.
- `.venv/bin/python` works and should be used as the invocation path until the virtualenv wrappers are regenerated.
- The API-surface test emitted FastAPI deprecation warnings for `@app.on_event` in `src/servers/l2_integration_server.py`. This is non-blocking today but should be migrated to lifespan handlers.

## Current Drift

The repo worktree still contains severe unresolved migration drift:

- large tracked deletions remain across `docs/`, `scripts/`, `src/`, `.github/`, `.security/`, and other surfaces
- new `.aurora/`, `deployment/launchd/`, and `runtime/mesh/` files are present as a partial replacement surface
- `main` currently has no upstream configured
- `.venv/bin/pytest` still embeds the non-authoritative root-style path `Aurora_Sim_Architecture/aurora-cloudbank-symbolic-main`
- `src/servers/l2_integration_server.py` still uses deprecated FastAPI `@app.on_event` hooks

This means the validated mesh runtime should be treated as the active operational path, while the rest of the deletion set remains under review.

## Deletion Classification

Deletion counts by major area:

- `docs/operational`: `128`
- `scripts`: `19`
- `venv_opal2`: `16`
- `src`: `15`
- `.security`: `13`
- `.github`: `11`
- `.aurora`: `9`
- `manifests`: `6`
- `.gitwiz`: `5`
- `tests`: `4`

Further breakdown:

- `docs/operational/reports`: `45`
- `docs/operational/guides`: `29`
- `docs/operational/completed`: `25`
- `docs/operational/status`: `14`
- `docs/operational/archived`: `13`
- `.github/workflows`: `9`
- `src/aurora`: `6`
- `src/aurora_fusion`: `5`

Recommended treatment by category:

- `docs/operational/*`: likely historical or reporting surfaces; do not restore blindly, but they are lower priority than source/policy deletions if no current references depend on them.
- `.github/workflows` and `.security/*`: review before deletion is accepted, because these are policy, CI, and publication surfaces rather than mere clutter.
- `src/*`, `tests/*`, and `manifests/*`: review before deletion is accepted, because these are code and validation surfaces.
- `venv_opal2/*`: likely environment artifact; restoration is usually lower value than documenting removal.
- deleted root-level one-off utilities: treat as legacy candidate scripts until a written migration spec says otherwise.

## Documentation Drift

During Phase 1 stabilization, these README-linked documents were confirmed missing from the current worktree:

- `docs/CHATGPT_AGENT_MODE_INTEGRATION.md`
- `docs/operational/README.md`
- `docs/operational/ORGANIZATION_SUMMARY.md`

The README now points here instead of treating those paths as current.

## Search Result

A direct path search across the current worktree found no full-path references to the deleted tracked file set from the active runtime code. That supports treating the active mesh runtime as a narrower, newer execution surface rather than a thin wrapper over the deleted legacy files.

This does not prove the deletions are safe to commit.

## Safe Operating Guidance

1. Treat the mesh runtime surface above as the only currently validated execution path.
2. Do not treat the broad deletion set as complete migration without a written migration spec.
3. Do not restore or delete large surfaces ad hoc; reconcile them by category.
4. Prefer repo-relative launch and validation paths over external automation paths.
5. Delay upstream/publication changes until the deletion set is resolved or explicitly accepted.

## Next Phase 1 Steps

1. Audit deleted files by category and identify which ones are still product-facing, policy-facing, or merely legacy noise.
2. Decide which deleted tracked files require restoration, which require formal deprecation, and which can remain removed under a migration record.
3. Add focused tests around the current mesh runtime so the validated surface stays protected while the rest of the repo is reconciled.
