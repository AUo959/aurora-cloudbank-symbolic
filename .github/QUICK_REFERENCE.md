# Aurora CloudBank Quick Reference Cheat Sheet

**🚀 One-page reference for AI agents and developers**

---

## ⚡ Quick Start (30 seconds)

```bash
make setup              # Bootstrap environment (NEVER use pip install directly!)
python scripts/dev-status.py  # Verify setup
make check              # Fast validation (lint + tests)
python api/aurora_api.py       # Start server
```

**🔗 Visit:** http://localhost:8000/docs (API documentation)

---

## 📁 File Paths (Common Mistakes!)

| Component | ❌ WRONG | ✅ CORRECT |
|-----------|----------|-----------|
| **API Server** | `python aurora_api.py` | `python api/aurora_api.py` |
| **Dependencies** | `pip install -r requirements.txt` | `make setup` |
| **Lock File** | `requirements.txt` | `requirements-lock.txt` |
| **Test Run** | `pytest` (slow!) | `pytest -m unit` (fast) |

---

## 🛠️ Essential Commands

### Setup & Validation
```bash
make setup              # Complete environment setup
make status             # Check environment status
make validate           # Validate dependencies
make check              # Lint + full tests (fast)
```

### Development
```bash
make run                # Start Aurora system
make test               # Full test suite
pytest -m unit          # Fast unit tests (<1s each)
pytest -m "not slow"    # Skip slow tests
pytest -m critical      # Must-pass production tests
```

### Code Quality
```bash
make lint-tools         # Lint tools/ only (matches CI)
make lint-all           # Comprehensive lint (all code)
make security           # Security scans (safety + bandit)
```

### Maintenance
```bash
make maintenance-scan   # Run SSMT v3.0 pipeline
make maintenance-status # Check automation schedules
make backup             # Backup environment
```

---

## 🎯 Module Import Patterns

### AuMemManager (Quantum Memory)
```python
from modules.aumemmanager import (
    HierarchicalMemoryManager,
    MemoryType,
    MemoryStatus
)

# Critical: Always set these!
memory_manager.add_memory(
    content=data,
    memory_type=MemoryType.AGENT,      # Use enum, not string!
    cultural_score=0.8,                # Required for CASK
    aurora_anchors=["T1:42", "SRB:1337"],  # Required for DLP
)
```

### Quantum Simulator
```python
from modules.quantum_simulator import (
    QuantumOrchestrator,
    ScenarioType,
    initialize_cache
)

# Critical: Initialize cache first!
initialize_cache()

# All operations are async
orchestrator = get_orchestrator()
result = await orchestrator.run_scenario(
    scenario_type=ScenarioType.SUPPLY_CHAIN,  # Use enum!
    parameters={"num_locations": 5},
    context_tag="sim_001"                     # Required for DLP!
)
```

### Optional Module Pattern
```python
# Always guard optional imports!
try:
    from modules.aumemmanager import HierarchicalMemoryManager
    HAS_AUMEM = True
except ImportError:
    HAS_AUMEM = False

# Later usage
if HAS_AUMEM:
    memory_manager = HierarchicalMemoryManager()
```

---

## 🔒 Aurora Command Patterns

### Chain Notation
```python
from src.aurora.core.symbolic_engine import SymbolicEngine

engine = SymbolicEngine()
results = engine.execute_chain(1, 999)  # Chain: #001//999//
```

### DLP Tracking (REQUIRED!)
```python
from src.core.native_dlp_export import NativeDLPTracker

tracker = NativeDLPTracker()
export = tracker.create_export(
    data=results,
    context_tag="operation_001",        # REQUIRED!
    symbolic_validation=True            # REQUIRED!
)
```

### Memory Seals
```python
# Seal state before critical operations
pre_seal = memory_manager.seal_current_state()
try:
    critical_operation()
    post_seal = memory_manager.seal_current_state()
except Exception:
    memory_manager.restore_from_seal(pre_seal)  # Restore on error
    raise
```

---

## 🧪 Testing Quick Reference

### Pytest Markers (Use These!)
```bash
# Speed-based
pytest -m unit              # Fast (<1s per test)
pytest -m integration       # Medium (1-10s)
pytest -m slow              # Slow (>10s)
pytest -m "not slow"        # CI pattern

# Component-based
pytest -m aurora            # Aurora core
pytest -m quantum           # Quantum simulator
pytest -m security          # Security tests
pytest -m api               # API endpoints

# Priority
pytest -m critical          # Must-pass production
pytest -m regression        # Regression prevention
```

### Common Test Commands
```bash
# Single file
pytest tests/test_chatgpt_agent_mode.py

# With coverage
pytest tests/ --cov=. --cov-report=html

# Verbose output
pytest -v tests/

# Stop on first failure
pytest -x tests/
```

---

## 🌐 API Endpoints Quick Map

### Core System
- `GET /health` - Health check
- `GET /api/health` - Detailed health status
- `GET /docs` - Interactive API docs
- `GET /metrics` - Prometheus metrics

### Agent Tools
- `GET /agent/tools` - List available tools
- `POST /agent/execute` - Execute agent tool

### AuMemManager (`/memory/*`)
- `POST /memory/create` - Create memory
- `GET /memory/search` - Semantic search
- `GET /memory/health` - Memory system health

### Quantum Simulator (`/quantum/*`)
- `POST /quantum/simulate` - Run simulation
- `POST /quantum/scenarios` - Complex scenarios
- `GET /quantum/backends` - Available backends

### Data Guardian (`/guardian/*`)
- `POST /guardian/detect` - PII detection
- `POST /guardian/redact` - PII redaction

### Insight Ledger (`/ledger/*`)
- `POST /ledger/record` - Record event
- `GET /ledger/query` - Query audit trail

---

## 🚨 Common Mistakes & Fixes

| Problem | Cause | Solution |
|---------|-------|----------|
| **Import errors** | Wrong dependencies | Run `make setup` (not pip) |
| **Module not found** | Wrong path | Check `api/aurora_api.py` path |
| **httpx conflicts** | Direct pip install | Use `make setup` for conflict resolution |
| **Tests too slow** | Running all tests | Use `pytest -m unit` for fast tests |
| **Optional module fails** | Missing try/except | Guard all optional imports |
| **DLP validation fails** | Missing context_tag | Always include DLP tracking |
| **Async errors** | Forgot await | All quantum ops need await |
| **Type errors** | Using strings for enums | Use `MemoryType.AGENT`, not `"agent"` |

---

## 📊 CI/CD Quick Reference

### Local CI Equivalents
```bash
make check              # = aurora-ci-minimal.yml
make lint-tools         # = code-quality.yml (scoped)
python scripts/validate_dependencies.py  # = dependency-validation.yml
```

### Quality Gates
- **Critical violations:** Block merge
- **High violations:** Tracked, don't block
- **Medium/Low:** Informational only

### Workflow Triggers
- Push to `main`/`develop` → Full CI
- PR opened/updated → Quality + Dependency validation
- Manual dispatch → On-demand runs

---

## 🔍 Debugging Quick Tips

### Check Environment
```bash
make status             # Environment overview
python scripts/dev-status.py  # Detailed diagnostics
pip check               # Dependency conflicts
```

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Log Locations
- API logs: stdout (when running server)
- Test logs: `.pytest_cache/`
- Security scans: `.backup/security/`
- Maintenance reports: `maintenance_report_*.json`

---

## 📚 Key Documentation

| Topic | File |
|-------|------|
| **Command Reference** | `.github/COMMAND_REFERENCE.md` |
| **Copilot Instructions** | `.github/copilot-instructions.md` |
| **Workflow Investigation** | `.github/AGENT_WORKFLOW_INVESTIGATION.md` |
| **Contributing** | `CONTRIBUTING.md` |
| **Security** | `.security/SECURITY_POLICY.md` |

---

## 🎓 Learn More

- **Architecture:** `docs/architecture.md`
- **AuMemManager:** `modules/aumemmanager/README.md`
- **Quantum Simulator:** `modules/quantum_simulator/README.md`
- **Thread Bridge v2:** `docs/THREAD_TRANSFER_BRIDGE_v2_PROTOCOL.md`

---

## 🆘 Getting Help

1. **Check diagnostics:** `python scripts/dev-status.py`
2. **Review investigation report:** `.github/AGENT_WORKFLOW_INVESTIGATION.md`
3. **Search issues:** https://github.com/AUo959/aurora-cloudbank-symbolic/issues
4. **Open new issue:** Include environment info + error messages

---

**💡 Pro Tips:**
- Always use `make setup` for environment bootstrap
- Use `pytest -m unit` for fast feedback loops
- Guard all optional imports with try/except
- Include DLP tracking in all operations
- Use enums (not strings) for types
- Check `make status` when things break

**📌 Bookmark this page for instant reference!**

---

*Last updated: 2025-11-05 | Version: 1.0.0*
