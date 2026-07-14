# Aurora CloudBank Symbolic

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-orange)](https://docs.pydantic.dev/)

A quantum-symbolic computing platform for enterprise AI. Combines hierarchical memory management, quantum circuit simulation, multi-model AI orchestration, geometric ethics enforcement, and production observability in a single FastAPI application.

> **New agent or contributor?** Start with [`AURORA_CONTEXT.json`](./AURORA_CONTEXT.json) (machine-readable, source-cited concept map) and [`AGENTS.md`](./AGENTS.md) (bootstrap protocol and rules).

---

## Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Modules](#modules)
- [API](#api)
- [Configuration](#configuration)
- [Testing](#testing)
- [Development](#development)
- [Contributing](#contributing)

---

## Quick Start

**Requirements:** Python 3.11+, pip

```bash
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# Create virtualenv and install dependencies
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set AURORA_SECRET_KEY, JWT_SECRET_KEY, CSRF_SECRET_KEY, WS_AUTH_SECRET
# (generate with: openssl rand -hex 32)

# Start the server
python api/aurora_api.py
```

Server runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

**Optional dependencies** (quantum computing backends, data analysis):

```bash
pip install -r requirements-optional.txt
```

---

## Architecture

```
aurora-cloudbank-symbolic/
├── api/                   # FastAPI application (aurora_api.py, route registration)
├── modules/               # Feature modules (30+ modules)
├── src/                   # Cross-cutting concerns
│   ├── middleware/        # CSRF, rate limiting, JWT, PII filtering, body size
│   ├── monitoring/        # Drift detection, ethics engine, audit logger
│   ├── observability/     # R2 telemetry, distributed tracing, Prometheus metrics
│   ├── synergy/           # Component registry and dependency graph
│   ├── integrations/      # ChatGPT and Gemini agent integrations
│   └── core/              # DLP tracking, request envelope, time utilities
├── tests/                 # 253 test files (pytest)
├── docs/                  # Reference documentation
├── scripts/               # Development and maintenance automation
└── cli/                   # Command-line tools
```

All modules follow a consistent layout: `__init__.py`, `core.py`, `api.py`, `models.py`. The main server (`api/aurora_api.py`) registers each module's router on startup, gracefully skipping any module whose optional dependencies are unavailable.

### Key design decisions

- **Graceful degradation**: Optional modules (quantum cloud backends, Qiskit, scipy) degrade to fallbacks rather than crashing startup. Feature availability is logged at startup.
- **Pydantic V2**: All request/response models use Pydantic V2 (`model_config`, `ConfigDict`). V1 patterns (`class Config`, `max_items`) are not used.
- **DLP tracking**: Every persistent operation carries a `context_tag` and generates a SHA-256 symbolic hash for audit trail continuity.
- **Async throughout**: All I/O-bound operations use `async def`. Blocking calls are isolated.

---

## Modules

### Core platform

| Module | Location | Description |
|---|---|---|
| AuMemManager | `modules/aumemmanager/` | Hierarchical memory: active (1K), compressed (5K), archived (50K) tiers. SHA-256 memory sealing. |
| Quantum Forge | `modules/quantum_forge/` | Quantum-symbolic agent generation (v3.0). Entanglement networks, joy-driven evolution, ethics-aware gates. |
| Quantum Simulator | `modules/quantum_simulator/` | 7 simulation scenarios (supply chain, energy grid, risk analysis, molecular, portfolio, crypto, general). 4 cloud backends: AWS Braket, Azure Quantum, IBM Quantum, Google Cirq. |
| AI Core | `modules/ai_core/` | Unified AI interface over Claude (Sonnet/Opus) and GPT (4o/4.1). Automatic model selection. |
| Symbolic Core | `modules/symbolic_core/` | Geometric algebra (Clifford, 10K dimensions), quantum-symbolic vector architecture. |
| Vector Gen | `modules/vector_gen/` | Symbolic vector chain management. 5 topologies, 6 injection modes. |

### Ethics and safety

| Module | Location | Description |
|---|---|---|
| Ethics Field | `modules/ethics_field/` | Geometric ethics curvature. Five-dimension weighted field (picard_delta_3, thermax_continuity, layer_integrity, collective_welfare, transparency) with hard-zero veto and resistance levels. |
| GUMAS | `modules/gumas/` | Ethics governance, drift threshold enforcement, alignment interventions. |
| Data Guardian | `modules/data_guardian/` | PII detection and log sanitization. |
| Insight Ledger | `modules/insight_ledger/` | Immutable audit trails, DLP compliance. |
| Resilience Sentinel | `modules/resilience_sentinel/` | Health monitoring and anomaly containment. |
| Reflective Autonomy | `modules/reflective_autonomy/` | Autonomous reasoning with self-monitoring. |

### Infrastructure

| Module | Location | Description |
|---|---|---|
| Nexus | `modules/nexus/` | Central integration hub (58 component dependencies). |
| Opal2 | `modules/opal2/` | Modular system with pluggable subsystems. |
| Checkpoint Vault | `modules/checkpoint_vault/` | State checkpointing and restoration. |
| Continuity | `modules/continuity/` | Thread continuity and T1/SRB anchor management. |
| HR System | `modules/hr_system/` | Human resource operations. |
| CASK | `modules/cask/` | Cultural awareness and sensitivity scoring. |
| QGIA | `modules/qgia/` | QGIA agent framework. |
| Crew Agents | `modules/crew_agents/` | Multi-agent crew coordination. |

### Cross-cutting services (src/)

| Component | Location | Description |
|---|---|---|
| Monitoring | `src/monitoring/` | Drift detector (z-score), ethics engine (rule-based), behavioral monitor, audit logger with hash-chain verification. |
| Observability | `src/observability/` | R2 agent telemetry: distributed tracing, Prometheus metrics export, P50/P95/P99 latency, PII filtering. |
| Synergy | `src/synergy/` | Component registry, dependency graph, health status, bottleneck detection. |
| Middleware | `src/middleware/` | CSRF protection, rate limiting (SlowAPI), JWT authentication, PII middleware, body size limits, idempotency. |

---

## API

The server exposes ~339 HTTP routes across 30+ routers. All routes return JSON.

**Access the interactive docs:**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`

**Endpoint groups (selected):**

| Group | Prefix | Description |
|---|---|---|
| AuMemManager | `/aumem/` | Memory CRUD, semantic retrieval, quantum vector creation, metrics |
| Quantum Simulator | `/api/quantum/` | Scenario execution, backend selection, result retrieval |
| Synergy | `/api/synergy/` | Component registry, dependency graph, health |
| Monitoring | `/api/monitoring/` | Drift alerts, ethics compliance, audit logs |
| R2 Telemetry | `/api/telemetry/` | Trace export, Prometheus metrics |
| Auth | `/api/auth/` | JWT token issuance and refresh |
| GUMAS | `/api/gumas/` | Ethics alignment enforcement |
| Sensors | `/api/sensors/` | System sensor array |

**CloudHub GUI routes:**

- `/` and `/simulation-console` — Aurora Simulation Console
- `/synergy-dashboard` — Component Synergy Dashboard UI
- `/legacy/vsa` — Retired Quantum VSA playground notice

See [`docs/reference/API_CATALOG.md`](docs/reference/API_CATALOG.md) for the full route listing.

---

## Configuration

Copy `.env.example` to `.env` and set the required values:

| Variable | Required | Description |
|---|---|---|
| `AURORA_SECRET_KEY` | Yes | 64-hex cryptographic signing key |
| `JWT_SECRET_KEY` | Yes | 64-hex JWT signing key |
| `CSRF_SECRET_KEY` | Yes | 64-hex CSRF HMAC key |
| `WS_AUTH_SECRET` | Yes | 64-hex WebSocket token HMAC key |
| `ALLOWED_CORS_ORIGINS` | No | Comma-separated allowed origins (default: localhost) |
| `RATE_LIMIT_ENABLED` | No | Enable rate limiting (default: `true`) |
| `REDIS_URL` | No | Redis URL for distributed rate limiting |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | JWT access token lifetime (default: 30) |

Generate keys: `openssl rand -hex 32`

For optional AI integrations:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API access |
| `OPENAI_API_KEY` | GPT API access |
| `IBM_QUANTUM_TOKEN` | IBM Quantum backend |
| `AZURE_QUANTUM_*` | Azure Quantum workspace credentials |
| `AWS_*` | AWS Braket credentials |

---

## Testing

```bash
# Full test suite
pytest

# Fast unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# By component
pytest -m quantum
pytest -m aurora
pytest -m security

# Skip slow tests
pytest -m "not slow"

# Specific file
pytest tests/test_quantum_forge_v3.py -v
```

**Test markers:** `unit`, `integration`, `slow`, `smoke`, `critical`, `quantum`, `aurora`, `security`, `api`, `observability`, `ai`, `simulation`, `resilience`, `benchmark`, `regression`

**Coverage:**

```bash
pytest --cov=modules --cov=src --cov-report=html
```

---

## Development

**Makefile targets:**

```bash
make setup          # Create venv, install deps, validate environment
make serve          # Start the API server (uvicorn, port 8000)
make test           # Run full test suite
make lint           # Lint modules/reflective_autonomy (scoped)
make lint-all       # Lint src/, modules/, tests/, tools/
make check          # lint-tools + full tests (fast stability check)
make security       # Run safety + bandit scans
make deps-check     # Dependency conflict detection
make health-check   # Repository health report
make quicksave DESC="..." # Snapshot development state
```

**Commit format** (conventional commits):

```
feat: add quantum memory compression
fix: resolve drift detection race condition
docs: update API reference
refactor: consolidate ethics field evaluators
test: add coverage for joy evolution engine
```

**Branch naming:** `feature/description` or `fix/description`

**Code style:**
- Black, 120-character line limit
- isort (black-compatible profile)
- flake8 with standard ignores (E203, W503)
- Type hints required on all public functions
- No comments explaining what the code does — only the non-obvious why

---

## Contributing

1. Fork the repository and create a feature branch.
2. Follow the module structure pattern (`core.py`, `api.py`, `models.py`, `tests/`).
3. Add tests with appropriate markers. Aim for >90% coverage on new code.
4. Run `make check` before pushing.
5. Open a pull request against `main` with a conventional commit title.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution guide.

---

## License

MIT — see [LICENSE](LICENSE).
