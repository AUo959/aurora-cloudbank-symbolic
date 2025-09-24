# Makefile for common developer tasks

install:
	pip install -r requirements.txt

lint:
	flake8 modules/reflective_autonomy

.PHONY: lint-tools
lint-tools:
	# Lint only modernized tool paths (matches CI scope)
	flake8 tools/symbolic tools/cli --max-line-length=120 --extend-ignore=E203,W503,F811

.PHONY: lint-all
lint-all:
	# Broad lint across src, modules, tests, and tools (may surface legacy issues)
	flake8 src modules tests tools/symbolic tools/cli --max-line-length=120 --extend-ignore=E203,W503

test:
	pytest tests

run:
	python modules/reflective_autonomy/loom_restore_script.py

.PHONY: check
check:
	# Fast stability check: scoped lint + full tests
	$(MAKE) lint-tools
	pytest -q

.PHONY: branch-status
branch-status:
	# Generate a branch status report relative to main
	bash ./branch_status_report.sh

.PHONY: sync
sync:
	# Fetch latest refs and prune stale branches
	git fetch --all --prune

.PHONY: branch-plan
branch-plan:
	# Generate a Markdown plan for branch cleanup
	bash ./scripts/branch_cleanup_plan.sh > BRANCH_CLEANUP_PLAN.md

.PHONY: pr-priority
pr-priority:
	# Generate prioritized PR action list from cleanup plan
	python3 scripts/pr_cleanup_priority_from_plan.py

# SSMT v3.0 Maintenance Automation
.PHONY: health-check
health-check:
	# Quick repository health status check
	python3 scripts/quick_health_check.py

.PHONY: maintenance-scan
maintenance-scan:
	# Full repository maintenance analysis
	python3 scripts/ssmt_v3_0_maintenance_pipeline.py

.PHONY: maintenance-manual
maintenance-manual:
	# Manual trigger of weekly maintenance
	python3 scripts/weekly_automation_scheduler.py --manual

.PHONY: maintenance-status
maintenance-status:
	# Check automation schedule and status
	python3 scripts/weekly_automation_scheduler.py

.PHONY: branch-cleanup-dry
branch-cleanup-dry:
	# Preview deletion of obvious obsolete branches (no changes pushed)
	DRY_RUN=1 bash ./scripts/branch_cleanup_exec.sh 'copilot/fix-*' || true
	DRY_RUN=1 bash ./scripts/branch_cleanup_exec.sh 'dependabot/*' || true

.PHONY: branch-cleanup-apply
branch-cleanup-apply:
	# Apply deletion of obvious obsolete branches (requires confirmation)
	DRY_RUN=0 bash ./scripts/branch_cleanup_exec.sh 'copilot/fix-*'
	DRY_RUN=0 bash ./scripts/branch_cleanup_exec.sh 'dependabot/*'

.PHONY: lint-stage1-opal2
lint-stage1-opal2:
	# Stage 1 whitespace/formatting fixes for modules/opal2, then lint tools as a canary
	python3 scripts/whitespace_fix_stage1.py modules/opal2
	flake8 modules/opal2 --max-line-length=120 --extend-ignore=E203,W503 || true

.PHONY: pr-triage
pr-triage:
	# Summarize open PRs; set GITHUB_TOKEN to increase rate limits
	python3 scripts/pr_triage_snapshot.py
