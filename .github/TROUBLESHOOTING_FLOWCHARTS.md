# Aurora CloudBank Troubleshooting Flowcharts

**Visual decision trees for common issues**

---

## 📊 Flowchart Index

1. [Setup & Installation Issues](#1-setup--installation-issues)
2. [Import & Dependency Errors](#2-import--dependency-errors)
3. [API Server Startup Problems](#3-api-server-startup-problems)
4. [Test Execution Issues](#4-test-execution-issues)
5. [Module Integration Problems](#5-module-integration-problems)
6. [DLP Tracking Failures](#6-dlp-tracking-failures)
7. [Performance Issues](#7-performance-issues)
8. [Security & Authentication Errors](#8-security--authentication-errors)

---

## 1. Setup & Installation Issues

```
┌─────────────────────────────────┐
│ Installation/Setup Failing?     │
└───────────┬─────────────────────┘
            │
            ▼
    ┌───────────────┐
    │ What command  │
    │ did you use?  │
    └───┬───────┬───┘
        │       │
        ▼       ▼
┌───────────┐ ┌──────────────────┐
│pip install│ │    make setup     │
│-r req.txt │ │                   │
└─────┬─────┘ └────────┬──────────┘
      │                 │
      │  ❌ WRONG      │  ✅ CORRECT
      │                 │
      ▼                 ▼
┌────────────────────┐ ┌────────────────────┐
│ STOP! Use:         │ │ Check output for   │
│ make setup         │ │ errors             │
│                    │ └──────────┬─────────┘
│ This handles:      │            │
│ - venv creation    │            ▼
│ - requirements-    │    ┌──────────────┐
│   lock.txt         │    │ Still fails? │
│ - httpx conflicts  │    └───┬──────┬───┘
│ - validation       │        │      │
└────────────────────┘        │      │
                              ▼      ▼
                        ┌─────────┐ ┌─────────────┐
                        │ Passes? │ │ Check for:  │
                        └────┬────┘ └──────┬──────┘
                             │             │
                             ▼             ▼
                        ┌─────────┐  ┌────────────────┐
                        │ Run:    │  │ - Python 3.12? │
                        │ make    │  │ - Disk space?  │
                        │ status  │  │ - Permissions? │
                        └─────────┘  │ - Network?     │
                                     └────────┬───────┘
                                              │
                                              ▼
                                     ┌────────────────┐
                                     │ Run:           │
                                     │ python scripts/│
                                     │ dev-status.py  │
                                     └────────────────┘
```

**Quick Fix Commands:**
```bash
# Clean slate
make clean
rm -rf .venv

# Fresh install
make setup

# Verify
make status
python scripts/dev-status.py
```

---

## 2. Import & Dependency Errors

```
┌──────────────────────────────────┐
│ Import Error / Module Not Found? │
└────────────┬─────────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Which module? │
     └───┬───────┬───┘
         │       │
         ▼       ▼
 ┌────────────┐ ┌─────────────────┐
 │ Core       │ │ Optional        │
 │ (fastapi,  │ │ (aumemmanager,  │
 │  httpx)    │ │  quantum, etc.) │
 └─────┬──────┘ └────────┬────────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌─────────────────────┐
│ Check:       │   │ Is import guarded?  │
│              │   └──────────┬──────────┘
│ pip check    │              │
│              │         ┌────┴────┐
│ If conflicts:│         │         │
│ make setup   │         ▼         ▼
└──────────────┘   ┌─────────┐ ┌─────────┐
                   │   YES   │ │   NO    │
                   └────┬────┘ └────┬────┘
                        │           │
                        ▼           ▼
                 ┌────────────┐  ┌──────────────┐
                 │ Expected!  │  │ Add guard:   │
                 │ Module is  │  │              │
                 │ optional   │  │ try:         │
                 │            │  │   import...  │
                 │ Feature    │  │   HAS_X=True │
                 │ disabled   │  │ except:      │
                 │ gracefully │  │   HAS_X=False│
                 └────────────┘  └──────────────┘
```

**Diagnostic Commands:**
```bash
# Check dependencies
pip check

# Validate environment
python scripts/validate_dependencies.py

# Check specific module
python -c "import <module_name>"

# See all installed packages
pip list
```

**Common Import Patterns:**
```python
# ✅ Correct: Optional import
try:
    from modules.aumemmanager import HierarchicalMemoryManager
    HAS_AUMEM = True
except ImportError:
    HAS_AUMEM = False
    print("AuMemManager not available - memory features disabled")

# Later usage
if HAS_AUMEM:
    manager = HierarchicalMemoryManager()
```

---

## 3. API Server Startup Problems

```
┌────────────────────────────┐
│ API Server Won't Start?    │
└──────────┬─────────────────┘
           │
           ▼
   ┌───────────────┐
   │ What command? │
   └───┬───────┬───┘
       │       │
       ▼       ▼
┌─────────────┐ ┌──────────────────┐
│python       │ │python api/       │
│aurora_api.py│ │aurora_api.py     │
└──────┬──────┘ └────────┬─────────┘
       │                  │
  ❌ WRONG           ✅ CORRECT
       │                  │
       ▼                  ▼
┌─────────────┐   ┌──────────────┐
│ File in api/│   │ Check error  │
│ subdirectory│   └──────┬───────┘
│             │          │
│ Use:        │          ▼
│ python api/ │   ┌─────────────────┐
│ aurora_api  │   │ Error Type?     │
│ .py         │   └──┬──────┬───┬───┘
└─────────────┘      │      │   │
                     ▼      ▼   ▼
              ┌──────────┐ ┌────────┐ ┌──────────┐
              │Port 8000 │ │Import  │ │Module    │
              │in use?   │ │errors? │ │router    │
              └────┬─────┘ └───┬────┘ │fails?    │
                   │           │      └────┬─────┘
                   ▼           ▼           │
            ┌──────────────┐ ┌────────┐   │
            │lsof -ti:8000│ │See     │   │
            │| xargs kill │ │Import  │   │
            │-9           │ │flowchart│   │
            │             │ └────────┘   │
            │OR:          │              │
            │uvicorn api. │              │
            │aurora_api:  │              │
            │app --port   │              │
            │8001         │              │
            └─────────────┘              │
                                         ▼
                                  ┌──────────────┐
                                  │Check module  │
                                  │available:    │
                                  │              │
                                  │If optional & │
                                  │missing ->    │
                                  │Expected!     │
                                  │              │
                                  │If required & │
                                  │missing ->    │
                                  │make setup    │
                                  └──────────────┘
```

**Diagnostic Commands:**
```bash
# Check if port in use
lsof -i:8000

# Start on different port
python api/aurora_api.py --port 8001
# OR
uvicorn api.aurora_api:app --port 8001

# Check server health
curl http://localhost:8000/health

# View logs
# (stdout when running)
```

---

## 4. Test Execution Issues

```
┌───────────────────────────┐
│ Tests Failing or Slow?    │
└─────────┬─────────────────┘
          │
          ▼
  ┌───────────────┐
  │ What's wrong? │
  └───┬───────┬───┘
      │       │
      ▼       ▼
┌──────────┐ ┌─────────────┐
│Too slow? │ │Actual       │
│          │ │failures?    │
└────┬─────┘ └──────┬──────┘
     │              │
     ▼              ▼
┌──────────────────┐ ┌────────────────┐
│Use markers:      │ │Check error     │
│                  │ │type:           │
│pytest -m unit    │ └────┬───────┬───┘
│(fast <1s)        │      │       │
│                  │      ▼       ▼
│pytest -m         │  ┌────────┐ ┌────────┐
│"not slow"        │  │Import  │ │Async   │
│(skip slow tests) │  │error?  │ │error?  │
│                  │  └───┬────┘ └───┬────┘
│OR specific file: │      │          │
│pytest tests/     │      ▼          ▼
│test_xxx.py       │  ┌─────────┐ ┌──────────┐
└──────────────────┘  │Check    │ │Missing   │
                      │deps &   │ │@pytest   │
                      │imports  │ │.mark     │
                      └─────────┘ │.asyncio? │
                                  │          │
                                  │Add to    │
                                  │async     │
                                  │tests     │
                                  └──────────┘
```

**Test Command Reference:**
```bash
# Fast tests only
pytest -m unit

# Skip slow tests (CI pattern)
pytest -m "not slow"

# Specific module
pytest -m aumemmanager

# Single file
pytest tests/test_chatgpt_agent_mode.py

# With coverage
pytest --cov=. --cov-report=html

# Verbose
pytest -v

# Stop on first failure
pytest -x

# Run last failed
pytest --lf
```

**Marker Reference:**
- `unit` - Fast (<1s)
- `integration` - Medium (1-10s)
- `slow` - Slow (>10s)
- `critical` - Must-pass
- `<module_name>` - Module-specific

---

## 5. Module Integration Problems

```
┌──────────────────────────────┐
│ Module Integration Failing?  │
└────────────┬─────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Where fails?  │
     └───┬───────┬───┘
         │       │
         ▼       ▼
┌─────────────┐ ┌─────────────────┐
│Import stage │ │Runtime (API     │
│             │ │route inclusion) │
└──────┬──────┘ └────────┬────────┘
       │                  │
       ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│Check:           │  │Check:            │
│1. Module path   │  │1. Router defined │
│2. __init__.py   │  │   with prefix/   │
│   exports       │  │   tags           │
│3. Dependencies  │  │2. AVAILABLE flag │
│   installed     │  │   set correctly  │
│4. Import guard  │  │3. Conditional    │
│   in api file   │  │   inclusion      │
└────────┬────────┘  │4. Success log    │
         │           └────────┬─────────┘
         │                    │
         ▼                    ▼
┌──────────────────┐   ┌────────────────┐
│Use checklist:    │   │Check logs:     │
│.github/MODULE_   │   │"✅ <Module>    │
│INTEGRATION_      │   │API routes      │
│CHECKLIST.md      │   │integrated"     │
│                  │   │                │
│Key items:        │   │If "❌" error:  │
│- __init__.py     │   │Check router    │
│- api_integration │   │import guard    │
│- router setup    │   └────────────────┘
└──────────────────┘
```

**Integration Verification:**
```bash
# Check module imports
python -c "from modules.<module_name> import *"

# Check API integration
curl http://localhost:8000/docs
# Look for module endpoints

# Check router available
python -c "from modules.<module_name>.api_integration import router; print(router)"

# Test module endpoint
curl http://localhost:8000/<module_prefix>/health
```

---

## 6. DLP Tracking Failures

```
┌────────────────────────────┐
│ DLP Tracking Not Working?  │
└──────────┬─────────────────┘
           │
           ▼
   ┌───────────────┐
   │ What fails?   │
   └───┬───────┬───┘
       │       │
       ▼       ▼
┌─────────────┐ ┌────────────────┐
│Export fails │ │Validation fails│
└──────┬──────┘ └────────┬───────┘
       │                  │
       ▼                  ▼
┌─────────────────┐  ┌──────────────────┐
│Check required:  │  │Check:            │
│                 │  │1. context_tag    │
│from src.core.   │  │   provided?      │
│native_dlp_      │  │2. symbolic_      │
│export import    │  │   validation     │
│NativeDLPTracker │  │   = True?        │
│                 │  │3. Proper format? │
│tracker =        │  └──────────────────┘
│NativeDLPTracker │
│()               │
│                 │
│export =         │
│tracker.create_  │
│export(          │
│  data=data,     │
│  context_tag=   │
│  "op_001",      │← REQUIRED!
│  symbolic_      │
│  validation=    │
│  True           │← REQUIRED!
│)                │
└─────────────────┘
```

**DLP Template:**
```python
from src.core.native_dlp_export import NativeDLPTracker

# Initialize tracker
tracker = NativeDLPTracker()

# Create export (ALWAYS include these!)
export = tracker.create_export(
    data=results,
    context_tag=f"operation_{operation_type}_{timestamp}",  # ← REQUIRED
    symbolic_validation=True  # ← REQUIRED
)

# Create manifest (for persistence)
manifest = tracker.create_export_manifest(
    export_id=export["export_id"],
    chain_notation="001//999//",
    t1_state=engine.t1.export(),
    srb_state=engine.srb.export()
)
```

---

## 7. Performance Issues

```
┌─────────────────────────┐
│ System Running Slow?    │
└────────┬────────────────┘
         │
         ▼
 ┌───────────────┐
 │ What's slow?  │
 └───┬───────┬───┘
     │       │
     ▼       ▼
┌──────────┐ ┌────────────────┐
│Tests     │ │API responses   │
└────┬─────┘ └────────┬───────┘
     │                │
     ▼                ▼
┌──────────────┐  ┌────────────────────┐
│Use markers:  │  │Check:              │
│              │  │1. Database N+1?    │
│pytest -m     │  │2. Missing caching? │
│unit          │  │3. Blocking I/O in  │
│              │  │   async code?      │
│Only runs     │  │4. Memory leaks?    │
│fast tests    │  └──────────┬─────────┘
│(<1s each)    │             │
└──────────────┘             ▼
                      ┌──────────────────┐
                      │Enable profiling: │
                      │                  │
                      │python -m cProfile│
                      │api/aurora_api.py │
                      │                  │
                      │OR:               │
                      │                  │
                      │py-spy record -o  │
                      │profile.svg --    │
                      │python api/       │
                      │aurora_api.py     │
                      └──────────────────┘
```

**Performance Diagnostics:**
```bash
# Profile code
python -m cProfile -o profile.stats script.py
python -m pstats profile.stats

# Memory profiling
pip install memory_profiler
python -m memory_profiler script.py

# Check resource usage
htop
# OR
top

# Database query profiling
# (if using DB - check for N+1 queries)

# API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/endpoint
```

---

## 8. Security & Authentication Errors

```
┌──────────────────────────────┐
│ Authentication/Security      │
│ Error?                       │
└────────────┬─────────────────┘
             │
             ▼
     ┌───────────────┐
     │ Error type?   │
     └───┬───────┬───┘
         │       │
         ▼       ▼
┌─────────────┐ ┌────────────────┐
│401          │ │403 Forbidden   │
│Unauthorized │ └────────┬───────┘
└──────┬──────┘          │
       │                 ▼
       ▼          ┌──────────────────┐
┌────────────────┐│Check:            │
│Check:          ││1. User has role? │
│1. Token        ││2. Route requires │
│   provided?    ││   specific perm? │
│2. Token valid? ││3. CSRF token?    │
│3. Token format?│└──────────────────┘
│                │
│Header format:  │
│Authorization:  │
│Bearer <token>  │
└────────────────┘
```

**Security Testing:**
```bash
# Test without auth (should fail)
curl http://localhost:8000/protected-endpoint

# Test with auth
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/protected-endpoint

# Check security middleware
grep -r "require_auth" api/

# Run security scans
make security

# Check for vulnerabilities
pip install safety
safety check
```

---

## Quick Decision Matrix

| Symptom | First Check | Quick Fix |
|---------|-------------|-----------|
| **Module not found** | `pip check` | `make setup` |
| **Port already in use** | `lsof -i:8000` | `lsof -ti:8000 \| xargs kill -9` |
| **Tests too slow** | Using markers? | `pytest -m unit` |
| **Import fails (optional)** | Has guard? | Expected - feature disabled |
| **DLP fails** | context_tag set? | Add required parameters |
| **API 404** | Correct path? | Check `/docs` for routes |
| **Server won't start** | Correct file? | `python api/aurora_api.py` |

---

## Emergency Commands

```bash
# Nuclear option - clean everything
make clean
rm -rf .venv
make setup

# Check everything
make status
python scripts/dev-status.py
make check

# Get help
cat .github/QUICK_REFERENCE.md
cat .github/AGENT_WORKFLOW_INVESTIGATION.md
```

---

## Getting More Help

1. **Check Quick Reference:** `.github/QUICK_REFERENCE.md`
2. **Review Investigation:** `.github/AGENT_WORKFLOW_INVESTIGATION.md`
3. **Run Diagnostics:** `python scripts/dev-status.py`
4. **Check Issues:** https://github.com/AUo959/aurora-cloudbank-symbolic/issues
5. **Ask Community:** Open new issue with environment info

---

*Version: 1.0.0 | Last Updated: 2025-11-05*
