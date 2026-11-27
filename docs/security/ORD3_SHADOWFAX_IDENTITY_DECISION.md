# ORD-3 and recovered SHADOWFAX custody decision

Tracking issue [#1361](https://github.com/AUo959/aurora-cloudbank-symbolic/issues/1361)

## Identity and authority

`ORD-3` is the L1 fleet identifier for the audit drone displayed as
Shadowfax. The CloudBank projection receipt attributes this identity to the
drone registry and fleet design. The ORD policy engine produces advisory
MCP dispatch orders. L1 mission admission requires a separate authorization
path. [Fleet authority receipt](../../config/l1_fleet_authority_receipt.json)

The recovered protocol record uses `shadowfax` as its protocol ID. Its
historical archive hash has been verified. Attribution and verification of
the internal protocol file and custody sign-off remain pending. The
available evidence leaves shared lineage undetermined. The L1 world
process continues to keep ORD-3 observable and blocks routine activation.
[Custody manifest](../ethics/recovered_protocols/recovered_protocol_manifest.json)
· [L1 fleet admission](../../simulation/l1_fleet.py)

## Arbitration configuration

The historical T12 configuration introduced the tribunal binding in
commit `43793c49`. A search of the tracked tree for the manifest basename
and binding key found the declaration and historical documentation. The
quantum Bayesian evaluator exports its own JavaScript manifest. The demo
and tests import the evaluator directly. The YAML declaration is removed.
Conflict detection and required arbitration remain in its configuration.
[Evaluator](../../src/core/quantum_bayesian.js)
· [Configuration](../../src/core/quantum_bayesian_manifest.yaml)

## Verification and open evidence

The configuration regression test requires the arbitration section to
contain only detection and arbitration requirements. The L1 fleet tests
continue to verify that ORD-3 is observable and barred from routine or
advisory-order activation. These checks address the configuration binding
and activation boundary. The Gate-001A event revision remains pending the
remaining lineage and runtime-surface reconciliation. Verification of the
external engagement requires Gate-001B evidence.
[Gate-001 verification](recovered_protocol_wiring_verification.md)
