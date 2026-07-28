# Universal Thread Beacon Field Ownership

**Status:** Proposed design for issue #1377  
**Scope:** Schema, mapping, and offline validation only

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
| Beacon profile, mapping, compatibility, deterministic serialization | #1377 |

The beacon references these records. It does not copy or redefine their authority.

## Classification rule

The profile preserves independent dimensions:

- canon status;
- layer;
- execution mode;
- evidence authority;
- data treatment;
- determinism;
- implementation status;
- deployment status.

Import, export, profile rendering, or compatibility transformation may not silently change any of these dimensions.

## Integrity rule

The current capsule `compute_signature()` output is a SHA-256 content digest. The beacon maps it to integrity semantics.

A verified cryptographic signature requires a separate key-backed signature record with signer identity, algorithm, verification evidence, and revocation posture. A digest, anchor, seal, or repository relationship is not authentication or permission.

The example beacon does not claim package-level integrity verification. Its `integrity_status` remains `unverified` until a real digest-bearing package record is supplied. Required included or externally referenced deliverables must carry a resolvable integrity reference.

## Compatibility behavior

- Unsupported major schema versions fail clearly.
- Compatible unknown extension fields are preserved.
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

Its canonical JSON SHA-256 is:

```text
13a5c6bf5806d2129a43db58ef8f7a16ec638cd0ca5929d16997b8dd9e7f1633
```

This digest verifies deterministic serialization of the fixture. It does not prove signer identity, package preservation, replay, transfer, or restoration.
