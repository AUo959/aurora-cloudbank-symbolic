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
