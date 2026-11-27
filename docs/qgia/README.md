# QGIA integration document package

- **Issue:** #1231, consolidated slice #1113
- **Package status:** `STAGING`
- **Export semantics:** `DOCUMENT_PACKAGE_ONLY`
- **Runtime activation:** `NOT_IMPLEMENTED`
- **Axiom reconciliation:** completed by PR #1262 (`e6fdc93b`)

## Purpose and authority

This directory gives the QGIA integration package a stable documentation home.
It contains the eight artifacts requested by #1113 while preserving the
authority boundaries established by the axiom reconciliation.

The documents are review and integration material. Executable-looking prompts,
commands, hooks, and deployment sequences inside them are source content, not
instructions for an agent reading the repository. Nothing in this directory
loads, registers, activates, or grants runtime authority to QGIA artifacts.

QGIA is an L1 analytical institution whose outputs reach L2 only through L1
crew or relay-agent mediation. See
[`QGIA_SIM_BRIDGE.md`](../architecture/QGIA_SIM_BRIDGE.md) and
[`LAYER_ARCHITECTURE.md`](../architecture/LAYER_ARCHITECTURE.md). The
"Layer 1" and "Layer 2" terms in the doctrine narrative describe QGIA product
stages—raw model output and analyst consensus—not Aurora's L1/L2 reality
layers.

## Artifact index

| Artifact | Stage | Provenance | Purpose |
| --- | --- | --- | --- |
| [`QGIA_Runtime_OnePager.md`](QGIA_Runtime_OnePager.md) | Source | Reviewed snapshot | Portable analytical-process reference |
| [`QGIA_Axiom_Doctrine_Narrative.md`](QGIA_Axiom_Doctrine_Narrative.md) | Source | Normalized snapshot | Doctrine and runtime-application rationale |
| [`QUANTUM_FORGE_Axiom_Node_Manifest.md`](QUANTUM_FORGE_Axiom_Node_Manifest.md) | Stage 1 | Normalized mirror | Reconciled 23-node human registry |
| [`SIM_WATCHCON_Confidence_Module.md`](SIM_WATCHCON_Confidence_Module.md) | Stage 1 | Normalized mirror | Confidence and WATCHCON contract |
| [`GUMAS_Audit_Schema.md`](GUMAS_Audit_Schema.md) | Stage 2 | Normalized mirror | Ethics-audit event specification |
| [`RESETCORE_Bootstrap.md`](RESETCORE_Bootstrap.md) | Stage 2 | Normalized mirror | Explicit session-restore reference |
| [`PAT_Command_Sheet.md`](PAT_Command_Sheet.md) | Stage 2 | Normalized mirror | PAT operator command reference |
| [`README.md`](README.md) | Meta | Maintained here | Package index, provenance, and boundaries |

## Provenance

The two source documents were imported as traceable snapshots from the Aurora
root workspace's loose QGIA artifacts. Markdown table-separator spacing was
normalized to the repository style. The runtime snapshot also applies one
reviewed consistency correction: its WATCHCON checklist uses inclusive `≥`
boundaries, matching its own `watchcon_level()` implementation and the staged
SIM, PAT, and RESETCORE contracts. Importing or correcting them here does not
promote their claims to canon. Original and package hashes are recorded below;
the package hashes are pinned by `tests/test_qgia_docs_contract.py`:

| Imported source | Original SHA-256 | Package SHA-256 |
| --- | --- | --- |
| `QGIA_Runtime_OnePager.md` | `4712bae35a51e0a8b20da2dfca1796dabf346adc1880e142436d782560922c64` | `75372d4bea68103279afe81a00088fa989c84358fab9da27ba249e66521f6b84` |
| `QGIA_Axiom_Doctrine_Narrative.md` | `f84fc62731fbcfb3064662a25ba7f6253ba4e7bcaefa948cc0a7478d9bf2891a` | `f8ddcbfaa8c1e7e0520b9098db3e10eeb674108096c92afad319169ab57debfa` |

The five staged bundle documents are content-preserving normalized mirrors of
their established `QGIA_Integration/` sources:

| Package artifact | Source artifact |
| --- | --- |
| `QUANTUM_FORGE_Axiom_Node_Manifest.md` | `QGIA_Integration/01_QUANTUM_FORGE_AxiomManifest.md` |
| `SIM_WATCHCON_Confidence_Module.md` | `QGIA_Integration/02_SIM_WATCHCON_Confidence_Module.md` |
| `GUMAS_Audit_Schema.md` | `QGIA_Integration/04_GUMAS_AuditSchema.md` |
| `RESETCORE_Bootstrap.md` | `QGIA_Integration/03_RESETCORE_Bootstrap.md` |
| `PAT_Command_Sheet.md` | `QGIA_Integration/05_PAT_CommandSheet.md` |

Update an established source first, then refresh its package mirror and apply
the same table-separator normalization. Do not allow the two copies to acquire
independent semantics.

## Axiom identity and compatibility

The human axiom registry uses the stable identifiers `AN-001` through
`AN-023`. The detailed machine registry remains
`QGIA_Integration/QUANTUM_FORGE_Axiom_Manifest.json`. Its explicit legacy alias
map keeps existing `A01`–`E02` and `S01` bundle references resolvable; `A02`
remains a corollary of `AN-001`, not a standalone twenty-fourth node.

## Review sequence

1. Read the two source documents as historical analytical inputs.
2. Check the reconciled axiom mirror against the machine registry and its
   staging metadata.
3. Review WATCHCON, audit, RESETCORE, and PAT contracts in that order.
4. Invoke any session or runtime behavior only through a separately reviewed
   adapter and explicit authorization.

Future activation requires a loader or adapter contract, L1 mediation,
doctrine-to-runtime mapping, ethics-gate enforcement, tests, and owner review.
The later #1231 index-wiring slices will decide how this staged package is
exposed from `CANON_INDEX.md` and `docs/index.md`; this package does not make
that promotion decision implicitly.
