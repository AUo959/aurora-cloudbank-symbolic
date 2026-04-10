# Aurora CloudBank Custom Command Reference

**Version:** 1.0.0  
**Last Updated:** 2025-11-03  
**Purpose:** Immediate reference for all agents working on Aurora CloudBank

---

## 🎯 Quick Command Index

| Command Pattern | Purpose | Example | See Section |
|----------------|---------|---------|-------------|
| `#NNN//MMM//` | Chain notation | `#001//999//` | [Chain Notation](#chain-notation) |
| `#NNN//MMM//TAG` | Tagged chain | `#005//001//ACC` | [Tagged Chains](#tagged-chains) |
| `T1:STATE` | Temporal anchor | `T1:42` | [Temporal Anchors](#temporal-anchors) |
| `SRB:RES` | Spatial-relational boundary | `SRB:1337` | [SRB Anchors](#srb-anchors) |
| `DLP:TAG` | Data lineage protocol | `DLP:export_001` | [DLP Protocol](#dlp-protocol) |
| `@seal:HASH` | Memory seal | `@seal:abc123` | [Memory Seals](#memory-seals) |

## 🚀 Common Workflow Commands

**Quick Access:** Frequently used command codes with direct documentation links.

### Predefined Workflows
- **[#321//.](../tools/command_chain/COMPREHENSIVE_SYNC_321.md)** - **Comprehensive Sync & Validate**
  - Universal "clean working tree" command with split implementations
  - **Integrated Python path:** `python tools/command_chain/cmd_321.py` or `python tools/command_chain/dispatcher.py 321`
  - **Integrated phases:** 6 (check → stage → commit → sync → validate → performance verify)
  - **Enhanced shell variant:** `bash scripts/sync_321_enhanced.sh`
  - **Enhanced extras:** VERSION/README automation and wiki sync, but this is a separate manual path, not the dispatcher-backed implementation
  - **Use anytime:** You want pending changes sorted with high quality and a clear execution path

- **[#808//.](../tools/command_chain/OPTIMIZING_PULSE_808.md)** - **Optimizing Pulse** (if exists)
  - Finds optimal path through complex workflows
  - Performance analysis and recommendations

### System Commands
- **#001//.** through **#999//.** - Numeric aliases for system operations
- See [`tools/command_chain/parser.py`](../tools/command_chain/parser.py) for full supported command list
- Check `tools/command_chain/*_[0-9][0-9][0-9].md` for command-specific documentation

### Command Syntax Patterns

**Distinguish between:**

1. **Chain Notation:** `#START//END//`
     - Example: `#001//999//` - Execute steps 1 through 999
     - Format: Two numbers with double slashes
     - Used for: Sequential execution ranges

2. **Command Codes:** `#CODE//.`
     - Example: `#321//.` - Execute predefined command 321
     - Format: Single number with terminator (`//.`)
     - Used for: Workflow shortcuts and macros

**Pattern Detection:**
- If you see `#NNN//.` (ends with dot) → **Command code** (check `tools/command_chain/`)
- If you see `#NNN//MMM//` (two numbers) → **Chain notation** (sequential execution)
- If you see `#NNN//` (no terminator) → **Error** (incomplete syntax)

---

---

## 📖 Core Command Systems

### Chain Notation

**Pattern:** `#START//END//`  
**Format:** Numbers are zero-padded to 3 digits  
**Purpose:** Defines symbolic execution chains with temporal progression

#### Basic Chain
```
#001//999//
```
- **Start:** Step 001
- **End:** Step 999
- **Behavior:** Execute all steps from 001 to 999 sequentially
- **T1 Anchor:** Advances with each step
- **SRB Anchor:** Resolves boundaries at each step

#### Usage Examples

**Feature Implementation:**
```python
# Phase 1 of feature roadmap
chain = "#005//001//"  # Foundation layer
engine.execute_chain(5, 1)
```

**Issue Tracking:**
```python
# Code quality issue #258
chain = "#001//258//"  # Links to GitHub issue
result = analyzer.run_with_chain("001//258//")
```

**Module Integration:**
```python
# Complete system integration
chain = "#001//999//"  # Full range execution
quantum_state = process_chain(chain)
```

#### Chain Properties

- **Immutable:** Once started, chain sequence cannot be modified
- **Anchored:** All chains maintain T1/SRB anchor state
- **Traceable:** Full execution history preserved
- **Composable:** Chains can reference other chains

#### Implementation

```python
from src.aurora.core.symbolic_engine import SymbolicEngine

engine = SymbolicEngine()

# Execute chain
results = engine.execute_chain(start=1, end=999)

# Access chain by notation
chain_id = "001//999//"
chain_data = engine.chains[chain_id]

# Export manifest
manifest = engine.export_manifest()
```

---

### Tagged Chains

**Pattern:** `#START//END//TAG`  
**Format:** Uppercase 3-letter tag suffix  
**Purpose:** Add semantic context to chain execution

#### Tag Categories

**Module Tags:**
- `ACC` - Compliance Co-Pilot
- `EDG` - Data Guardian (Ethics)
- `TIL` - Insight Ledger (Temporal)
- `QSS` - Quantum Simulator
- `VSA` - Vector Symbolic Architecture
- `MEM` - Memory Manager (AuMemManager)

**Phase Tags:**
- `P1` - Phase 1 (Foundation)
- `P2` - Phase 2 (Core Services)
- `P3` - Phase 3 (Integration)
- `P4` - Phase 4 (User Interfaces)
- `P5` - Phase 5 (Production Hardening)
- `P6` - Phase 6 (Documentation)
- `P7` - Phase 7 (Launch)

**Operation Tags:**
- `TST` - Test/Validation
- `INT` - Integration
- `DEP` - Deployment
- `SEC` - Security
- `OPT` - Optimization

#### Examples

```python
# Foundation for Compliance Co-Pilot
"#005//001//ACC"  # Phase 5, Foundation, Compliance module

# Integration phase for Quantum Simulator
"#005//003//QSS"  # Phase 5, Integration, Quantum module

# Security hardening across all modules
"#005//005//SEC"  # Phase 5, Hardening, Security focus
```

---

### Temporal Anchors

**Pattern:** `T1:STATE_VALUE`  
**Purpose:** Track temporal progression through symbolic operations  
**Behavior:** Monotonically increasing state counter

#### T1 Anchor States

```python
from src.aurora.core.symbolic_engine import T1Anchor

# Initialize
t1 = T1Anchor()
print(t1.state)  # 0

# Advance with data
new_state = t1.advance("operation_data")
print(t1.state)  # State increases based on data length

# Export state
anchor_data = t1.export()
# {'type': 'T1', 'state': 42}
```

#### Usage Context

**Before Operation:**
```python
initial_t1 = engine.t1.state  # T1:0
```

**During Operation:**
```python
# T1 advances automatically during chain execution
results = engine.execute_chain(1, 100)
# Each step advances T1
```

**After Operation:**
```python
final_t1 = engine.t1.state  # T1:10542
delta = final_t1 - initial_t1  # Temporal distance
```

#### Validation

```python
def validate_t1_progression(before_state, after_state):
    """Ensure T1 anchor progressed correctly"""
    assert after_state > before_state, "T1 must advance monotonically"
    return True
```

---

### SRB Anchors

**Pattern:** `SRB:RESOLUTION_VALUE`  
**Purpose:** Track spatial-relational boundary resolutions  
**Behavior:** Hash-based boundary state tracking

#### SRB Anchor Operations

```python
from src.aurora.core.symbolic_engine import SRBAnchor

# Initialize
srb = SRBAnchor()
print(srb.resolution)  # 0

# Resolve boundary
resolution = srb.resolve("module_boundary_001")
print(srb.resolution)  # Hash-based resolution value

# Export state
boundary_data = srb.export()
# {'type': 'SRB', 'resolution': 837}
```

#### Boundary Types

**Module Boundaries:**
```python
srb.resolve("module:compliance_co_pilot")
srb.resolve("module:data_guardian")
srb.resolve("module:quantum_simulator")
```

**Phase Boundaries:**
```python
srb.resolve("phase:foundation_complete")
srb.resolve("phase:core_services_ready")
srb.resolve("phase:integration_validated")
```

**State Boundaries:**
```python
srb.resolve("state:pre_quantum_transform")
srb.resolve("state:post_quantum_transform")
srb.resolve("state:memory_sealed")
```

---

### DLP Protocol

**Pattern:** `DLP:CONTEXT_TAG`  
**Purpose:** Data Lineage Protocol - Track data provenance and transformations  
**Required:** All exports must include DLP tags

#### DLP Tag Structure

```python
from src.core.native_dlp_export import NativeDLPTracker

tracker = NativeDLPTracker()

# Create DLP-tagged export
export = tracker.create_export(
    data={"results": [...], "metrics": {...}},
    context_tag="export_quantum_state_001",
    symbolic_validation=True
)
```

#### DLP Components

**Context Tag:** Identifies operation context
```python
context_tag = "export_quantum_state_001"
context_tag = "chain_execution_005_001"
context_tag = "module_integration_complete"
```

**Symbolic Hash Validation:** Ensures data integrity
```python
validation = {
    "hash": "sha256:abc123...",
    "timestamp": "2025-11-03T14:30:00Z",
    "chain": "001//999//"
}
```

**Manifest Creation:** Persists complete lineage
```python
manifest = tracker.create_export_manifest(
    export_id="manifest_001",
    chain_notation="001//999//",
    t1_state=engine.t1.export(),
    srb_state=engine.srb.export()
)
```

#### Required Pattern

**Every agent operation producing output MUST:**

1. **Tag with context:**
```python
context_tag = f"agent_operation_{operation_type}_{timestamp}"
```

2. **Validate symbolically:**
```python
symbolic_hash = hash(f"{data}_{chain_notation}_{t1_state}")
```

3. **Create manifest:**
```python
manifest = create_export_manifest(
    export_id=context_tag,
    chain_notation=current_chain,
    t1_state=engine.t1.export(),
    srb_state=engine.srb.export()
)
```

---

### Memory Seals

**Pattern:** `@seal:HASH_VALUE`  
**Purpose:** Quantum memory integrity markers  
**System:** AuMemManager integration

#### Memory Seal Operations

```python
# Seal memory with current state
seal_hash = memory_manager.seal_memory(
    chain="001//999//",
    t1_state=engine.t1.state,
    srb_resolution=engine.srb.resolution
)

# Reference: @seal:abc123def456
seal_ref = f"@seal:{seal_hash}"
```

#### Seal Validation

```python
def validate_memory_seal(seal_ref, current_state):
    """Verify memory seal integrity"""
    seal_hash = seal_ref.replace("@seal:", "")
    
    expected_hash = compute_seal_hash(
        chain=current_state.chain,
        t1=current_state.t1,
        srb=current_state.srb
    )
    
    return seal_hash == expected_hash
```

#### Use Cases

**Before Critical Operations:**
```python
# Seal state before quantum transformation
pre_seal = f"@seal:{memory_manager.seal_current_state()}"
quantum_transform()
post_seal = f"@seal:{memory_manager.seal_current_state()}"
```

**Checkpoint Recovery:**
```python
# Restore to sealed state
checkpoint = "@seal:abc123def456"
memory_manager.restore_from_seal(checkpoint)
```

---

## 🔧 Agent Integration Patterns

### Pattern 1: Chain-Based Operation

```python
def agent_execute_with_chain(operation_type, start, end):
    """Standard chain execution pattern for agents"""
    
    # 1. Initialize engine
    from src.aurora.core.symbolic_engine import SymbolicEngine
    engine = SymbolicEngine()
    
    # 2. Capture initial state
    initial_t1 = engine.t1.state
    initial_srb = engine.srb.resolution
    
    # 3. Execute chain
    chain_notation = f"{start:03d}//{end:03d}//"
    results = engine.execute_chain(start, end)
    
    # 4. Create DLP export
    from src.core.native_dlp_export import NativeDLPTracker
    tracker = NativeDLPTracker()
    
    export = tracker.create_export(
        data=results,
        context_tag=f"agent_{operation_type}_{chain_notation}",
        symbolic_validation=True
    )
    
    # 5. Create manifest
    manifest = tracker.create_export_manifest(
        export_id=f"manifest_{chain_notation}",
        chain_notation=chain_notation,
        t1_state=engine.t1.export(),
        srb_state=engine.srb.export()
    )
    
    return {
        "chain": chain_notation,
        "results": results,
        "export": export,
        "manifest": manifest,
        "t1_delta": engine.t1.state - initial_t1,
        "srb_delta": engine.srb.resolution - initial_srb
    }
```

### Pattern 2: Tagged Module Operation

```python
def agent_module_operation(module_tag, operation):
    """Execute module-specific operation with proper tagging"""
    
    # Map module tags to chain ranges
    MODULE_CHAINS = {
        "ACC": (5, 1),    # Compliance Co-Pilot
        "EDG": (5, 2),    # Data Guardian
        "TIL": (5, 3),    # Insight Ledger
        "QSS": (5, 4),    # Quantum Simulator
    }
    
    start, end = MODULE_CHAINS[module_tag]
    chain = f"#00{start}//00{end}//{module_tag}"
    
    # Execute with proper chain context
    result = agent_execute_with_chain(
        operation_type=f"module_{module_tag}",
        start=start,
        end=end
    )
    
    result["tagged_chain"] = chain
    return result
```

### Pattern 3: Memory-Sealed Operation

```python
def agent_sealed_operation(operation_func, *args, **kwargs):
    """Execute operation with memory seal checkpoints"""
    
    # 1. Seal pre-operation state
    pre_seal = memory_manager.seal_current_state()
    print(f"Pre-operation seal: @seal:{pre_seal}")
    
    try:
        # 2. Execute operation
        result = operation_func(*args, **kwargs)
        
        # 3. Seal post-operation state
        post_seal = memory_manager.seal_current_state()
        print(f"Post-operation seal: @seal:{post_seal}")
        
        return {
            "result": result,
            "pre_seal": f"@seal:{pre_seal}",
            "post_seal": f"@seal:{post_seal}",
            "integrity": "verified"
        }
        
    except Exception as e:
        # 4. Restore to pre-seal on error
        memory_manager.restore_from_seal(pre_seal)
        raise Exception(f"Operation failed, restored to @seal:{pre_seal}") from e
```

---

## 📝 Agent Checklist

Before ANY agent operation, verify:

- [ ] **Chain notation** selected and validated (`#NNN//MMM//`)
- [ ] **T1 anchor** initial state captured
- [ ] **SRB anchor** initial resolution captured
- [ ] **DLP context tag** prepared
- [ ] **Symbolic engine** initialized
- [ ] **Memory seal** created (if critical operation)

During operation, ensure:

- [ ] **T1 advances** monotonically
- [ ] **SRB resolves** boundaries correctly
- [ ] **Chain execution** completes all steps
- [ ] **Error handling** includes seal restoration

After operation, confirm:

- [ ] **DLP export** created with context tag
- [ ] **Symbolic validation** hash generated
- [ ] **Export manifest** persisted
- [ ] **T1 delta** documented
- [ ] **SRB delta** documented
- [ ] **Memory seal** verified (if applicable)

---

## 🚨 Common Mistakes to Avoid

### ❌ Missing Chain Notation
```python
# WRONG - No chain context
results = process_data(input_data)

# RIGHT - Chain-aware processing
chain = "#001//999//"
results = engine.execute_chain(1, 999)
```

### ❌ Forgetting DLP Tags
```python
# WRONG - No data lineage
return {"data": results}

# RIGHT - DLP-tracked export
export = tracker.create_export(
    data=results,
    context_tag="operation_xyz",
    symbolic_validation=True
)
return export
```

### ❌ Ignoring Anchor State
```python
# WRONG - Lost anchor progression
result = operation()
return result

# RIGHT - Anchor-aware execution
initial_t1 = engine.t1.state
result = operation()
final_t1 = engine.t1.state
return {
    "result": result,
    "t1_delta": final_t1 - initial_t1
}
```

### ❌ Breaking Memory Seals
```python
# WRONG - Unsafe critical operation
quantum_transform(data)  # No recovery path

# RIGHT - Sealed critical operation
pre_seal = memory_manager.seal_current_state()
try:
    quantum_transform(data)
    post_seal = memory_manager.seal_current_state()
except:
    memory_manager.restore_from_seal(pre_seal)
    raise
```

---

## 📚 Quick Reference Files

| File | Purpose | Location |
|------|---------|----------|
| Symbolic Engine | Chain execution | `src/aurora/core/symbolic_engine.py` |
| DLP Tracker | Data lineage | `src/core/native_dlp_export.py` |
| AuMemManager | Memory seals | `modules/aumemmanager/` |
| Copilot Instructions | Agent guidelines | `.github/copilot-instructions.md` |
| Feature Roadmap | Tagged chains | `docs/FEATURE_IMPLEMENTATION_ROADMAP_7PHASE.md` |

---

## 🔍 Command Lookup

**Need to find a specific command?**

```bash
# Search for chain notation examples
grep -r "#[0-9]\{3\}//[0-9]\{3\}//" .

# Find DLP usage
grep -r "DLP:" . --include="*.py"

# Locate T1 anchor references
grep -r "T1:" . --include="*.py"

# Find memory seal operations
grep -r "@seal:" . --include="*.py"
```

---

## 📞 Support

**Questions about commands?**
- Check `.github/copilot-instructions.md` for context
- Review `src/aurora/core/symbolic_engine.py` for implementation
- See `docs/FEATURE_IMPLEMENTATION_ROADMAP_7PHASE.md` for examples

**Command not working?**
1. Verify chain notation format (`#NNN//MMM//`)
2. Check T1/SRB anchor initialization
3. Confirm DLP tracker import
4. Validate symbolic engine state

---

*This reference is automatically available to all agents via `.github/copilot-instructions.md` integration.*
