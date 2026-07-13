# Recovered Protocol Fixtures

This directory contains **sanitized canonical example fixtures** for each recovered ethics protocol. They serve as the authoritative reference shape for schema validation, test tooling, and onboarding.

## What a fixture is

A fixture is a single-protocol JSON document that:
- Contains **all required fields** from `custody_record.schema.json` and the per-protocol structure defined in `recovered_protocol_manifest.schema.json`
- Represents the **correct shape** of a fully-populated entry — not a live custody record
- Uses `PENDING` for all hash/date fields that have not yet been verified
- Is **schema-valid** at all times — if a fixture fails schema validation, it is a bug in the fixture, not the schema

## What a fixture is not

- Not a live custody record — do not treat PENDING fields as verified
- Not runtime authorization — no fixture here activates enforcement wiring
- Not the live manifest — the live manifest is at `docs/ethics/recovered_protocols/recovered_protocol_manifest.json`

## Intake rules

1. **One file per protocol.** Filename must be `{protocol_id}.fixture.json`.
2. **All 11 `custody_record` fields must be present.** Missing fields are a schema error.
3. **Hash fields must be `PENDING` or a valid 64-char lowercase hex string.** No freeform strings.
4. **`verification_date` must be `PENDING` or `YYYY-MM-DD`.** No other formats.
5. **`promotion_decision` must be a valid enum value.** See `custody_record.schema.json` for the full list.
6. **SHADOWFAX only:** `source_classification` must be `missing_dependency` and `promotion_decision` must be `blocked_pending_bundle_location`. This is schema-enforced.
7. **Moriarty only:** `unresolved_blockers` must include the HARD BLOCK annotation until containment tests pass.

## Filling a fixture when real custody data becomes available

When a source package is located and hash-verified:

1. Update `source_package_name` to the real package name.
2. Update `source_package_sha256` to the verified 64-char hex hash.
3. Update `internal_file_path` to the real path inside the package.
4. Update `internal_file_sha256` to the verified 64-char hex hash.
5. Update `verification_date` to `YYYY-MM-DD`.
6. Update `reviewer_or_agent_surface` to the reviewer's name or agent surface ID.
7. Remove resolved items from `unresolved_blockers`. If all blockers are resolved, set to `[]`.
8. Update `promotion_decision` per the wiring gate in `recovered_protocol_manifest.json`.
9. Re-run schema validation before committing.

Do **not** update `promotion_decision` to `approved_for_runtime_wiring` without operator approval and all wiring gate conditions met.

## Validation

```bash
# Validate a single fixture's custody_record
ajv validate \
  -s docs/ethics/recovered_protocols/schemas/custody_record.schema.json \
  -d docs/ethics/recovered_protocols/fixtures/sherlock.fixture.json \
  --spec=draft2020

# Validate the live manifest (which embeds all custody_records)
ajv validate \
  -s docs/ethics/recovered_protocols/schemas/recovered_protocol_manifest.schema.json \
  -d docs/ethics/recovered_protocols/recovered_protocol_manifest.json \
  --spec=draft2020
```

## SHADOWFAX notice

The SHADOWFAX standalone bundle has not been located. `shadowfax.fixture.json` has:
- `source_classification: missing_dependency`
- `promotion_decision: blocked_pending_bundle_location`

This state is schema-enforced (see `custody_record.schema.json` `if/then` branch). Any change to SHADOWFAX's `promotion_decision` requires the bundle to be located, hash-verified, and operator-approved first.

## Schema references

- `../schemas/custody_record.schema.json` — validates the `custody_record` object
- `../schemas/recovered_protocol_manifest.schema.json` — validates the full manifest
- `../schemas/validate_manifest.test.json` — test fixture with positive and negative cases
