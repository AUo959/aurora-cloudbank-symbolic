# SHERLOCK / WATSON protocol core

This directory contains the provider-neutral integrity core for the standalone
SHERLOCK and WATSON products.

- **SHERLOCK** seals a provenance-sensitive evidence record as
  `opal2.sherlock.casefile.v1`.
- **WATSON** binds contextual synthesis to the exact SHERLOCK digest as
  `opal2.watson.brief.v1`.
- **Verify** recomputes the complete `opal2.sherlock-watson.bundle.v1` digest
  chain and fails closed if either evidence or analysis was changed.

The core intentionally performs no web retrieval and calls no language model.
Those concerns belong to provider adapters. This keeps the evidence boundary
portable and prevents a model vendor, Aurora runtime, or connector choice from
becoming part of the product's truth contract.

See `docs/architecture/OPAL2__PRODUCT_SPEC__SHERLOCK_WATSON__v1.0__2026-08-07.md`.
