# Character identity continuity and assignment provenance

## Authority and scope

CanonRec controls Aurora character identity authority. CloudBank's
`config/l1_character_identity_registry.json` is a non-authoritative runtime
overlay: it resolves historical references, preserves assignment history, and
prevents duplicate-person creation. It cannot create a canon person, resolve a
canon dispute, or override a CanonRec entity record.

Every resolved person has a stable CanonRec entity key independent of a
department identifier, role, clearance, title, or staffing seat. Assignment
identifiers may change over time; persona continuity remains attached to the
stable person.

```text
stable person identity
ORION.ENTITY.0039 (Tobias Qin)
        |
        +-- roster v1.1: ENG_010, L3_RESEARCH, Operations Staff
        |
        `-- roster v1.4: SIM_002, L3_TECHNICAL,
                         Simulation & Cognitive Systems (current)
```

The effective dates of the two Tobias records are the same because both
changes landed on 2025-11-09. Their roster-version sequence establishes the
supersession order; the runtime must not infer a more precise timestamp.

## Resolution contract

`simulation/character_identity.py` validates and resolves:

- the stable CanonRec entity key;
- the preferred name and approved name variants;
- current and historical assignment identifiers;
- ordered role, division, and clearance history with source provenance;
- unresolved references that must fail closed.

`simulation/character_loader.py` retains the identifier found in the source as
`source_character_id`, while `character_id` becomes the current assignment ID
and `stable_entity_key` carries person continuity. Consequently, a historical
`ENG_010` document resolves to Tobias Qin at `ORION.ENTITY.0039` and current ID
`SIM_002`; it does not instantiate a second Tobias.

Roster validation examines every parsed profile, including profiles that share
a display name. If historical and current IDs resolve to the same stable entity
in separate sections, validation reports duplicate-person creation caused by an
ID migration.

## Sorensen reference quarantine

CanonRec and Command & Ethics sources identify Prof. Elena Sorensen as
`ORION.ENTITY.0010` / `ETH_003`. Later Phase-3 collaborator prose contains
`Prof. Karl Sorensen`, but no independent person or entity record was found.
That reference is therefore `quarantined_unresolved_reference`:

- it is not an approved alias for Elena;
- it is not evidence for a separate Karl entity;
- the loader must not instantiate a person from it;
- the overlay records Elena only as a possible referent, not a resolution.

CanonRec review may later resolve the wording. Until then, new material should
use Prof. Elena Sorensen where that identity is supported or preserve the Karl
text as explicitly historical/conflicted provenance.

## Identity versus role and seat continuity

A stable identity answers *who is this?* A role or staffing seat answers *what
assignment exists, and who occupies it now?* They have separate lifecycles:

- a person can retain one entity key through promotion, transfer, leave, or ID
  migration;
- a seat can be created, reassigned, vacated, or retired without creating or
  deleting a person;
- a progressive run-state persona may accumulate observations without changing
  the canon identity;
- a new run-scoped staff record remains non-canonical until the independent
  canon-promotion process establishes an identity.

This separation lets future HR and progressive-persona work reuse the same
identity layer without treating organizational changes as new people.

## Change procedure

1. Establish or change person identity in CanonRec through its review process.
2. Refresh the CloudBank provenance boundary through the Aurora root workflow.
3. Add an ordered assignment record with exact source paths and confidence.
4. Preserve superseded identifiers; do not rewrite historical documents merely
   to make their assignment IDs look current.
5. Run the identity schema, resolver, duplicate-person, and canon-consistency
   tests before publishing a CloudBank projection update.
