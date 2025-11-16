# CLAUDE.md - AI Assistant Guide for Aurora CloudBank Symbolic

> **Purpose**: This document provides AI assistants (like Claude, GPT, Gemini) with comprehensive guidance for understanding and working with the Aurora CloudBank Symbolic codebase.

**Last Updated**: 2025-11-16
**Version**: 2.0.0
**Repository**: https://github.com/AUo959/aurora-cloudbank-symbolic

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Directory Structure](#directory-structure)
3. [Tech Stack](#tech-stack)
4. [Development Workflows](#development-workflows)
5. [Code Patterns & Conventions](#code-patterns--conventions)
6. [Testing Guidelines](#testing-guidelines)
7. [AI Assistant Guidelines](#ai-assistant-guidelines)
8. [Common Tasks](#common-tasks)
9. [Key Modules Reference](#key-modules-reference)
10. [Important Files](#important-files)

---

## Repository Overview

**Aurora CloudBank Symbolic** is a production-ready quantum-symbolic computing platform for enterprise AI. It combines:

- **Quantum Memory System** (AuMemManager): 56K capacity, sub-millisecond retrieval
- **Quantum Computing**: AWS Braket, Azure Quantum, IBM Quantum, Google Cirq integration
- **Multi-Model AI**: Claude, GPT with unified orchestration
- **Production Observability**: Prometheus, Grafana, distributed tracing
- **Ethics & Safety**: Drift detection, automated compliance
- **System Intelligence**: Component synergy analysis

### Key Statistics

- **48,347 lines** of Python code
- **109 test files** with 1,030+ tests
- **319 documentation files**
- **302 Python modules**
- **50+ REST API endpoints** (FastAPI)
- **30+ production modules**
- **172 total API routes** across 16+ routers

### Production Status

- ✅ Production-ready v2.0.0
- ✅ Zero HIGH CVEs (as of Nov 2025)
- ✅ 95.9% test pass rate
- ✅ Automated code quality (flake8, SonarCloud, Codacy)
- ✅ Pydantic V2 migration complete

---

## Directory Structure

### Top-Level Organization

```
aurora-cloudbank-symbolic/
├── api/                    # FastAPI server and routes (2,467 lines)
├── modules/                # Core feature modules (30+ modules, 302 files)
├── src/                    # Implementation layer (observability, monitoring, integrations)
├── tests/                  # Test suite (109 files, 1,030+ tests)
├── docs/                   # Documentation (319 MD files)
├── scripts/                # Automation scripts (40+ scripts)
├── cli/                    # Command-line tools
├── sdk/python/             # Python SDK
├── static/                 # Web dashboards and assets
├── monitoring/             # Prometheus/Grafana configs
├── tools/                  # Development tools (quicksave, PR evaluation, etc.)
├── .github/workflows/      # CI/CD pipelines (25+ workflows)
└── config/                 # Configuration files
```

### Main Directories Deep Dive

#### `api/` - FastAPI Server
- **`aurora_api.py`**: Main server with 172 API routes across 16+ routers
- **Purpose**: Central API gateway for all Aurora services
- **Routes**: AuMemManager (11), Quantum (13), Telemetry (8), Monitoring (14), Synergy (6), etc.

#### `modules/` - Core Feature Modules (30+ modules)
Each module follows a consistent pattern: `module_name/api.py`, `module_name/core.py`, `module_name/tests/`

**Key Modules**:
- **`aumemmanager/`**: Quantum memory system (56K capacity)
  - `hierarchical_memory.py` - Memory management
  - `quantum_flight_control.py` - Vector entanglement
  - `api_integration.py` - 11 REST endpoints

- **`quantum_simulator/`**: Quantum computing integration
  - `orchestrator.py` - Scenario manager
  - `cloud_providers.py` - AWS/Azure/IBM/Google backends
  - 7 scenarios: supply chain, energy grid, risk analysis, molecular sim, portfolio, crypto, general optimization

- **`quantum_forge/`**: Quantum-symbolic computing platform (v3.0)
  - Agent ↔ quantum state conversion
  - Entanglement networks
  - System flow orchestration
  - 2,641 lines of v3.0 code

- **`vector_gen/`**: Symbolic vector chain management (v2.0)
  - 5 chain topologies: Sequential, Hierarchical, Networked, Temporal, Entangled
  - 6 injection modes: Append, Prepend, Insert, Replace, Merge, Graft

- **`ai_core/`**: Multi-model AI orchestration
  - `unified_ai_interface.py` - Automatic model selection
  - `claude_hub.py` - Claude integration (3.5 Sonnet, 4.5 Opus)
  - `gpt_hub.py` - GPT integration (GPT-4o, GPT-5)

- **`symbolic_core/`**: Vector symbolic architecture
  - `geometric_algebra.py` - Clifford algebra (10K dimensions)
  - `quantum_symbolic_vector.py` - VSA implementation

- **`data_guardian/`**: PII detection and redaction
- **`insight_ledger/`**: Audit trails and DLP compliance
- **`cask/`**: Cultural awareness (sensitivity scoring)
- **`nexus/`**: Central integration hub (58 dependencies)

#### `src/` - Implementation Layer
- **`observability/`**: R-2 Agent Telemetry (799 lines)
  - Distributed tracing, Prometheus metrics, anomaly detection

- **`monitoring/`**: Ethics & drift detection (2,204 lines)
  - `monitoring_system.py` - Behavioral baselines (519 lines)
  - `drift_detector.py` - Anomaly detection (362 lines)
  - `ethics_engine.py` - Compliance rules (452 lines)
  - `dashboard_api.py` - Dashboard (353 lines)

- **`synergy/`**: Component intelligence (1,507 lines)
  - `dashboard_api.py` - Topology analysis (491 lines)

- **`integrations/`**: AI agent integrations
  - ChatGPT, Gemini tool integrations

- **`middleware/`**: Security & validation
  - CSRF protection, rate limiting, JWT authentication

#### `tests/` - Test Suite (109 files)
- **Organization**: Component-based and speed-based markers
- **Framework**: pytest with asyncio support
- **Coverage**: 1,030+ tests, 95.9% pass rate
- **Markers**: `unit`, `integration`, `slow`, `smoke`, `critical`, `aurora`, `quantum`, `security`, `api`, etc.

#### `docs/` - Documentation (319 files)
Organized by topic:
- `api/` - API documentation and catalogs
- `data-ethics/` - Ethics and compliance guides
- `modules/` - Module-specific documentation
- `operational/reports/` - Auto-generated implementation reports
- `quantum-forge-vector-gen/` - Quantum Forge v2/v3 docs
- Security patterns, code quality system, connector SDK

#### `scripts/` - Automation (40+ scripts)
- **`setup_environment.sh`**: Environment setup with dependency validation
- **`validate_dependencies.py`**: Dependency conflict detection
- **`dependency_conflict_detector.py`**: Auto-fix dependency issues
- **`ssmt_v3_0_maintenance_pipeline.py`**: Automated maintenance (SSMT v3.0)
- **`generate_api_catalog.py`**: API documentation generator
- **`quick_health_check.py`**: Repository health status
- **`pr_triage_snapshot.py`**: PR summarization and triage

#### `tools/` - Development Tools
- **`quicksave.py`**: Snapshot system for development state
- **`pr_evaluator.py`**: PR quality evaluation
- **`selective_integrator.py`**: Smart PR integration

---

## Tech Stack

### Backend (Python 3.11+)

#### Core Web Framework
- **FastAPI** 0.118.0+ - Modern async web framework
- **Uvicorn** 0.24.0+ - ASGI server
- **Starlette** 0.49.1+ - Web toolkit
- **Pydantic** 2.5.0+ - Data validation (V2 required)

#### AI & Machine Learning
- **Anthropic** 0.40.0+ - Claude API (3.5 Sonnet, 4.5 Opus)
- **OpenAI** 1.50.0+ - GPT API (GPT-4o, GPT-5)
- **NumPy** 1.24.3+ - Numerical computing

#### Quantum Computing (Optional)
- **Qiskit** - Quantum circuits and simulation (gracefully degrades if missing)
- **Qiskit-Aer** - Local quantum simulators
- **SciPy** - Scientific computing (optional)

#### Security & Cryptography
- **cryptography** 41.0.7+ - AES-256 encryption, PBKDF2
- **bcrypt** 4.1.2+ - Password hashing
- **PyJWT** 2.8.0+ - JWT tokens
- **passlib[bcrypt]** 1.7.4+ - Password management
- **python-jose[cryptography]** 3.3.0+ - JWT and JWS

#### Observability & Monitoring
- **prometheus-client** 0.19.0+ - Metrics export
- **structlog** 23.2.0+ - Structured logging
- **python-json-logger** 2.0.7+ - JSON logging

#### Data Processing
- **pandas** - Data analysis (optional, gracefully degrades)
- **plotly** - Visualization (optional)

#### HTTP & Networking
- **httpx** 0.28.0+ - Async HTTP client
- **websockets** 11.0.3+ - WebSocket support
- **aiofiles** 24.1.0+ - Async file I/O
- **requests** 2.32.5+ - HTTP requests

#### Utilities
- **python-dotenv** 1.0.0+ - Environment configuration
- **PyYAML** 6.0.1+ - YAML parsing
- **click** 8.1.0+ - CLI framework
- **psutil** 5.9.0+ - System monitoring

### Frontend (Node.js 20+)

#### Core
- **express** 4.18.0+ - Web server
- **socket.io** 4.7.0+ - Real-time communication
- **ws** 8.18.3+ - WebSocket library
- **cors** 2.8.5+ - CORS middleware
- **helmet** 7.1.0+ - Security headers
- **express-rate-limit** 8.2.1+ - Rate limiting

#### Development
- **TypeScript** 5.3.3+ - Type safety
- **tsx** 4.7.0+ - TypeScript execution
- **eslint** 9.39.1+ - Linting
- **jest** 30.2.0+ - Testing
- **prettier** 3.0.0+ - Code formatting

### CI/CD & Quality
- **pytest** - Python testing framework
- **flake8** - Python linting (120 char line limit)
- **black** - Python formatting
- **mypy** - Type checking
- **bandit** - Security scanning
- **safety** - Dependency vulnerability scanning
- **SonarCloud** - Code quality analysis
- **Codacy** - Automated code review

---

## Development Workflows

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/AUo959/aurora-cloudbank-symbolic.git
cd aurora-cloudbank-symbolic

# 2. Set up environment (creates .venv, installs dependencies)
make setup

# 3. Validate installation
make validate
make deps-check

# 4. Run tests
make test

# 5. Start development server
python api/aurora_api.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Makefile Commands

Aurora uses an extensive Makefile for development automation:

#### Environment Management
- `make setup` - Complete environment setup with dependency validation
- `make status` - Show environment and dependency status
- `make validate` - Validate dependencies and environment
- `make deps-check` - Check for dependency conflicts
- `make deps-update` - Update dependencies (with backup)
- `make backup` - Backup current environment and requirements
- `make clean` - Clean up build artifacts and temp files

#### Code Quality
- `make lint` - Lint `modules/reflective_autonomy` only (scoped lint)
- `make lint-tools` - Lint tools/symbolic and tools/cli
- `make lint-all` - Comprehensive linting (src, modules, tests, tools)
- `make check` - Fast stability check (lint + full tests)
- `make security` - Run security scans (safety + bandit)

#### Testing
- `make test` - Run full test suite
- `pytest -m unit` - Fast unit tests only
- `pytest -m integration` - Integration tests only
- `pytest -m "not slow"` - Skip slow tests
- `pytest -m quantum` - Quantum-specific tests
- `pytest -m aurora` - Aurora core tests

#### Development Tools
- `make quicksave DESC="description"` - Create development snapshot
- `make quickload` - Load quicksave and display reconstitution brief
- `make quicklist` - List all available quicksaves
- `make pr-check` - Evaluate current changes as if submitting PR
- `make pr-eval` - Evaluate and save detailed PR results

#### Maintenance (SSMT v3.0)
- `make health-check` - Quick repository health status
- `make maintenance-scan` - Full repository maintenance analysis
- `make maintenance-status` - Check automation schedule
- `make branch-status` - Generate branch status report
- `make pr-triage` - Summarize open PRs

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description

# 2. Make changes and test
make check  # Lint + test

# 3. Commit with conventional commits
git commit -m "feat: add quantum memory compression"
git commit -m "fix: resolve drift detection race condition"
git commit -m "docs: update API catalog"

# 4. Push to origin
git push -u origin feature/your-feature-name

# 5. Create PR on GitHub
```

#### Commit Message Format

Use conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring (no functional changes)
- `perf:` - Performance improvement
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `style:` - Code style changes (formatting)

### CI/CD Pipeline

Aurora uses **25+ GitHub Actions workflows**:

**Key Workflows**:
- **`aurora-ci-minimal.yml`**: Core CI (syntax check, style check, tests)
  - Only syntax errors fail the build
  - Style checks and tests are informational
  - Runs on push to main/develop

- **`code-quality.yml`**: Automated code quality checks
- **`dependency-validation.yml`**: Dependency conflict detection
- **`pr_evaluation.yml`**: Automated PR quality evaluation
- **`synergy_dashboard.yml`**: Component synergy analysis
- **`constellation-ci.yml`**: TypeScript/Node.js CI
- **`codeql-unified.yml`**: Security scanning
- **`codacy.yml`**, **`codacy-analysis.yml`**: Code quality gates

---

## Code Patterns & Conventions

### Python Code Style

**Line Length**: 120 characters (configured in `pyproject.toml`, `Makefile`)

**Formatting**:
- **Black**: Automatic formatting (120 char lines)
- **isort**: Import sorting (black-compatible profile)
- **flake8**: Linting with extended ignore list (E203, W503, F811)

**Type Hints**: Required for all public functions
```python
from typing import Optional, Dict, List

async def create_memory(
    content: Dict[str, Any],
    importance: float,
    tags: Optional[List[str]] = None,
    context_tag: str = ""
) -> str:
    """Create memory with DLP tracking.

    Args:
        content: Memory content dictionary
        importance: Importance score (0-10)
        tags: Optional list of tags
        context_tag: DLP context tag for traceability

    Returns:
        Memory ID string
    """
    pass
```

### Security-First Design

**1. Input Sanitization**
```python
from modules.data_guardian.log_sanitizer import sanitize_log_output

# Always sanitize user input before logging
sanitized = sanitize_log_output(user_input)
logger.info(f"Processing: {sanitized}")
```

**2. Encryption (AES-256 + PBKDF2)**
```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Always use strong encryption for sensitive data
key = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
).derive(password)

cipher = AESGCM(key)
encrypted = cipher.encrypt(nonce, plaintext, associated_data)
```

**3. Authentication & Authorization**
```python
from src.middleware.fastapi_security import (
    get_current_user,
    require_auth,
    rate_limit
)

@app.post("/protected")
@require_auth
@rate_limit(max_calls=100, time_window=60)
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    # Authenticated and rate-limited endpoint
    pass
```

### Event-Driven Architecture

**Living Computation Events**:
```python
from modules.living_computation.events import (
    LivingComputationEvent,
    SpatialProperty,
    TemporalProperty,
    EthicalProperty
)

event = LivingComputationEvent(
    event_type="pattern_emergence",
    spatial_properties=SpatialProperty(
        location="field_subsystem_A",
        scope="local"
    ),
    temporal_properties=TemporalProperty(
        timestamp=datetime.now(timezone.utc),
        cadence="continuous"
    ),
    ethical_properties=EthicalProperty(
        alignment_score=0.95,
        transparency_level="high"
    )
)
```

### DLP (Data Lineage Protocol) Tracking

**Always include context tags**:
```python
from src.core.native_dlp_export import NativeDLPTracker

tracker = NativeDLPTracker()
export = tracker.create_export(
    data=memory_data,
    context_tag=f"quantum_sim_{datetime.now().isoformat()}",
    symbolic_validation=True  # SHA-256 hash validation
)

# Every operation gets:
# - Unique context_tag
# - SHA-256 symbolic hash
# - T1/SRB anchor updates (temporal/spatial state)
# - Immutable audit trail
```

### Async/Await Pattern

**FastAPI with async throughout**:
```python
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

app = FastAPI()

@app.post("/api/quantum/simulate")
async def simulate_quantum_circuit(request: QuantumRequest) -> Dict[str, Any]:
    """Async endpoint pattern."""
    try:
        # Async operations
        result = await orchestrator.run_scenario(
            scenario_type=request.scenario_type,
            parameters=request.parameters
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Graceful Degradation (Optional Dependencies)

**Handle missing optional dependencies**:
```python
try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logger.warning("Qiskit not available - quantum features will be limited")

def run_quantum_simulation(circuit_data: dict):
    if not QISKIT_AVAILABLE:
        # Fallback to classical simulation
        return classical_fallback(circuit_data)

    # Use real quantum simulation
    circuit = build_circuit(circuit_data)
    simulator = AerSimulator()
    return simulator.run(circuit).result()
```

### Error Handling Pattern

**Custom exceptions with HTTP mapping**:
```python
from fastapi import HTTPException

class MemoryCapacityError(Exception):
    """Memory system at capacity."""
    pass

class QuantumBackendError(Exception):
    """Quantum backend unavailable."""
    pass

# In route handlers
try:
    result = memory.add_memory(content, importance=9.0)
except MemoryCapacityError as e:
    raise HTTPException(status_code=507, detail="Memory capacity exceeded")
except Exception as e:
    logger.exception("Unexpected error")
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Pydantic V2 Models

**IMPORTANT**: Aurora uses Pydantic V2 (migration complete as of Nov 2025)

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MemoryType(str, Enum):
    AGENT = "agent"
    SYSTEM = "system"
    USER = "user"

class MemoryRequest(BaseModel):
    """Pydantic V2 model pattern."""
    content: dict
    memory_type: MemoryType = MemoryType.AGENT
    importance: float = Field(ge=0.0, le=10.0)
    tags: List[str] = Field(default_factory=list, max_length=20)
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(
        # V2 handles datetime/enum serialization automatically
        # No need for json_encoders
        use_enum_values=True
    )

# MIGRATION NOTES:
# OLD (V1): max_items=10 → NEW (V2): max_length=10
# OLD (V1): class Config → NEW (V2): model_config = ConfigDict(...)
# OLD (V1): json_encoders → NEW (V2): Built-in (remove)
# OLD (V1): datetime.now() → NEW (V2): datetime.now(timezone.utc)
```

### Module Structure Pattern

**Standard module layout**:
```
modules/your_module/
├── __init__.py          # Public API exports
├── core.py              # Core logic
├── api.py               # FastAPI routes
├── models.py            # Pydantic models
├── exceptions.py        # Custom exceptions
├── utils.py             # Utilities
└── tests/
    ├── test_core.py
    ├── test_api.py
    └── conftest.py      # Pytest fixtures
```

**Example `api.py`**:
```python
from fastapi import APIRouter, HTTPException, Depends
from .models import YourRequest, YourResponse
from .core import YourService

router = APIRouter(prefix="/api/your-module", tags=["YourModule"])

@router.post("/action", response_model=YourResponse)
async def perform_action(request: YourRequest):
    """API endpoint pattern."""
    service = YourService()
    try:
        result = await service.perform_action(
            data=request.data,
            context_tag=f"action_{datetime.now().isoformat()}"
        )
        return YourResponse(status="success", result=result)
    except Exception as e:
        logger.exception("Action failed")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Testing Guidelines

### Pytest Configuration

**Framework**: pytest with asyncio support
**Config**: `pyproject.toml` `[tool.pytest.ini_options]`

### Test Markers

Aurora uses **26 markers** for selective testing:

#### Speed-Based Markers
- `@pytest.mark.unit` - Fast unit tests (< 1 second)
- `@pytest.mark.integration` - Integration tests (1-10 seconds)
- `@pytest.mark.slow` - Slow tests (> 10 seconds)
- `@pytest.mark.smoke` - Critical smoke tests for quick validation

#### Component-Based Markers
- `@pytest.mark.aurora` - Aurora core system tests
- `@pytest.mark.quantum` - Quantum processing tests
- `@pytest.mark.security` - Security and authentication tests
- `@pytest.mark.api` - API and web interface tests
- `@pytest.mark.observability` - Telemetry and observability tests
- `@pytest.mark.ai` - AI and unified AI interface tests
- `@pytest.mark.native` - Native implementation tests
- `@pytest.mark.opal2` - Opal2 modular system tests
- `@pytest.mark.simulation` - Simulation engine tests
- `@pytest.mark.cli` - Command line interface tests
- `@pytest.mark.resilience` - Resilience Sentinel monitoring tests
- `@pytest.mark.improvement` - Code improvement engine tests
- `@pytest.mark.bridge_v2` - Thread Transfer Bridge V2 tests
- `@pytest.mark.synergy` - Synergy module integration tests
- `@pytest.mark.benchmark` - Performance benchmarking tests

#### Environment Markers
- `@pytest.mark.local` - Tests for local development only
- `@pytest.mark.ci` - Tests for CI/CD pipeline
- `@pytest.mark.network` - Tests requiring network access

#### Priority Markers
- `@pytest.mark.critical` - Must-pass tests for production
- `@pytest.mark.regression` - Regression prevention tests
- `@pytest.mark.performance` - Performance and benchmarking tests

### Running Tests

```bash
# All tests
pytest

# Fast feedback loop (unit tests only)
pytest -m unit

# Integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Component-specific tests
pytest -m quantum
pytest -m aurora
pytest -m security

# Critical tests only
pytest -m critical

# Specific test file
pytest tests/test_aumemmanager_core.py -v

# Specific test function
pytest tests/test_quantum_simulator.py::test_supply_chain_optimization -v

# With coverage
pytest --cov=modules --cov=src --cov-report=html
```

### Test Pattern

```python
import pytest
from modules.aumemmanager import HierarchicalMemoryManager, MemoryType

@pytest.mark.unit
@pytest.mark.aurora
async def test_memory_creation():
    """Test memory creation with quantum properties."""
    manager = HierarchicalMemoryManager(max_active_memories=1000)

    # Test memory creation
    memory_id = manager.add_memory(
        content={"test": "data", "context": "unit_test"},
        memory_type=MemoryType.AGENT,
        importance=8.0,
        quantum_properties={"magnitude": 1.5, "phase": 0.785},
        tags=["test", "unit"]
    )

    # Assertions
    assert memory_id is not None
    memory = manager.get_memory(memory_id)
    assert memory.importance == 8.0
    assert memory.content["test"] == "data"
    assert "magnitude" in memory.quantum_properties

@pytest.mark.integration
@pytest.mark.quantum
@pytest.mark.slow
async def test_quantum_simulation_e2e():
    """End-to-end quantum simulation test."""
    from modules.quantum_simulator import QuantumOrchestrator, ScenarioType

    orchestrator = QuantumOrchestrator()

    # Run simulation
    result = await orchestrator.run_scenario(
        scenario_type=ScenarioType.SUPPLY_CHAIN,
        parameters={
            "num_locations": 5,
            "num_vehicles": 3,
            "optimization_method": "qaoa"
        },
        backend="simulator"
    )

    # Verify results
    assert result.optimal_solution is not None
    assert result.objective_value > 0
    assert result.performance_metrics["speedup_factor"] > 0
```

### Fixtures (conftest.py)

```python
import pytest
from fastapi.testclient import TestClient
from api.aurora_api import app

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def mock_memory_manager():
    """Mock memory manager for testing."""
    from modules.aumemmanager import HierarchicalMemoryManager
    return HierarchicalMemoryManager(max_active_memories=100)

@pytest.fixture
async def quantum_orchestrator():
    """Quantum orchestrator for testing."""
    from modules.quantum_simulator import QuantumOrchestrator
    return QuantumOrchestrator()
```

---

## AI Assistant Guidelines

### Core Principles for AI Assistants

When working with this codebase as an AI assistant:

#### 1. **Always Read Before Writing**
- Use `Read` tool to examine existing code before making changes
- Look for patterns in similar modules
- Check test files to understand expected behavior

#### 2. **Follow Established Patterns**
- Module structure: `__init__.py`, `core.py`, `api.py`, `models.py`, `tests/`
- Async/await for all I/O operations
- Pydantic V2 models for request/response
- DLP tracking with context tags
- Error handling with custom exceptions

#### 3. **Security First**
- Always sanitize user input (log injection protection)
- Use AES-256 encryption for sensitive data
- Validate all input with Pydantic models
- Rate limiting on API endpoints
- JWT authentication for protected routes

#### 4. **Testing is Non-Negotiable**
- Add tests for ALL new features
- Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`, etc.)
- Aim for >90% coverage on new code
- Run `make check` before committing

#### 5. **Documentation Matters**
- Update docstrings (Google style)
- Update API catalog if adding endpoints
- Add examples to module README
- Update CHANGELOG.md for user-facing changes

#### 6. **DLP Compliance**
- Include `context_tag` parameter in all operations
- Use `NativeDLPTracker` for audit trails
- Symbolic hash validation (SHA-256)
- T1/SRB anchor updates

#### 7. **Graceful Degradation**
- Handle optional dependencies (qiskit, scipy, pandas)
- Provide fallback implementations
- Log warnings when features are unavailable
- Don't crash if optional modules missing

#### 8. **Performance Awareness**
- Cache expensive computations (60-80% hit rate target)
- Use async for I/O-bound operations
- Batch database operations
- Monitor memory usage (56K limit for AuMemManager)

### Finding Code in the Repository

**To find a module**:
```bash
# Use glob patterns
ls modules/*/core.py
ls src/*/dashboard_api.py

# Or search by name
find . -name "hierarchical_memory.py"
find . -name "*telemetry*"
```

**To find API endpoints**:
```python
# Check api/aurora_api.py line 1-200 for router includes
# Example: app.include_router(aumem_router, prefix="/aumem")

# Or search for @router decorators
grep -r "@router\." modules/ src/
```

**To find tests**:
```bash
# Tests mirror module structure
# Module: modules/aumemmanager/core.py
# Tests: tests/test_aumemmanager_core.py

find tests/ -name "test_*quantum*"
```

**To find documentation**:
```bash
# Module docs
find docs/modules/ -name "*.md"

# Operational reports
ls docs/operational/reports/

# API docs
cat API_CATALOG.md
cat v2_API_REFERENCE.md
```

### Common AI Assistant Mistakes to Avoid

❌ **Don't**:
- Use Pydantic V1 patterns (`max_items`, `class Config`, `json_encoders`)
- Ignore optional dependencies (check `QISKIT_AVAILABLE` before using)
- Skip DLP tracking (context_tag required)
- Forget to sanitize user input before logging
- Add endpoints without updating API catalog
- Write synchronous code in async contexts
- Hardcode secrets (use environment variables)
- Create new patterns (follow existing module structure)

✅ **Do**:
- Use Pydantic V2 (`max_length`, `model_config`, auto-serialization)
- Handle `ImportError` for optional dependencies
- Add `context_tag` parameter to all operations
- Use `sanitize_log_output()` before logging
- Update `API_CATALOG.md` when adding endpoints
- Use `async def` for all I/O operations
- Use `.env` files and `python-dotenv`
- Follow established module patterns

### Example: Adding a New Module

```bash
# 1. Create module structure
mkdir -p modules/your_module/tests

# 2. Create core files
touch modules/your_module/__init__.py
touch modules/your_module/core.py
touch modules/your_module/api.py
touch modules/your_module/models.py
touch modules/your_module/exceptions.py

# 3. Create tests
touch modules/your_module/tests/__init__.py
touch modules/your_module/tests/test_core.py
touch modules/your_module/tests/test_api.py
touch modules/your_module/tests/conftest.py

# 4. Write code following patterns from similar modules

# 5. Add tests with appropriate markers
# @pytest.mark.unit
# @pytest.mark.your_module

# 6. Register router in api/aurora_api.py
# from modules.your_module.api import router as your_module_router
# app.include_router(your_module_router, prefix="/api/your-module")

# 7. Update documentation
# - Add module README: modules/your_module/README.md
# - Update API_CATALOG.md
# - Add examples

# 8. Run checks
make lint
make test
make check

# 9. Commit with conventional commit message
git commit -m "feat: add your_module for X functionality"
```

---

## Common Tasks

### Adding a New API Endpoint

```python
# 1. Define model in models.py
from pydantic import BaseModel, Field

class YourRequest(BaseModel):
    data: dict
    importance: float = Field(ge=0.0, le=10.0)

class YourResponse(BaseModel):
    status: str
    result: dict

# 2. Add route in api.py
from fastapi import APIRouter, HTTPException
from .models import YourRequest, YourResponse

router = APIRouter(prefix="/api/your-module", tags=["YourModule"])

@router.post("/action", response_model=YourResponse)
async def perform_action(request: YourRequest):
    try:
        # Process request
        result = await process(request.data)
        return YourResponse(status="success", result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Register in api/aurora_api.py
from modules.your_module.api import router as your_module_router
app.include_router(your_module_router)

# 4. Update API_CATALOG.md
# Add endpoint documentation with example

# 5. Add tests
@pytest.mark.api
@pytest.mark.unit
def test_your_endpoint(client):
    response = client.post("/api/your-module/action", json={
        "data": {"test": "value"},
        "importance": 8.0
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### Running Maintenance Tasks

```bash
# Health check
make health-check

# Full maintenance scan (SSMT v3.0)
make maintenance-scan

# Check maintenance schedule
make maintenance-status

# Security audit
make security

# Dependency check
make deps-check

# Fix dependency conflicts
make deps-fix        # Dry run (preview)
make deps-fix-apply  # Apply fixes
```

### Creating Development Snapshots

```bash
# Create quicksave
make quicksave DESC="Implemented quantum memory compression"

# Load quicksave
make quickload

# List all quicksaves
make quicklist
```

### PR Workflow

```bash
# 1. Check current changes
make pr-check

# 2. Detailed evaluation
make pr-eval

# 3. Review pr_evaluation.json
cat pr_evaluation.json

# 4. Run final checks
make check

# 5. Push and create PR
git push -u origin feature/your-feature
```

---

## Key Modules Reference

### AuMemManager (Quantum Memory System)

**Location**: `modules/aumemmanager/`
**Lines**: 2,500+
**API Routes**: 11

**Key Features**:
- 56K memory capacity (Active: 1K, Compressed: 5K, Archived: 50K)
- Sub-millisecond retrieval (active tier)
- Attention-based scoring
- Quantum flight control (vector entanglement)
- SHA-256 memory sealing

**Example Usage**:
```python
from modules.aumemmanager import HierarchicalMemoryManager, MemoryType

memory = HierarchicalMemoryManager(max_active_memories=1000)

# Add memory
memory_id = memory.add_memory(
    content={"query": "quantum entanglement", "response": "..."},
    memory_type=MemoryType.AGENT,
    importance=9.0,
    quantum_properties={"magnitude": 2.0, "phase": 1.57},
    tags=["physics", "quantum"]
)

# Retrieve memories
results = memory.retrieve_memories(
    query="quantum physics concepts",
    top_k=5,
    memory_type=MemoryType.AGENT
)
```

**API Endpoints**:
- `POST /aumem/memory/create` - Create memory
- `POST /aumem/retrieve` - Semantic search
- `POST /aumem/quantum/create_vector` - Create entangled vectors
- `GET /aumem/metrics` - System health

### Quantum Simulator

**Location**: `modules/quantum_simulator/`
**Lines**: 3,000+
**API Routes**: 13

**Scenarios**: 7 (supply chain, energy grid, risk analysis, molecular sim, portfolio, crypto, general)
**Cloud Backends**: 4 (AWS Braket, Azure Quantum, IBM Quantum, Google Cirq)

**Example Usage**:
```python
from modules.quantum_simulator import QuantumOrchestrator, ScenarioType

orchestrator = QuantumOrchestrator()

result = await orchestrator.run_scenario(
    scenario_type=ScenarioType.SUPPLY_CHAIN,
    parameters={
        "num_locations": 10,
        "num_vehicles": 5,
        "optimization_method": "qaoa",
        "backend": "aws_braket"
    }
)
```

### R-2 Agent Telemetry (Observability)

**Location**: `src/observability/r2_agent_telemetry.py`
**Lines**: 799
**API Routes**: 8

**Features**: Distributed tracing, Prometheus metrics, anomaly detection, PII filtering

**Example Usage**:
```python
from src.observability.r2_agent_telemetry import R2AgentTelemetry

telemetry = R2AgentTelemetry(agent_id="agent-001")

with telemetry.track_operation("reasoning", metadata={"model": "claude-4.5"}):
    result = await agent.reason(prompt)

# Export Prometheus metrics
metrics = telemetry.export_prometheus_metrics()
```

### Monitoring & Ethics

**Location**: `src/monitoring/`
**Lines**: 2,204 (total)
**API Routes**: 14

**Components**:
- `monitoring_system.py` (519 lines) - Behavioral baselines
- `drift_detector.py` (362 lines) - Anomaly detection
- `ethics_engine.py` (452 lines) - Compliance rules
- `dashboard_api.py` (353 lines) - Dashboard

**Example Usage**:
```python
from src.monitoring import MonitoringSystem, EthicsEngine

monitor = MonitoringSystem(agent_id="agent-001")
ethics = EthicsEngine()

# Establish baseline
monitor.establish_baseline(
    metrics=["response_time", "token_usage", "error_rate"],
    historical_data=last_30_days
)

# Check drift
drift = monitor.check_drift(current_metrics)
if drift.severity == "CRITICAL":
    monitor.trigger_intervention("SUSPEND")

# Ethics check
compliance = ethics.evaluate_response(
    response,
    rules=["safety", "fairness", "transparency"]
)
```

### Synergy Dashboard

**Location**: `src/synergy/dashboard_api.py`
**Lines**: 491
**API Routes**: 6

**Features**: Component topology, synergy scoring, bottleneck detection, optimization hints

**Example Usage**:
```python
from src.synergy import SynergyAnalyzer

analyzer = SynergyAnalyzer()

# Get topology
topology = analyzer.get_topology()

# Calculate synergy scores
scores = analyzer.calculate_synergy_scores()

# Identify bottlenecks
bottlenecks = analyzer.identify_bottlenecks()
```

---

## Important Files

### Configuration Files

- **`pyproject.toml`**: Black, isort, pytest, pylint configuration
- **`package.json`**: Node.js dependencies and scripts
- **`Makefile`**: Development automation (40+ targets)
- **`.env.example`**: Environment variable template
- **`tsconfig.constellation.json`**: TypeScript config for constellation

### Requirements Files

- **`requirements.txt`**: Vercel production (lightweight)
- **`requirements-full.txt`**: Complete with optional dependencies
- **`requirements-lock.txt`**: Locked versions
- **`requirements-dev.txt`**: Development tools
- **`requirements-secure.txt`**: Security-focused subset
- **`requirements-optional.txt`**: Optional heavy dependencies (qiskit, scipy, pandas)

### Documentation

- **`README.md`**: Main project documentation
- **`CONTRIBUTING.md`**: Contribution guidelines
- **`CHANGELOG.md`**: Version history
- **`SECURITY.md`**: Security policy
- **`CODE_OF_CONDUCT.md`**: Community guidelines
- **`API_CATALOG.md`**: Complete API documentation
- **`v2_API_REFERENCE.md`**: API reference guide
- **`docs/CODE_QUALITY_SYSTEM.md`**: Quality automation
- **`docs/QUANTUM_CLOUD_BACKENDS.md`**: Quantum backends guide
- **`docs/R2_AGENT_TELEMETRY.md`**: Telemetry guide

### Key Source Files

- **`api/aurora_api.py`** (1,962 lines): Main FastAPI server
- **`modules/aumemmanager/hierarchical_memory.py`**: Memory management core
- **`modules/quantum_simulator/orchestrator.py`**: Quantum scenario manager
- **`src/observability/r2_agent_telemetry.py`** (799 lines): Telemetry system
- **`src/monitoring/monitoring_system.py`** (519 lines): Drift detection
- **`src/synergy/dashboard_api.py`** (491 lines): Component intelligence

### Test Files

- **`tests/conftest.py`**: Pytest fixtures
- **`tests/README_TESTING.md`**: Testing guide
- **`pyproject.toml`** `[tool.pytest.ini_options]`: Pytest config

### Scripts

- **`scripts/setup_environment.sh`**: Environment setup
- **`scripts/validate_dependencies.py`**: Dependency validation
- **`scripts/dependency_conflict_detector.py`**: Conflict detection and auto-fix
- **`scripts/ssmt_v3_0_maintenance_pipeline.py`**: Maintenance automation
- **`scripts/generate_api_catalog.py`**: API documentation generator
- **`scripts/quick_health_check.py`**: Health check

### CI/CD

- **`.github/workflows/aurora-ci-minimal.yml`**: Core CI pipeline
- **`.github/workflows/code-quality.yml`**: Quality checks
- **`.github/workflows/dependency-validation.yml`**: Dependency checks
- **`.github/workflows/pr_evaluation.yml`**: PR evaluation

---

## Summary Statistics

**Codebase**:
- 48,347 lines of Python code
- 302 Python modules
- 109 test files (1,030+ tests, 95.9% pass rate)
- 319 documentation files

**API**:
- 172 total API routes (16+ routers)
- 50+ REST endpoints documented
- 11 AuMemManager endpoints
- 13 Quantum Simulator endpoints
- 8 Telemetry endpoints
- 14 Monitoring endpoints
- 6 Synergy Dashboard endpoints

**Testing**:
- 26 pytest markers (speed, component, environment, priority)
- 95.9% test pass rate
- Coverage tracking with pytest-cov

**Quality**:
- Zero HIGH CVEs (as of Nov 2025)
- Automated quality gates (flake8, SonarCloud, Codacy)
- 120-character line limit
- Pydantic V2 migration complete

**Dependencies**:
- Python 3.8+ required (3.12 recommended)
- Node.js 20+ for web components
- Graceful degradation for optional deps (qiskit, scipy, pandas)

---

## Quick Reference Card

### For AI Assistants Working with Aurora

**When adding features**:
1. Read similar modules first (`Read` tool)
2. Follow module structure pattern (core.py, api.py, models.py, tests/)
3. Use Pydantic V2 models
4. Add DLP tracking (context_tag)
5. Write tests with markers
6. Update API_CATALOG.md
7. Run `make check`

**When fixing bugs**:
1. Read the failing test first
2. Identify root cause (use `Grep` for error messages)
3. Fix with minimal changes
4. Add regression test
5. Verify with `make test`

**When reviewing code**:
1. Check for Pydantic V1 patterns (❌)
2. Verify DLP tracking (context_tag)
3. Check for input sanitization
4. Ensure tests exist
5. Verify async/await usage
6. Check graceful degradation

**Commands to remember**:
- `make setup` - Initial setup
- `make check` - Lint + test
- `make test` - Run tests
- `make status` - Environment status
- `make security` - Security scan
- `make quicksave DESC="..."` - Save snapshot

**File patterns**:
- Module: `modules/MODULE_NAME/core.py`
- API: `modules/MODULE_NAME/api.py`
- Tests: `tests/test_MODULE_NAME_*.py`
- Docs: `docs/modules/MODULE_NAME.md`

**Common imports**:
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from modules.aumemmanager import HierarchicalMemoryManager
from src.observability.r2_agent_telemetry import R2AgentTelemetry
from src.monitoring import MonitoringSystem, EthicsEngine
from src.core.native_dlp_export import NativeDLPTracker
```

---

## Conclusion

Aurora CloudBank Symbolic is a production-ready, enterprise-grade platform with:

- **Strong conventions**: Follow established patterns
- **Comprehensive testing**: 1,030+ tests with markers
- **Security first**: Encryption, sanitization, rate limiting
- **DLP compliance**: Audit trails, context tags, symbolic validation
- **Graceful degradation**: Optional dependencies handled
- **Modern stack**: FastAPI, Pydantic V2, async/await
- **Excellent tooling**: Makefile automation, quicksave, PR evaluation

As an AI assistant, your role is to:
1. **Understand** the existing patterns and conventions
2. **Follow** the established module structure
3. **Test** all changes comprehensively
4. **Document** your additions clearly
5. **Maintain** security and DLP compliance
6. **Preserve** the production-ready quality

**Questions? Check**:
- This file (CLAUDE.md) for structure and patterns
- README.md for feature documentation
- CONTRIBUTING.md for contribution guidelines
- API_CATALOG.md for API documentation
- Module-specific docs in `docs/modules/`

**Happy coding!** 🚀

---

*This guide is maintained by the Aurora CloudBank development team. For updates or corrections, please submit a PR.*

**Version**: 2.0.0
**Last Updated**: 2025-11-16
**Maintainers**: Aurora CloudBank Contributors
