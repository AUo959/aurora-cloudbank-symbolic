# Canon provenance and repository boundary

## Authority chain

CanonRec is the authority repository for Aurora / ORIONCORE canon. CloudBank is
the runtime repository and carries checked-in mirrors and runtime projections so
that a standalone application checkout remains reproducible.

```text
AUo959/CanonRec
       |
       | canon authority
       v
Aurora root propagation / integration gates
       |
       v
AUo959/aurora-cloudbank-symbolic
  checked-in mirrors + non-authoritative runtime projections
```

CloudBank material may be operationally richer or shaped differently for
runtime use. That does not make a differing CloudBank projection an independent
canon authority.

## Current verified canonical-validation mirror

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
the base CloudBank application. Checked-in mirrors/projections permit local
runtime startup.

CanonRec is required when:

- authoritative canon is reviewed, promoted, or reconciled;
- a managed mirror is refreshed;
- the Aurora root runs its complete CloudBank + CanonRec integration suite;
- a reviewer needs to trace a CloudBank canon claim to its authority source.

## Staff-registry authority decision — 2026-08-08

The prior state correctly observed that these files are materially different:

- CanonRec: `canon/L1/station/ORION_STATION_CANONICAL_STAFF_REGISTRY.json`
- CloudBank: `ORION_STATION_CANONICAL_STAFF_REGISTRY.json`

The unresolved question was **authority**, not byte equality. The owner decision
for L1 preflight is now:

> **CanonRec controls staff canon authority. The CloudBank registry is a
> provenance-bound runtime projection and is not an independent staff SSOT.**

This resolves the authority blocker without pretending the two files are
identical or mechanically merging them.

Machine-readable status lives in `config/canon_provenance.json` under
`resolved_surfaces`.

## Orbital-locus authority decision — 2026-06-13

CanonRec's owner ruling in
`canon/L1/station/STATION_PURPOSE_DEFINITION.md` establishes that Orion Station
is stationed at a Lagrange point in real space. CloudBank projects that ruling
into `config/l1_runtime_baseline.json` as
`resolved_siting_class_exact_point_unresolved`.

This resolves the broad siting conflict without overclaiming precision:

- `38,600 km` remains a STAGING datum and is not current siting authority;
- `Earth-Moon L4` remains a historical named candidate, not exact current canon;
- the exact point/system, range, and exact one-way light-time remain unresolved;
- CanonRec's approximate nonzero latency model is usable only with `APPROX`
  certainty and a positive advancement window.

The authority and projection hashes are recorded under the
`orion_station_orbital_locus` resolved surface in
`config/canon_provenance.json`.

### Conflict behavior

If the CanonRec authority record and the CloudBank runtime projection disagree:

1. do not silently choose the CloudBank value as canon;
2. preserve the CloudBank value as provenance-labeled runtime/reference data if
   it remains operationally useful;
3. quarantine the conflicting field from canon-sensitive causality where
   necessary;
4. reconcile/promote through the normal canon workflow;
5. do not fabricate a third value merely to make the files agree.

The authority decision therefore removes the previous
`owner_authority_decision_required` startup blocker while preserving evidence.

## L1 runtime baseline

`config/l1_runtime_baseline.json` is the machine-readable preflight contract for
the first live L1 run. It records:

- CanonRec authority;
- the staff projection boundary;
- the Earth-side Pilot boundary;
- typed population uncertainty;
- canonical Lagrange-point siting with exact-point uncertainty;
- historical `SIMULATION_STATE.json` as non-genesis provenance;
- canonical Phase-1 benchmark v2;
- Picard_Delta_3 / Triplex fail-closed requirements.

This baseline does not promote CloudBank runtime facts into CanonRec.

## Refresh procedure

From the canonical Aurora root workspace:

```bash
python3 tools/canon_sync.py --check
```

When CanonRec legitimately changes, use the root propagation workflow to stage
CloudBank mirror/projection updates, refresh `config/canon_provenance.json`, run
canon/provenance tests, and carry the result through normal branch and CI
review. Do not copy authority files manually without updating provenance.
