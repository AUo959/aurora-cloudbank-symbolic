# Aurora Durable Task Execution Record SOP

**Version:** 1.0  
**Date:** 2026-08-12  
**Status:** proposed operating doctrine  
**Scope:** repository-affecting work in `aurora-cloudbank-symbolic` and related Aurora repositories

## Purpose

Handoffs preserve continuity between agents and sessions, but they are not sufficient as the authoritative execution reference for substantial work.

For non-trivial tasks, Aurora requires a **Durable Task Execution Record (DTER)** committed to Git before implementation begins. The DTER is the durable answer to:

- what are we trying to accomplish;
- why are we doing it;
- what authority and evidence are we relying on;
- what is in scope and out of scope;
- what files/systems are expected to change;
- what invariants must not be violated;
- what sequence and gates govern execution;
- what decisions changed the plan;
- what validation proves completion;
- what remains unresolved;
- where another agent should resume.

A handoff MUST reference the DTER when one exists. A handoff MUST NOT replace it.

## Coordination chain

The standard durable reference chain is:

```text
Queue / GitHub Issue
        ↓
Durable Task Execution Record (DTER)
        ↓
Plans / Specs / ADRs / Recovery Records
        ↓
Implementation Commits + Tests + Receipts
        ↓
Pull Request / Review
        ↓
Handoff / Session Continuation
```

The work queue selects and prioritizes work. Session claims and handoffs coordinate who is acting. The DTER defines the execution contract. GitHub commits, reviews, tests, and merge history remain implementation canon.

## When a DTER is required

Create and commit a DTER **before implementation mutation** when any of the following are true:

1. the task spans multiple files, subsystems, repositories, or meaningful steps;
2. the task changes architecture, runtime behavior, simulation behavior, authority boundaries, schemas, APIs, or persistent state;
3. the task is a migration, restoration, recovery, refactor, integration, or deployment;
4. the task contains destructive, difficult-to-reverse, or preservation-sensitive operations;
5. the task changes canon-bearing, governance, ethics, security, or lineage-sensitive material;
6. determinism, reproducibility, provenance, or auditability is a stated requirement;
7. the work is expected to span agents, platforms, sessions, or days;
8. implementation depends on a non-trivial set of assumptions or owner decisions;
9. the operator explicitly asks for a plan or committed intent before execution.

A DTER is normally unnecessary for a single trivial typo/doc correction or a narrowly obvious one-file maintenance patch with no architectural consequences.

### Emergency exception

Incident containment may require an immediate safety mutation before a DTER can be committed. In that case:

- make only the minimum containment change;
- record the exact emergency mutation and reason in the PR/issue;
- create the DTER immediately afterward before remediation or expansion continues.

The exception is for containment, not convenience.

## Naming and location

Default location:

`ops/task_records/`

Default filename:

`AURORA__TASK_RECORD__<TOPIC>__vX.X__YYYY-MM-DD.md`

Example:

`AURORA__TASK_RECORD__GUMAS_DETERMINISTIC_BATTLE_RUNTIME__v1.0__2026-08-12.md`

Use the same root filename for revisions and increment the version logically.

Recommended task identifier inside the record:

`TASK-YYYYMMDD-<short-slug>`

## Required DTER structure

Every DTER MUST contain the following sections.

### 1. Identity and links

- task id;
- status;
- owner / active worker;
- repository / branch;
- queue id, issue, PR, and related task links where available;
- creation commit once known;
- latest controlling revision.

### 2. Objective

State the intended outcome in testable terms. Avoid implementation detail unless it is itself part of the requirement.

### 3. Acceptance statement

A concise statement of what must be true before the task can be called complete.

### 4. Authority and source inputs

List the files, commits, canon sources, specifications, owner decisions, recovery artifacts, external evidence, or runtime observations that are authoritative for the task.

Distinguish:

- independently verified evidence;
- externally supplied evidence;
- assumptions;
- derived decisions.

### 5. Scope

Explicitly list:

- in scope;
- out of scope;
- protected or immutable surfaces.

### 6. Current state and known gaps

Record what exists before mutation, including blockers, contradictions, missing source, technical debt, and unresolved assumptions.

### 7. Planned mutations

Describe expected code/data/doc mutations at a useful path or subsystem level.

This is an intent map, not a promise that every predicted path must change. Unexpected mutations must be recorded later as plan deltas.

### 8. Execution sequence and gates

Define the ordered phases of work and the condition required to leave each phase.

No later phase should begin when an earlier blocking gate is unsatisfied unless the record is explicitly revised.

### 9. Invariants and non-negotiables

List properties that must remain true throughout execution, such as:

- archival bytes remain immutable;
- no canon promotion without explicit authority;
- no destructive deletion without approval;
- deterministic input produces deterministic output;
- adapters may translate but may not become authority;
- safety or ethics constraints remain binding.

### 10. Validation and acceptance tests

Define the tests, replay checks, CI, audits, receipts, manual inspections, or comparison criteria required to prove completion.

A task is not complete because the implementation "looks right" if objective validation is available.

### 11. Stop conditions and owner decisions

Identify conditions that require the worker to stop rather than improvise, including:

- conflicting authority;
- unexpected destructive scope;
- missing source or provenance;
- security/ethics boundary changes;
- materially different architecture than planned;
- owner-level choices.

### 12. Rollback and recovery

Describe how to return to the pre-task state or otherwise recover safely if the implementation fails.

For destructive or preservation-sensitive tasks, record backups, hashes, witness artifacts, or restore points before mutation.

### 13. Decision and plan-delta log

Maintain a chronological record of material changes to the plan.

Each entry should include:

- date/time or commit;
- decision/change;
- reason/evidence;
- authority;
- consequence for scope, sequence, or validation.

Do not silently rewrite prior decisions after implementation has depended on them.

### 14. Evidence and receipts

As work proceeds, record:

- important commit SHAs;
- source/artifact hashes;
- CI or test results;
- generated validation receipts;
- benchmark/replay results;
- review findings;
- superseded artifacts.

### 15. Current status and next action

Maintain a compact cold-start state:

- current phase;
- completed gates;
- open blockers;
- exact next action;
- whether owner input is required.

This is the section handoffs should point to first.

### 16. Completion record

On completion or abandonment, record:

- final status (`completed`, `aborted`, `superseded`, or `rolled_back`);
- merge/closing commit or PR;
- validation result;
- residual risks / follow-up work;
- links to successor task records where applicable.

## Pre-implementation commit rule

For a DTER-required task, the first task-specific implementation PR/branch MUST contain a committed DTER before substantive code/data mutation begins.

Recommended sequence:

1. refresh live repository and issue/PR state;
2. claim/coordinate the task as required;
3. create the DTER from the standard template;
4. commit the DTER;
5. link it from the issue/PR/queue entry;
6. only then begin substantive implementation.

If discovery work is needed to write an accurate plan, read-only investigation may precede the DTER. Discovery mutations should not.

## Relationship to plans and specifications

A DTER is an index and execution contract, not a replacement for detailed engineering artifacts.

Use separate plans/specifications when depth is needed. The DTER should link them and state their authority.

For example:

```text
DTER
 ├─ architecture spec
 ├─ recovery report
 ├─ migration plan
 ├─ test plan
 └─ validation receipt
```

This prevents a large task from becoming one monolithic document while preserving a single durable point of reference.

## Relationship to handoffs

A handoff for a DTER-governed task MUST include at minimum:

- DTER path;
- DTER version;
- controlling commit/PR head;
- current phase;
- next action;
- unresolved decision/blocker.

The receiving agent should be able to cold-start by reading the DTER and its linked authority set without depending on chat history.

## Relationship to the work queue

When a queue item enters active implementation and requires a DTER:

- add the DTER to the item's `context_pack` when practical;
- include a `task_record` reference if/when the queue schema supports it;
- ensure `next_action` does not conflict with the DTER's current phase;
- on completion, reconcile queue state against merged GitHub evidence.

The queue remains the prioritization layer. The DTER remains the execution reference.

## Plan revisions and preservation of history

Minor factual/status updates may update the current DTER version.

Create a new DTER version when there is a material change to:

- objective;
- architecture;
- authority boundary;
- destructive scope;
- acceptance criteria;
- validation strategy;
- owner-approved direction.

The new version MUST link the superseded version and explain the delta. Do not delete the old record solely because the plan changed.

## Destructive operations rule

Classification is advisory. Destructive authority is separate.

No artifact may be deleted merely because it is labeled duplicate, redundant, deprecated, superseded, generated, or low-value.

Before destructive cleanup, the DTER must identify:

- explicit deletion authorization;
- content hashes or equivalent identity evidence;
- semantic/version/lineage comparison where applicable;
- dependency/reference checks;
- recovery path or retained witness;
- exact deletion scope.

Filename or basename equality is never sufficient evidence of content identity.

## Definition of done for this SOP

This operating doctrine is effective when substantial work can be resumed from GitHub alone through a predictable reference chain, without requiring reconstruction of intent from an ephemeral handoff or chat transcript.
