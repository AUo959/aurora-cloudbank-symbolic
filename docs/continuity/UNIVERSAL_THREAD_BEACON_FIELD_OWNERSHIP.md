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

## Compatibility behavior

- Unsupported major schema versions fail clearly.
- Compatible unknown extension fields are preserved.
- Transformations and losses are recorded.
- Required deliverables fail validation when unavailable or intentionally omitted.
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
317e046c81f69bb15d1978274f3f9be4d63d9e5d5f1c8806114e9ae4396c39aa
```

This digest verifies deterministic serialization of the fixture. It does not prove signer identity, package preservation, replay, transfer, or restoration.
