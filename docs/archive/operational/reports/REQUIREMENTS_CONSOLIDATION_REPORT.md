# Requirements Consolidation Report
**Date**: October 7, 2025  
**Status**: ✅ Complete

---

## 🎯 Objective
Consolidate 7+ fragmented requirements files into 3 well-organized, maintainable dependency files.

---

## 📊 Before Consolidation

### Files Found (9 total)
```
requirements.txt              (13 lines)  - Minimal core deps
requirements-lock.txt         (73 lines)  - Locked versions
requirements-test.txt         (1 line)    - Single test dep
requirements-secure.txt       (49 lines)  - Security-focused
requirements_secure.txt       (44 lines)  - Duplicate security file
requirements-nexus.txt        (18 lines)  - Nexus-specific
requirements-optional.txt     (21 lines)  - Optional features
docs/operational/archived/requirements.txt         (16 lines)  - Archived
docs/operational/archived/requirements-test.txt    (0 lines)   - Archived empty
```

### Issues Identified
1. **Duplication**: `requirements-secure.txt` and `requirements_secure.txt` (different content)
2. **Fragmentation**: Dependencies scattered across 7 active files
3. **Inconsistency**: Varying version pinning strategies (exact vs minimum)
4. **Confusion**: Overlapping content between files
5. **Maintenance burden**: Changes required in multiple files

---

## ✅ After Consolidation

### 3 Consolidated Files

#### 1. `requirements.txt` (71 lines) - Core Runtime
**Purpose**: Production-ready dependencies for running Aurora CloudBank Symbolic

**Sections**:
- Core Web Framework (FastAPI, Uvicorn, Pydantic, Starlette)
- HTTP & Networking (httpx, websockets, aiofiles)
- Security & Cryptography (cryptography, bcrypt, JWT, passlib)
- Data Processing & Scientific Computing (numpy, scipy, pandas)
- Configuration & Utilities (dotenv, YAML, click, logging)
- Quantum Computing (Qiskit for Nexus)
- Visualization & Monitoring (plotly, prometheus)
- Database & Caching (Redis)
- Rate Limiting & API Utilities
- System Utilities (requests, urllib3, certifi)

**Strategy**: Minimum version requirements (>=) for flexibility

---

#### 2. `requirements-dev.txt` (50 lines) - Development & Testing
**Purpose**: Tools for development, testing, security scanning, and deployment

**Sections**:
- Testing Framework (pytest, pytest-asyncio, pytest-cov, coverage)
- Code Quality & Formatting (black, flake8, isort, mypy)
- Security Scanning (bandit, safety, pip-audit, semgrep)
- Development Productivity (pre-commit, GitPython, watchfiles)
- Documentation (mkdocs, mkdocs-material, rich, Pygments)
- Deployment & Production Tools (gunicorn)
- Dependency Management (dparse, packaging)

**Usage**: `pip install -r requirements.txt -r requirements-dev.txt`

---

#### 3. `requirements-optional.txt` (68 lines) - Optional Features
**Purpose**: Enhanced features with graceful fallbacks in code

**Sections**:
- Geometric Algebra (clifford - used in symbolic_core with mock fallback)
- Enhanced NLQS (nltk, transformers for NLP features)
- Advanced Visualization (matplotlib, seaborn)
- Jupyter Notebook Support (jupyter, ipykernel, ipywidgets)
- Additional Quantum Backends (cirq, pennylane)
- Performance Optimization (numba, cython)
- Database Extensions (SQLAlchemy, PostgreSQL)
- Message Queue & Async Processing (Celery, Kombu)
- Monitoring & Telemetry (OpenTelemetry, Sentry)

**Usage**: `pip install -r requirements-optional.txt`

---

## 📦 Archived Files

Moved to `.archived_requirements/`:
- `requirements-lock.txt` (locked versions for reference)
- `requirements-test.txt` (superseded by requirements-dev.txt)
- `requirements-secure.txt` (consolidated into main files)
- `requirements_secure.txt` (duplicate, consolidated)
- `requirements-nexus.txt` (Nexus deps now in requirements.txt)

**Rationale**: Keep for historical reference but remove from active use.

---

## 🔧 Migration Guide

### For Existing Developers

**Old Setup**:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
pip install -r requirements-secure.txt
```

**New Setup**:
```bash
# Production/Runtime only
pip install -r requirements.txt

# Development (includes testing, linting, security scanning)
pip install -r requirements.txt -r requirements-dev.txt

# Optional features (Jupyter, enhanced viz, etc.)
pip install -r requirements-optional.txt
```

### For CI/CD Pipelines

**Update your CI configuration**:
```yaml
# Production
- pip install -r requirements.txt

# Testing & Security Scanning
- pip install -r requirements.txt -r requirements-dev.txt
- pytest tests/
- bandit -r src/
- pip-audit
```

---

## 📈 Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Active Files | 7 | 3 | 57% reduction |
| Clarity | Low | High | Clear purpose per file |
| Duplication | High | None | Eliminated |
| Maintainability | Poor | Excellent | Single source of truth |
| Onboarding | Confusing | Clear | 3 simple install commands |

---

## 🔍 Dependency Highlights

### Security Validated
- ✅ httpx >= 0.28.0 (httpcore 1.x compatibility)
- ✅ h11 >= 0.16.0 (security updates)
- ✅ cryptography >= 41.0.7 (latest security patches)
- ✅ requests >= 2.32.5 (security fixes)
- ✅ urllib3 >= 2.5.0 (latest stable)

### Critical Dependencies
- **FastAPI >= 0.104.1**: Core web framework
- **Pydantic >= 2.5.0**: Data validation
- **Qiskit >= 1.4.2**: Quantum computing (Nexus)
- **Redis >= 5.0.0**: Caching and memory management

### Optional with Fallbacks
- **clifford**: Geometric algebra (mock fallback in code)
- **nltk/transformers**: Enhanced NLP (basic NLP without)
- **cirq/pennylane**: Additional quantum backends (Qiskit primary)

---

## 🎯 Next Steps

### Immediate
- [x] Create 3 consolidated requirements files
- [x] Archive old requirements files
- [x] Document migration guide

### Short-term (Next Sprint)
- [ ] Update CI/CD pipelines to use new structure
- [ ] Update documentation (README.md, setup guides)
- [ ] Notify team of consolidation
- [ ] Add requirements.txt to pre-commit validation

### Long-term (Next Quarter)
- [ ] Create requirements-lock.txt from pip freeze after stability
- [ ] Consider Poetry or pip-tools for advanced dependency management
- [ ] Implement automated dependency security scanning
- [ ] Regular quarterly dependency audits

---

## 📖 Documentation References

- **Installation Guide**: See README.md
- **Development Setup**: See CONTRIBUTING.md
- **Security Policy**: See SECURITY.md
- **Archived Files**: `.archived_requirements/`

---

*Generated by Aurora CloudBank Symbolic Requirements Consolidation*  
*Follows Agent Playbook: DLP tagging, T1/SRB anchors preserved*
