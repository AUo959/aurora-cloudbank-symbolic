# Aurora CloudBank Symbolic – Copilot Instructions

## Project Overview
Aurora CloudBank Symbolic is an advanced quantum-symbolic computing platform that combines Vector Symbolic Architecture (VSA), quantum memory management, cultural intelligence, and AI agent tools. The system features FastAPI endpoints, ChatGPT Agent Mode integration, Claude Sonnet 4 support, and the AuMemManager quantum memory system.

**Key Technologies:**
- **Backend:** Python 3.12+, FastAPI 0.117.1, HTTPX 0.28.1
- **Testing:** pytest with async support, custom markers for selective testing
- **Linting:** Flake8 with 120-char line limit
- **AI Integration:** ChatGPT Agent Mode, Claude Sonnet 4, DLP tracking
- **Quantum Components:** Geometric Algebra (Clifford), Vector Symbolic Architecture
- **Memory System:** AuMemManager hierarchical memory with 56,000+ capacity

## Core Concepts
This repository models a quantum-symbolic governance stack where every feature must preserve:
- **T1/SRB anchors** - Temporal and Symbolic Reference Base anchors for state tracking
- **DLP tags** - Data Lineage Protocol tags for traceability
- **Memory seals** - Quantum memory integrity markers
## Repository Structure

### Key Entry Points
- **`aurora_api.py`** - Main FastAPI application server with 27 API routes (16 core + 11 AuMemManager)
- **`aurora_cli.py`** - Command-line interface for system operations
- **`Makefile`** - Primary development task automation (setup, test, lint, check)

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
- **FastAPI Surface** (`aurora_api.py`): Rate-limited endpoints, ChatGPT Agent Mode (`/agent/*`), Sonnet 4 toggles, AuMemManager router injection
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
2. **Check Status:** `make status` - View Python version, venv, and setup state

### Common Commands
- **`make check`** - Fast stability check: scoped lint (`lint-tools`) + full pytest suite
- **`make lint-tools`** - Lint modernized tools only (tools/symbolic, tools/cli) - matches CI scope
- **`make lint-all`** - Broad lint (src, modules, tests, tools) - may surface legacy issues
- **`make test`** - Run full test suite with pytest
- **`pytest tests/test_chatgpt_agent_mode.py`** - Run specific test file
- **`pytest -m unit`** - Run fast unit tests only (using markers)
- **`make run`** - Start the Aurora system
- **`python aurora_api.py`** - Launch FastAPI server manually

### Service Endpoints
- **Health Check:** `/health` and `/api/health`
- **Agent Tools:** `/agent/tools` - Discover available ChatGPT agent tools
- **API Routes:** 27 total endpoints (16 core + 11 AuMemManager)

### Maintenance Automation
- **`make maintenance-scan`** - Run SSMT v3.0 automated maintenance pipeline
- **`make maintenance-status`** - Inspect maintenance schedules
- **`make security`** - Run comprehensive security scans (safety, bandit)
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

1. **Breaking DLP Chain:** Always include context tags and symbolic validation
2. **Hardcoded Dependencies:** Use try/except for optional imports (e.g., AuMemManager)
3. **Missing Test Markers:** Tag tests appropriately for selective execution
4. **Ignoring Anchor Protocols:** T1/SRB anchors must advance with chain notation
5. **Exposing Handler Details:** Sanitize tool payloads before returning to clients
6. **Blocking Optional Failures:** Mock optional components; never break core features
7. **Long Lines:** Respect 120-char limit consistently
8. **Sync in Async:** Use async patterns throughout; never block the event loop

## Additional Resources

- **Repository Health:** See `AURORA_HEALTH_OPTIMIZATION_COMPLETE.md` for metrics
- **Security Policy:** `.security/SECURITY_POLICY.md`
- **Live Demo:** https://auo959.github.io/aurora-cloudbank-symbolic
- **Contributing:** `CONTRIBUTING.md` for contribution guidelines
- **Maintenance Reports:** Check `maintenance_report_*.json` for automation status
