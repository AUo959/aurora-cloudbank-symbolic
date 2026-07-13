# API Catalog Governance

**Status:** Active governance decision
**Last reviewed:** 2026-07-13
**Inventory:** `docs/api/api_surface_inventory.json`

## Decision

CloudBank uses a primary FastAPI application plus declared standalone services.
The main API catalog is not monolith-only, and it is not free-form
multi-service sprawl. Every active HTTP or WebSocket service must have an owner,
entrypoint, mount path, runtime class, and status in
`docs/api/api_surface_inventory.json`.

Decision label:

```text
primary-fastapi-with-declared-standalone-services
```

## Source of Truth Order

For API catalog claims, use this order:

1. Committed runtime entrypoints and routers
2. `docs/api/api_surface_inventory.json`
3. Generated OpenAPI/catalog snapshots under `docs/api/`
4. Human-facing docs and historical reports

If generated snapshots disagree with current router code, mark the snapshot as
stale and regenerate it. Do not repeat the stale route as current.

## Required Inventory Fields

Each inventory entry must include:

- `id`
- `owner`
- `runtime`
- `entrypoint`
- `mount_path`
- `service_class`
- `status`
- `status_evidence`
- `notes`

## Status Semantics

| Status | Meaning |
| --- | --- |
| active | Included or launched by committed runtime evidence without optional dependency gating. |
| active-optional | Included by the main app through guarded import or optional dependency handling. |
| active-standalone | Runs as a separate service or helper and is not mounted into the main app. |
| superseded | Kept for compatibility or tests, but no longer the route authority. |
| test-only | Mounted or exercised by tests only. |
| inactive-unverified | Present in repo, but no current production or operator mount was verified. |
| generated-snapshot | Derived catalog output; useful for details, not ownership authority. |

## Current Governance Notes

- `api/aurora_api.py` is the main FastAPI app and owner of the primary HTTP
  aggregation surface.
- Monitoring is now active in the main app through `/monitoring`, `/sentinel`,
  `/api/drift`, and `/r2-telemetry` entries.
- HR is split by function: `/rd` is R&D productization, while `/hr_system` is
  staffing and character generation.
- `src/servers/l2_integration_server.py` is the canonical Mesh Runtime V1
  service surface for `/api/mesh/*`, `/api/bridge/*`, and `/ws/mesh`.
- `src/api/mesh_api.js` is not the current production mesh authority based on
  repo evidence. It is a legacy Express router and test target.
- `src/bridge/enhanced_api_bridge.js` is a compatibility bridge, superseded as
  route authority by the Python mesh runtime unless a deployment surface later
  mounts it explicitly.
- `docs/api/API_CATALOG.json` and `docs/api/api_schema.json` are generated
  snapshots. `API_CATALOG.json` records `generated_at` and `source_commit`;
  `api_schema.json` records the same values as `x-generated-at` and
  `x-source-commit`. Use them for route detail only after completing the
  currency check below.

## Snapshot Currency Check

The generated metadata identifies the runtime commit that was assembled, not
the commit that later stored the generated files. Verify all of the following:

1. The timestamp and source commit agree across both generated JSON files.
2. The source commit exists and is an ancestor of the checkout being reviewed.
3. No route-bearing files under `api/`, `modules/`, or `src/` changed after the
   source commit. If they did, inspect the changes and regenerate when any HTTP
   or WebSocket surface changed.

The catalog's `total_routes` is the number of OpenAPI paths. The `routes` array
contains one record per supported HTTP operation, so its length can be larger.
Neither count proves inventory ownership coverage.

## Update Workflow

1. Add or modify the runtime router or service entrypoint.
2. Update `docs/api/api_surface_inventory.json` with owner, mount, status, and
   evidence.
3. Update `docs/architecture/RUNTIME_PATH_DRIFT_LEDGER.md` if older docs,
   commands, or routes now conflict.
4. Regenerate OpenAPI/catalog snapshots when route-level detail changed with
   `python3 scripts/generate_api_catalog.py`. The default output is the tracked
   `docs/api/` directory, independent of caller working directory.
5. Run `python3 -m pytest -q tests/test_api_surface_inventory.py` for inventory
   schema, required-field, and named regression checks. This is a structural
   test, not a complete comparison with live router registrations. Automated
   router-coverage validation is tracked in issue #1204.

## 2026-07-13 Review Receipt

- Issues #1142, #1144, and #1145 were resolved before this review.
- The catalog and schema snapshots were regenerated with matching timestamps
  and source commit metadata.
- Mesh-agent routes, the QGIA forecast router, the read-only PAT terminal
  overlay, and the unimplemented RD consent contract were reconciled in #1144;
  consent implementation remains explicitly tracked in #1200.
- A manual comparison of `api/aurora_api.py` router registrations with the
  inventory found and added four omitted active routers: L1 Station, Sensor
  Array, Checkpoint Vault, and CASK.
- The existing inventory test was confirmed to be structural rather than a
  completeness proof. Issue #1204 tracks a deterministic router-coverage
  validator; until it lands, every review must include the manual comparison.

## Review Cadence

Review this inventory when:

- A router is added to or removed from `api/aurora_api.py`.
- A standalone service gains operator or deployment support.
- A generated API snapshot is refreshed.
- A stale docs issue cites conflicting route or command paths.
