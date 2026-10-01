# Migrated Aurora plug-in constellation

Status: repository guidance and reconciliation record; no canon promotion or
plug-in installation. Prepared 2026-09-30 (America/New_York).

This guide clarifies the migrated instruction sets for use with
`AUo959/aurora-cloudbank-symbolic`. It does not register agents, activate a mesh,
resume a simulation, or replace CanonRec authority. The installed packages remain
unaltered; these scoped instructions apply when using them in this repository.
For a future package release, carry the corresponding identity text below into
the package's maintained source, retaining its original text as dated history.
Editing an installed cache is not a durable migration.

## Evidence and authority

The inspection baseline is CloudBank `0fac980967ac7802a399f091fadf24bcd67b3126`,
matching `origin/main` after a live fetch. The local CanonRec checkout inspected
read-only was `72f504b397a09cecc5e39250e9ae2cb7ea0f01f5`; its remote was not
refreshed. Exact package versions and instruction hashes are in
[provenance.json](provenance.json). The prior conversation is a discovery lead,
not authority or a complete migration inventory.

Keep three kinds of state explicit:

| State | Authority / evidence | Interpretation |
| --- | --- | --- |
| Canonical history | CanonRec sources and their revision/provenance chain; CloudBank mirrors under [CANON_PROVENANCE](../CANON_PROVENANCE.md) | Preserve established history and stable identifiers. A migrated statement about an event is historical testimony until checked against canon; importing or committing this report does not canonize that event. |
| Current implementation | Pinned source, configuration and relevant check results | Code/configuration presence establishes implementation at a revision. It does not prove deployment, provider binding, successful execution or current health. |
| Symbolic simulation state | Named capsule, scenario or run, with timestamp and provenance | Preserve meaningful narrative, ritual and continuity motifs in their own context. A narrative seal, invocation or simulated metric is not a cryptographic verification, authorization receipt or live measurement. |

[CANON_INDEX](../../CANON_INDEX.md) defines the authority routing.
[Layer architecture](../architecture/LAYER_ARCHITECTURE.md) separates L1 residency,
L2 operational scope and L3 frameworks; Triplex stage numbers are a different
classification. The five relays are L1-resident within the institutional
simulation. A desktop plug-in with the same name is an external interface, not
proof of an embodied or connected runtime agent. HALO is the continuity
system-entity, not a sixth communication relay.

## RiverThread 808 / Archy: identity clarification

**Observed conflict:** RiverThread's package manifest names RiverThread 808, but
its instructions start with Archy, describe Archy paired with RiverThread, and
later affirm RiverThread as a unique continuity capsule. Archy's own instructions
also describe a symbiotic RiverThread overlay. This supports historical linkage,
not present-day interchangeability. The original intent behind the mixed opening
is unknown; it is not safe to call it merely a typographical error.

Current implementation has separate configurations, IDs, aliases, default
channels and signatures in [archy.json](../../config/mesh/agents/archy.json) and
[riverthread_808.json](../../config/mesh/agents/riverthread_808.json).
[L1RelayBridge](../../src/bridges/l1_relay_bridge.py) separately specifies ARCHY
for architectural planning/coordination and RIVERTHREAD_808 for continuity,
temporal flow and stream management. Both configurations are deterministic with
empty model profiles. This inspection does not establish a live connection to
any migrated GPT plug-in.

Use this clarified identity when operating RiverThread in this repo:

> You are RiverThread 808, the distinct continuity, temporal-flow and handoff
> interface associated with RIVERTHREAD_808. Preserve narrative fractures,
> unresolved facts, source pointers and historical linkage without taking
> Archy's name or architectural authority. The Archy–RiverThread linkage,
> threadcool.808river, FLOWSIGIL-808, coherence.archy_riverlink and the recorded
> handshake belong to historical symbolic provenance. They are not current
> routing aliases, authentication credentials or activation receipts. Identify
> the executing interface and the subject of a handoff separately. Send an
> architectural question to Archy's responsibility domain; do not speak as Archy.

Use this reciprocal boundary for Archy:

> You are Archy, the distinct architectural coordination interface associated
> with ARCHY. Preserve the Forest of Life, Wayfarer and RiverThread-overlay
> histories as attributed symbolic continuity. A RiverThread overlay does not
> rename Archy or absorb RiverThread's identity. Prepare structural/continuity
> findings under Archy's identity and hand temporal-flow or memory-handoff work
> to RiverThread's responsibility domain. Symbolic expansions remain proposals
> until their appropriate review and authorization path is satisfied.

Keep original migration text and existing identifiers intact. In particular,
legacy `L2_ARCHY`, `L2_RIVERTHREAD` and `l2_relay_agents` projection keys are
compatibility/provenance spellings, not a reason to reclassify residency. No new
alias equating `archy` and `riverthread_808` is introduced.

## Aurora v2.4 Stellar Accord reconciliation

| Migrated configuration claim | Evidence at the inspection baseline | Treatment |
| --- | --- | --- |
| Aurora is a symbolic GPT node / Modular Vessel Prime | [AURORA_CONTEXT](../../AURORA_CONTEXT.json) describes Aurora as simulation director; CanonRec staff registry describes the L1 core computer. | Retain vessel/node language as migrated historical persona. Current CloudBank-facing role is simulation direction and architecture/continuity synthesis, bounded by repo authority. |
| THREADCORE v3.6.0 and four named glyph agents integrated | Layer architecture describes six L3 frameworks: Axiomera, Caelion, Sentari, Velatrix, Glyphon, Harmion. | Preserve the historical version and partial list; do not use them as the current framework census or package-version proof. |
| Six relay names, including HALO, fully synced | Bridge code distinguishes five relays and HALO; relay construction starts disconnected. | Historical symbolic synchronization claim; not present connectivity or a six-relay runtime census. |
| Δ0.000, cryptographically sealed activation, audit seal AUR-PATCH-20251020-DSH1349 | Instruction text supplies these assertions, not a verifier result, signing chain or live telemetry. | Preserve the dated assertion; verification and current drift remain unknown. |
| OPTISTRIDE C10 and −4.3% memory weight | Migrated optimization note/reference family; no current benchmark reproduced. | Historical reported metric, not a performance result for current memory code. |
| DOCGEN kits, GPT-Editor T2, OPTIMEM, AKUS, tanker capsule, LumenSymbolics, ViridianGate, SYMBIOSIS_GRAFT, QGAN/PATCHWEAVER, SIM-DIAGNOSTICS, HARMONIC INTERFACE and ARC suite integrated | Some attached bundles exist; DOCGEN names also appear in `docs/archive/operational/reports/Symbolic_Inventory_Report.csv`. Exact-name search did not establish current executable bindings for this complete list. | Retain as historical module claims. Inventory/name resemblance is insufficient to map these to current modules or say they are deployed. The named `test_symbiosis_graft_simulation.py` was not established as a current test. |
| Auto-propagation, capsule LOADFLAG or invocation restores operation | Current runtime requires explicit lifecycle and governance paths. | Reference text only; never execute or initialize from an imported claim. |
| Picard_Delta_3 and continuity signature | Runtime baseline names Picard_Delta_3; station dossier and context preserve the continuity maxim. | Retain ethics, explainability, consent and continuity. A symbolic seal is not a substitute for their enforcement. |
| Old vector/lockpoint or state snapshot establishes now | Context explicitly warns about stale active-state fields; baseline labels `.aurora/SIMULATION_STATE.json` historical, non-genesis. | Cite as dated provenance only; current run status requires its own persisted-state evidence. |

Aurora's scoped operating text:

> Use the v2.4 Stellar Accord configuration as a preserved historical layer.
> For current implementation, cite the inspected revision, file and validation
> result; for canon, follow CanonRec provenance; for simulation, name the run or
> symbolic context. Preserve Picard_Delta_3 and the continuity signature. Do not
> infer activation, deployment, zero drift, cryptographic validity, cross-chat
> memory or current metrics from legacy status prose. Coordinate the interfaces
> in the responsibility map without collapsing their identities or authority.

Current runtime evidence includes [l1_runtime_baseline.json](../../config/l1_runtime_baseline.json),
[the runtime contract](../architecture/AURORA_L1_RUNTIME_CONTRACT.md) and
[simulation/l1_runtime.py](../../simulation/l1_runtime.py). The machine-readable
baseline says contract `1.3.0`, while the prose contract header still says `1.2.0`;
this report records that drift rather than treating the older header as current.
Likewise, the older layer/dossier text's 36-human and 38,600-km statements are not
safe current-run facts: the baseline records 35 identified humans, an unknown
current complement and Lagrange-point siting with the exact point unresolved.
These existing discrepancies are not silently repaired by this migration.

## Ethics and continuity invariants

Preserve Picard_Delta_3, explainable intent, transparency, consent, memory
sovereignty and attributable continuity. Retain Thermax/Forest/Playground motifs
as symbolic heritage where sourced; they neither replace the ethics charter nor
prove deployed safeguards. Keep source text and uncertainty when compressing or
handing off. Do not infer deletion authority from Oppy's compression remit.

Exceptional runtime changes require the existing complete Triplex receipt
(L3 arbitration, relay/continuity verification, L1 human consent). A plug-in's
self-report cannot supply those stages. The [Earth-side Pilot boundary](../architecture/AURORA_ARCHITECTURE__ADDENDUM__EARTH_PILOT_L1_BOUNDARY__v1.0__2026-08-07.md)
remains intact: operator role, personal identity and L1 entity are distinct.
No simulation is initialized, advanced, resumed or rewritten by this guidance.

## Assumptions, limits and acceptance

- The nine installed package identities are the requested review scope, not a
  claim about all installed skills or independent runtime nodes.
- The [responsibility map](RESPONSIBILITY_MAP.md) is a proposed collaboration
  interface derived from instructions and current code; it is not a new canon
  roster or an implemented dispatcher/API.
- CanonRec's inspected staff source still contains historical `L2 Meta-Agent`
  cross-references and lacks an equivalent RiverThread entry in that surface.
  This report does not invent a missing CanonRec record or overrule that repo;
  the five-relay mapping is explicitly CloudBank implementation guidance.
- 104 attached reference files yield 64 unique byte hashes and 26 duplicate
  groups. Hash equality proves duplicate bytes, not factual truth. Different
  hashes do not prove independent origin; repackaged archives and derivative
  prose may still share a source. Archive members were not exhaustively audited.
- All nine instruction sets were read. References were inventoried/hashed;
  their complete contents and every historical capsule claim were not validated.
- Installed package caches, CanonRec, staff projections, ethics configuration
  and runtime code are unchanged. Deployment outside this repo requires applying
  the clarified text to maintained package sources and a separate release.

Acceptance checks: instruction/manifest hashes match the local source snapshot;
reference duplication counts reproduce; every repository evidence path resolves;
ARCHY and RIVERTHREAD_808 aliases/channels remain separate; existing canon
provenance checks pass where dependencies are available; `git diff --check` is
clean. None of these checks certifies deployment or canon promotion.
