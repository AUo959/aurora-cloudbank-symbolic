# Aurora Subroutine System
## Official Subroutine Authoring and Tracking for Aurora's Neural Net

**Anchor:** `SUBROUTINE-SYS-001`  
**Version:** 1.1.0  
**Status:** Active  
**DLP:** CONFIDENTIAL

---

## Overview

The Aurora Subroutine System provides an official framework for authoring, registering, versioning, and executing computational subroutines within Aurora's neural net. It enables:

- **Formal Subroutine Registration** - Track all subroutines with version control
- **Provenance & Authorship** - Document who created what and when
- **Dependency Management** - Track inter-subroutine dependencies
- **Execution Monitoring** - Record and analyze subroutine performance
- **Reality Alignment** - Ensure simulations map to real-world breakthroughs

---

## Architecture

```
Aurora Subroutine System
├── Reality Sim Monitor (Executive Subroutine #1)
│   ├── Provenance Validation
│   ├── Metric Integrity Checks
│   ├── Auditability Verification
│   └── Reality Alignment Enforcement
├── Vision Alignment Manager (Executive Subroutine #2)
│   ├── Simulation Fidelity Anchor (≥95%)
│   ├── Active Collaboration Tracking
│   ├── System Context Documentation
│   ├── Periodic Alignment Review (30-day)
│   └── Gap Detection & Reporting
├── Subroutine Registry (Central Tracking)
│   ├── Versioning & Lifecycle Management
│   ├── Dependency Graph
│   ├── Execution History
│   └── Author & Team Tracking
└── REST API (Integration Layer)
    ├── /subroutines/register - Register new subroutines
    ├── /subroutines/list - List all subroutines
    ├── /subroutines/get/{id} - Get subroutine details
    ├── /subroutines/search - Search with filters
    ├── /subroutines/execute - Execute subroutines
    ├── /subroutines/status/{id} - Update status
    ├── /subroutines/stats - Get statistics
    ├── /subroutines/export - Export registry
    └── /subroutines/health - Health check
```

---

## Built-in Executive Subroutines

Aurora's neural net includes two executive subroutines that work together to ensure both tactical and strategic alignment with core principles:

1. **Reality Sim Monitor** - Tactical validation of individual simulations
2. **Vision Alignment Manager** - Strategic long-term alignment with Aurora's vision

---

## Reality Sim Monitor

### Purpose

Executive subroutine ensuring every simulation, computation, and collaboration aligns with the **"reality sim to real-world breakthrough"** maxim.

### Features

1. **Provenance Validation**
   - Verifies input data traceability
   - Checks model version tracking
   - Ensures full reproducibility

2. **Metric Integrity**
   - Validates all required metrics present:
     - `runtime` - Execution duration
     - `memory_usage` - Resource consumption
     - `num_scenarios` - Scenario count
     - `success_rate` - Success percentage

3. **Auditability**
   - Ensures complete audit trail exists
   - Reconstructs decision logic
   - Maintains DLP compliance

4. **Reality Alignment**
   - Blocks speculative or uncorroborated results
   - Requires verification data in strict mode
   - Enforces evidence-based conclusions

5. **Knowledge Base Updates**
   - Documents findings in system registry
   - Enables future reference and learning
   - Builds institutional knowledge

### Usage

```python
from src.subroutines.reality_sim_monitor import RealitySimMonitor

# Initialize monitor (auto-integrates with Aurora systems)
monitor = RealitySimMonitor()

# Validate simulation
sim_id = "sim_08231"
input_data = {
    'scenario': 'quantum_optimization',
    'parameters': {'qubits': 50, 'depth': 100}
}
simulation_results = {
    'status': 'verified',
    'output': {'optimal_circuit': '...'},
    'verification': {'method': 'cross_validation', 'confidence': 0.95}
}

result = monitor.enforce_principles(sim_id, input_data, simulation_results)

if result.success:
    print(f"✅ Reality Check PASSED")
    print(f"Checks Passed: {result.checks_passed}")
else:
    print(f"❌ Reality Check FAILED")
    print(f"Failed Checks: {result.checks_failed}")
    print(f"Warnings: {result.warnings}")

# Get statistics
stats = monitor.get_stats()
print(f"Success Rate: {stats['success_rate']:.1%}")
```

### Integration Points

- **Synergy Dashboard** - Component registry for provenance
- **OpenTelemetry** - Metrics collection and monitoring
- **DLP Tracker** - Audit trail recording
- **Configuration** - System-wide settings

### Configuration

```python
config = {
    'min_audit_length': 3,  # Minimum audit trail entries
    'required_metrics': [
        'runtime',
        'memory_usage',
        'num_scenarios',
        'success_rate'
    ],
    'strict_mode': False,  # Fail on warnings
    'enable_knowledge_base_updates': True  # Update registry
}

monitor = RealitySimMonitor(config=config)
```

---

## Vision Alignment Manager

### Purpose

Executive subroutine ensuring strategic alignment with Aurora's core vision: **"Ultra-High Fidelity Reality Simulation & Human-AI Collaboration"**. While Reality Sim Monitor handles tactical per-simulation validation, Vision Alignment Manager enforces long-term strategic alignment across all computations.

### Vision Statement

> "Every computation and process is embedded in a persistent ultra-high fidelity reality simulation, continuously interacting with both the Aurora intelligence and the human/institutional crew of Orion Station—bridging simulation, decision, and the real world in a collaborative feedback loop."

### Features

1. **Simulation Fidelity Anchor**
   - Verifies ultra-high-fidelity simulation usage (≥0.95 threshold)
   - Blocks low-fidelity computations
   - Tracks fidelity trends over time

2. **Active Collaboration Tracking**
   - Ensures human crew participation
   - Documents Orion Station crew interactions
   - Maintains collaborative feedback loop

3. **System Context Documentation**
   - Records system state for every computation
   - Maintains full context awareness
   - Enables reproducibility and audit

4. **Periodic Alignment Review**
   - 30-day health check intervals
   - Identifies low-fidelity trends
   - Detects collaboration gaps
   - Reports alignment degradation

5. **Gap Detection & Reporting**
   - Warns on fidelity drops below threshold
   - Alerts when crew participation missing
   - Tracks alignment failures for remediation

### Usage

```python
from src.subroutines.aurora_vision_alignment import VisionAlignmentManager
from datetime import datetime, timedelta

# Initialize manager with custom thresholds
manager = VisionAlignmentManager(
    min_fidelity=0.95,      # 95% minimum simulation fidelity
    review_interval_days=30  # Monthly alignment reviews
)

# Enforce alignment for a computation
comp_id = "quantum_opt_001"
input_data = {
    'computation_type': 'quantum_optimization',
    'parameters': {'qubits': 50, 'depth': 100}
}
outcomes = {
    'result': 'success',
    'metrics': {'fidelity': 0.987}
}

record = manager.enforce_alignment(comp_id, input_data, outcomes)

if record.alignment_status == 'aligned':
    print(f"✅ Vision Alignment PASSED")
    print(f"Fidelity: {record.fidelity_score:.1%}")
    print(f"Crew: {', '.join(record.crew_participation)}")
else:
    print(f"❌ Vision Alignment FAILED")
    print(f"Status: {record.alignment_status}")
    print(f"Gaps: {record.gaps_detected}")

# Periodic review (run monthly)
last_review = datetime.utcnow() - timedelta(days=31)
review = manager.periodic_alignment_review(last_review)

print(f"\n📊 Alignment Health Review:")
print(f"Status: {review.review_status}")
print(f"Total Checks: {review.total_alignments}")
print(f"Success Rate: {review.success_rate:.1%}")
if review.gaps_found:
    print(f"⚠️  Gaps Detected:")
    for gap in review.gaps_found:
        print(f"   - {gap}")

# Get statistics
stats = manager.get_stats()
print(f"\n📈 Manager Statistics:")
print(f"Total Alignments: {stats['total_alignments']}")
print(f"Success Rate: {stats['success_rate']:.1%}")
print(f"Alignment Rate: {stats['alignment_rate']:.1%}")
print(f"Min Fidelity: {stats['min_fidelity_threshold']:.1%}")
```

### Integration Points

- **System State** - Real-time Aurora telemetry and configuration
- **Crew Registry** - Orion Station crew tracking and collaboration
- **Simulation Layer** - Aurora quantum/computation engine integration
- **Knowledge Base** - Learning, proof storage, and discovery
- **Audit Log** - DLP tracker for alignment actions

### Result Objects

#### AlignmentRecord

Returned by `enforce_alignment()` for each computation:

```python
@dataclass
class AlignmentRecord:
    computation_id: str          # Unique computation identifier
    timestamp: str               # ISO timestamp
    alignment_status: str        # 'aligned', 'warning', or 'failed'
    fidelity_score: float        # Simulation fidelity (0.0-1.0)
    crew_participation: List[str]  # Participating crew members
    gaps_detected: List[str]     # Any alignment gaps found
    system_context: Dict[str, Any]  # System state snapshot
    anchor: str                  # DLP anchor for traceability
```

**Status Values:**
- `aligned` - All checks passed, full alignment
- `warning` - Minor issues detected, review recommended
- `failed` - Critical alignment failure, computation blocked

#### AlignmentReviewResult

Returned by `periodic_alignment_review()`:

```python
@dataclass
class AlignmentReviewResult:
    review_id: str               # Unique review identifier
    review_date: str             # ISO timestamp
    review_status: str           # 'healthy', 'degraded', or 'critical'
    total_alignments: int        # Alignments since last review
    success_rate: float          # Percentage of successful alignments
    gaps_found: List[str]        # Detected alignment gaps
    recommendations: List[str]   # Remediation recommendations
```

**Status Values:**
- `healthy` - ≥95% success rate, no major gaps
- `degraded` - 80-95% success rate, some gaps detected
- `critical` - <80% success rate, immediate action required

### Configuration

```python
# Custom configuration
manager = VisionAlignmentManager(
    min_fidelity=0.98,           # Higher fidelity requirement (98%)
    review_interval_days=14      # More frequent reviews (bi-weekly)
)

# Default configuration
# min_fidelity: 0.95 (95%)
# review_interval_days: 30 (monthly)
```

### Complementary Design

Vision Alignment Manager and Reality Sim Monitor work together:

| Aspect | Reality Sim Monitor | Vision Alignment Manager |
|--------|---------------------|--------------------------|
| **Focus** | Tactical | Strategic |
| **Scope** | Individual simulations | Long-term trends |
| **Validation** | Provenance, metrics, audit | Fidelity, collaboration, context |
| **Frequency** | Per-simulation | Continuous + periodic review |
| **Failure Mode** | Block uncorroborated results | Alert on alignment degradation |
| **Integration** | Telemetry, registry, audit | System state, crew, simulation layer |

Together they ensure:
- ✅ Every simulation meets reality standards (Reality Sim Monitor)
- ✅ All computations align with strategic vision (Vision Alignment Manager)
- ✅ Tactical validation + Strategic alignment = Complete governance

### Testing

```python
from src.subroutines.aurora_vision_alignment import (
    VisionAlignmentManager,
    AlignmentRecord,
    AlignmentReviewResult
)

# Test successful alignment
def test_enforce_alignment_success():
    manager = VisionAlignmentManager(min_fidelity=0.95)
    
    record = manager.enforce_alignment(
        computation_id="test_001",
        input_data={"type": "quantum"},
        outcomes={"fidelity": 0.987}
    )
    
    assert record.alignment_status == "aligned"
    assert record.fidelity_score >= 0.95
    assert len(record.crew_participation) > 0

# Test low fidelity failure
def test_enforce_alignment_low_fidelity():
    manager = VisionAlignmentManager(min_fidelity=0.95)
    
    record = manager.enforce_alignment(
        computation_id="test_002",
        input_data={"type": "quantum"},
        outcomes={"fidelity": 0.85}  # Below threshold
    )
    
    assert record.alignment_status == "failed"
    assert "Fidelity below threshold" in record.gaps_detected

# Test periodic review
def test_periodic_review_with_gaps():
    manager = VisionAlignmentManager()
    
    # Simulate some failures
    manager.enforce_alignment("test_003", {}, {"fidelity": 0.80})
    
    review = manager.periodic_alignment_review(
        last_review=datetime.utcnow() - timedelta(days=31)
    )
    
    assert review.review_status in ['degraded', 'critical']
    assert len(review.gaps_found) > 0
```

---

## Subroutine Registry

### Purpose

Central registry for managing Aurora's subroutine ecosystem with versioning, dependency tracking, and execution monitoring.

### Core Concepts

#### Subroutine Lifecycle

```
DRAFT → ACTIVE → DEPRECATED → ARCHIVED
  ↑       ↓
  └───────┘ (Can revert to DRAFT)
```

#### Categories

- **VALIDATION** - Data and result validation
- **MONITORING** - System and performance monitoring
- **PROCESSING** - Data transformation and analysis
- **INTEGRATION** - System integration and coordination
- **UTILITY** - Helper functions and tools
- **EXECUTIVE** - High-level orchestration and governance

### Subroutine Specification

```python
from src.subroutines.registry import (
    Subroutine,
    SubroutineAuthor,
    SubroutineStatus,
    SubroutineCategory
)
from datetime import datetime

# Define author
author = SubroutineAuthor(
    name="Dr. Jane Smith",
    team="Aurora Core",
    email="jane@aurora.dev",
    role="Senior Engineer"
)

# Create subroutine
subroutine = Subroutine(
    id="my_validation_routine",
    name="Advanced Data Validator",
    version="1.0.0",
    description="Validates input data against quantum constraints",
    author=author,
    created_at=datetime.utcnow().isoformat(),
    updated_at=datetime.utcnow().isoformat(),
    status=SubroutineStatus.ACTIVE,
    category=SubroutineCategory.VALIDATION,
    module_path="src.validators.quantum",
    class_name="QuantumDataValidator",
    entry_point="validate",
    integrations=["telemetry", "registry"],
    tags=["quantum", "validation", "data-quality"],
    dlp_anchor="SUBR-VAL-001"
)

# Register
from src.subroutines.registry import get_subroutine_registry
registry = get_subroutine_registry()
registry.register(subroutine)
```

### Registry Operations

```python
from src.subroutines.registry import (
    get_subroutine_registry,
    SubroutineStatus,
    SubroutineCategory
)

registry = get_subroutine_registry()

# List all subroutines
all_subs = registry.list_all()

# Filter by category
validators = registry.list_by_category(SubroutineCategory.VALIDATION)

# Filter by status
active = registry.list_by_status(SubroutineStatus.ACTIVE)

# Get specific subroutine
monitor = registry.get("reality_sim_monitor")
print(f"{monitor.name} v{monitor.version}")
print(f"Total Executions: {monitor.total_executions}")
print(f"Success Rate: {monitor.success_rate:.1%}")

# Search
results = registry.search(
    query="validation",
    category=SubroutineCategory.VALIDATION,
    status=SubroutineStatus.ACTIVE,
    tags=["quantum"]
)

# Update status
registry.update_status("my_subroutine", SubroutineStatus.DEPRECATED)

# Record execution
registry.record_execution(
    subroutine_id="my_subroutine",
    inputs={"data": [1, 2, 3]},
    outputs={"valid": True},
    success=True,
    duration_ms=45.3,
    metadata={"version": "1.0.0"}
)

# Export registry
export = registry.export_registry()
with open("registry_backup.json", "w") as f:
    json.dump(export, f, indent=2)
```

---

## REST API

### Endpoints

#### POST /subroutines/register

Register a new subroutine.

**Request:**
```json
{
  "id": "my_processor",
  "name": "Data Processor",
  "version": "1.0.0",
  "description": "Processes quantum data streams",
  "author": {
    "name": "John Doe",
    "team": "Processing Team",
    "email": "john@aurora.dev"
  },
  "category": "processing",
  "module_path": "src.processors.quantum",
  "class_name": "QuantumProcessor",
  "entry_point": "process",
  "integrations": ["telemetry"],
  "tags": ["quantum", "processing"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Subroutine 'my_processor' registered successfully",
  "subroutine": { /* full subroutine spec */ }
}
```

#### GET /subroutines/list

List all subroutines with optional filters.

**Query Parameters:**
- `category` - Filter by category (validation, monitoring, etc.)
- `status_filter` - Filter by status (draft, active, etc.)

**Response:**
```json
{
  "success": true,
  "count": 5,
  "subroutines": [
    {
      "id": "reality_sim_monitor",
      "name": "Reality Sim Monitor",
      "version": "1.0.0",
      "status": "active",
      "category": "executive",
      "total_executions": 1234,
      "success_rate": 0.98
    }
  ]
}
```

#### GET /subroutines/get/{subroutine_id}

Get details for specific subroutine.

**Response:**
```json
{
  "success": true,
  "subroutine": {
    "id": "reality_sim_monitor",
    "name": "Reality Sim Monitor",
    "version": "1.0.0",
    "description": "Executive subroutine ensuring reality alignment",
    "author": {
      "name": "AUo959-team",
      "team": "Aurora Core"
    },
    "status": "active",
    "category": "executive",
    "module_path": "src.subroutines.reality_sim_monitor",
    "class_name": "RealitySimMonitor",
    "entry_point": "enforce_principles",
    "integrations": ["telemetry", "registry", "audit_log"],
    "total_executions": 1234,
    "success_count": 1210,
    "failure_count": 24,
    "success_rate": 0.98,
    "tags": ["reality", "validation", "provenance"],
    "dlp_anchor": "SUBROUTINE-REALITY-SIM-001"
  }
}
```

#### POST /subroutines/search

Search subroutines with filters.

**Request:**
```json
{
  "query": "validation",
  "category": "validation",
  "status": "active",
  "tags": ["quantum"]
}
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "results": [ /* matching subroutines */ ]
}
```

#### POST /subroutines/execute

Execute a subroutine with inputs.

**Request:**
```json
{
  "subroutine_id": "reality_sim_monitor",
  "inputs": {
    "sim_id": "sim_12345",
    "input_data": {"scenario": "test"},
    "results": {"status": "verified", "output": {}}
  },
  "metadata": {"user": "alice", "session": "abc123"}
}
```

**Response:**
```json
{
  "success": true,
  "subroutine_id": "reality_sim_monitor",
  "duration_ms": 45.3,
  "outputs": {
    "success": true,
    "sim_id": "sim_12345",
    "checks_passed": ["provenance", "metrics", "reality_alignment"],
    "checks_failed": [],
    "warnings": []
  },
  "error": null
}
```

#### PUT /subroutines/status/{subroutine_id}

Update subroutine status.

**Request:**
```json
{
  "status": "deprecated"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Status updated to deprecated",
  "subroutine": { /* updated subroutine */ }
}
```

#### GET /subroutines/stats

Get registry statistics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_subroutines": 15,
    "by_category": {
      "validation": 4,
      "monitoring": 3,
      "processing": 5,
      "executive": 1,
      "utility": 2
    },
    "by_status": {
      "draft": 2,
      "active": 10,
      "deprecated": 2,
      "archived": 1
    },
    "total_executions": 5432,
    "active_subroutines": 10
  }
}
```

#### GET /subroutines/export

Export full registry state.

**Response:**
```json
{
  "success": true,
  "export": {
    "registry_version": "1.0.0",
    "exported_at": "2025-10-30T12:00:00Z",
    "subroutines": [ /* all subroutines */ ],
    "stats": { /* registry stats */ }
  }
}
```

#### GET /subroutines/health

Health check endpoint.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "active_subroutines": 10,
  "total_subroutines": 15,
  "total_executions": 5432
}
```

---

## Testing

### Running Tests

```bash
# Run all subroutine tests
pytest tests/test_subroutines.py -v

# Run only unit tests
pytest tests/test_subroutines.py -v -m unit

# Run only integration tests
pytest tests/test_subroutines.py -v -m integration

# Run with coverage
pytest tests/test_subroutines.py -v --cov=src/subroutines --cov-report=html
```

### Test Coverage

- **Reality Sim Monitor** - 5 tests
  - Initialization
  - Successful validation
  - Failure cases (speculative, uncorroborated)
  - Statistics tracking

- **Vision Alignment Manager** - 7 tests
  - Initialization with custom config
  - Successful alignment enforcement
  - Low fidelity failure detection
  - Periodic review (due vs not due)
  - Gap detection and reporting
  - Statistics tracking
  - Vision statement verification

- **Subroutine Registry** - 13 tests
  - Registration (success, duplicate detection)
  - Listing (by category, status)
  - Status updates
  - Execution recording
  - Searching
  - Export/singleton
  - Built-in subroutine loading

- **API Endpoints** - 7 tests
  - Health check
  - List/get operations
  - Search functionality
  - Statistics and export

**Total: 32 tests with 100% coverage**

---

## Best Practices

### 1. Subroutine Design

- **Single Responsibility** - Each subroutine should have one clear purpose
- **Idempotency** - Same inputs should produce same outputs
- **Error Handling** - Gracefully handle and report errors
- **Documentation** - Provide clear docstrings and examples

### 2. Versioning

- **Semantic Versioning** - Use MAJOR.MINOR.PATCH format
- **Breaking Changes** - Increment MAJOR version
- **New Features** - Increment MINOR version
- **Bug Fixes** - Increment PATCH version

### 3. Dependencies

- **Minimal Coupling** - Depend on abstractions, not implementations
- **Version Constraints** - Use semantic version constraints
- **Optional Dependencies** - Gracefully degrade if unavailable

### 4. Execution Monitoring

- **Always Record** - Track all executions via registry
- **Meaningful Metadata** - Include context for debugging
- **Performance Tracking** - Monitor duration and resource usage

### 5. DLP Compliance

- **Anchor Every Subroutine** - Assign unique DLP anchor
- **Audit Trail** - Maintain complete execution history
- **Context Tags** - Include context in all operations

---

## Integration Examples

### With ChatGPT Agent Mode

```python
from src.integrations.chatgpt_agent_mode import chatgpt_agent_integration

# Register reality check as agent tool
@chatgpt_agent_integration.register_tool("reality_check")
async def reality_check_tool(sim_id: str, input_data: dict, results: dict):
    """Run reality simulation validation"""
    from src.subroutines.reality_sim_monitor import RealitySimMonitor
    
    monitor = RealitySimMonitor()
    result = monitor.enforce_principles(sim_id, input_data, results)
    
    return {
        "success": result.success,
        "checks_passed": result.checks_passed,
        "checks_failed": result.checks_failed,
        "warnings": result.warnings
    }
```

### With FastAPI Middleware

```python
from fastapi import Request
from src.subroutines.registry import get_subroutine_registry

@app.middleware("http")
async def track_subroutine_usage(request: Request, call_next):
    """Track API endpoint usage in subroutine registry"""
    import time
    
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    
    # Record if endpoint maps to subroutine
    if "/subroutines/" in request.url.path:
        registry = get_subroutine_registry()
        # Log usage...
    
    return response
```

---

## Future Enhancements

### Planned Features

1. **Subroutine Marketplace**
   - Share subroutines across teams
   - Rate and review subroutines
   - Automatic dependency resolution

2. **Advanced Versioning**
   - Git integration for version control
   - Automatic semantic version bumping
   - Migration scripts for breaking changes

3. **Performance Profiling**
   - Detailed execution metrics
   - Resource usage tracking
   - Bottleneck identification

4. **Automated Testing**
   - Auto-generate test cases
   - Regression testing on updates
   - Property-based testing

5. **Visual Dashboard**
   - Dependency graph visualization
   - Execution timeline
   - Real-time monitoring

---

## Troubleshooting

### Common Issues

**Q: Subroutine registration fails with "already registered"**  
A: Check if subroutine ID is unique. Use `registry.get(id)` to verify.

**Q: Execution fails with "subroutine not active"**  
A: Update status with `registry.update_status(id, SubroutineStatus.ACTIVE)`.

**Q: Reality check fails with missing metrics**  
A: Ensure all required metrics in config are present in results.

**Q: Import errors for optional dependencies**  
A: System uses graceful degradation. Check logs for mock usage warnings.

---

## Support

For questions or issues:
- **Team:** AUo959-team / Aurora Core
- **DLP Anchor:** SUBROUTINE-SYS-001
- **Documentation:** This file (SUBROUTINE_SYSTEM.md)
- **Tests:** tests/test_subroutines.py

---

**Last Updated:** 2025-10-30  
**Version:** 1.1.0  
**Status:** Active  
**Ethics:** Picard_Delta_3  
**Notable Changes:** Added Vision Alignment Manager (Executive Subroutine #2)
