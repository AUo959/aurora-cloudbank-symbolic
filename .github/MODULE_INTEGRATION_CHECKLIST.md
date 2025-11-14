# Aurora Module Integration Checklist

**Use this checklist when integrating a new module into Aurora CloudBank**

---

## Module Information

- **Module Name:** _________________________
- **Module Path:** `modules/________________________/`
- **Integration Date:** _________________________
- **Developer:** _________________________
- **Issue/PR Reference:** _________________________

---

## Phase 1: Module Structure ✅

### Directory Structure
- [ ] Create module directory: `modules/<module_name>/`
- [ ] Add `__init__.py` with proper exports
- [ ] Create `README.md` with module documentation
- [ ] Add module-specific tests in `tests/modules/test_<module_name>.py`
- [ ] Create API integration file: `api_integration.py` (if API endpoints needed)

### File Organization
- [ ] Core logic in `<module_name>.py` or organized submodules
- [ ] Configuration in `config.py` (if needed)
- [ ] Schemas/models in `schemas.py` or `models.py`
- [ ] Utilities in `utils.py` (if needed)
- [ ] Constants in `constants.py` (if needed)

### Example Structure:
```
modules/<module_name>/
├── __init__.py                 # Exports main classes
├── README.md                   # Module documentation
├── <module_name>.py            # Core implementation
├── api_integration.py          # FastAPI router (optional)
├── schemas.py                  # Pydantic models
├── config.py                   # Configuration
└── utils.py                    # Helper functions
```

---

## Phase 2: Core Implementation ✅

### Module Class/Functions
- [ ] Main class/function implemented with clear docstrings
- [ ] Type hints on all public methods/functions
- [ ] Async/await pattern used consistently (if async operations)
- [ ] Error handling with specific exception types
- [ ] Logging with proper levels (DEBUG, INFO, WARNING, ERROR)

### Aurora Integration Requirements
- [ ] DLP tracking integration (`NativeDLPTracker`)
  ```python
  from src.core.native_dlp_export import NativeDLPTracker
  ```
- [ ] T1/SRB anchor support (if applicable)
  ```python
  from src.aurora.core.symbolic_engine import SymbolicEngine
  ```
- [ ] CASK cultural awareness (if handling user data)
- [ ] Memory sealing support (if stateful)

### Dependencies
- [ ] All dependencies listed in `requirements-lock.txt`
- [ ] Optional dependencies clearly marked
- [ ] No hardcoded dependencies - use try/except imports
- [ ] Graceful degradation for missing optional deps

### Example Import Guard:
```python
try:
    from optional_package import OptionalFeature
    HAS_OPTIONAL = True
except ImportError:
    HAS_OPTIONAL = False
    # Provide mock or graceful failure
```

---

## Phase 3: API Integration ✅

### FastAPI Router (if applicable)
- [ ] Create router with proper prefix and tags
  ```python
  router = APIRouter(prefix="/<module_name>", tags=["<Module Name>"])
  ```
- [ ] Pydantic request/response models defined
- [ ] Security middleware applied (HTTPBearer)
- [ ] Rate limiting configured
- [ ] CSRF protection enabled
- [ ] All endpoints have proper docstrings
- [ ] OpenAPI documentation generated correctly

### Integration into `api/aurora_api.py`
- [ ] Import router with try/except guard
  ```python
  try:
      from modules.<module_name>.api_integration import router as <module_name>_router
      MODULE_AVAILABLE = True
  except ImportError:
      MODULE_AVAILABLE = False
  ```
- [ ] Conditional router inclusion
  ```python
  if MODULE_AVAILABLE and MODULE_ROUTER:
      app.include_router(MODULE_ROUTER)
  ```
- [ ] Success/failure logging added
- [ ] Module availability flag set correctly

### Endpoint Checklist (for each endpoint)
- [ ] Async handler function
- [ ] Security dependency (`Depends(require_auth)` if needed)
- [ ] Request validation (Pydantic models)
- [ ] DLP tracking included
- [ ] Error handling with HTTPException
- [ ] Response model defined
- [ ] Status codes correct (200, 201, 400, 404, 500)

---

## Phase 4: Testing ✅

### Unit Tests
- [ ] Test file created: `tests/test_<module_name>.py`
- [ ] Basic functionality tests (happy path)
- [ ] Error handling tests (edge cases)
- [ ] Mock external dependencies
- [ ] Async tests use `@pytest.mark.asyncio`
- [ ] Test coverage > 80%

### Pytest Markers
- [ ] Add appropriate markers to tests:
  ```python
  @pytest.mark.unit          # Fast tests
  @pytest.mark.integration   # Integration tests
  @pytest.mark.<module_name> # Module-specific marker
  ```
- [ ] Add marker to `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  markers = [
      "<module_name>: <Module Name> tests"
  ]
  ```

### Test Coverage
- [ ] Unit tests for all public methods
- [ ] Integration tests for API endpoints (if applicable)
- [ ] Security tests (authentication, authorization)
- [ ] Performance tests (if performance-critical)
- [ ] DLP tracking validation tests

### Example Test Structure:
```python
import pytest
from modules.<module_name> import MainClass

@pytest.mark.unit
@pytest.mark.<module_name>
class TestMainClass:
    def test_basic_functionality(self):
        obj = MainClass()
        result = obj.method()
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_async_method(self):
        obj = MainClass()
        result = await obj.async_method()
        assert result is not None
```

---

## Phase 5: Documentation ✅

### Module README
- [ ] Overview/purpose of module
- [ ] Installation instructions (if special dependencies)
- [ ] Quick start examples
- [ ] API reference (if applicable)
- [ ] Configuration options
- [ ] Known limitations
- [ ] Contributing guidelines

### Code Documentation
- [ ] Docstrings for all public classes/functions
- [ ] Type hints on all parameters/returns
- [ ] Inline comments for complex logic
- [ ] Example usage in docstrings

### Integration Documentation
- [ ] Update main `README.md` with module reference
- [ ] Add to Architecture section (if significant)
- [ ] Update API documentation
- [ ] Add to copilot instructions (if patterns needed)

### Docstring Template:
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When this exception occurs
    
    Example:
        >>> result = function_name("value", 42)
        >>> print(result)
    """
```

---

## Phase 6: Configuration ✅

### Environment Variables (if needed)
- [ ] Add to `.env.example`
- [ ] Document in module README
- [ ] Validate at startup
- [ ] Provide sensible defaults

### Settings Integration
- [ ] Add to `src/core/config.py` (if using centralized config)
- [ ] Validation with Pydantic
- [ ] Type hints for all settings
- [ ] Documentation in docstrings

### Example Config:
```python
from pydantic import BaseModel, Field

class ModuleConfig(BaseModel):
    enabled: bool = Field(default=True, description="Enable module")
    option_1: str = Field(default="default", description="Option 1")
    option_2: int = Field(default=100, description="Option 2")
```

---

## Phase 7: CI/CD Integration ✅

### Workflow Integration
- [ ] Module tested in CI pipeline
- [ ] Optional dependency handling in workflows
- [ ] Artifact generation (if applicable)
- [ ] Performance benchmarks (if applicable)

### Quality Checks
- [ ] Passes flake8 linting
- [ ] Passes mypy type checking (if used)
- [ ] No critical SonarCloud issues
- [ ] Security scan passes (bandit)

### CI Commands Verification:
```bash
# Run locally before committing
make check              # Lint + tests
make lint-tools         # Scoped lint
pytest -m <module_name> # Module-specific tests
make security           # Security scans
```

---

## Phase 8: Security Review ✅

### Security Checklist
- [ ] No hardcoded secrets/credentials
- [ ] Input validation on all user inputs
- [ ] Output sanitization (prevent XSS)
- [ ] SQL injection prevention (if using DB)
- [ ] CSRF protection on state-changing endpoints
- [ ] Rate limiting configured
- [ ] Authentication required (where appropriate)
- [ ] Authorization checks implemented

### Data Handling
- [ ] PII detection/redaction (if handling user data)
- [ ] Encryption at rest (if storing sensitive data)
- [ ] Encryption in transit (HTTPS)
- [ ] Data retention policies documented
- [ ] GDPR compliance (if applicable)

### Audit Trail
- [ ] DLP tracking on all operations
- [ ] Insight Ledger integration (if significant operations)
- [ ] Error logging (but no sensitive data in logs)
- [ ] Access logging

---

## Phase 9: Performance Optimization ✅

### Performance Checks
- [ ] Benchmarks established
- [ ] No N+1 query problems (if using DB)
- [ ] Caching implemented (where appropriate)
- [ ] Async operations used for I/O
- [ ] Connection pooling (if external services)
- [ ] Resource limits configured

### Monitoring
- [ ] Health check endpoint (if applicable)
- [ ] Metrics collection (Prometheus format)
- [ ] Error rate tracking
- [ ] Performance metrics tracking

---

## Phase 10: Deployment ✅

### Pre-Deployment
- [ ] All tests passing locally
- [ ] All tests passing in CI
- [ ] Documentation complete
- [ ] Peer review completed
- [ ] Security review completed

### Deployment Steps
- [ ] Merge to develop branch first
- [ ] Test in development environment
- [ ] Create release PR to main
- [ ] Update CHANGELOG.md
- [ ] Tag release version
- [ ] Deploy to production

### Post-Deployment
- [ ] Verify health checks passing
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Announce to team
- [ ] Update documentation site (if applicable)

---

## Phase 11: Maintenance Planning ✅

### Ongoing Maintenance
- [ ] Monitoring alerts configured
- [ ] Incident response plan documented
- [ ] Backup/restore procedures (if stateful)
- [ ] Upgrade path documented
- [ ] Deprecation policy defined (if applicable)

### Technical Debt
- [ ] Known issues documented
- [ ] TODO comments tracked
- [ ] Performance improvements identified
- [ ] Code refactoring opportunities noted

---

## Validation Checklist 🎯

Before marking module integration as complete, verify:

- [ ] ✅ Module follows Aurora architectural patterns
- [ ] ✅ DLP tracking implemented correctly
- [ ] ✅ Optional imports guarded properly
- [ ] ✅ All tests passing with appropriate markers
- [ ] ✅ API endpoints secured and documented
- [ ] ✅ CI/CD pipeline passes
- [ ] ✅ Security review completed
- [ ] ✅ Documentation complete
- [ ] ✅ Performance benchmarks met
- [ ] ✅ Peer review approved

---

## Integration Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| **Developer** | _______________ | _________ | _______________ |
| **Tech Lead** | _______________ | _________ | _______________ |
| **Security** | _______________ | _________ | _______________ |
| **DevOps** | _______________ | _________ | _______________ |

---

## Notes & Issues

**Integration Notes:**
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________

**Open Issues:**
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________

**Future Improvements:**
_______________________________________________________________________
_______________________________________________________________________
_______________________________________________________________________

---

**Module Status:** ⬜ Planning | ⬜ In Progress | ⬜ Testing | ⬜ Complete

---

*Template Version: 1.0.0 | Last Updated: 2025-11-05*
