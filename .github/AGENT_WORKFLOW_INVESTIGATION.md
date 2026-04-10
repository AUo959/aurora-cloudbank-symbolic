# Agent Workflow Investigation Report
**Date:** 2025-11-05  
**Purpose:** Document common agent mistakes, architectural patterns, and workflow improvements

---

## 1. Common Agent Workflow Mistakes ❌

### A. Dependency Installation Pattern
**CRITICAL MISTAKE:** Agents frequently run `pip install -r requirements.txt` directly

**Why This Fails:**
- Project uses `requirements-lock.txt` for pinned dependencies (not `requirements.txt`)
- Direct pip installs bypass dependency conflict detection
- Misses venv setup and validation checks
- Known httpx/httpcore version conflicts require special handling

**Correct Pattern:**
```bash
make setup  # Runs scripts/setup_environment.sh with conflict resolution
```

**Evidence:**
- `scripts/setup_environment.sh` (227 lines) - Dedicated bootstrapping with version checks
- `scripts/dependency_conflict_detector.py` - Detects and fixes httpx/httpcore conflicts
- `Makefile` setup target orchestrates proper installation sequence
- Multiple CI workflows reference this pattern

---

### B. API Server Entry Point Confusion
**CRITICAL MISTAKE:** Running `python aurora_api.py` from root directory

**Why This Fails:**
- Main API server is at `api/aurora_api.py` (1,615 lines)
- Root `aurora_api.py` references are legacy/documentation artifacts
- Incorrect path causes import errors

**Correct Patterns:**
```bash
python api/aurora_api.py           # Direct execution
make run                           # Via Makefile
uvicorn api.aurora_api:app         # Production
```

**Evidence:**
- `api/aurora_api.py` exists (confirmed via file_search)
- README references both paths inconsistently
- Common failure pattern in error traces

---

### C. Optional Module Import Pattern
**COMMON MISTAKE:** Importing optional modules without guards

**Why This Fails:**
- AuMemManager, Quantum Simulator, Data Guardian are optional
- Imports fail if dependencies not installed
- Breaks core functionality unnecessarily

**Correct Pattern:**
```python
# In api/aurora_api.py (lines 33-40)
try:
    from modules.aumemmanager.api_integration import router as aumemmanager_router
    AUMEMMANAGER_AVAILABLE = True
except ImportError:
    print("AuMemManager not available - some memory features disabled")
    AUMEMMANAGER_AVAILABLE = False

# Later usage (line 117)
if AUMEMMANAGER_AVAILABLE and AUMEMMANAGER_ROUTER:
    app.include_router(AUMEMMANAGER_ROUTER)
```

**Evidence:**
- Consistent pattern across all optional modules in `api/aurora_api.py`
- Similar pattern in `src/integrations/chatgpt_agent_mode.py`
- Graceful degradation principle documented

---

### D. Testing Pattern Misunderstanding
**COMMON MISTAKE:** Running full test suite for quick validation

**Why This Causes Issues:**
- Full test suite includes slow tests (>10 seconds)
- Some tests have external dependencies
- CI uses selective markers

**Correct Patterns:**
```bash
# Fast validation (< 1 minute)
pytest -m unit               # Fast unit tests only
pytest -m "not slow"         # Skip slow tests
make check                   # Scoped lint + full tests

# Comprehensive (CI-equivalent)
make test                    # All tests with markers
pytest -m critical           # Must-pass production tests
```

**Evidence:**
- `pyproject.toml` defines 15+ pytest markers
- `tests/` directory has marker decorations
- CI workflows use selective testing

---

## 2. Undocumented Architectural Patterns 🏗️

### A. Module Router Injection Pattern
**Pattern:** FastAPI dynamically includes optional module routers

**Implementation:**
```python
# api/aurora_api.py structure:
# 1. Try import optional module router
# 2. Set AVAILABLE flag
# 3. Conditionally include_router()
# 4. Log success/failure

# Modules using this pattern:
- AuMemManager (modules/aumemmanager/api_integration.py)
- Data Guardian (modules/data_guardian/api.py)
- Insight Ledger (modules/insight_ledger/api.py)
- Quantum Simulator (modules/quantum_simulator/api.py)
```

**Why This Matters:**
- Agents adding new modules should follow this pattern
- Router must have `prefix` and `tags` for API organization
- No hardcoded dependencies on optional features

---

### B. DLP Tracking Requirement
**Pattern:** All significant operations require DLP (Data Lineage Protocol) tracking

**Required Components:**
```python
from src.core.native_dlp_export import NativeDLPTracker

tracker = NativeDLPTracker()
export = tracker.create_export(
    data=results,
    context_tag="operation_identifier",  # REQUIRED
    symbolic_validation=True             # REQUIRED
)
```

**What Gets Tracked:**
- Agent tool executions
- Chain operations (symbolic engine)
- Memory operations (AuMemManager)
- Quantum simulations
- API responses

**Evidence:**
- `src/core/native_dlp_export.py` (431 lines)
- Referenced in all major operation handlers
- Agent tools enforce DLP in responses

---

### C. Security Middleware Architecture
**Pattern:** Centralized security configuration with graceful fallbacks

**Implementation:**
```python
# src/middleware/fastapi_security.py
from src.middleware.fastapi_security import (
    limiter,         # Rate limiting
    require_auth,    # Authentication
    secure_compare,  # Timing-safe comparison
    security         # HTTPBearer scheme
)

# All endpoints use dual-definition pattern:
@router.post("/endpoint")
async def endpoint_with_security(token: HTTPAuthorizationCredentials = Depends(require_auth)):
    return await endpoint_implementation()

async def endpoint_implementation():
    # Actual logic without security coupling
    pass
```

**Why This Matters:**
- Security is centralized, not scattered
- Testing can bypass security layer
- Rate limiting is automatic for all routes

---

## 3. Module-Specific Patterns 📦

### A. AuMemManager Module

**Import Pattern:**
```python
from modules.aumemmanager import (
    HierarchicalMemoryManager,
    MemoryItem,
    MemoryType,
    MemoryStatus,
    QuantumSymbolicVector,
    AttentionWeight
)
```

**Key Features:**
- 56,000+ memory capacity
- Three-tier architecture (Active/Compressed/Archived)
- Quantum vector flight control
- CASK cultural awareness integration
- DLP tracking built-in

**API Pattern:**
```python
# Router at modules/aumemmanager/api_integration.py
router = APIRouter(prefix="/memory", tags=["AuMemManager"])

# Global singleton pattern
memory_manager = HierarchicalMemoryManager(max_active_memories=1000)

# All endpoints use Pydantic models for validation
```

**Common Mistakes:**
- Forgetting to set `cultural_score` (defaults to 0.0)
- Not specifying `aurora_anchors` for DLP compliance
- Missing `quantum_properties` for vector operations

---

### B. Quantum Simulator Module

**Import Pattern:**
```python
from modules.quantum_simulator import (
    QuantumOrchestrator,
    ScenarioEngine,
    QuantumBackend,
    ScenarioType
)
```

**Key Features:**
- 7 scenario types (supply chain, energy, risk, optimization)
- QAOA and VQE quantum algorithms
- Mock/Simulator/Cloud provider backends
- Intelligent caching (60-80% hit rates)
- WebSocket streaming support

**API Pattern:**
```python
# Router at modules/quantum_simulator/api.py
router = APIRouter(prefix="/quantum", tags=["Quantum Simulator"])

# Orchestrator singleton with DLP integration
orchestrator = get_orchestrator()
dlp_integration = get_dlp_integration()
```

**Common Mistakes:**
- Not initializing cache before first simulation
- Forgetting to await async operations
- Using wrong `ScenarioType` enum values
- Missing DLP context tags in requests

---

## 4. CI/CD Workflow Patterns 🔄

### A. Multi-Workflow Strategy
**Pattern:** Specialized workflows for different concerns

**Active Workflows:**
1. **aurora-ci-minimal.yml** - Core syntax/style checks (10 min timeout)
2. **code-quality.yml** - Flake8 + SonarCloud analysis (Issue #258)
3. **dependency-validation.yml** - Python 3.11/3.12 matrix testing
4. **codeql-unified.yml** - Security analysis
5. **codacy-analysis.yml** - Third-party quality analysis

**Key Patterns:**
- `continue-on-error: true` for non-critical checks
- Artifact uploads for reports (30-day retention)
- Smart PR commenting (updates existing comments)
- Selective path triggers to avoid noise

---

### B. Dependency Validation Workflow
**Critical Pattern:** Two-phase dependency validation

**Phase 1: Dry Run**
```yaml
- name: Test dependency resolution (dry run)
  continue-on-error: true
  run: |
    pip install -r requirements-lock.txt --dry-run --report dependency_report.json
```

**Phase 2: Actual Install + Validation**
```yaml
- name: Install dependencies
  run: pip install -r requirements-lock.txt

- name: Validate dependency compatibility
  run: pip check

- name: Run Aurora dependency validator
  run: python scripts/validate_dependencies.py
```

**Why This Matters:**
- Catches conflicts before actual installation
- Generates reports for debugging
- Tests on multiple Python versions (3.11, 3.12)

---

### C. Code Quality Workflow (Issue #258)
**Pattern:** Automated quality analysis with issue creation

**Flow:**
1. Run flake8 analysis via `src/core/code_quality_analyzer.py`
2. Generate JSON report with severity breakdown
3. On main branch + critical violations → Create GitHub issues
4. On PRs → Smart comment with quality summary
5. Upload artifacts for 30-day retention

**Quality Gates:**
- Critical violations block merge
- High/Medium violations are tracked but don't block
- Low violations are informational

**Evidence:**
- `.github/workflows/code-quality.yml`
- `src/core/code_quality_analyzer.py`
- Issue #258 implementation complete

---

## 5. Recommended Copilot Instructions Updates 📝

### New Sections to Add:

**A. Common Mistakes Section**
```markdown
## Common Pitfalls to Avoid

1. **Breaking DLP Chain:** Always include context tags and symbolic validation
2. **Hardcoded Dependencies:** Use try/except for optional imports (e.g., AuMemManager)
3. **Missing Test Markers:** Tag tests appropriately for selective execution
4. **Ignoring Anchor Protocols:** T1/SRB anchors must advance with chain notation
5. **Exposing Handler Details:** Sanitize tool payloads before returning to clients
6. **Blocking Optional Failures:** Mock optional components; never break core features
7. **Long Lines:** Respect 120-char limit consistently
8. **Sync in Async:** Use async patterns throughout; never block the event loop
9. **Wrong pip Command:** NEVER run `pip install -r requirements.txt` - use `make setup`
10. **Wrong API Path:** Server is `api/aurora_api.py` not root `aurora_api.py`
```

**B. Module Import Patterns Section**
```markdown
### AuMemManager Module

**Import Pattern:**
```python
from modules.aumemmanager import (
    HierarchicalMemoryManager,
    MemoryType,
    MemoryStatus
)
```

**Usage:**
- Always set `cultural_score` for CASK integration
- Include `aurora_anchors` for DLP compliance
- Use `MemoryType` enum, not strings

### Quantum Simulator Module

**Import Pattern:**
```python
from modules.quantum_simulator import (
    QuantumOrchestrator,
    ScenarioEngine,
    ScenarioType
)
```

**Usage:**
- Initialize cache before simulations
- All operations are async (use await)
- Include DLP context tags in requests
```

**C. CI/CD Integration Section**
```markdown
## CI/CD Integration

### Quality Checks (Issue #258)
- All PRs run automated code quality analysis
- Critical violations block merge
- Reports uploaded as artifacts (30-day retention)

### Dependency Validation
- Tests on Python 3.11 and 3.12
- Dry-run phase catches conflicts early
- Uses `requirements-lock.txt` for reproducibility

### Running CI Locally
```bash
make check                    # Fast check (lint + tests)
make lint-tools              # Scoped lint (CI-equivalent)
python scripts/validate_dependencies.py  # Dependency check
```
```

---

## 6. Priority Recommendations 🎯

### High Priority (Immediate):
1. ✅ Add "Common Mistakes" section to copilot instructions
2. ✅ Document module-specific import patterns
3. ✅ Add CI/CD integration guidance
4. ⚠️  Update all README references to use `api/aurora_api.py`

### Medium Priority (Next Sprint):
1. Create troubleshooting flowchart for dependency issues
2. Add video walkthrough of proper setup workflow
3. Document all pytest markers with examples
4. Create module integration checklist

### Low Priority (Future):
1. Automated detection of wrong import patterns
2. Pre-commit hook for DLP tracking
3. Module template generator
4. Interactive setup wizard

---

## 7. Files Referenced 📁

**Scripts:**
- `scripts/setup_environment.sh` - Bootstrapping script
- `scripts/validate_dependencies.py` - Dependency validator
- `scripts/dependency_conflict_detector.py` - Conflict resolution

**Core Files:**
- `api/aurora_api.py` - Main FastAPI server (1,615 lines)
- `src/core/native_dlp_export.py` - DLP tracker (431 lines)
- `src/middleware/fastapi_security.py` - Security middleware
- `Makefile` - Task automation (50+ targets)

**Module Files:**
- `modules/aumemmanager/__init__.py` - Memory manager exports
- `modules/aumemmanager/api_integration.py` - FastAPI router
- `modules/quantum_simulator/__init__.py` - Quantum exports
- `modules/quantum_simulator/api.py` - FastAPI router

**CI/CD:**
- `.github/workflows/code-quality.yml` - Quality analysis
- `.github/workflows/dependency-validation.yml` - Dependency checks
- `.github/workflows/aurora-ci-minimal.yml` - Core CI

**Configuration:**
- `pyproject.toml` - Test markers and Python config
- `requirements-lock.txt` - Pinned dependencies
- `.flake8` - Linting configuration

---

**Investigation completed by:** GitHub Copilot  
**Next steps:** Update copilot instructions with findings
