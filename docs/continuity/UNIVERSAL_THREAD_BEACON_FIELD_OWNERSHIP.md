# Universal Thread Beacon Field Ownership

**Status:** Proposed design for issue #1377  
**Scope:** Bound minimum-profile schema, mapping, and offline validation only

## Purpose

The Universal Thread Beacon is a neutral entry-point view over an existing continuity package. It does not replace the package, identity, policy, ledger, or presentation systems it references.

## Ownership map

| Beacon surface | Authoritative owner |
|---|---|
| Continuity object identity and relationships | #1368 |
| Deliverable bytes, inventory, integrity, checkpoints, restore staging, reconciliation, rollback | #1374 |
| Legacy package inventory and migration custody | #1375 |
| Sourced summaries, semantic anchors, confidence, drift | #1371 |
| Symbolic names, glyphs, lore, and presentation aliases | #1372 |
| Command execution contracts and receipts | #1373 |
| Trust, consent, authorization, retention, revocation, deletion, execution risk | `AUo959/Aurora_ORIONCORE_Directory_Main#46`, implemented through #1380 |
| Beacon profile, mapping, compatibility, canonical serialization | #1377 |

The beacon references these records. It does not copy or redefine their authority.

## Schema binding

The offline reader accepts only the committed UTB schema identity:

```text
specification: UTB-PS-001
schema version: 1.0.0
schema id: https://raw.githubusercontent.com/AUo959/aurora-cloudbank-symbolic/main/schemas/continuity/universal_thread_beacon.schema.json
```

A syntactically valid but unrelated JSON Schema cannot establish UTB conformance. Future schema versions require an explicit reader update and compatibility decision.

## Profile scope

Version 1.0.0 defines the `minimum` profile only. The name `full` remains reserved until its required manifests, policy records, integrity records, and completeness behavior are specified and tested. A beacon claiming `profile: full` fails validation in this version.

## Classification rule

The profile preserves independent dimensions:

- canon status;
- residency layer;
- operational scope layers;
- execution mode;
- evidence authority;
- data treatment;
- determinism;
- implementation status;
- deployment status.

Residency answers where the represented continuity object belongs. Operational scope identifies which layer records or work it is explicitly scoped to serve. Scope does not grant authority, and neither field may be inferred from the other.

Import, export, profile rendering, or compatibility transformation may not silently change any classification dimension.

## Integrity rule

The current capsule `compute_signature()` output is a SHA-256 content digest. The beacon maps it to integrity semantics.

A verified cryptographic signature requires a separate key-backed signature record with signer identity, algorithm, verification evidence, and revocation posture. A digest, anchor, seal, or repository relationship is not authentication or permission.

The example beacon does not claim package-level integrity verification. Its `integrity_status` remains `unverified` until a real digest-bearing package record is supplied. Required included or externally referenced deliverables must carry a resolvable integrity reference.

## Compatibility and canonicalization

- The reader enforces `compatibility.minimum_reader_version`.
- The profile declares `canonicalization: utb-json-subset-v1`.
- The canonical subset permits null, booleans, strings containing Unicode scalar values, arrays, objects with printable-ASCII keys, and integers in the range `-9007199254740991` through `9007199254740991`.
- Floating-point values, non-finite values, oversized integers, duplicate keys, non-ASCII object keys, invalid UTF-8, and lone surrogates fail validation.
- These restrictions avoid implementation-specific numeric rendering and key-order behavior across compatible readers.
- Compatible unknown extension fields are preserved only when they conform to the canonical subset.
- Transformations and losses are recorded.
- Required deliverables fail validation when unavailable or intentionally omitted.
- Included and externally referenced deliverables require integrity references.
- Schema validation proves declaration conformance only.

## Non-activation boundary

The initial implementation does not:

- create another archive format;
- execute referenced content;
- restore state;
- replay or inherit context;
- activate a relay or network operation;
- resolve secrets;
- grant authorization;
- promote content into canon;
- change GUMAS behavior.

## Deterministic fixture

`docs/continuity/universal_thread_beacon.example.json` is a proposed-design fixture mapped from the current capsule surface at baseline `84a361019312660cada1cbfce91ddf6203569a21`.

Its `utb-json-subset-v1` SHA-256 is:

```text
7f2999044964283108b44cd739e40a16309d1d9aea3bcca78f03e5d85f9e6ed9
```

This digest verifies canonical serialization of the fixture under the declared subset. It does not prove signer identity, package preservation, replay, transfer, or restoration.
