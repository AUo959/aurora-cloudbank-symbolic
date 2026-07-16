# SIM Module

**Expansion:** Simulation Integrity Module
**Status:** Formal QGIA contract; no standalone `modules/sim` runtime package
**Layer:** Governs L1 review of signals used to scope L2 simulations

## Purpose

SIM defines QGIA confidence scoring, WATCHCON thresholds, analytical-product
separation, and violation routing. Its current committed authority is the
[`SIM WATCHCON/Confidence Module`](../../QGIA_Integration/02_SIM_WATCHCON_Confidence_Module.md).
That document is a system contract, not evidence of a separately deployed
service.

## Layer Boundary

SIM's own references to "Layer 1" and "Layer 2" describe QGIA product stages:
raw model output and analyst consensus. They are not Aurora's reality layers.
In Aurora terminology, QGIA output is advisory input reviewed at L1. L1 crew
and relay agents may translate approved parameters into an L2 GUMAS task; SIM
cannot directly trigger or self-task L2.

## WATCHCON and Routing

The contract defines WATCHCON 5 through 1 using Tier I probability thresholds,
with WATCHCON 1 also triggered by a confirmed phase transition. Axiom or
product-boundary violations carry named GUMAS event codes and routing actions.
These declarations govern handling but do not prove that every route is
automated in runtime code.

## Related References

- [`docs/architecture/LAYER_ARCHITECTURE.md`](../architecture/LAYER_ARCHITECTURE.md) — authoritative Aurora reality layers
- [`docs/architecture/QGIA_SIM_BRIDGE.md`](../architecture/QGIA_SIM_BRIDGE.md) — required QGIA-to-L1-to-L2 mediation
- [`docs/LAYER_BOUNDARY_REFERENCE.md`](../LAYER_BOUNDARY_REFERENCE.md) — namespaced QGIA/Aurora terminology
- [`docs/INCIDENT_RESPONSE_RUNBOOK.md`](../INCIDENT_RESPONSE_RUNBOOK.md) — operator escalation path

## Validation Gap

No `modules/sim` package or dedicated SIM activation test is present. Treat SIM
as a committed doctrine contract until a separately reviewed runtime entrypoint
and executable enforcement tests are added.
