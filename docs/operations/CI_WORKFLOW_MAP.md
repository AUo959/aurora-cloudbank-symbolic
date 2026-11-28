# CI ownership and consolidation

Baseline: 41 workflow files on November 8, 2026 UTC; 37 remain after the
November 9 cleanup. This is a partial consolidation, not completion of the roadmap's roughly eight core
validation lanes. Deployment, event routing, scheduled maintenance and project
board automation are not interchangeable with pull request validation.

## Python validation owner

`aurora-ci-minimal.yml` owns the hash-checked Python environment, fatal syntax
checks, advisory style (120 columns), OPAL2 and critical tests, and mandatory
full Python suite. Its fatal syntax exclusions are narrowed to preserve the
union of the previous lint coverage. Its public check remains **CI Check**.

`k8s-deploy.yml` retains **Run Tests** and verifies canonical CI before automatic
container builds. Manual Kubernetes runs retain independent tests and the explicit
`skip_tests` input. Manifest validation, container build, SBOM and deployment remain.
The redundant `code-quality.yml` receipt-only compatibility gate was retired.

Constellation CI now installs the root npm graph once. Its blocking TypeScript
check and advisory lint, build and npm audit retain their diagnostic artifacts.
Audit runs before the blocking check, so type failures cannot suppress it. The
old integration job only printed a placeholder and was removed. Actual contract,
OpenAPI, schema, Python type and manifest checks remain in
`constellation-integration.yml`; root Node/web tests and frontend tests remain
separate because they exercise distinct commands or dependency graphs.

## Exact result reuse

Canonical CI uploads `ci-verification-<run_attempt>` containing
`ci-verification.json`, even after failure. The record binds the repository,
event, ref/PR identity, branch head, actual checkout, run ID, attempt and job result. The consumer
queries only `aurora-ci-minimal.yml` runs with its event and head SHA, filters
them to the same PR number or push branch, chooses the
latest run, requires its successful completion, and downloads only that attempt's
receipt. Both head and checkout must match: for PRs the checkout is the synthetic
merge commit, while the run API's head is the source branch commit.

Fork-origin runs can have an empty PR association in GitHub metadata. In that
case the attempt-specific receipt resolves the PR identity before run selection.
A newer run with unresolved identity blocks acceptance of older results until
its receipt is available; an unrelated PR's verified identity can be excluded.
The final status recheck uses only metadata and previously verified identities
keyed by run ID and attempt; it never downloads after the final status snapshot.
A failed attempt for the current PR still fails the gate. Missing receipts or
invalid source identity fail closed.

A successful branch-only test, an old merge-base checkout, manual run, previous
attempt, expired/malformed/oversized artifact, failed run, or unrelated workflow
cannot satisfy the gate. Missing or stale receipts time out closed after 15
minutes; jobs allow 20 minutes including checkout. A rerun started during receipt
download invalidates acceptance. No workflow is automatically dispatched, no
code from artifacts is executed, and the consumer token has only contents/read
and actions/read. Canonical CI's permission scope is unchanged.

Pull requests always trigger canonical validation. Kubernetes excludes Markdown-only
pushes; verifier, test or canonical workflow changes trigger its validation. Manual
Kubernetes runs do not need a canonical receipt.

## Workflow inventory

| Responsibility | Workflows |
| --- | --- |
| Canonical Python | `aurora-ci-minimal` |
| JavaScript and browser application | `node-tests`, `frontend-ci` |
| Specialized validation | `cross-platform-paths`, `dependency-validation`, `model-catalog-validation`, `catastrophe-prevention`, `queue-validation`, `safety_commit` |
| Code scanning | `codeql-unified` |
| Constellation contracts and integration | `constellation-ci`, `constellation-integration` |
| Build, publish and collaboration | `k8s-deploy`, `aurora-release`, `aurora_agent_runner`, `deploy-pages`, `symbolic-bundle`, `collab-sync`, `cross-repo-capsule-exchange`, `synergy_dashboard` |
| Constellation events and scheduled services | `constellation-event-publisher`, `constellation-event-router`, `constellation-health-audit`, `constellation-knowledge-aggregator` |
| Queue, PR and project-board automation | `auto-assign-and-review`, `auto-labeler`, `auto-merge-admin`, `ci-status-project-automation`, `pr-selective-integration`, `pr_evaluation`, `project-board-ci-sync`, `queue-decision-escalation`, `queue-issue-ingestion`, `sonarcloud-issue-reporter`, `stale-and-blocked-report` |
| State maintenance and manual administration | `simulation-state-freshness`, `admin-quick-push` |

Names omit the `.yml` extension. Retired: `branch-protection` (three echo-only
jobs), `codacy` and `codacy-analysis` (disabled jobs), and `code-quality`
(receipt-only duplicate). External Codacy app checks and configuration remain.

## Required checks and consumer audit

On November 9, read-only main branch metadata reports required **CI Check**
(Actions app 15368, non-admin enforcement). Effective rules add Copilot review,
deletion and non-fast-forward protection, without additional workflow requirements.
The full protection administration endpoint returns 403; this is not a complete
administration export. No protection setting was changed.

Repository workflow consumers use wildcard workflow-run routing rather than the
retired filenames. No workflow_call, dispatch or required-check dependency on the
retired lanes was found in maintained workflows. Active auditor and Copilot
instructions now point to canonical CI; obsolete Codacy dispatch instructions were
replaced with external-app troubleshooting. Historical investigation reports retain
old filenames as historical evidence.

## Remaining consolidation and rollback

The roadmap remains open: specialized validation and legacy build/publish owners
still need review before claiming roughly eight core lanes. Keep unique security,
platform, dependency-resolution, frontend and deployment coverage. Check PR and
resulting main runs and synchronize root pins and receipts.

For receipt timeouts, inspect canonical CI for the same event and head, rerun it
if needed, then rerun the consumer. Never accept stale proof. Reverting this
cleanup restores the retired compatibility workflows and separate Constellation
jobs. The canonical receipt format and Kubernetes proof gate were not changed.
