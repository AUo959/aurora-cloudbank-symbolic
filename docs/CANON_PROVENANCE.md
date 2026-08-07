# Canon provenance and repository boundary

## Authority chain

CanonRec is the authority repository for Aurora / ORIONCORE canon. CloudBank is
the runtime repository and carries checked-in mirrors so that a standalone
application checkout remains reproducible.

```text
AUo959/CanonRec
  canon/L3/canonical_validation.yaml
       |
       | Aurora root tools/canon_sync.py
       v
AUo959/aurora-cloudbank-symbolic
  config/canonical_validation.yaml
       |
       v
  runtime and tests/test_canon_consistency.py
```

The Aurora root also generates managed files under `config/mesh/memory/` from
its newest L1 entity ledger. Those generated memories are a separate payload
family; they are not direct copies of CanonRec files.

## Current verified snapshot

| Field | Value |
| --- | --- |
| CanonRec repository | `https://github.com/AUo959/CanonRec` |
| CanonRec revision | `c1f25e57a99ed98f8df6ed8eb2a93ba94bd2aa14` |
| Source path | `canon/L3/canonical_validation.yaml` |
| CloudBank mirror | `config/canonical_validation.yaml` |
| Source and mirror SHA-256 | `c0604d68b3d2a0e8d35336caa4e8275ca0d19409a43f23d6f65e43dbf04c7cd6` |
| Verified | 2026-07-29 |

The machine-readable form is `config/canon_provenance.json`. Its CloudBank
hashes are enforced by `tests/test_canon_provenance.py`. The cross-repository
source/destination comparison is enforced from the Aurora root workspace.

## Runtime requirement

A CanonRec checkout is not a package, import, mount, or startup dependency for
the base CloudBank FastAPI application. The checked-in mirror is sufficient for
startup and local consistency tests.

CanonRec is required when:

- authoritative canon is reviewed, promoted, or reconciled;
- a mirror is refreshed;
- the Aurora root runs its complete CloudBank + CanonRec L1 integration suite;
- a reviewer needs to trace a CloudBank canon claim to its authority source.

## Unreconciled staff registry

The following files are materially different and are not currently part of the
managed propagation contract:

- CanonRec: `canon/L1/station/ORION_STATION_CANONICAL_STAFF_REGISTRY.json`
- CloudBank: `ORION_STATION_CANONICAL_STAFF_REGISTRY.json`

Their current hashes are recorded in `config/canon_provenance.json`. The
CloudBank file identifies itself as a reconstructed registry, while the
CanonRec file is an older v2.4.1 manifest. Selecting one, or defining a
deterministic merge, requires an owner authority decision. Until then, neither
file should be presented as the sole machine-readable staff SSOT.

## Refresh procedure

From the canonical Aurora root workspace:

```bash
python3 tools/canon_sync.py --check
```

When CanonRec legitimately changes, use the root propagation workflow to stage
the CloudBank update, refresh `config/canon_provenance.json`, run the CloudBank
canon/provenance tests, and carry the result through normal branch and CI
review. Do not copy authority files manually without updating provenance.
