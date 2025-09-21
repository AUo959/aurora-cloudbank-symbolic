Runtime live thread diagnostics

This folder contains ephemeral, runtime-generated diagnostics. These files should not be tracked in Git.

- Files: `diagnostics.json` and other `*.json`
- Purpose: transient state for local runs (counters, timestamps)
- Git: this directory’s `*.json` files are ignored via root `.gitignore`

If you need a template, see `diagnostics.sample.json`.
