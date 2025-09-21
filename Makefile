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

# Staged lint targets for tracking
.PHONY: lint-stage1
lint-stage1:
	# Stage 1: Whitespace and formatting issues
	flake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=W293,E303,E302

.PHONY: lint-stage2  
lint-stage2:
	# Stage 2: Import issues
	flake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=F401,F811

.PHONY: lint-stage3
lint-stage3:
	# Stage 3: Undefined names and logic errors
	flake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=F821,E999

.PHONY: lint-stage4
lint-stage4:
	# Stage 4: Line length issues
	flake8 modules/opal2 modules/cask src/core src/bridges src/servers --max-line-length=120 --extend-ignore=E203,W503 --select=E501

.PHONY: lint-tracking
lint-tracking:
	# Generate lint tracking report
	python scripts/lint_tracking_manager.py --report
