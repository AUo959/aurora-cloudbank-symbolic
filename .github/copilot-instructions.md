# Aurora CloudBank Symbolic – Agent Playbook
- This repo models a quantum-symbolic governance stack; every feature must preserve T1/SRB anchors, DLP tags, and memory seals.
## Architecture hotspots
- `aurora_api.py` is the FastAPI surface: rate-limited endpoints, ChatGPT Agent Mode (`/agent/*`), Sonnet 4 toggles, and optional AuMemManager router injection.
- `src/integrations/chatgpt_agent_mode.py` defines the agent tool registry and session store; tests expect unknown tools to raise `HTTPException` and error payloads to return `success=False`.
- `src/aurora/core/symbolic_engine.py` runs chain notation (`001//999//`) while advancing T1 and SRB anchors; chain exports feed DLP manifests.
- `src/core/native_dlp_export.py` is the canonical DLP tracker: always add `context_tag`, anchor protocols, and call `create_export_manifest` when persisting results.
- `modules/symbolic_core/` houses geometric algebra (Clifford with graceful mock fallback) and Sonnet 4 integration; keep imports aligned with existing patterns.
- `modules/aumemmanager/` exposes the quantum memory API; treat it as optional and guard imports like the existing router wiring.
## Daily workflows
- Bootstrap with `make setup` (runs `scripts/setup_environment.sh`), then `python scripts/dev-status.py` to confirm the environment.
- Use `make check` for scoped lint + pytest; run targeted suites (e.g., `pytest tests/test_chatgpt_agent_mode.py`) before touching agent or DLP logic.
- Launch the service via `python aurora_api.py`; health endpoints live at `/health` and `/api/health`, agent discovery at `/agent/tools`.
- For maintenance automation, rely on `make maintenance-scan` (SSMT v3.0 pipeline) and `make maintenance-status` to inspect schedules.
## Coding patterns
- Every reflex log or agent response must include `context_tag` and `symbolic_hash_validation`; reuse `NativeDLPTracker` helpers instead of ad-hoc metadata.
- FastAPI handlers enforce CSRF via `HTTPBearer`; when adding endpoints, mirror the dual definition pattern (`async def` with security + public async implementation).
- When extending agent tools, register them in `ChatGPTAgentModeIntegration._register_default_tools` and provide async handlers returning structured dicts.
- Preserve graceful degradation: wrap optional dependencies in `try/except ImportError` and provide minimal mocks as seen in GA and Sonnet hubs.
- Sanitise tool payloads with `_sanitize_tools_info` (remove `handler`) before responses; tests assert this behaviour.
## Validation checklist
- Keep Flake8's 120-char limit, async pytest style, and ensure new exports pass through `NativeExportSystem`.
- After significant changes run `pytest tests/test_chatgpt_agent_mode.py tests/test_aurora_symbolic.py` plus any touched module suites.
- For deliverables touching security or memory sealing, update or generate manifests via `NativeDLPTracker.create_export_manifest` and call out anchor protocols in docs.
