# AI-assisted authorship and contribution provenance

Aurora CloudBank Symbolic is maintained by a human owner and developed with
substantial assistance from software agents and repository automation. This
document explains how to interpret that work and how new contributions should
record it.

## Accountability

The repository owner remains accountable for project direction, access,
publication, and merge decisions. An agent may investigate, propose, implement,
test, or review work within an authorized task, but agent output does not grant
itself permission to merge, deploy, alter secrets, promote canon, or cross an
L1/L2/L3 authority boundary.

Git authorship is provenance, not authority. A named author, co-author, bot, or
agent identity records participation in producing a change; it does not make the
commit a canon ruling or an approval receipt.

## What the existing history records

The Git history contains several recurring identity classes:

- human/owner identities, including `Travis Streets` and `AUo959`;
- historical project identities such as `Aurora CloudBank`;
- agent identities such as `Claude`, `claude-code`, GitHub Copilot, and
  `copilot-swe-agent[bot]`;
- automation identities such as Dependabot, GitHub Actions, and the Aurora
  constellation bot.

Some agent-assisted changes, especially work performed through Codex, use the
maintainer's configured Git author identity. Their agent provenance may instead
be present in the pull-request description, branch name, task receipt, or
review record. Therefore, `git shortlog` is useful evidence but is not a
complete attribution ledger.

This policy applies prospectively. Do not rewrite historical commits merely to
normalize attribution.

## Required provenance for new contributions

For a materially agent-assisted pull request:

1. State the agent or automation system in the pull-request description.
2. Describe the agent's scope: investigation, implementation, test generation,
   review, documentation, or another bounded role.
3. Record the validation actually executed and distinguish local results from
   hosted checks or human review.
4. Identify material human decisions, especially authority, security, canon,
   deployment, and irreversible-state decisions.
5. Preserve relevant issue, task, receipt, and source links so another reviewer
   can reconstruct why the change exists.

When the tool controls the commit identity, use a stable, recognizable agent or
bot identity. When a human author records a commit that was materially
co-produced by an agent, use a valid `Co-authored-by` trailer when the platform
provides a stable attributable identity. If it does not, the pull-request
disclosure is the required provenance record; do not invent an email address or
impersonate a provider-owned identity.

Minor completion, formatting, search, or command assistance need not produce a
line-by-line authorship ledger. The disclosure should be proportionate, but it
must not conceal substantial generated code, analysis, or documentation.

## Review and canon boundaries

Agent-assisted work follows the same quality, security, review, and branch
protection gates as any other contribution. Automated checks are evidence, not
approval by themselves.

Generated narrative, recovered material, simulations, and model output do not
become Aurora canon because they were committed or because an agent described
them confidently. Canon authority and promotion remain governed by
[`CANON_INDEX.md`](CANON_INDEX.md),
[`docs/CANON_PROVENANCE.md`](docs/CANON_PROVENANCE.md), and the applicable
CanonRec process.

Do not commit private prompts, credentials, hidden chain-of-thought, or raw
session transcripts as authorship evidence. Record concise decisions, inputs,
outputs, validations, and receipts instead.

## Reading a contribution record

Use these surfaces together when attribution matters:

1. the issue or task defining the requested outcome and authority;
2. the pull-request description and review record;
3. the commit author and any co-author trailers;
4. hosted checks and deterministic validation receipts;
5. the final merge identity and protected-branch result.

No single surface substitutes for the others. This layered record is the
repository's authorship model.
