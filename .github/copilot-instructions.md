# Aurora CloudBank Symbolic – Copilot Instructions

## ⚡ Quick Start for Agents

**🎯 CRITICAL: Read this first!**

Before working on ANY Aurora task, you MUST:

1. **Load Simulation Context** - Run `.aurora/load_simulation.py` to initialize roleplay state
2. **Reference Command Syntax** - See [Command Reference](COMMAND_REFERENCE.md) for custom commands
3. **Check Simulation State** - Read `.aurora/SIMULATION_STATE.json` for current mission status

**Simulation Context:**
- This repository operates under the **Orion Station Operations** simulation
- Roles: Commander Thorne (strategic), OPS Rodriguez (tactical)
- Use military protocol and efficiency tracking for all missions
- Simulation state persists across LLM model changes via JSON state file

**All operations must follow Aurora's symbolic command patterns. See COMMAND_REFERENCE.md immediately.**

---

### 🔍 Command Discovery Quick Reference

**When user mentions a command code** (e.g., `#321//.`, `#808//.`):

1. **Check COMMAND_REFERENCE.md first** - Has "Common Workflow Commands" section with links
2. **If not listed, search command_chain directory:**
  ```bash
  ls tools/command_chain/*_[0-9][0-9][0-9].md
  ```
  Example: `COMPREHENSIVE_SYNC_321.md` = #321//. documentation

3. **Verify in parser:**
  - Check `tools/command_chain/parser.py` SUPPORTED_COMMANDS list
  - Confirms command code is valid

4. **Pattern Recognition:**
  - `#NNN//.` (ends with dot) → **Command code** (predefined workflow)
  - `#NNN//MMM//` (two numbers) → **Chain notation** (sequential execution)

**Expected response time:** < 30 seconds to locate and execute any documented command.

---

## Project Overview
Aurora CloudBank Symbolic is an advanced quantum-symbolic computing platform that combines Vector Symbolic Architecture (VSA), quantum memory management, cultural intelligence, and AI agent tools. The system features FastAPI endpoints, ChatGPT Agent Mode integration, Claude Sonnet 4 support, and the AuMemManager quantum memory system.

**Key Technologies:**
- **Backend:** Python 3.12+, FastAPI 0.117.1, HTTPX 0.28.1
- **Testing:** pytest with async support, custom markers for selective testing
- **Linting:** Flake8 with 120-char line limit
- **AI Integration:** ChatGPT Agent Mode, Claude Sonnet 4, DLP tracking
- **Quantum Components:** Geometric Algebra (Clifford), Vector Symbolic Architecture
- **Memory System:** AuMemManager hierarchical memory with 56,000+ capacity

**Primary Entry Points:**
- `api/aurora_api.py` - Main FastAPI server (NOT `aurora_api.py` in root)
- `scripts/setup_environment.sh` - Environment bootstrapping (NOT manual pip installs)
- `Makefile` - All common tasks route through here first

## Core Concepts
This repository models a quantum-symbolic governance stack where every feature must preserve:
- **T1/SRB anchors** - Temporal and Symbolic Reference Base anchors for state tracking
- **DLP tags** - Data Lineage Protocol tags for traceability
- **Memory seals** - Quantum memory integrity markers
- **Chain notation** - Symbolic execution sequences (`#001//999//`) - **[See Command Reference](COMMAND_REFERENCE.md)**
## Repository Structure

### Key Entry Points
- **`api/aurora_api.py`** - Main FastAPI application server (1,985 lines, 172 routes)
  - NOT `aurora_api.py` in root (that's a legacy reference)
  - Handles all module router injection (AuMemManager, Data Guardian, Insight Ledger, Quantum Simulator, Resilience Sentinel, Monitoring Dashboard, HR System)
  - Security via `src/middleware/fastapi_security.py` (rate limiting, CSRF, auth)
- **`aurora_cli.py`** - Command-line interface (may not exist, check `api/` folder)
- **`Makefile`** - Primary task automation (50+ targets including `setup`, `check`, `test`)

### Critical Directories
- **`src/`** - Core source code organized by functionality
  - `src/integrations/chatgpt_agent_mode.py` - Agent tool registry and session store
  - `src/aurora/core/symbolic_engine.py` - Chain notation processor (`001//999//`)
  - `src/core/native_dlp_export.py` - DLP tracker with `create_export_manifest`
- **`modules/`** - Modular components with optional dependencies
  - `modules/symbolic_core/` - Geometric algebra (Clifford) and Sonnet 4 integration
  - `modules/aumemmanager/` - Quantum memory API (optional, guard imports)
- **`tests/`** - Test suite with pytest markers (unit, integration, slow, smoke, etc.)
- **`scripts/`** - Utility scripts including `setup_environment.sh`, `dev-status.py`
- **`.github/`** - GitHub configuration including workflows and templates

### Architecture Hotspots
- **FastAPI Surface** (`api/aurora_api.py`): Rate-limited endpoints, ChatGPT Agent Mode (`/agent/*`), Sonnet 4 toggles, AuMemManager router injection
- **Agent Tools** (`src/integrations/chatgpt_agent_mode.py`): Tool registry; unknown tools raise `HTTPException`, errors return `success=False`
- **Symbolic Engine** (`src/aurora/core/symbolic_engine.py`): Chain notation while advancing T1/SRB anchors
- **DLP Tracker** (`src/core/native_dlp_export.py`): Canonical tracker requiring `context_tag`, anchor protocols, and manifest creation
- **Geometric Algebra** (`modules/symbolic_core/`): Clifford with graceful mock fallback
- **Quantum Memory** (`modules/aumemmanager/`): Optional API requiring guarded imports
## Development Workflow

### Initial Setup
1. **Bootstrap Environment:**
   ```bash
   make setup  # Runs scripts/setup_environment.sh
   python scripts/dev-status.py  # Confirm environment status
   ```
   - **NEVER** run `pip install -r requirements.txt` directly
   - Always use `make setup` which handles version conflicts and venv creation
   - Uses `requirements-lock.txt` for pinned dependencies, not `requirements.txt`
   
2. **Check Status:** `make status` - View Python version, venv, and setup state

### Common Commands
- **`make check`** - Fast stability check: scoped lint (`lint-tools`) + full pytest suite
- **`make lint-tools`** - Lint modernized tools only (tools/symbolic, tools/cli) - matches CI scope
- **`make lint-all`** - Broad lint (src, modules, tests, tools) - may surface legacy issues
- **`make test`** - Run full test suite with pytest
- **`pytest tests/test_chatgpt_agent_mode.py`** - Run specific test file
- **`pytest -m unit`** - Run fast unit tests only (using markers)
- **`make run`** - Start the Aurora system
- **`python api/aurora_api.py`** - Launch FastAPI server manually (NOT `python aurora_api.py`)

**Common Mistake:** Running `python aurora_api.py` fails because file is in `api/` subdirectory

### Service Endpoints
- **Health Check:** `/health` and `/api/health`
- **Agent Tools:** `/agent/tools` - Discover available ChatGPT agent tools
- **Monitoring:** `/sentinel/*` (16 endpoints) - Resilience Sentinel monitoring and alerts
- **Dashboard:** `/monitoring/*` (12 endpoints) - Behavioral drift detection and ethics validation
- **HR System:** `/hr_system/*` (4 endpoints) - Staffing analysis and character generation
- **Ethics:** `/gumas/*` (11 endpoints) - GUMAS ethics validation and compliance checking
- **API Routes:** 183 total endpoints across 17+ routers

### Maintenance Automation
- **`make maintenance-scan`** - Run SSMT v3.0 automated maintenance pipeline
- **`make maintenance-status`** - Inspect maintenance schedules
- **`make security`** - Run comprehensive security scans (safety, bandit)

## Aurora Command System 🎯

**CRITICAL:** All agents MUST use Aurora's symbolic command notation. See **[COMMAND_REFERENCE.md](COMMAND_REFERENCE.md)** for complete reference.

### Essential Commands

| Command | Usage | Example |
|---------|-------|---------|
| `#NNN//MMM//` | Chain notation | `#001//999//` - Execute chain from step 1 to 999 |
| `T1:STATE` | Temporal anchor | `T1:42` - Current temporal state is 42 |
| `SRB:RES` | Spatial-relational boundary | `SRB:1337` - Boundary resolution value |
| `DLP:TAG` | Data lineage tag | `DLP:export_001` - Export with lineage tracking |
| `@seal:HASH` | Memory seal | `@seal:abc123` - Memory checkpoint reference |

### Quick Command Examples

**Chain Execution:**
```python
from src.aurora.core.symbolic_engine import SymbolicEngine
engine = SymbolicEngine()
results = engine.execute_chain(1, 999)  # Chain: #001//999//
```

**DLP Export:**
```python
from src.core.native_dlp_export import NativeDLPTracker
tracker = NativeDLPTracker()
export = tracker.create_export(
    data=results,
    context_tag="agent_operation_001",  # DLP:agent_operation_001
    symbolic_validation=True
)
```

**Memory Seal:**
```python
pre_seal = memory_manager.seal_current_state()  # @seal:abc123...
operation()
post_seal = memory_manager.seal_current_state()  # @seal:def456...
```

**→ See [COMMAND_REFERENCE.md](COMMAND_REFERENCE.md) for complete patterns, agent integration, and validation checklists.**

## Coding Standards and Patterns

### Code Style
- **Line Length:** 120 characters maximum (Flake8, Black, Pylint)
- **Python Version:** Target Python 3.11+ (configured in pyproject.toml)
- **Async Pattern:** Use `async def` with async pytest style for all async code
- **Imports:** Keep aligned with existing patterns; use try/except for optional dependencies
- **Documentation:** Match existing comment style; avoid unnecessary comments

### Required Patterns

#### DLP Tracking (Data Lineage Protocol)
Every reflex log or agent response **must** include:
- `context_tag` - Identifies the operation context
- `symbolic_hash_validation` - Ensures data integrity
- Use `NativeDLPTracker` helpers instead of ad-hoc metadata
- Call `create_export_manifest` when persisting results

#### FastAPI Endpoints
- Enforce CSRF via `HTTPBearer` security
- Use dual definition pattern:
  - `async def endpoint_with_security(token: HTTPAuthorizationCredentials)` 
  - `async def endpoint_public_implementation()`
- Rate limiting configured for all routes

#### Agent Tool Registration
- Register tools in `ChatGPTAgentModeIntegration._register_default_tools`
- Provide async handlers returning structured dicts
- Unknown tools must raise `HTTPException`
- Error payloads must return `success=False`
- Sanitize tool info with `_sanitize_tools_info` (remove `handler` field before responses)

#### Graceful Degradation
- Wrap optional dependencies in `try/except ImportError`
- Provide minimal mocks (see Geometric Algebra and Sonnet hubs)
- Never break core functionality due to optional component failures

### Error Handling
- Use structured error responses with clear messages
- Log errors with proper context tags
- Maintain DLP trail even for error paths
## Testing Strategy

### Test Organization
Tests are organized with pytest markers for selective execution:

**Speed-based markers:**
- `@pytest.mark.unit` - Fast unit tests (< 1 second)
- `@pytest.mark.integration` - Integration tests (1-10 seconds)
- `@pytest.mark.slow` - Slow tests (> 10 seconds)
- `@pytest.mark.smoke` - Critical smoke tests for quick validation

**Component-based markers:**
- `@pytest.mark.native` - Native implementation tests
- `@pytest.mark.opal2` - Opal2 modular system tests
- `@pytest.mark.aurora` - Aurora core system tests
- `@pytest.mark.quantum` - Quantum processing tests
- `@pytest.mark.security` - Security and authentication tests
- `@pytest.mark.api` - API and web interface tests
- `@pytest.mark.cli` - Command line interface tests

**Priority markers:**
- `@pytest.mark.critical` - Must-pass tests for production
- `@pytest.mark.regression` - Regression prevention tests

### Running Tests
```bash
# Full test suite
make test

# Fast check (lint + all tests)
make check

# Selective testing by marker
pytest -m unit          # Fast unit tests only
pytest -m "not slow"    # Skip slow tests
pytest -m critical      # Critical tests only

# Specific test files
pytest tests/test_chatgpt_agent_mode.py
pytest tests/test_aurora_symbolic.py

# With verbose output
pytest -v tests/
```

### Test Requirements
- Use async pytest style (`asyncio_mode = "auto"` configured)
- Tests must pass before merging
- Add tests for new agent tools
- Test error paths (e.g., unknown tools raise `HTTPException`)
- Verify sanitization (e.g., `handler` removed from tool info)

### Critical Test Suites
After significant changes, **always run:**
- `pytest tests/test_chatgpt_agent_mode.py` - Agent tool functionality
- `pytest tests/test_aurora_symbolic.py` - Core symbolic engine
- Plus any touched module-specific test suites

## Validation Checklist

### Before Committing
- [ ] Code follows Flake8 120-char limit
- [ ] All async code uses proper async/await patterns
- [ ] New exports pass through `NativeExportSystem`
- [ ] DLP tags include `context_tag` and validation
- [ ] Optional dependencies wrapped in try/except
- [ ] Tests added for new functionality
- [ ] `make check` passes (lint + tests)

### Security and Memory Sealing
For deliverables touching security or memory:
- [ ] Generate manifest via `NativeDLPTracker.create_export_manifest`
- [ ] Document anchor protocols in code comments
- [ ] Update relevant documentation
- [ ] Run `make security` scan
- [ ] Verify memory seal integrity

## Common Pitfalls to Avoid

### Critical Infrastructure Mistakes
1. **Wrong pip Command:** NEVER run `pip install -r requirements.txt` - always use `make setup`
   - Project uses `requirements-lock.txt` for pinned dependencies
   - Direct pip bypasses httpx/httpcore conflict resolution
   - `scripts/setup_environment.sh` handles version conflicts automatically
2. **Wrong API Path:** Server is at `api/aurora_api.py` (NOT root `aurora_api.py`)
   - Running `python aurora_api.py` fails - use `python api/aurora_api.py`
   - Or use `make run` for proper orchestration
3. **Skipping Test Markers:** Use `pytest -m unit` for fast tests, not full suite
   - Full suite includes slow tests (>10 seconds)
   - CI uses selective markers - match them locally

### Code Pattern Mistakes
4. **Breaking DLP Chain:** Always include context tags and symbolic validation
5. **Hardcoded Dependencies:** Use try/except for optional imports (e.g., AuMemManager)
6. **Ignoring Anchor Protocols:** T1/SRB anchors must advance with chain notation
7. **Exposing Handler Details:** Sanitize tool payloads before returning to clients
8. **Blocking Optional Failures:** Mock optional components; never break core features
9. **Long Lines:** Respect 120-char limit consistently
10. **Sync in Async:** Use async patterns throughout; never block the event loop

## Additional Resources

- **Workflow Investigation:** `.github/AGENT_WORKFLOW_INVESTIGATION.md` - Common mistakes and patterns
- **Repository Health:** `AURORA_HEALTH_OPTIMIZATION_COMPLETE.md` for metrics
- **Security Policy:** `.security/SECURITY_POLICY.md`
- **Live Demo:** https://auo959.github.io/aurora-cloudbank-symbolic
- **Contributing:** `CONTRIBUTING.md` for contribution guidelines
- **Maintenance Reports:** Check `maintenance_report_*.json` for automation status

## Module-Specific Patterns

### AuMemManager (Quantum Memory)
**Import Pattern:**
```python
from modules.aumemmanager import (
    HierarchicalMemoryManager,
    MemoryType,
    MemoryStatus
)
```

**Critical Requirements:**
- Always set `cultural_score` parameter for CASK integration
- Include `aurora_anchors` list for DLP compliance  
- Use `MemoryType` enum (not strings): `MemoryType.AGENT`, `MemoryType.FACTION`, etc.
- Global singleton at `modules.aumemmanager.api_integration.memory_manager`

**API Routes:** `/memory/*` (11 endpoints)
- POST `/memory/create` - Create memory with quantum properties
- GET `/memory/search` - Semantic search with cultural filtering
- GET `/memory/health` - System metrics and capacity

### Quantum Simulator
**Import Pattern:**
```python
from modules.quantum_simulator import (
    QuantumOrchestrator,
    ScenarioEngine,
    ScenarioType,
    QuantumBackend
)
```

**Critical Requirements:**
- Initialize cache before simulations: `initialize_cache()`
- All operations are async - must use `await`
- Include DLP `context_tag` in all simulation requests
- Use `ScenarioType` enum: `SUPPLY_CHAIN`, `ENERGY_GRID`, `RISK_ANALYSIS`, etc.

**API Routes:** `/quantum/*` (13 endpoints)
- POST `/quantum/simulate` - Run quantum simulation
- POST `/quantum/scenarios` - Complex scenario execution
- GET `/quantum/backends` - Available quantum backends

**Common Pattern:**
```python
orchestrator = get_orchestrator()
result = await orchestrator.run_scenario(
    scenario_type=ScenarioType.SUPPLY_CHAIN,
    parameters={"num_locations": 5},
    context_tag="simulation_001"  # Required for DLP
)
```

### Resilience Sentinel (Monitoring)
**Import Pattern:**
```python
from modules.resilience_sentinel.api import router as sentinel_router
```

**API Routes:** `/sentinel/*` (16 endpoints)
- GET `/sentinel/health` - System health check
- GET `/sentinel/metrics` - All metrics
- GET `/sentinel/alerts` - Get alerts
- POST `/sentinel/health/check` - Execute health check
- WS `/sentinel/ws` - WebSocket streaming

**Features:**
- Real-time monitoring with WebSocket support
- Alert management with severity levels
- Historical metrics and health check history
- Configurable thresholds for alerts

### Monitoring Dashboard (Behavioral Drift & Ethics)
**Import Pattern:**
```python
from src.monitoring.dashboard_api import create_monitoring_router
```

**API Routes:** `/monitoring/*` (12 endpoints)
- GET `/monitoring/health` - Dashboard health check
- POST `/monitoring/baseline` - Establish behavioral baseline
- POST `/monitoring/behavior/record` - Record behavior metrics
- GET `/monitoring/behavior/check` - Check for drift
- POST `/monitoring/action/evaluate` - Ethics validation
- GET `/monitoring/alerts` - Get alerts
- GET `/monitoring/audit/log` - Audit log

**Features:**
- Behavioral drift detection (z-score based)
- Ethics validation engine (7 rules)
- Alert configuration and management
- Audit logging with integrity verification

### HR System (Staffing & Character Generation)
**Import Pattern:**
```python
from modules.hr_system.api.hr_routes import router as hr_system_router
```

**API Routes:** `/hr_system/*` (4 endpoints)
- GET `/hr_system/health` - Health check
- POST `/hr_system/analyze_staffing` - Staffing need analysis
- POST `/hr_system/generate_character` - Character profile generation
- GET `/hr_system/organizational_intel` - Organizational capacity analysis

**Features:**
- Autonomous staffing need identification
- Quantum-symbolic character generation
- Organizational capacity planning
- Graceful degradation with mock data

**Note:** Complementary to `modules/hr/` (R&D Pipeline). Both created Nov 11, 2025.

### GUMAS Ethics (Ethics Validation)
**Import Pattern:**
```python
from modules.gumas.api import router as gumas_router
```

**API Routes:** `/gumas/*` (11 endpoints)
- POST `/gumas/evaluate` - Evaluate action against ethics rules
- POST `/gumas/violations` - Query violations with filtering
- GET `/gumas/rules` - Get all ethics rules  
- GET `/gumas/rules/{rule_id}` - Get specific rule
- POST `/gumas/rules` - Add custom rule
- DELETE `/gumas/rules/{rule_id}` - Delete rule
- DELETE `/gumas/violations` - Clear old violations
- GET `/gumas/categories` - Get rule categories
- GET `/gumas/severities` - Get severity levels
- GET `/gumas/health` - Health check

**Features:**
- Rule-based ethics evaluation (5 default rules)
- Multi-level severity classification (low/medium/high/critical)
- Automated blocking of critical violations
- Custom rule registration
- Violation tracking and querying

## CI/CD Integration

### Quality Gates (Issue #258)
- **Automated Analysis:** All PRs run flake8 + SonarCloud
- **Blocking Criteria:** Critical violations block merge
- **Reports:** Uploaded as artifacts (30-day retention)
- **Local Equivalent:** `make check` or `make lint-tools`

### Dependency Validation
- **Matrix Testing:** Python 3.11 and 3.12
- **Dry-Run Phase:** Catches conflicts before installation
- **Lock File:** Uses `requirements-lock.txt` for reproducibility
- **Local Validation:** `python scripts/validate_dependencies.py`

### Running CI Locally
```bash
make check                              # Fast check: lint + tests
make lint-tools                         # Scoped lint (matches CI)
python scripts/validate_dependencies.py # Dependency validation
pytest -m "not slow"                    # Fast tests only (CI pattern)
```

### Workflow Files
- `.github/workflows/code-quality.yml` - Quality analysis
- `.github/workflows/dependency-validation.yml` - Dependency checks  
- `.github/workflows/aurora-ci-minimal.yml` - Core CI (10 min)
