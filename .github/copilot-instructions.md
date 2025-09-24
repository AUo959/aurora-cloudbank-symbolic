# Aurora CloudBank Symbolic System - AI Coding Instructions

This is Aurora CloudBank, a quantum-enhanced symbolic governance system with Vector Symbolic Architecture (VSA), cultural awareness simulation, and AI-powered processing. The architecture emphasizes symbolic anchor continuity, memory sealing, and ethical governance.

## 🏗️ Architecture Overview

**Core Pattern**: Hybrid quantum-symbolic processing with temporal anchoring
- **Symbolic Engine**: `src/aurora/core/symbolic_engine.py` - T1/SRB anchor management
- **API Layer**: `aurora_api.py` - FastAPI with quantum/geometric algebra endpoints  
- **Module System**: `modules/` - reflective_autonomy, symbolic_core, opal2, cask
- **DLP System**: `src/core/native_dlp_export.py` - Data lineage and provenance tracking

**Key Architectural Concepts**:
- **T1 Anchors**: Temporal state tracking (`self.t1.advance(data)`)
- **SRB Anchors**: Spatial-Relational Boundary resolution (`self.srb.resolve(boundary)`)
- **Memory Sealing**: SHA256 integrity protection with audit trails
- **Chain Notation**: `001//999//` format for symbolic execution sequences

## 🔄 Development Workflows

**Quick Status Check**: `python3 scripts/dev-status.py`
**Development Server**: `make run` or `python modules/reflective_autonomy/loom_restore_script.py`
**Testing**: `python scripts/test_runner.py` or `pytest tests/`
**Linting**: `flake8` with 120-char line limit, `black` formatting
**Docker**: `docker-compose up --build` (includes health checks)

**Critical Debugging Workflows**:
- `rollback_autoseal()` - Call after merges to ensure memory state sealing
- `entropy_snap()` - On-demand entropy capture and symbolic drift assessment
- `anchor://seal <name>` - CLI entrypoint for symbolic anchor sealing
- `drift://scan <module>` - Module-specific symbolic drift scanning
- `reflexivity_scan --explain` - State-tracing and debugging actions

**Essential GitWiz Tools**:
- `gitwiz_anchor_lint` - Anchor convention validation and linting
- `gitwiz_snapshot_report` - Anchor sealing and rollback integration
- `gitwiz_driftchart` - Branch volatility tracking and proactive monitoring
- `scripts/gitwiz_*.py` - Complete automated repository management suite

**Critical Scripts**:
- `scripts/aurora_health_monitor.py` - System health validation
- `scripts/infallible_codespace_init.py` - Environment bootstrapping  
- `tools/symbolic/memory_sealer.py` - Cryptographic state sealing with audit trails

## 📋 Project-Specific Patterns

**Import Conventions**:
```python
from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.sonnet4_integration_hub import sonnet4_hub
from src.core.native_dlp_export import NativeDLPTracker, NativeExportSystem
```

**Symbolic Operation Pattern**:
```python
# Always use DLP tracking for symbolic operations with required context_tag
dlp_tracker = NativeDLPTracker()
tag_id = dlp_tracker.tag_symbolic_operation(symbolic_data)
tag = dlp_tracker.tags[tag_id]
tag.add_anchor_protocol("EOS_SEED_ORION")
tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
tag.metadata['context_tag'] = "required_for_continuity"  # REQUIRED for all reflex logs

# Standardized anchor conventions (canonized)
tag.add_anchor_protocol("T1")  # Temporal anchor
tag.add_anchor_protocol("SRB_TICK")  # Spatial-relational boundary
tag.add_anchor_protocol("ANCHOR_LOCKED")  # State lock verification
tag.metadata['state_tag'] = "symbolic_state_identifier"
```

**DLP Tagging Standards (Canonized)**:
```python
# Use standardized DLP classifications on all exports
tag.metadata.update({
    'dlp_level': 'DLP_L1_OK',      # or DLP_L2_LOCKED, DLP_RISK_P2
    'symbolic_hash_validation': True,  # Required for cross-layer communication
    'context_tag': 'operation_context'  # REQUIRED for all reflex logs
})
```

**API Endpoint Pattern** (FastAPI with geometric algebra):
```python
@app.post("/quantum/symbolic_vector")
async def symbolic_vector(request: VectorRequest):
    ga = GeometricAlgebra()
    result = ga.mult(request.x, request.y)  # Geometric product
    return {"result": ga.pretty(result)}
```

**Error Handling**: Use graceful degradation with mock implementations when dependencies unavailable (see `geometric_algebra.py`)

## 🔧 Configuration & Dependencies

**Python**: 3.11+ with FastAPI, NumPy, Qiskit, Clifford algebra
**Node.js**: 18+ for command node services and crypto utilities
**Line Length**: 120 characters (Black/Flake8 configured)
**Testing**: pytest with asyncio support

**Key Dependencies**:
- `fastapi`, `uvicorn` - API server
- `qiskit`, `qiskit-aer` - Quantum computing
- `clifford` - Geometric algebra (optional with fallback)
- `pandas`, `plotly` - Data analysis and visualization

## 🚀 Integration Points

**Quantum-Symbolic Bridge**: All quantum operations must maintain symbolic state continuity
**CASK Integration**: Cultural awareness via `modules/cask/` and `CASK_Assets.zip`
**Claude Sonnet 4**: Enhanced reasoning through `sonnet4_integration_hub.py`
**Docker Services**: Multi-container with aurora-cloudbank (port 8000) and aurora-cli

**Cross-Component Communication (Strict Schema Enforcement)**:
```python
# All Simbridge → CASK proxy calls require explicit validation
def cask_proxy_call(payload):
    # Declare symbolic anchor with typed schema
    anchor = {
        'symbolic_anchor': 'CASK_PROXY_BRIDGE',
        'payload_structure': validate_typed_schema(payload),
        'verification_logic': compute_symbolic_hash(payload)
    }
    return process_with_anchor_validation(anchor, payload)

# Cross-layer handoff requirements (Simbridge, CASK, THREADCORE)
def layer_handoff(source_layer, target_layer, data):
    assert data.get('symbolic_hash_validation') == True
    assert 'typed_schema' in data
    return verified_handoff(source_layer, target_layer, data)
```

**Export Manifests**: All symbolic operations generate JSON manifests with:
- `anchor_protocols` (e.g., "EOS_SEED_ORION", "Picard_Delta_3")
- `t1_srb_anchors` for temporal/spatial tracking
- SHA256 memory seals for integrity verification
- `context_tag` (REQUIRED for continuity support)

## ⚖️ Ethical & Security Patterns

**Ethics Protocol**: "Picard_Delta_3" - embedded in all major operations
**Memory Ethics**: Sensitive data wiping, anti-obfuscation mandate
**Security Scanning**: `scripts/aurora_security_scanner.py` for vulnerability detection
**Governance**: `modules/reflective_autonomy/` implements self-healing governance loop

**Post-Merge Memory Sealing Protocol**:
```python
# Always call after merges and rollback scenarios
def post_merge_workflow():
    rollback_autoseal()  # Ensures memory state sealing
    entropy_snap()       # Captures entropy and assesses symbolic drift
    audit_trail_update() # Updates audit trails for traceability
```

**Reflexivity Requirements**:
```python
# All reflex logs MUST include context_tag for continuity
reflex_log = {
    'operation': 'symbolic_processing',
    'context_tag': 'processing_context',  # REQUIRED
    'audit_trail': generate_audit_trail(),
    'memory_seal': compute_sha256_seal()
}
```

**Critical Files for Security**:
- `.security/secure_helpers.py` - Input sanitization and validation
- `crypto_refactored.js` - Encryption with anchor manifest export
- `scripts/security_audit.sh` - Automated security validation
