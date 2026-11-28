# Queue automation PR lifecycle

Queue ingestion and decision escalation propose generated metadata through PRs.
They never push to `main`, merge a proposal, or change branch protection.

Before generating a new proposal, each workflow looks for an open same-repository
`github-actions[bot]` PR in its existing timestamped branch namespace. If one
exists, the newest proposal is retained and new generation is deferred. The
escalation workflow also defers issue pings, preventing repeat notifications
while its previous `last_surfaced` update is still under review. When no proposal
of that kind remains open, the next run generates from current `main` again.

Notification comments carry a durable marker derived from the gate id and its
pre-update `opened`/`last_surfaced` baseline. Before posting, the helper reads all
comment pages and skips an existing matching `github-actions[bot]` marker. If
delivery or subsequent PR creation fails partway through, the next run skips
delivered notifications and retries the remaining gates. A merged surfacing
update changes the baseline, allowing the next eligible escalation cycle.
Comment lookup errors fail the job before posting; closed issues are skipped.

The helper refuses a matching proposal with an unexpected author, fork, base,
head SHA, or changed-file scope. It checks all pages of open PRs and changed
files. Workflow changes and executable code never qualify as generated data.

GitHub places PR events created with `GITHUB_TOKEN` behind approval. Explicit
`workflow_dispatch` is supported by that token, so the publishing workflows
request `aurora-ci-minimal.yml` (`CI Check`) and `queue-validation.yml` on the
validated proposal branch. Each dispatcher job requires `actions: write`.
An existing dispatch on the same head is retained, including failures: weekly
runs do not automatically rerun failing checks. An operator diagnoses failures
and retries explicitly. A partial dispatch failure fails the producer job;
its next run reuses the proposal and requests only the missing workflow.

See [GitHub's workflow trigger contract](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

## Rollout and existing backlog

After this change is reviewed and merged, run the two producer workflows once.
They select the latest existing ingestion/escalation proposals and request their
checks. Queue schema and view freshness remain enforced; old proposals may
expose genuine drift. Review that drift before merging. New escalation proposals
regenerate `OPEN_GATES.md` alongside the registry update.

Older generations remain open for operator comparison and explicit disposition.
This change does not close them automatically. Verify content differences and
preserve any unique work before choosing which generations are superseded.
Approval-required legacy workflow runs are not bulk-approved by this helper.

Validate locally without GitHub writes:

```sh
python -m pytest --noconftest tests/test_publish_queue_pr.py \
  tests/test_queue_issue_ingestion.py tests/test_gate_escalation.py \
  tests/test_work_queue_schema.py -q
python ops/work_queue/sync_queue.py --check
```

Live dispatch and required-check acceptance must be verified after merge.
Local mocked regressions establish lifecycle behavior, not a completed rollout.
