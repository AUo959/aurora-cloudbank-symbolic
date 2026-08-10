# SHERLOCK / WATSON — OPAL2 Product Specification

**Document ID:** `OPAL2__PRODUCT_SPEC__SHERLOCK_WATSON`  
**Version:** v1.0  
**Date:** 2026-08-07  
**Product names:** **SHERLOCK**, **WATSON**  
**Foundry:** OPAL2  
**Status:** implementation baseline

## 1. Product thesis

SHERLOCK and WATSON are portable AI-product capabilities, not Aurora lore.
Aurora is one development environment and consumer of the products. OPAL2 is
the foundry/runtime that turns the discovered capability into a reusable,
inspectable tool contract.

The pair addresses a recurring failure mode in AI systems:

> Retrieval without interpretation can be technically correct but unusable;
> interpretation without disciplined evidence can become confident invention.

The product therefore separates the two responsibilities:

```text
question / case
      |
      v
 SHERLOCK
 evidence investigation
      |
      | immutable case-file handoff
      v
  WATSON
 contextual synthesis
      |
      v
 decision-ready brief
```

The handoff boundary is the product's central integrity feature. WATSON may
interpret an exact SHERLOCK record but may not rewrite it.

## 2. SHERLOCK

**Product role:** Evidence Intelligence.

SHERLOCK is responsible for provenance-sensitive investigation. A complete
SHERLOCK case file can contain source inventory and locators, observations tied
to sources, chronology and authority information, contradictions, established
facts, derived findings, confidence information, unresolved questions, and
excluded or unsupported claims where useful.

SHERLOCK must preserve the distinction between source observation, derived
finding, and unresolved state. It does not contain, enforce, adjudicate, or
silently repair the subject being investigated.

The OPAL2 protocol core does not itself fetch sources. A retrieval/agent adapter
produces the investigation payload; the neutral core validates, canonicalizes,
and seals that payload as a digest-addressed case file.

## 3. WATSON

**Product role:** Contextual Intelligence.

WATSON consumes a verified SHERLOCK case file and produces contextual synthesis,
including correlations, interpretations, competing hypotheses, coherence tests
or explanatory models, recommendations, and residual uncertainty.

WATSON must not alter the SHERLOCK record. Its output carries the exact
SHERLOCK case digest it analyzed. Any mutation to the evidence record breaks
verification.

The neutral core similarly does not require a particular language model. A
synthesis/agent adapter creates the brief; OPAL2 binds the brief to the exact
case file and produces a verifiable evidence-to-analysis bundle.

## 4. Portable protocol core

Reference implementation: `modules/opal2/tools/sherlock_watson.py`

Tool IDs:

- `opal2.sherlock.casefile`
- `opal2.watson.brief`
- `opal2.sherlock-watson.verify`

Artifact schemas:

- `opal2.sherlock.casefile.v1`
- `opal2.watson.brief.v1`
- `opal2.sherlock-watson.bundle.v1`

### Integrity chain

1. SHERLOCK canonicalizes the evidence record.
2. The record is SHA-256 addressed.
3. WATSON must receive a case file whose digest verifies.
4. WATSON's brief embeds the SHERLOCK digest.
5. The WATSON brief is separately SHA-256 addressed.
6. The combined bundle is SHA-256 addressed.
7. Verification recomputes the full chain and fails closed on mutation.

This makes the epistemic boundary inspectable rather than prompt-dependent.

## 5. Product modes

### Quick Investigate
Run SHERLOCK and return the evidence case file.

### Investigate + Analyze
Run SHERLOCK, lock the case-file revision, then run WATSON against that exact
revision and return both artifacts.

### Challenge Analysis
Run a new WATSON synthesis against the same locked SHERLOCK case file. Competing
analysis is allowed; evidence mutation is not.

### Re-investigate
Run SHERLOCK again with new evidence and create a new case-file digest/revision.
Existing WATSON briefs remain bound to the earlier case rather than silently
moving to the new evidence set.

## 6. Provider architecture

The portable core is intentionally provider-neutral.

```text
retrieval sources / connectors / repo / web / documents
                     |
          InvestigationProvider
                     |
                 SHERLOCK
                     |
          sealed evidence case file
                     |
            SynthesisProvider
                     |
                  WATSON
                     |
            bound analysis bundle
```

Possible adapters include hosted model providers, local models, repository
agents, document-search systems, web research systems, or human analyst input.
No provider is allowed to bypass the digest boundary.

## 7. OPAL2 relationship

This product is a direct expression of OPAL2's purpose: capabilities discovered
inside larger systems can be extracted into neutral, portable tools.

Aurora-specific anchors, simulation concepts, ethics labels, or project canon
must not become required fields in the SHERLOCK/WATSON portable contract.
Aurora may supply an adapter or policy profile just as any other consumer may.

Longer-term `.opaltool` packages should be able to carry the protocol core,
schemas, fixtures, provider-interface declarations, and conformance tests.
Package activation remains subject to OPAL2's existing signature/isolation
roadmap.

## 8. User and agent discoverability

Human-facing names should remain **SHERLOCK** and **WATSON**.

Agents should also receive functional metadata so use does not depend on knowing
the names in advance:

- SHERLOCK: `evidence-provenance`, `casefile-sealing`,
  `fact-inference-separation`;
- WATSON: `contextual-synthesis-binding`, `immutable-evidence-handoff`,
  `hypothesis-provenance`.

Recommended trigger:

> Use SHERLOCK -> WATSON when a task requires both provenance-sensitive
> investigation and contextual interpretation.

Do not invoke the full workflow for trivial questions where the audit overhead
adds no value.

## 9. Separation of duties

- SHERLOCK investigates; it does not mutate or enforce.
- WATSON contextualizes; it does not alter SHERLOCK logs or enforce.
- Containment and adjudication, if a deployment has such systems, are separate
  downstream responsibilities and are not implicit capabilities of this
  product.

## 10. Ship boundary

### Implemented in this baseline

- neutral SHERLOCK case-file schema and validation;
- deterministic canonicalization and digest addressing;
- WATSON-to-SHERLOCK immutable binding;
- full bundle verification;
- OPAL2 `Opal2Tool` implementations for case sealing, brief binding, and
  verification;
- focused tests for deterministic output and mutation detection.

### Next product work

- register all three tools in the default OPAL2 standalone API registry;
- expose a concise CLI/user workflow in addition to generic `/tools/{id}/run`;
- define `InvestigationProvider` and `SynthesisProvider` adapter interfaces;
- implement at least one neutral provider pair;
- add end-to-end fixture cases and challenge/re-investigate revision tests;
- export the protocol as a deterministic `.opaltool` artifact;
- add a small UI showing locked SHERLOCK evidence beside WATSON interpretation;
- perform clean-room execution outside Aurora.

## 11. Product principle

Aurora may discover a useful capability. OPAL2's job is to make that capability
portable enough that a user who has never heard of Aurora can still use it.

SHERLOCK / WATSON is the first reference product where that discovery-to-product
loop is itself the point.
