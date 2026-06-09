# Dependency Workflow

## Overview

Aurora uses a two-file dependency system to balance flexibility with reproducibility.

## Files

- **`requirements.txt`** — Human-edited floor constraints (e.g. `fastapi>=0.118.0`). Edit this when adding or upgrading a dependency.
- **`requirements-lock.txt`** — Machine-generated, fully-pinned snapshot (`pip freeze | sort`). Never edit by hand. Commit alongside `requirements.txt` changes.

## How to Add or Upgrade a Dependency

1. Edit `requirements.txt` with the new package or updated constraint.
2. Install: `pip install -r requirements.txt`
3. Regenerate the lock file: `pip freeze | sort > requirements-lock.txt`
4. Commit both files together.

## CI Drift Check

The CI workflow (`aurora-ci-minimal.yml`) includes a non-blocking step that compares the committed `requirements-lock.txt` against the packages actually installed in the CI environment. If they differ, a warning is emitted but the build is **not** blocked (`continue-on-error: true`).

This makes environment drift visible without preventing merges during transitional periods.
