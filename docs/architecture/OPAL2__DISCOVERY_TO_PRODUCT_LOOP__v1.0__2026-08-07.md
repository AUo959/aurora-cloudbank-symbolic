# OPAL2 — Discovery-to-Product Loop

**Document ID:** `OPAL2__DISCOVERY_TO_PRODUCT_LOOP`  
**Version:** v1.0  
**Date:** 2026-08-07  
**Status:** project principle / productization guidance

## Principle

A capability discovered while building Aurora is not required to remain an
Aurora-specific feature.

OPAL2 exists to identify capabilities that have independent utility, extract
their portable contract, remove unnecessary Aurora dependencies, validate the
result in a neutral runtime, and package it for reuse.

The intended loop is:

```text
Aurora work / simulation / operations
              |
              v
     useful capability appears
              |
              v
       evidence that it works
              |
              v
             OPAL2
   extract neutral contract
   remove project-only coupling
   validate + package + expose
              |
              v
      standalone product/tool
              |
        +-----+-----+
        |           |
        v           v
      Aurora      everyone else
      adapter      neutral use
```

## Productization test

A candidate capability is a strong OPAL2 extraction target when most of these
are true:

1. It solves a problem that exists outside Aurora.
2. Its value can be explained without Aurora terminology.
3. Its core inputs and outputs can be represented by a neutral contract.
4. Project-specific policy can be moved behind an adapter/profile.
5. It can be tested independently of the system in which it was discovered.
6. Its provenance and limitations can be stated honestly.
7. A neutral user or agent could discover when to invoke it by capability, not
   by knowing project lore.

## SHERLOCK / WATSON as reference extraction

SHERLOCK / WATSON is the clearest current example.

The workflow surfaced naturally during Aurora canon reconciliation:

- SHERLOCK traced evidence, authority, chronology, contradictions, and unknowns.
- WATSON consumed that evidence and produced contextual interpretation without
  rewriting the investigation record.

Nothing about that problem is inherently specific to Orion Station. The same
pattern applies to repository archaeology, incident analysis, due diligence,
research synthesis, policy conflicts, documentation drift, and other
evidence-sensitive work.

OPAL2 therefore treats SHERLOCK / WATSON as a standalone product whose first
consumer happens to be Aurora.

## Guardrail

Extraction must not become marketing-by-renaming.

A product is not portable merely because Aurora-specific nouns were removed.
The neutral contract must stand on its own, the implementation must avoid
hidden project dependencies, and clean-room tests must demonstrate that it can
operate outside Aurora.

Likewise, OPAL2 should not force every internal mechanism into a standalone
product. Extraction is warranted when independent utility is demonstrated.

## Relationship to the foundry

`docs/architecture/OPAL2_FOUNDRY_ARCHITECTURE.md` defines the technical foundry:
manifests, registry, execution envelopes, packaging, and runtime boundaries.

This document defines the upstream discovery rule: **how a capability earns its
way into that foundry.**

Together they express the larger OPAL2 purpose:

> discover useful capabilities in complex systems, then make the useful parts
> independently usable.
