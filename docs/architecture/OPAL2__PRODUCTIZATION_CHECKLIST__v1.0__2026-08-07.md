# OPAL2 Productization Checklist

**Version:** v1.0  
**Date:** 2026-08-07

Use this checklist when promoting a capability discovered inside Aurora into a
neutral OPAL2 product.

- [ ] Independent problem/value can be explained without Aurora terminology.
- [ ] Neutral input/output contract exists.
- [ ] Project-specific policy is adapter/profile-only.
- [ ] Evidence and limitations are documented.
- [ ] Core can be imported and tested without Aurora runtime state.
- [ ] User/agent discovery uses functional capabilities, not insider names only.
- [ ] Relevant invariants are machine-enforced rather than prompt-only.
- [ ] Provider/network/model assumptions are explicit.
- [ ] Clean-room fixtures exist.
- [ ] `.opaltool` export and verification are supported when package scope is ready.
- [ ] Emit and validate a shipment manifest against [`shipment-manifest.schema.json`](../../constellation-contracts/schemas/shipment-manifest.schema.json), starting from the [worked example](../../constellation-contracts/manifests/shipment-manifest.example.json).
- [ ] Standalone execution outside Aurora has been demonstrated.
- [ ] Product claims do not exceed the implemented boundary.

SHERLOCK / WATSON is the first reference product evaluated against this list.
