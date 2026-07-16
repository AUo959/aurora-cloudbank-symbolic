# Getting Started — Engineer Onboarding

> **You are in the right place.** This document is written for humans — specifically engineers who are new to Aurora CloudBank Symbolic and want to understand what they're working with, get their environment running, and make a real system call, all within 30–45 minutes.
>
> If you are an AI agent, see [`AGENTS.md`](./AGENTS.md) and [`CLAUDE.md`](./CLAUDE.md) instead.

---

## What Is This System?

Aurora CloudBank Symbolic is a **quantum-symbolic AI platform** built as a single FastAPI application. At its core it does four things:

1. **Manages hierarchical memory** — active, compressed, and archived tiers with SHA-256 sealing (`modules/aumemmanager/`)
2. **Enforces ethics geometrically** — a five-dimension curvature field that can hard-veto any operation (`modules/ethics_field/`, `modules/gumas/`)
3. **Simulates quantum circuits** — 7 scenarios across 4 cloud backends (AWS Braket, Azure Quantum, IBM Quantum, Google Cirq) with graceful degradation when backends are unavailable (`modules/quantum_simulator/`)
4. **Orchestrates multi-model AI** — unified interface over Claude and GPT with automatic model selection (`modules/ai_core/`)

The system serves ~339 HTTP routes across 30+ modules. Every operation carries a `context_tag` and generates a SHA-256 audit hash. Nothing is anonymous.

---

## The 3 Runtime Surfaces

Before you write a line of code, know that Aurora has three distinct interfaces:

| Surface | Entry Point | Purpose |
|---------|-------------|--------|
| **REST API** | `http://localhost:8000` | Primary interface; all module functionality exposed here |
| **Interactive Docs** | `http://localhost:8000/docs` | Swagger UI — run live calls from your browser, no client needed |
| **Simulation Console** | `http://localhost:8000/` (when served) | Aurora GUI CloudHub — visual dashboard for simulation state |

Start with the REST API + Swagger UI. The dashboard is a bonus once you're oriented.

---

## Step 1 — Environment Setup (5 min)

```bash
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# Recommended: use the guided setup target
make onboard
```

`make onboard` will:
- Create a Python 3.11+ virtual environment
- Install core dependencies
- Validate the environment
- Print a live system health report
- Start the dev server with hot-reload

If you prefer manual setup:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Generate required secrets
cp .env.example .env
openssl rand -hex 32   # Run 4 times; paste each output into the 4 required fields in .env
# Required keys: AURORA_SECRET_KEY, JWT_SECRET_KEY, CSRF_SECRET_KEY, WS_AUTH_SECRET

python api/aurora_api.py
```

> **Tip:** The server gracefully degrades — if you don't have AWS/Azure/IBM quantum credentials, those backends are skipped at startup and everything else still works. You'll see this logged on boot.

---

## Step 2 — Your First Real API Call (5 min)

Once the server is running at `http://localhost:8000`, open Swagger UI at `http://localhost:8000/docs`.

### Quickest verification — system health:

```bash
curl http://localhost:8000/api/synergy/health
```

Expected: a JSON object showing registered components, health status, and dependency graph stats. This confirms the core is alive.

### Write a memory entry:

```bash
curl -X POST http://localhost:8000/aumem/store \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Engineer onboarding test entry",
    "context_tag": "onboarding_hello",
    "tier": "active"
  }'
```

Expected: a JSON response with a `memory_id`, `symbolic_hash` (SHA-256), and `tier`. The hash is your audit trail anchor — every operation in Aurora is traceable.

### Check ethics compliance on a payload:

```bash
curl -X POST http://localhost:8000/api/gumas/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "test_eval",
    "context_tag": "onboarding_ethics_check",
    "payload": {"intent": "neutral_observation"}
  }'
```

Expected: ethics field curvature scores across all five dimensions, a pass/fail verdict, and resistance level. This is the system's ethics engine in action — the same one that governs every module operation.

---

## Step 3 — Understand the Module Layout (10 min)

Every module in `modules/` follows this structure:

```
modules/<module_name>/
├── __init__.py      # Module exports
├── core.py          # Business logic
├── api.py           # FastAPI router (routes registered by aurora_api.py on startup)
└── models.py        # Pydantic V2 request/response schemas
```

The main server (`api/aurora_api.py`) registers each module's router at startup. If a module's optional dependencies aren't installed, it's skipped — never crashes the server.

### The 6 modules every engineer should read first:

| Module | Path | Why It Matters |
|--------|------|-----------------|
| AuMemManager | `modules/aumemmanager/` | Everything persists through here; understand tiers first |
| Ethics Field | `modules/ethics_field/` | Hard-veto authority over all operations; read before building anything that writes |
| GUMAS | `modules/gumas/` | Ethics governance layer; drift enforcement |
| AI Core | `modules/ai_core/` | If you touch Claude or GPT integration, start here |
| Nexus | `modules/nexus/` | 58-component integration hub; understand before adding a new module |
| Continuity | `modules/continuity/` | Thread continuity and anchor management; critical for session-aware features |

---

## Step 4 — Key Reference Files (5 min, skim only)

| File | Size | Read When |
|------|------|-----------|
| [`README.md`](./README.md) | 11K | Now — full module table and API group listing |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | 11K | Before your first PR |
| [`CANON_INDEX.md`](./CANON_INDEX.md) | 2K | When you need to find the authoritative source for a concept |
| [`CHANGELOG.md`](./CHANGELOG.md) | 25K | When you need to understand what changed and when |
| [`SECURITY.md`](./SECURITY.md) | 5K | Before touching auth, middleware, or any PII-adjacent code |
| [`.env.example`](./.env.example) | 6K | When configuring optional integrations |
| [`AU_CORE_MASTER_TREE.yaml`](./AU_CORE_MASTER_TREE.yaml) | 6K | When you need the canonical system topology |

---

## Step 5 — Run the Test Suite (5 min)

```bash
# Full suite (253 test files)
pytest

# Fast smoke test — just verify nothing is broken
pytest -m smoke

# Target a specific module
pytest tests/test_quantum_forge_v3.py -v

# Coverage report
pytest --cov=modules --cov=src --cov-report=html
```

All new code requires >90% test coverage. Tests use conventional pytest markers: `unit`, `integration`, `slow`, `smoke`, `critical`, `quantum`, `aurora`, `security`.

---

## Dual-Audience Path Map

Aurora serves both human engineers and AI agents. Here is the canonical entry point for each:

| Audience | First File | Second File | Third File |
|----------|------------|-------------|------------|
| **Human Engineer (you)** | This file | [`README.md`](./README.md) | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| **AI Agent (Copilot, Claude, GPT)** | [`AGENTS.md`](./AGENTS.md) | [`CLAUDE.md`](./CLAUDE.md) | [`AURORA_CONTEXT.json`](./AURORA_CONTEXT.json) |
| **New Module Builder** | [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Any existing module as reference | [`CANON_INDEX.md`](./CANON_INDEX.md) |
| **Security/Auth Work** | [`SECURITY.md`](./SECURITY.md) | `src/middleware/` | `.env.example` |
| **Ethics/GUMAS Work** | `modules/ethics_field/` | `modules/gumas/` | `src/monitoring/` |

---

## Common Gotchas

- **`make setup` vs `make onboard`** — `setup` installs the environment. `onboard` installs + orients + starts the server. Use `onboard` the first time.
- **Missing `.env`** — the server will start but auth and some middleware will fail silently. Always run `cp .env.example .env` and fill in the 4 required keys before `make serve`.
- **Duplicate directories** — `QGIA_Integration/` and `QGIA_integration/` both exist (case difference). The canonical path is `modules/qgia/`. The root-level directories are legacy artifacts.
- **`operations/` vs `ops/`** — both exist. `operations/` is the active directory; `ops/` is legacy. When in doubt, check `CANON_INDEX.md`.
- **Quantum backends** — if you don't have cloud quantum credentials, set `QUANTUM_BACKEND=simulator` in your `.env`. The system will use the local fallback simulator for all quantum routes.
- **Pydantic V2** — all models use `model_config` / `ConfigDict`. Do not use V1 patterns (`class Config`, `max_items`). The linter will catch these.

---

## Make Targets Quick Reference

```bash
make onboard         # First-time setup + orientation + server start
make setup           # Environment setup only
make status          # Check Python/venv/env health
make serve           # Start API server (port 8000)
make serve-dev       # Start with hot-reload
make test            # Full pytest suite
make check           # Scoped lint + full tests (pre-push check)
make health-check    # Repository health report
make security        # safety + bandit scans
make quicksave DESC="..."  # Snapshot development state
make help            # Full target list
```

---

## What to Build Next

Once oriented, the most common first contributions are:

1. **Add a new module** — follow the `core.py / api.py / models.py` pattern; register in `api/aurora_api.py`
2. **Extend an existing route** — find the module's `api.py`, add a route, add a Pydantic model in `models.py`, test it
3. **Add an ethics rule** — modify `modules/ethics_field/core.py`; all five dimensions are weighted and composable
4. **Add a memory operation** — work through `modules/aumemmanager/core.py`; respect the tier boundaries
5. **Write an integration test** — add to `tests/` with the appropriate markers, aim for a real API call via `TestClient`

Welcome to Orion Station.
