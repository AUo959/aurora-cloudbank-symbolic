# Legacy Asset Inventory

**Issue:** #1375  
**Status:** Proposed read-only Phase 0 implementation

## Purpose

`tools/salvage/inventory_legacy_assets.py` inventories supplied legacy Aurora/GUMAS artifacts without applying migration or executing recovered content.

The output is a proposed-disposition report. It is not canon promotion, implementation evidence, or permission to use an artifact.

## Source-custody boundary

The inventory:

- reads regular source files without modifying them;
- refuses to write its report inside the inventoried source tree;
- records file and directory symlinks without following them;
- records FIFOs, sockets, devices, and other non-regular entries as blocked without opening them;
- records unreadable-directory traversal failures rather than silently omitting subtrees;
- calculates SHA-256 digests for files within configured limits;
- treats unreadable, oversized, suspicious, and unsupported content as blocked or quarantined;
- never extracts archive content to disk;
- never executes scripts, binaries, prompts, manifests, or configuration;
- never resolves secret references;
- never applies a migration mapping.

Use an output path outside the source package:

```bash
python tools/salvage/inventory_legacy_assets.py \
  /path/to/read-only-source \
  --output /separate/report-location/inventory.json
```

## Archive posture

Phase 0 safely inspects ZIP metadata and eligible member bytes in memory only.

Before constructing Python's `ZipFile` object, the tool performs a bounded End of Central Directory preflight. That preflight rejects archives whose declared entry count or central-directory size exceeds configured limits, so the count gate operates before the standard library materializes every member record.

It blocks:

- malformed or missing End of Central Directory metadata;
- multi-disk ZIPs;
- ZIP64 metadata, pending a separately reviewed bounded parser;
- central directories exceeding the configured byte limit;
- absolute member paths;
- `..` traversal;
- symlink and special-file members;
- duplicate member paths that create ambiguous custody records;
- nested archives;
- archives exceeding the configured member-count limit;
- members exceeding configured size;
- archives exceeding configured total uncompressed size;
- suspicious compression ratios;
- member size mismatches;
- unreadable members.

Unix executable mode bits on ZIP members are preserved as safety signals. Executable archive members are categorized as `executable` and quarantined consistently with executable filesystem files.

All numeric limits must be finite and positive. Values such as `NaN` are rejected rather than silently disabling a guard.

Other archive formats are inventoried as outer files and marked `unsupported_archive`. They are not extracted or parsed in this phase.

## Classification and disposition

Artifacts receive a content category:

- `code`;
- `data`;
- `documentation`;
- `generated_media`;
- `configuration`;
- `archive`;
- `executable`;
- `unknown`.

They also receive a proposed disposition:

- `retain_review`;
- `archive`;
- `review`;
- `quarantine`;
- `blocked`.

These values are recommendations for review. They do not alter source custody or establish canon status.

## Secret handling

The tool uses conservative filename and content heuristics to flag potential secrets. Reports contain flags, hashes, sizes, paths, and classifications—not matched secret values.

A heuristic match is not proof that a valid credential exists. Absence of a match is not proof that a package is secret-free.

Provider-side credential safety cannot be inferred from repository or package inspection.

## Artifact identity and duplicate detection

Filesystem artifact identity includes source kind, relative path, digest, and size. Archive-member identity additionally includes the containing archive path. Identical member paths and bytes in different archives therefore remain distinct custody records.

Exact duplicate groups are based on matching SHA-256 digests from physical filesystem files and eligible archive members. Projection records such as unsupported-archive notices are excluded so they cannot create false duplicate groups. Duplicate groups contain unique artifact IDs.

Duplicate paths inside the same ZIP are blocked as ambiguous rather than being assigned colliding inventory records. Likely or semantic duplicates remain future work and must not be inferred from names alone.

## Determinism

Artifact ordering, artifact identifiers, duplicate groups, and `report_id` are deterministic for a stable source tree and configured limits.

`generated_at` is intentionally excluded from `report_id`, allowing custody reports generated at different times to identify the same observed source state.

## Existing selective-integration manifest

`manifests/selective_integration/modules_manifest.json` is treated as historical planning input:

```yaml
canon_status: historical_state
evidence_authority: reference_evidence
migration_role: legacy_candidate_manifest
trusted_for_mutation: false
```

Its scores, specialist names, telemetry proposals, risk notes, and backout plans may be preserved as historical context. They are not accepted migration decisions or current technical evidence.

## Explicit non-goals

This phase does not:

- migrate files;
- rewrite registries;
- delete duplicates;
- execute recovered code;
- validate historical metrics;
- activate commands, capsules, relays, or workflows;
- promote conversation or archive material into canon;
- change L1/L2/L3 authority;
- change GUMAS deterministic behavior.
