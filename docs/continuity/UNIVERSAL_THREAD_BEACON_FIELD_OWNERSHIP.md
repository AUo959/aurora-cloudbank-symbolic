# Universal Thread Beacon Field Ownership

- **Status:** Proposed design for issue #1377
- **Scope:** Bound minimum-profile schema, mapping, and offline validation only

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

The command-line reader loads only the schema committed at:

```text
schemas/continuity/universal_thread_beacon.schema.json
```

Validation is bound to the complete parsed contents of that bundled schema, not merely to self-asserted metadata. A copied `$id`, specification marker, or version marker cannot make a relaxed or unrelated schema authoritative. The bundled schema also carries:

```text
specification: UTB-PS-001
schema version: 0.1.0
schema id: https://raw.githubusercontent.com/AUo959/aurora-cloudbank-symbolic/main/schemas/continuity/universal_thread_beacon.schema.json
```

Future schema contents or versions require an explicit reader update and compatibility decision.

## Profile scope

Version 0.1.0 defines the `minimum` profile only. The name `full` remains reserved until its required manifests, policy records, integrity records, and completeness behavior are specified and tested. A beacon claiming `profile: full` fails validation in this version.

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

The reader enforces `compatibility.minimum_reader_version`. Semantic-version components contain at most nine decimal digits, so malformed or adversarially large components fail through a controlled validation result.

The profile declares `canonicalization: utb-json-subset-v1`. This name defines both a value domain and an exact byte encoding.

### Value domain

- null, booleans, strings containing Unicode scalar values, arrays, and objects;
- object keys are printable ASCII from U+0020 through U+007E;
- integers range from `-9007199254740991` through `9007199254740991`;
- floating-point and non-finite values are not permitted;
- duplicate keys, invalid UTF-8, lone surrogates, and unsupported values fail validation;
- compatible unknown extension fields are preserved only when they conform to this domain.

### Canonical byte encoding

- output is UTF-8 without a byte-order mark or trailing newline;
- no insignificant whitespace is emitted;
- object keys are sorted by ascending ASCII code;
- array order is preserved;
- literals are exactly `null`, `true`, and `false`;
- integers use ordinary base-10 notation, with `0` for zero and no exponent or leading plus sign;
- strings are enclosed in quotation marks;
- quotation mark and reverse solidus are escaped as `\"` and `\\`;
- backspace, tab, line feed, form feed, and carriage return use `\b`, `\t`, `\n`, `\f`, and `\r`;
- other U+0000 through U+001F controls use lowercase `\u00xx` escapes;
- every other Unicode scalar value is emitted directly as UTF-8, without optional escaping or Unicode normalization;
- solidus, `<`, `>`, `&`, U+2028, and U+2029 are not escaped unless they fall under another mandatory rule.

These rules make the bytes hashed by compatible readers explicit. A reader that emits `\u003c` for `<`, normalizes Unicode, changes key order, or uses alternate escaping is not producing `utb-json-subset-v1` bytes.

Transformations and losses remain recorded. Required deliverables fail validation when unavailable or intentionally omitted. Included and externally referenced deliverables require integrity references. Schema validation proves declaration conformance only.

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
d2b5b2c564c969d5bc177d6ebb81f50946f2b6c01f9e7f202b5b24c5e37422b6
```

This digest verifies the exact canonical UTF-8 bytes of the fixture under the declared rules. It does not prove signer identity, package preservation, replay, transfer, or restoration.
