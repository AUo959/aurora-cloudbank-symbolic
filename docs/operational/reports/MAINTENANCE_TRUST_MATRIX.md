# Maintenance Trust Matrix

Updated: 2026-03-08

## Trusted Canonical Entrypoints

- `scripts/repo_health_monitor.py`: canonical repository health report generator.
- `scripts/scheduled_maintenance.sh`: canonical maintenance runner.
- `scripts/branch_manager.py`: canonical branch analysis and cleanup engine.
- `scripts/ensure_python.sh`: canonical Python 3.11 discovery and installation helper.
- `scripts/gitwiz.py`: canonical repository operations CLI.
- `scripts/setup_dependencies.sh`: diagnostic-first Python environment bootstrap.
- `scripts/archive_large_files.py`: dry-run-first ZIP archive helper.

## Compatibility Wrappers

- `scripts/repository_health_monitor_enhanced.py` -> `scripts/repo_health_monitor.py`
- `scripts/repository_health_monitor_v2.py` -> `scripts/repo_health_monitor.py`
- `scripts/scheduled_maintenance_enhanced.py` -> `scripts/scheduled_maintenance.sh`
- `scripts/aurora_branch_manager.py` -> `scripts/branch_manager.py`
- `scripts/branch_cleanup.py` -> `scripts/branch_manager.py`
- `scripts/automated_branch_cleanup.py` -> `scripts/branch_cleanup.py`
- `scripts/automated_branch_cleanup_enhanced.py` -> `scripts/automated_branch_cleanup.py`
- `scripts/branch_cleanup_automation.py` -> `scripts/automated_branch_cleanup.py`
- `scripts/gitwiz_enhanced.py` -> `scripts/gitwiz.py`

## Residual Risks

- `scripts/ci-maintenance.sh` still contains broad `rm -rf` cleanup patterns and needs a separate guarded rewrite.
- Several legacy setup scripts still mutate the environment directly instead of defaulting to diagnostics.
- The host machine still lacks `python3.11`, so the repo cannot fully exercise the intended bootstrap path.
