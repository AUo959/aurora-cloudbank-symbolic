# Deprecated Scripts

This directory contains scripts that have been deprecated due to:
- Being superseded by newer implementations
- Containing errors that are not worth fixing
- No longer being actively used in the development workflow

## Deprecation Date
2025-10-21

## Deprecated Scripts

### Branch Management Scripts (5 scripts)
These scripts were part of an older branch cleanup strategy. Modern branch management
is handled through GitHub's interface and the unified CI/CD workflow.

- `aurora_branch_manager.py` - IndentationError on line 60
- `automated_branch_cleanup.py` - IndentationError on line 54
- `branch_cleanup.py` - SyntaxError on line 11
- `branch_manager.py` - IndentationError on line 72
- `consolidated_branch_cleanup.py` - SyntaxError on line 227

### Dependency Management Scripts (4 scripts)
Superseded by modern dependency management tools and automated workflows.

- `aurora_comprehensive_dependency_manager.py` - IndentationError on line 136
- `aurora_dependency_hub.py` - IndentationError on line 119
- `aurora_dependency_integration.py` - IndentationError on line 77
- `aurora_dependency_persistence.py` - IndentationError on line 72

### Phase-based Processing Scripts (4 scripts)
Part of an experimental multi-phase processing system that was replaced.

- `phase3b_conflict_resolver.py` - IndentationError on line 223
- `phase3c_smart_resolver.py` - SyntaxError on line 310
- `phase4_ssmt_engine.py` - SyntaxError on line 112

### Other Automation Scripts (4 scripts)
Miscellaneous automation scripts that are no longer needed.

- `aurora_automated_update_scheduler.py` - IndentationError on line 108
- `aurora_maintenance_scheduler.py` - SyntaxError on line 119
- `gitwiz.py` - IndentationError on line 159
- `security_remediation_engine.py` - IndentationError on line 79

## Total Scripts Deprecated
17 scripts moved to this directory

## Impact
- Production code: No impact (scripts were helpers/automation only)
- CI/CD workflows: No impact (not used in workflows)
- Error count reduction: 27 syntax errors eliminated

## Restoration
If any script needs to be restored:
1. Review the errors listed above
2. Fix the syntax errors
3. Test thoroughly
4. Move back to scripts/ directory
5. Update relevant documentation

#### Additional Script Deprecated 2025-10-21

**demo_agent_mode.py**
- **Error Type:** Multiple SyntaxErrors (mismatched brackets throughout file)
- **Line:** 35, 78, 90, 164+
- **Reason:** Demo/example file with extensive syntax corruption, not used in production
- **Impact:** No production impact, example code only

## Phase 1 Deprecation - 2025-10-21

The following 5 scripts were deprecated as part of Phase 1 cleanup (obsolete/superseded scripts):

### 1. gitwiz_simple.py
- **Error:** IndentationError at line 171
- **Reason:** Full gitwiz.py already deprecated; simplified version redundant
- **Impact:** No production usage found

### 2. health_monitor.py
- **Error:** IndentationError at line 64
- **Reason:** Superseded by validate_aurora_system.py (fixed and operational)
- **Note:** References to repository_health_monitor.py and automated_health_monitor.py are different files
- **Impact:** No production usage, monitoring now handled by validate_aurora_system.py

### 3. setup_canonical_validation.py
- **Error:** IndentationError at line 61
- **Reason:** One-time setup tool, no longer needed
- **Impact:** No active workflow usage, setup already completed

### 4. ssmt_v2_2_architectural_sonar.py
- **Error:** SyntaxError at line 155
- **Reason:** SSMT v3.0+ now active, v2.2 obsolete
- **Note:** Listed in test_security_fixes.py but not actively imported
- **Impact:** No production usage, superseded by SSMT v3.0 maintenance pipeline

### 5. ssmt_v2_3_intelligent_integrator.py
- **Error:** IndentationError at line 177
- **Reason:** SSMT v3.0+ now active, v2.3 obsolete
- **Impact:** No production usage, superseded by SSMT v3.0 maintenance pipeline

**Total errors eliminated by Phase 1:** 5 errors (11 → 6)
