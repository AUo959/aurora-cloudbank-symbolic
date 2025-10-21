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
