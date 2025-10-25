# Aurora CloudBank Symbolic System Makefile
# Common developer tasks with dependency management

# Environment settings
PYTHON := python3
VENV_DIR := .venv
PIP := $(VENV_DIR)/bin/pip
PYTHON_VENV := $(VENV_DIR)/bin/python

install:
	pip install -r requirements.txt

# New dependency management targets
.PHONY: setup validate deps-check deps-update backup help

setup: ## Set up development environment with dependency validation
	@echo "🚀 Setting up Aurora CloudBank environment..."
	@bash scripts/setup_environment.sh

validate: ## Validate dependencies and environment
	@if [ ! -d "$(VENV_DIR)" ]; then echo "❌ Virtual environment not found. Run 'make setup' first."; exit 1; fi
	@echo "🔍 Validating dependencies..."
	@source $(VENV_DIR)/bin/activate && python scripts/validate_dependencies.py

deps-check: validate ## Check for dependency conflicts
	@echo "🧪 Checking for dependency conflicts..."
	@source $(VENV_DIR)/bin/activate && pip check

deps-update: ## Update dependencies (with backup)
	@echo "📦 Updating dependencies..."
	@if [ ! -d ".backup/requirements" ]; then mkdir -p .backup/requirements; fi
	@cp requirements-lock.txt .backup/requirements/requirements-lock.txt.$(shell date +%Y%m%d_%H%M%S) 2>/dev/null || true

backup: ## Backup current environment and requirements
	@echo "💾 Creating backup..."
	@mkdir -p .backup/{requirements,venv}
	@cp requirements*.txt .backup/requirements/ 2>/dev/null || true
	@if [ -d "$(VENV_DIR)" ]; then source $(VENV_DIR)/bin/activate && pip freeze > .backup/requirements/pip_freeze.$(shell date +%Y%m%d_%H%M%S).txt; fi

status: ## Show environment status
	@echo "📊 Aurora CloudBank Status"
	@echo "========================="
	@echo "Python: $(shell python3 --version 2>/dev/null || echo 'Not found')"
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "Virtual Environment: ✅ Active"; \
		echo "Pip: $(shell source $(VENV_DIR)/bin/activate && pip --version | cut -d' ' -f2)"; \
	else \
		echo "Virtual Environment: ❌ Not found"; \
	fi
	@if [ -f ".env_status.json" ]; then \
		echo "Setup Status: $(shell cat .env_status.json | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"; \
	else \
		echo "Setup Status: ⚠️  Unknown"; \
	fi

security: validate ## Run comprehensive security scans
	@echo "🔒 Running Aurora CloudBank Security Scans..."
	@source $(VENV_DIR)/bin/activate && pip install safety bandit --quiet
	@echo "1. Dependency vulnerability scan:"
	@source $(VENV_DIR)/bin/activate && safety check --json --output .backup/security/safety_report.json 2>/dev/null || echo "⚠️ Some vulnerabilities detected - check .backup/security/safety_report.json"
	@echo "2. Code security analysis:"
	@source $(VENV_DIR)/bin/activate && bandit -r . -f json -o .backup/security/bandit_report.json --exclude .venv,.backup,node_modules 2>/dev/null || echo "⚠️ Security issues detected - check .backup/security/bandit_report.json"
	@mkdir -p .backup/security
	@echo "✅ Security reports generated in .backup/security/"

clean: ## Clean up build artifacts and temporary files
	@echo "🧹 Cleaning Aurora CloudBank environment..."
	@rm -rf $(VENV_DIR)
	@rm -rf .pytest_cache htmlcov *.egg-info build/ dist/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Environment cleaned"

help: ## Show available targets
	@echo "Aurora CloudBank Development Commands:"
	# Quicksave targets
quicksave: ## Create a quicksave snapshot (usage: make quicksave DESC="description")
	@python3 tools/quicksave.py create "$(DESC)" --focus "Session work" --next "Continue from here"

quickload: ## Load current quicksave and display reconstitution brief
	@python3 tools/quicksave.py load

quicklist: ## List all available quicksaves
	@python3 tools/quicksave.py list

help: ## Show this help message
	@echo 'Aurora CloudBank Symbolic System - Available targets:'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

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
