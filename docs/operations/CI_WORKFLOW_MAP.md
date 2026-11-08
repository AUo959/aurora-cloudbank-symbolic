# CI ownership and consolidation

Baseline: 41 workflow files on November 8, 2026 UTC. This is the first
consolidation tranche, not completion of the roadmap's roughly eight core
validation lanes. Deployment, event routing, scheduled maintenance and project
board automation are not interchangeable with pull request validation.

## Python validation owner

`aurora-ci-minimal.yml` owns the hash-checked Python environment, fatal syntax
checks, advisory style (120 columns), OPAL2 and critical tests, and mandatory
full Python suite. Its fatal syntax exclusions are narrowed to preserve the
union of the previous lint coverage. Its public check remains **CI Check**.

`code-quality.yml` retains **code_quality**, but verifies this result instead of
installing an independent, unpinned linter. `k8s-deploy.yml` retains **Run Tests**
and verifies the result before automatic container builds. Manual Kubernetes
runs retain their original independent installation/lint/test path and explicit
`skip_tests` input. Manifest validation, container build, SBOM and deployment
steps remain separate. The notification job now explicitly depends on `test`
so its existing test-result expression is valid.

On matching automatic events, this removes one duplicate Python environment
installation and test suite from Kubernetes, and one unpinned lint installation
from Code Quality. It does not claim measured runner-minute or latency savings:
verification jobs poll using runners and canonical CI remains on the critical
path. Code Quality now reports the combined canonical outcome, including tests.

## Exact result reuse

Canonical CI uploads `ci-verification-<run_attempt>` containing
`ci-verification.json`, even after failure. The record binds the repository,
event, ref/PR identity, branch head, actual checkout, run ID, attempt and job result. The consumer
queries only `aurora-ci-minimal.yml` runs with its event and head SHA, filters
them to the same PR number or push branch, chooses the
latest run, requires its successful completion, and downloads only that attempt's
receipt. Both head and checkout must match: for PRs the checkout is the synthetic
merge commit, while the run API's head is the source branch commit.

A successful branch-only test, an old merge-base checkout, manual run, previous
attempt, expired/malformed/oversized artifact, failed run, or unrelated workflow
cannot satisfy the gate. Missing or stale receipts time out closed after 15
minutes; jobs allow 20 minutes including checkout. A rerun started during receipt
download invalidates acceptance. No workflow is automatically dispatched, no
code from artifacts is executed, and the consumer token has only contents/read
and actions/read. Canonical CI's permission scope is unchanged.

Pull requests always trigger canonical and quality validation. Their push
ignore paths agree and Kubernetes excludes Markdown-only pushes, so documentation-only pushes do not create a quality gate
waiting for intentionally absent canonical CI. A manual Kubernetes run does not
need a canonical receipt and can test arbitrary refs independently.

## Workflow inventory

| Responsibility | Workflows |
| --- | --- |
| Canonical Python and compatibility entry points | `aurora-ci-minimal`, `code-quality` |
| JavaScript and browser application | `node-tests`, `frontend-ci` |
| Specialized validation | `cross-platform-paths`, `dependency-validation`, `model-catalog-validation`, `catastrophe-prevention`, `queue-validation`, `safety_commit` |
| Code scanning and status compatibility | `codeql-unified`, `branch-protection`, `codacy-analysis`, `codacy` |
| Constellation contracts and integration | `constellation-ci`, `constellation-integration` |
| Build, publish and collaboration | `k8s-deploy`, `aurora-release`, `aurora_agent_runner`, `deploy-pages`, `symbolic-bundle`, `collab-sync`, `cross-repo-capsule-exchange`, `synergy_dashboard` |
| Constellation events and scheduled services | `constellation-event-publisher`, `constellation-event-router`, `constellation-health-audit`, `constellation-knowledge-aggregator` |
| Queue, PR and project-board automation | `auto-assign-and-review`, `auto-labeler`, `auto-merge-admin`, `ci-status-project-automation`, `pr-selective-integration`, `pr_evaluation`, `project-board-ci-sync`, `queue-decision-escalation`, `queue-issue-ingestion`, `sonarcloud-issue-reporter`, `stale-and-blocked-report` |
| State maintenance and manual administration | `simulation-state-freshness`, `admin-quick-push` |

Names omit the `.yml` extension. Codacy workflows are explicitly disabled in the
baseline; external Codacy checks are a separate integration. The three jobs in
`branch-protection.yml` currently print success without substantive validation.
They are retained, not represented as real security or health coverage.

## Remaining consolidation

Repository access cannot read branch-protection settings (GitHub returns 403).
Therefore this tranche preserves all workflow filenames and public check names,
including placeholders and disabled entry points. Before removing them, obtain
the actual required-check/workflow settings and map them to substantive owners.
Do not infer that a check is optional from a green PR or an empty API response.

Next inventory reviews should compare constellation validation with the
canonical suite, examine legacy build/publish paths and their consumers, and
replace placeholder branch-protection checks with substantive validation.
Keep unique security, platform, dependency-resolution, frontend and deployment
coverage. Validate each migration on both a PR and its resulting main push;
update the root queue with measured results and remaining work.

To recover from a gate timeout, inspect the canonical run for the same event and
head. Rerun canonical CI for the current checkout if necessary, then rerun the
consumer job. Never accept a stale receipt to make a build proceed. Reverting
the three changed workflow files restores the independent jobs; the helper,
tests and this map can then be removed in the same reviewed rollback.
