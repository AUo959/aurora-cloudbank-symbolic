# Aurora CloudBank – Copilot Instructions (concise)

Quantum-enhanced symbolic governance with Vector Symbolic Architecture (VSA), ethical anchors, and agent-mode APIs. This guide gives AI coding agents the minimum project-specific context to be productive fast.

## Architecture at a glance
- API: `aurora_api.py` (FastAPI) exposes geometric algebra and ChatGPT Agent Mode endpoints.
- Symbolic engine: `src/aurora/core/symbolic_engine.py` (T1 temporal + SRB spatial anchors, chain notation `001//999//`).
- Geometric algebra: `modules/symbolic_core/geometric_algebra.py` (uses `clifford` if available; mock fallback otherwise).
- Data lineage: `src/core/native_dlp_export.py` (DLP tags, anchors, manifests).
- Reflective autonomy bootstrap: `modules/reflective_autonomy/loom_restore_script.py` (used by `make run`).

## Core patterns you must follow
- DLP tagging is required for symbolic/quantum ops. Always include `context_tag` and anchor protocols.
  ```python
  from src.core.native_dlp_export import NativeDLPTracker
  tracker = NativeDLPTracker()
  tag_id = tracker.tag_symbolic_operation({"concepts": ["alpha"], "dimension": 512})
  tag = tracker.tags[tag_id]
  tag.add_anchor_protocol("EOS_SEED_ORION")
  tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
  tag.metadata.update({"context_tag": "op_context", "dlp_level": "DLP_L1_OK", "symbolic_hash_validation": True})
  ```
- Geometric algebra must degrade gracefully: keep the mock path working when `clifford` isn’t installed.
- Use chain notation helpers from `SymbolicEngine.execute_chain(start, end)`; export manifests via `export_manifest()`.

## Developer workflow (verified commands)
- Quick status dashboard: `python3 scripts/dev-status.py`
- Run (reflective bootstrap): `make run` (calls `modules/reflective_autonomy/loom_restore_script.py`)
- Fast dev launcher (menu): `./scripts/quick-start.sh`
- Tests: `pytest tests/`
- Lint: `flake8 .` (120-char line limit); format with `black` if present
- Docker (API 8000, CLI sidecar): `docker-compose up --build`

## API surface (key endpoints)
- Geometric algebra:
  - POST `/geometric/vector` (x,y,z) → GA vector
  - POST `/geometric/mult` (a,b as expressions like `e1 e2`) → product via `GeometricAlgebra.mult`
- Agent Mode (see `docs/CHATGPT_AGENT_MODE_INTEGRATION.md`):
  - GET `/agent/tools` – tool registry (OpenAPI-like)
  - POST `/agent/execute` – execute tool with validated params
  - POST `/agent/session` – create/update/get/delete session
  - GET `/sonnet4/status`, POST `/sonnet4/enable`

### Copy-paste examples
- Execute geometric algebra:
  - POST `/agent/execute`
  - Body:
    ```json
    {
      "tool_name": "geometric_algebra",
      "parameters": {
        "expression_a": "e1 + 2",
        "expression_b": "e2",
        "operation": "mult"
      }
    }
    ```
- Create a session, then update it:
  - POST `/agent/session` with `{ "action": "create", "state_data": {"context": "demo"} }`
  - Then POST `/agent/session` with `{ "action": "update", "session_id": "<returned_id>", "state_data": {"step": 1} }`

## Conventions and imports
```python
from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.sonnet4_integration_hub import sonnet4_hub  # used by aurora_api.py
from src.core.native_dlp_export import NativeDLPTracker
```
- All reflex logs and cross-layer handoffs must set `context_tag` and `symbolic_hash_validation=True`.
- Ethics protocol: `Picard_Delta_3`; anchor seed often `EOS_SEED_ORION`.

## Gotchas (repo-verified)
- Docker healthcheck points to `/api/health`, but API exposes `/health`. Update compose or add `/api/health` if needed.
- `aurora_api.py` imports `src.integrations.chatgpt_agent_mode.chatgpt_agent_integration`; if missing, implement a minimal stub exposing `discover_tools()` and `execute_tool()` to keep Agent Mode endpoints working.
- GA input parsing is strict (`parse_multivector` only accepts blade keys and numerics). Keep inputs sanitized.

## Security & memory sealing
- Use `tools/symbolic/memory_sealer.py` to produce SHA256 seals and audit trails for files/dirs/threads.
- Run repository health scans via `scripts/aurora_health_monitor.py`.

## File pointers (start here)
- API: `aurora_api.py` • Symbolic: `src/aurora/core/symbolic_engine.py` • DLP: `src/core/native_dlp_export.py`
- Docs: `docs/CHATGPT_AGENT_MODE_INTEGRATION.md` • Dev tools: `scripts/dev-status.py`, `scripts/quick-start.sh`

If anything above is unclear or incomplete (e.g., Agent Mode stub expectations, additional endpoints to document), tell me what you need and I’ll refine this guide.
