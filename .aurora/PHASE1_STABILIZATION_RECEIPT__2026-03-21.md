# Phase 1 Stabilization Receipt

Date: 2026-03-21
Scope: `aurora-cloudbank-symbolic-main`
Status: partial stabilization

## Applied Fixes

- Corrected the checked-in LaunchAgent plist to reference the authoritative nested repo path under `GUMAS_SIM_2.5`.
- Removed the checked-in LaunchAgent dependency on `~/.codex/automations/aurora-package-watch/mesh-runtime-launch.sh`.
- Updated `scripts/install_mesh_runtime_launch_agent.sh` to generate the LaunchAgent from the live repo root instead of copying a hardcoded plist with stale paths.
- Added `docs/PHASE1_MESH_RUNTIME_BOUNDARY.md` to record the validated mesh runtime surface and current migration drift.
- Added `tests/test_mesh_runtime_surface.py` to protect the current mesh runtime initialization path.
- Added `tests/test_mesh_runtime_api_surface.py` to protect the FastAPI mesh dashboard, health, WebSocket, and message-routing contract.
- Classified the tracked deletion set by category so review can focus on source, policy, and workflow surfaces before historical docs.

## Why

The prior runtime handoff mixed two incompatible path models:
- the authoritative nested repo path in `GUMAS_SIM_2.5/...`
- the ambiguous root-level `Aurora_Sim_Architecture/...` path warned about in the workspace control-plane instructions

It also depended on an external automation script outside the repo boundary.

## Validation Targets

- `plutil -lint deployment/launchd/com.aurora.mesh-runtime.plist`
- `zsh -n scripts/install_mesh_runtime_launch_agent.sh`
- `zsh -n scripts/mesh-runtime-launch.sh`
- `.venv/bin/python -c 'from pathlib import Path; from src.mesh.runtime import MeshRuntime; ...'`
- `.venv/bin/python -m py_compile src/servers/l2_integration_server.py src/mesh/runtime.py src/mesh/live_agents.py src/aurora/cli/mesh_cli.py`
- `.venv/bin/python -m pytest tests/test_mesh_runtime_surface.py tests/test_mesh_runtime_api_surface.py -q`

## Remaining Risk

This does not resolve the broader destructive drift in the repo worktree:
- large tracked deletions remain
- `main` still has no upstream configured
- migration intent is still not explicitly recorded
- the `.venv/bin/pytest` wrapper still points at the stale root-style path and should not be treated as authoritative validation
- `src/servers/l2_integration_server.py` still emits FastAPI `@app.on_event` deprecation warnings during API tests

This receipt covers only the low-risk runtime-handoff correction.
