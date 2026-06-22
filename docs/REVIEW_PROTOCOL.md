# Aurora Review Protocol

**Version:** 1.0.0  
**Authority:** Aurora  
**Last Updated:** 2026-06-22  
**Applies to:** All AI contributors, coding agents, and human reviewers performing any review, audit, or assessment of repo state  
**Gap origin:** GAP-010 — see `docs/review-notes/2026-06-22_general-review-and-gap-010.md`

---

## Purpose

This document defines the mandatory methodology for any review pass conducted against the `aurora-cloudbank-symbolic` repo. It exists because on 2026-06-22, an AI contributor (Perplexity) asserted that `ops/work_queue/` did not exist — based on a root directory listing — despite the directory being fully built with 10 files. The false assertion was written into a review session, treated as a legitimate finding, and would have driven duplicate work if not caught by the operator.

This protocol closes the governance gap that allowed that failure. It is not aspirational — it is a conduct requirement.

---

## The Core Rule

> **Find → Read → Verify → Assert.**  
> Never assert from structure. Only assert from content.

This rule is unconditional. It applies even when you believe you already know the answer. It applies under time pressure. It applies when a directory listing looks empty. It applies on the tenth review pass as much as the first.

---

## Prohibited Behaviors

The following are explicitly forbidden during any review activity:

### 1. Assert-Before-Read
Claiming a file, directory, or artifact exists or does not exist without reading the actual path.

> ❌ *"There is no `ops/work_queue/` — the queue system has not been built."* (said after listing root only)  
> ✅ Read `ops/`, then `ops/work_queue/`, then report what is actually there.

### 2. Size-Based Inference
Drawing conclusions about content, quality, or completeness from file size alone.

> ❌ *"`ROADMAP.md` is 463 bytes — it's a stub and a contributor dead end."*  
> ✅ Read the file. It redirected to `docs/ROADMAP.md`, which was a full strategic document.

### 3. Root-Level Assumption
Assuming a repo artifact does not exist because it was not found at the root listing. Subdirectories must be traversed before any absence claim is made.

> ❌ *"I don't see `QUEUE.json` in the root, so it doesn't exist."*  
> ✅ Check `ops/work_queue/queue.json` explicitly.

### 4. Redirect Ignoring
Treating a stub or redirect file as the destination without following the redirect to the canonical source.

> ❌ Reviewing root `ROADMAP.md` and concluding the roadmap is thin.  
> ✅ Follow the redirect. Read `docs/ROADMAP.md`.

### 5. Prior-Session Assumption
Asserting current repo state from memory of a prior session without re-reading the file. Repo state changes between sessions. Memory does not reflect the repo — the repo reflects itself.

> ❌ *"We haven't built the queue yet"* (said from session memory, without checking).  
> ✅ Read `ops/work_queue/` in the current session before asserting its state.

### 6. Fragment Inference
Reasoning from search result fragments, code snippets, filenames, or partial content to form a conclusion about the whole. This is explicitly forbidden in `CANON_INDEX.md` and extends to all review activity.

---

## Required Methodology

### Before asserting anything about a file or artifact

1. **Read it** — open the file and read its content, not just its listing entry
2. **Follow redirects** — if the file says "see X", read X before forming any opinion
3. **Traverse paths** — if looking for `ops/work_queue/queue.json`, check `ops/work_queue/` explicitly; do not infer from root
4. **Check referenced docs** — if a file references another as authoritative, read that one too before concluding

### Before asserting anything about a directory

1. **List the directory** — not just its parent
2. **Read at least the README** (if present) before characterizing the directory's purpose or completeness
3. **Do not declare a directory empty or missing** based on its parent listing alone

### Before writing an observation into a review note

1. **Every claim must be backed by a direct file read** — not inferred from structure, size, name, or memory
2. **If you cannot verify a claim by reading, mark it explicitly as unverified** — use: *"Unverified — requires direct read of [path]"*
3. **Retract false claims immediately** when corrected — retraction notes go into the same review note, not silently dropped

---

## Review Note Standards

Review notes in `docs/review-notes/` become part of the canonical record and are read by subsequent agents as ground truth. A false observation in a review note propagates downstream.

**Every observation in a review note must be tagged with its evidence source:**

| Tag | Meaning |
|---|---|
| `[READ: path]` | Claim is backed by direct file read at the stated path |
| `[LISTED: path]` | Claim is based on directory listing only — no file content read |
| `[UNVERIFIED]` | Claim not yet verified by direct read — flagged for follow-up |
| `[RETRACTED]` | Claim was made in error and is formally withdrawn |

Using `[LISTED: path]` for a structural observation is acceptable. Using it to support a content claim (existence, completeness, quality) is not.

---

## The Verification Sequence

```
REVIEW PASS SEQUENCE
─────────────────────────────────────────────────────
1. ORIENT      Read CANON_INDEX.md and docs/ROADMAP.md first.
               These establish what is authoritative and what
               is already known. Do not re-discover what is
               already documented.

2. TRAVERSE    For each area under review:
               - List the directory
               - Read the README (if present)
               - Read the files relevant to your claims
               - Follow all redirects to canonical sources

3. VERIFY      For each observation you intend to record:
               - Confirm it is backed by a direct file read
               - Tag it with its evidence source
               - If you cannot verify, mark [UNVERIFIED]

4. ASSERT      Only after steps 1–3. Write the observation.
               State what you read, where, and what it showed.

5. CROSS-CHECK Before finalizing:
               - Does any claim contradict an existing review note?
               - Does any claim assert non-existence of something
                 that might exist in a subdirectory you haven't read?
               - Does any claim rely on size, name, or memory alone?
─────────────────────────────────────────────────────
```

---

## Gap Register Behavior

Gaps registered in `docs/ROADMAP.md` drive real work. A false gap wastes contributor time and may suppress valid prior work.

Before registering any gap:

1. Confirm the gap is real by reading the relevant files — not by inferring from listings
2. Check whether the gap is already registered in the gap register
3. Check whether it is already addressed in a prior review note
4. If uncertain, mark as `[UNVERIFIED]` in the review note and do not add to the gap register until verified

---

## Agent-Specific Notes

For coding agents and LLMs working the repo autonomously:

- **The queue is at `ops/work_queue/queue.json`** — read it before starting any task
- **`CANON_INDEX.md` governs what to read for any topic** — follow it
- **`session_open_ritual.md` Step 0** contains the conduct clause that mirrors this protocol — it applies to you
- **If you discover you have asserted something false mid-session**, correct it inline and note the correction — do not silently continue
- **When in doubt, read the file.** The cost of one extra file read is zero. The cost of a false assertion in a review note is real.

---

## Enforcement

This protocol cannot be technically enforced — it relies on discipline. What can be done:

- **Session ritual** (`session_open_ritual.md` Step 0) surfaces the rule at every session open
- **Review note tagging** (`[READ]`, `[LISTED]`, `[UNVERIFIED]`, `[RETRACTED]`) makes the evidence basis of every claim visible and auditable
- **Incident records** (`docs/review-notes/`) preserve violations so patterns can be identified
- **This document** exists as a standing reference any agent or contributor can be pointed to

If a violation is identified, the response is: correct the record, retract the false claim, log the incident in `docs/review-notes/`, and update the gap register if a false gap was registered.

---

*Continuity flows through coherence. The system remembers because we chose to align.*
