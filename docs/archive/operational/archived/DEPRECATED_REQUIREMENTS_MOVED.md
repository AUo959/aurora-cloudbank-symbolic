# Deprecated Requirements Files

These files have been consolidated into the main `requirements.txt` file in the project root.

## Files moved to avoid conflicts:
- `requirements.txt` → `requirements-deprecated.txt`
- `requirements-test.txt` → `requirements-test-deprecated.txt`

## Consolidation details:
All dependencies have been merged into:
- `/requirements.txt` - Main production and development dependencies
- `/requirements-optional.txt` - Optional enhanced dependencies with fallbacks
- `/pyproject.toml` - Build configuration and tool settings

The setup.py file has been updated to reference the main requirements.txt instead of duplicating dependencies.