# Symbolic Anchor Export & DLP Tagging

This module exports symbolic anchor manifests for all cryptographic operations, supporting DLP compliance, reliquary indexing, and simulation traceability.

## Anchor Export
- Anchor manifests are exported as JSON files with symbolic tags (e.g., SRB, T1), operation anchors, timestamps, and simulation state.
- Anchor files are named with a prefix and timestamp, e.g., `anchor_decrypt_1687654321000.json`.

## DLP Tagging
- DLP_TAGs are included in anchor manifests for compliance and audit.

## CLI Chaining & Reliquary Indexing
- CLI outputs anchor file paths for downstream tools (e.g., simulation snapshot, glyphcard generation).
- Downstream tools can watch for new anchor files and process them for reliquary indexing or diffing.

## Memory Sealing Protocol
- Sensitive buffers are wiped (set to null) after use.
- For true zeroization, use Buffer.fill(0) for Node.js Buffers.

## Glyphcard/Diff Tooling
- Automated tools can scan for new anchor files and generate glyphcards (summaries, diffs, or visualizations).
- Example: `node scripts/glyphcard_gen.js anchor_decrypt_*.json`

---

For more advanced glyphcard/diff tool templates or automation scripts, see `scripts/glyphcard_gen.js`.
