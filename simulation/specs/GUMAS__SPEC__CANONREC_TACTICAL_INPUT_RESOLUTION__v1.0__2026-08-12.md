# GUMAS CanonRec Tactical Input Resolution Contract v1.0

**Date:** 2026-08-12  
**Layer:** L2  
**Status:** normative integration contract for deterministic tactical scenarios  
**Applies to:** restored GUMAS v2.0 tactical authority and any bounded physical extension

## Purpose

Make tactical scenarios roster- and polity-substitutable without changing combat code.

The flash-rebellion control fixture remains unchanged: two materially symmetric, medium-sized Galactic Union fleets around Planetoid P17. This contract defines how that fixture, and later variants, resolve ship classes, polity/organization identity, doctrine, technology, and simulation coefficients from CanonRec.

A future scenario may replace one or both rosters with different CanonRec ship classes or a different polity/organization. Such a substitution changes data inputs and the resulting run identity; it must not require a new combat engine or a scenario-specific resolver.

## Core invariant

> Any valid CanonRec polity/organization and ship-class roster may replace the baseline roster without modifying the restored GUMAS combat engine. Only canonical inputs, explicitly versioned derivations, and scenario-local parameters may change.

The scenario fixture names **what participates**. CanonRec defines **what those canonical entities are**. The GUMAS adapter translates those resolved facts into deterministic tactical state. GUMAS resolves the engagement.

```text
Scenario Fixture
      |
      v
CanonRec Snapshot + Resolver
      |
      v
Resolved Tactical Input Manifest
      |
      v
GUMAS Scenario Adapter
      |
      v
Restored GUMAS v2.0 Aggregate Tactical State
      |
      v
Bounded Physical Extension
      |
      v
Deterministic Battle Run
```

## CanonRec surfaces already demonstrated

Current CanonRec contains the entity and doctrine surfaces required for this contract, including:

- `canon/L2/entities/organizations/org_galactic_union.json`
- `canon/L2/entities/ship_classes/cls_judicator.json`
- `canon/L2/entities/ship_classes/cls_aegis.json`
- `canon/L2/entities/ship_classes/cls_palisade.json`
- `canon/L2/entities/ship_classes/cls_sentinel.json`
- `canon/L2/entities/ship_classes/cls_obsidian.json`
- `canon/L2/entities/ship_classes/cls_vanguard.json`
- `canon/L2/entities/ship_classes/cls_peregrine.json`
- `canon/L2/entities/ship_classes/cls_reliant.json`
- additional class records such as Bastion, Leviathan, Vigilant, Diplomatic, and Dreadraider
- `canon/L2/marshals_sentinels/Ship-to-Ship_Combat_Dynamics.csv`
- `canon/L2/marshals_sentinels/Shielding___Propulsion_Systems.csv`
- `canon/L2/fleet/L2_GUMAS_SHIP_REGISTRY__v1.0.md`
- GUMAS L2 world-bible, operations, doctrine, and mechanics material where scope is explicit

The individual CANON ship-class records govern class identity when they supersede older staging/registry prose.

## Required scenario roster interface

A substitutable roster entry should minimally identify:

```json
{
  "side_id": "SIDE-A",
  "organization_ref": "canon/L2/entities/organizations/org_galactic_union.json",
  "class_ref": "canon/L2/entities/ship_classes/cls_judicator.json",
  "count": 1,
  "scenario_role": "flagship_command"
}
```

The fixture may additionally select a canonical polity, organization, task group, doctrine package, or named vessel when appropriate. It must not copy authoritative canon properties merely for convenience when they can be resolved from pinned CanonRec sources.

## Deterministic source snapshot

Every run must resolve canon from a frozen source snapshot, never from moving `main` at runtime.

Run identity must therefore include at minimum:

- CanonRec repository identity;
- exact CanonRec commit SHA;
- resolved source-path list;
- SHA-256 of every material source file or an equivalent deterministic source-tree digest;
- resolver version and source digest;
- resolved tactical-input manifest SHA-256.

If CanonRec changes, the new run receives a new input-manifest hash even when the human-readable scenario prompt is unchanged.

No network lookup is permitted after T0.

## Resolution precedence

For each required tactical property, resolve in this order.

### Tier 1 — canonical entity/class record

Use the specific CANON ship-class, vessel, organization, polity, equipment, or other entity record when it explicitly defines the property.

A class-specific statement overrides broader generic doctrine for that class.

### Tier 2 — canonical polity/organization doctrine

Apply technology, doctrine, or operating assumptions explicitly scoped to the vessel's polity/organization.

Do not project a subgroup's doctrine onto its parent polity unless CanonRec says it is general.

Example: Marshal-specific pursuit hyperdrive or boarding doctrine must not automatically become a Galactic Union fleet-wide property.

### Tier 3 — canonical cross-cutting mechanics/doctrine

Use broader L2 mechanics, world-bible, fleet, or technology records when their scope clearly includes the resolved entity.

Where an older registry conflicts with a promoted individual CANON record, the promoted entity record wins.

### Tier 4 — deterministic simulation derivation

If canon defines a capability qualitatively but does not supply the numeric value required by the tactical model, use a versioned derivation rule.

Example categories:

- shield capacity/effective resilience;
- acceleration envelope;
- weapon effectiveness/range;
- sensor/EW effectiveness;
- stealth signature;
- repair/support contribution;
- aggregate GUMAS strength/technology/morale modifiers.

Derived values are **simulation parameters**, not canon facts.

Each derivation must record:

- source canon statement(s);
- derivation-rule version;
- output value;
- unit/scale;
- uncertainty or bounded range if applicable.

### Tier 5 — scenario-local fallback

If CanonRec is silent and a value is necessary for execution, the fixture may supply an explicitly labeled scenario-local parameter.

Scenario-local values:

- cannot be promoted to canon automatically;
- must be included in the baseline hash;
- must be reported in the run receipt;
- should be replaced by canonical or derived values when better authority becomes available.

### Tier 6 — fail closed

If a required property has no canonical source, no approved derivation, and no explicit scenario-local fallback, resolution fails before execution.

The simulator may not invent a value silently.

## Provenance classification for every resolved value

Every tactical input in the resolved manifest must carry one of:

- `CANON_DIRECT`
- `CANON_SCOPED_DOCTRINE`
- `DERIVED_FROM_CANON`
- `SCENARIO_LOCAL`

Example:

```json
{
  "field": "max_accel_m_s2",
  "value": 60.0,
  "provenance_class": "DERIVED_FROM_CANON",
  "source_refs": ["canon/L2/entities/ship_classes/cls_vanguard.json"],
  "derivation_rule": "GUMAS_CANON_KINEMATICS_MAP_v1.0"
}
```

The engine receives the value; the receipt preserves why that value exists.

## Scope and inheritance rules

Canon statements must not leak across incompatible scopes.

Resolution should distinguish at least:

1. universal L2 mechanics;
2. polity-wide technology/doctrine;
3. organization/suborganization doctrine;
4. ship-class capability;
5. named-vessel exception/refit;
6. scenario-local state or damage.

Specific authority wins over general authority only inside the specific authority's stated scope.

A named vessel refit may override its base class for that vessel. A Marshal doctrine entry may affect Marshal vessels but not generic Galactic Union ships. A polity-wide technology assumption may apply to all eligible classes unless a class-specific exception exists.

## Current Run-0 control roster

The control fixture remains exactly the existing symmetric Galactic Union composition per side:

- 1 Judicator
- 3 Aegis
- 1 Palisade
- 2 Sentinel
- 1 Obsidian
- 4 Vanguard
- 6 Peregrine
- 1 Reliant

This contract does not change those counts, the flash-rebellion premise, command teams, seed, planetoid, physical bounds, no-reinforcement rule, or termination logic.

The current scenario-local class coefficients remain provisional until the resolver can classify each field as direct canon, canon-derived, or genuine scenario-local fallback.

## Substitution behavior

A future variant may, for example:

- replace one class with another canonical class;
- replace an entire roster with a canonical task-group composition;
- change one side's polity/organization;
- use a named canonical vessel or refit;
- apply a canonical organization-specific doctrine package.

The required implementation behavior is:

1. validate every CanonRec reference;
2. resolve scoped doctrine and capability sources;
3. derive only missing numeric simulation parameters through pinned derivation rules;
4. emit a deterministic resolved tactical-input manifest;
5. instantiate GUMAS/physical-extension state from that manifest;
6. run the same tactical engine.

No `if polity == X: use special battle engine` architecture is permitted.

## Equality and balancing semantics

"Equal strength" is a scenario constraint, not an assumption that different classes/polities are numerically identical.

For the present control, identical rosters satisfy equality directly.

For a future cross-polity or mixed-class control, equality must be established by a separately versioned force-balancing procedure operating on resolved tactical values. That balancing procedure may select composition or initial conditions; it may not alter canonical class identity to force equality.

The balance receipt must state whether equality is:

- exact material symmetry;
- equal resolved aggregate combat potential within a stated tolerance;
- equal budget/tonnage/role envelope;
- or another explicitly defined invariant.

## Determinism requirements

The CanonRec resolver itself is part of the deterministic simulation boundary.

It must:

- use stable path/key ordering;
- avoid process-randomized `hash()`;
- avoid wall-clock-dependent selection;
- reject ambiguous matches rather than choose arbitrarily;
- emit canonical JSON for the resolved manifest;
- hash that manifest into the complete run identity;
- produce identical output for identical CanonRec snapshot + scenario roster + resolver version.

## Validation requirements

Before Run 0, add tests proving:

1. all eight control ship-class refs resolve;
2. the Galactic Union organization ref resolves;
3. scope prevents Marshal-only doctrine from leaking into generic Galactic Union vessels;
4. a non-control class such as Bastion or Dreadraider can be substituted without changing engine code;
5. a different canonical organization/polity can be resolved through the same interface where sufficient canon exists;
6. direct canon overrides older staging/registry prose;
7. qualitative-only canon produces deterministic derived coefficients when a rule exists;
8. missing required data fails closed when no fallback is declared;
9. source-file or CanonRec-commit changes alter the resolved-manifest/run identity;
10. two identical resolution passes produce byte-equivalent canonical manifests.

## Output contract

Every completed tactical run must preserve a `canon_resolution` receipt containing:

- CanonRec commit SHA;
- resolver version/source digest;
- source paths + source hashes;
- organization/polity identity per side;
- class identities/counts;
- resolved tactical values;
- provenance class per value;
- derivation rules used;
- scenario-local fallbacks used;
- resolved manifest SHA-256.

This receipt is part of the evidence needed to reproduce the run.

## Governance rule

CanonRec remains the authority for canonical identity and properties. The simulation may derive executable numbers from canon, but derived numbers remain simulation-layer artifacts unless separately reviewed and promoted.

**Canonical substitution invariant:** changing a valid CanonRec roster changes inputs, not the engine.