# GUMAS P4 — Infrastructure Alignment and Authority Audit

**Artifact:** GUMAS__AUDIT__P4_INFRASTRUCTURE_ALIGNMENT__v1.0__2026-11-15
**Status:** EVIDENCE-BOUND / CONDITIONAL GO for isolated P4 feature development; **NO GO for merge or live activation**
**Audit date:** 2026-11-15
**CloudBank main:** \`4a4c60b7b75c6e4af312f4d233a6f63ed30e0b01\`
**Root main:** \`6f28f881fb5eddf5c974b98e35f697183539bb54\`
**CanonRec main:** \`394560862a06eeda75e379d87715d43104c4fc66\`
**P3 head / parent:** \`bf4561c4d0bde70564b5e8fcae6b0cf7aeb58ba1\` (draft PR #1704)
**Previous stack:** P0 #1701 → P1 #1702 → P2 #1703 → P3 #1704.
**Audit limitation:** GitHub source/PR/CI evidence, not an attested live deployment or independently cloned multi-repository runtime test.

## Decision

Proceed with a **new stacked P4 draft** restricted to data-defined
institutional decision contracts over the existing synthetic kernel.
Do not change the primary FastAPI application, active GUMAS ethics router,
mesh, QGIA, naming registry, CanonRec, L1, or THREADCORE. No experimental
situation is admitted as canon. Reproducibility for P0-P3 with absent
P4 contracts is a hard regression gate. Do not merge until unresolved
P3 static-analysis findings are dispositioned and independent cross-platform
review is recorded.

## Evidence and alignment matrix

| Interface | Repository source / verified state | P4 decision |
|---|---|---|
| Repository authority | Root \`catalog/repo_authority_policy.yaml\`, \`catalog/repo_registry.yaml\`; CloudBank \`ARCHITECTURE_QUICKMAP.md\`, \`docs/CANON_PROVENANCE.md\`. CanonRec controls canon, root routes integration, CloudBank is a runtime mirror/projection | Code remains in CloudBank's own Git history; no upstream registry or canon mutation |
| Layer model | CloudBank \`AGENTS.md\`, \`docs/architecture/LAYER_ARCHITECTURE.md\`. L1-resident relay/crew supervise L2 but do not reside inside L2; L3 is a conceptual framework, not a runtime polity engine | L2-only synthetic actor choices; no L1 dispatch or L3 enforcement bypass |
| Live service topology | CloudBank \`docs/architecture/RUNTIME_TOPOLOGY_AND_L3_AUTHORITY.md\`: FastAPI \`api/aurora_api.py\`, active \`/gumas\` ethics route in \`modules/gumas/api/routes.py\`; mesh is separately owned | P4 has no API mount, no service startup hook, no mesh route, no mutable external store |
| Existing GUMAS namespace | CloudBank \`modules/gumas/naming.py\` implements deterministic naming and CanonRec registry exchange. \`simulation/runtime/gumas_unified\` is absent from CloudBank \`main\` and exists only on unmerged P0-P3 branches | Use a distinct sandbox package; do not replace \`modules/gumas\`, register any actor or infer canonical polity names |
| Integration provenance | P0 #1701 causal physics; P1 #1702 evidence-only ACE/tactical adapters; P2 #1703 synthetic identity and declarative clock coordinates; P3 #1704 escrow/vote engine | P4 only changes local institutional ratification predicate, retains kernel as sole L2 writer |
| External source execution | ACE root #85, tactical CloudBank #1506 remain separate, unmerged upstream work | No imports/executions of ACE or tactical sources, no tactical Run 0, no external clock event delivery |
| Real-world intelligence | \`docs/architecture/QGIA_SIM_BRIDGE.md\`: QGIA evidence passes through L1 crew/relay interpretation before L2 scenario tasking | No autonomous QGIA intake or decisions |
| Code review | Root \`docs/AURORA_PEER_REVIEW_PROTOCOL_v1.md\`: cross-repo changes require complementary review and auditable receipt; independent verification mandatory | Request independent review before promotion; this self-audit is not such a review |
| Existing operational state | Root most recent briefs in repo are 2026-08-28 and 2026-08-15; registry generated 2026-09-08. Those are historical, not fresh live checkout or session-claim proofs | Live GitHub refs/CI used for current PR status; no claims about local workspace claims, unsynced changes, or live deployment |
| PR #1704 quality gates | P3 targeted \`74/74\` tests and GitGuardian green at \`bf4561c\`. SonarCloud reports C reliability rating; Codacy reports 1 high ErrorProne and 1 medium Complexity. Specific annotations could not be retrieved; dashboard requires access | Do not call P3 or stacked P4 quality-gate clean. External findings are inherited merge blockers until independently resolved |

## Specific P4 integration contract

- Add \`GovernanceProtocol\` as a versioned, **synthetic scenario datum** keyed
  by existing \`Institution.institution_id\`. No new canon labels.
- Support exactly three supplementary decision modes:
  - \`delegated\`: one explicitly recorded delegate's ballot is decisive;
  - \`unanimous\`: all recorded institution members must consent;
  - \`veto\`: regular quorum/threshold plus assent of named veto holders.
- An institution without a P4 protocol must retain **exact P3 quorum
  logic and receipt/projection payload shapes**; no default fields injected.
- A governance protocol can be installed only in initial fixture state.
  P4 introduces no uncontrolled runtime rule mutation.
- \`propose_relief\`/ballot/ratification/dispatch retain kernel
  copy–validate–commit and hash-linked receipts. Institutional legality
  must never be conflated with physical feasibility.
- The *same* P0 route/time/energy/capacity/escrow mechanisms govern material
  outcomes regardless of institutional protocol. No polity-name branches,
  arbitrary Earth-derived rebellion priors or civilization end states.
- Physical access remains local to council seat; remote voting and
  cross-star-system institutional consent are **explicitly deferred** until
  an information-propagation and remote-ballot contract is designed.
- Model-state hashing omits P4 \`governance_rules\` when empty. Existing
  P0/P2 fixed-hash tests and P3 deterministic behavior must remain valid.
- Read-only institution/operator projections may display a configured P4
  rule, but may not inject a private agent belief or assert external
  CanonRec/ACE authority.

## Audit risk register

| ID | Severity | Evidence | Disposition |
|---|---|---|---|
| P4-A1 | BLOCKING MERGE | P3 SonarCloud C reliability rating and Codacy two findings, PR #1704 | Must resolve, or document independently reviewed explicit waiver; do not auto-merge |
| P4-A2 | BLOCKING LIVE INTEGRATION | P0-P3 all draft; unified runtime path absent on CloudBank main | Retain stacked draft and isolated test-only usage |
| P4-A3 | HIGH | No independent L3-authenticated source identity or clock mapping | Continue fixture-only source references |
| P4-A4 | HIGH | Actual canonical FTL, biology, economics and history not validated by P0 physical fixture | No production claims or canonical polity assumptions |
| P4-A5 | MEDIUM | P3 unanimous quorum does not represent independent delegated and veto governance; may encourage polity-agnostic-but-monolithic rule logic | P4 adds composition by explicit governance mode without name checks |
| P4-A6 | MEDIUM | Older root briefs and repo registry do not prove current local claims | State evidence freshness and provenance clearly |
| P4-A7 | MEDIUM | Root peer-review protocol requires independent re-verification; not accomplished solely by same-author tests | Independent review gate before merge |
| P4-A8 | MEDIUM | P2 millisecond tactical mapping is declarative, not unified high-resolution executable clock | No scheduling or remote communication shortcuts |

## Validation protocol

From the P4 stacked branch, after commit:

    python -m unittest discover -s tests -p 'test_gumas_unified*.py' -v
    python -m simulation.runtime.gumas_unified.scenario
    python -m simulation.runtime.gumas_unified.political_scenario
    python -m simulation.runtime.gumas_unified.governance_scenario

Demand: all previous P0-P3 tests green, P4 mode invariants green, no new
service wiring, unchanged baseline P0 hash, P3 unchanged event/projection
shape when no explicit P4 override, same conserved goods/energy under all
modes, exact actor-local information rules, fixed source authority boundaries.

The result is an architectural **integration design and proof-of-concept**;
it is not proof of full compatibility with unmerged upstream PRs or actual
Aurora production deployments. An independent reviewer must inspect the
diff, source hashes, external quality findings and repository integration
gates before merge. Canon promotion would require its own authorization.
