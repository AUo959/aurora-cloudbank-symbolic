# Infallible Codespaces Initialization

This guide describes the self-healing bootstrap process used by the Aurora repository.

## Overview

The script `scripts/infallible_codespace_init.py` is executed automatically when a Codespace is created. It installs all dependencies with automatic retries and runs the onboarding script. Each step has three fallbacks, ensuring that common network hiccups or package issues do not interrupt the build.

You can re-run the bootstrap script at any time:

```bash
python3 scripts/infallible_codespace_init.py
```

If a step fails after all retries the script will continue with the next step so the development environment remains usable.
