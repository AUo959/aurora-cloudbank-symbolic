# Review Notes — Agent Intake Layer

This directory is a **persistent intake queue** for architectural observations, tensions, risks, and improvement opportunities surfaced during sessions, audits, or reviews.

Agents should check this directory regularly. Notes in `status: open` are eligible to be picked up as tasks or opened as GitHub issues.

**Central roadmap:** [`docs/ROADMAP.md`](../ROADMAP.md)  
**Execution queue:** [GitHub Issues](https://github.com/AUo959/aurora-cloudbank-symbolic/issues)

---

## Where this fits

```text
outside/session review
  → docs/review-notes/entries/YYYYMMDD-short-slug.md
  → triage status: open | picked_up | issued | resolved | wont_fix
  → GitHub issue when actionable
  → docs/ROADMAP.md when priority affects sequencing
  → implementation PR
  → update issue + review note + roadmap
```

Use review notes for observations that should not disappear but are not yet fully scoped as implementation work. Use GitHub Issues once the evidence, impact, and acceptance criteria are clear.

---

## Directory Structure

```text
docs/review-notes/
├── README.md              ← This file (schema + workflow)
├── _template.md           ← Copy this to create a new note
└── entries/
    └── YYYYMMDD-slug.md   ← Individual review note files
```

---

## Lifecycle

```text
open → picked_up → issued → resolved
         ↓
       wont_fix
```

| Status | Meaning |
|---|---|
| `open` | Ready to be picked up by an agent or developer |
| `picked_up` | An agent or developer has claimed this note |
| `issued` | A GitHub issue has been opened (link in `issue_url`) |
| `resolved` | The underlying problem has been addressed |
| `wont_fix` | Deliberately deferred or accepted as-is |

---

## Schema

Every entry must include the following frontmatter:

```yaml
---
id: YYYYMMDD-slug          # Unique identifier matching the filename
date: YYYY-MM-DD           # Date the note was filed
filed_by: <name or agent>  # Who or what filed this note
status: open               # Lifecycle status (see above)
priority: low|medium|high|critical
category: architecture|security|performance|governance|testing|documentation|other
affected_files:            # List of files this note relates to
  - path/to/file.py
issue_url:                 # GitHub issue URL once opened (leave blank until issued)
tags: []                   # Optional free-form tags
---
```

Followed by a freeform body with at minimum:

- **Observation** — what was noticed
- **Risk / Impact** — why it matters
- **Suggested Actions** — concrete next steps (use `- [ ]` task checkboxes)

---

## Agent Instructions

When scanning this directory:

1. List all entries in `entries/` where `status: open`.
2. Evaluate priority and category to decide whether to pick up or open an issue.
3. To open an issue: copy the note's **Observation** as the issue body, link back to the note file, then update `status: issued` and `issue_url` in the frontmatter.
4. If the issue changes project sequencing, update [`docs/ROADMAP.md`](../ROADMAP.md) in the same PR or a follow-up docs PR.
5. To pick up directly: update `status: picked_up`, implement the suggested actions, then update to `resolved` when done.
6. Never delete note files — they are a permanent audit record. Only update their `status`.

---

*Continuity flows through coherence. The system remembers because we chose to align.*
