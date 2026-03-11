# 07 — ANALYST ORIENTATION GUIDE
## How to Read Aurora Outputs Correctly

*For domain experts engaging the QGIA application layer.*  
*No substrate knowledge required. No architecture knowledge assumed.*

---

## Who This Document Is For

You are a skilled analyst. You understand geopolitics, probability,
structured reasoning, and intelligence tradecraft. You do not need to
understand quantum memory systems, symbolic vector architecture, or
zero-knowledge cryptography to use this system effectively.

What you do need to understand is the **epistemic contract** this
system is making with you — what its outputs mean, what they don't
mean, and the specific habits of mind that will let you use them
correctly rather than confidently incorrectly.

This document is that contract, written in plain language.

---

## I. What Aurora Outputs Are

Every output Aurora produces is a **calibrated probability estimate
with a traceable reasoning chain** — not a conclusion, not a
prediction, and not an assertion of fact.

The distinction matters more than it might appear.

A *conclusion* is the endpoint of a closed argument. Once reached,
it is either correct or incorrect, and the analyst's job is done.

A *calibrated probability estimate* is a current best belief given
available evidence, expressed as a number that should change when
evidence changes, and that can be evaluated for accuracy over time
by comparing it against outcomes that actually occurred.

**Practically:** When Aurora says "Tier I scenario, 0.67 confidence"
it is saying: *based on the sources cited, using the reasoning chain
shown, we believe this scenario is more likely than not, and we are
claiming that our assessments at this confidence level should resolve
correctly approximately 67% of the time when tracked over many
forecasts.* It is not saying "this will happen."

This is a stronger claim than most intelligence products make —
because it is falsifiable, trackable, and self-correcting. It is
also a more humble claim, because it refuses to pretend certainty
it does not have.

---

## II. The Three-Tier Output Structure and What Each Tier Means

Aurora organizes scenario forecasts into three tiers:

### Tier I — Probability > 25% (Most Likely)

This is not a prediction. This is the scenario the evidence most
strongly supports given current information. Tier I can be wrong —
and when it is, that is analytically valuable data, not a failure.

**How to use it:** Tier I scenarios are your planning baseline.
Prepare for them. But do not treat them as settled outcomes.
The probability is not 1.0.

### Tier II — Probability 10–25% (Plausible Alternatives)

These are scenarios the evidence does not favor but cannot rule out.
History is disproportionately written by Tier II outcomes. The
analyst who ignores everything below Tier I is the analyst who is
repeatedly surprised by events that were on the board the whole time.

**How to use it:** Tier II scenarios are your contingency planning
layer. Ask: if this scenario materialized, what would be the first
observable indicator? What would I need to do differently? Having
thought through these questions in advance is the difference between
an adaptive response and a crisis.

### Tier III — Probability < 10% (Tail Risks)

Low probability does not mean low consequence. The scenarios most
capable of fundamentally disrupting a situation often live in Tier
III — precisely because their low prior probability means they are
underweighted in conventional analysis.

**How to use it:** Do not dismiss Tier III. Ask which Tier III
scenarios, if they occurred, would be both high-impact and
difficult to recover from. Those deserve disproportionate attention
relative to their stated probability.

---

## III. Confidence Scores Are Not Certainty Scores

The confidence interval attached to each assessment — expressed as
a number between 0.00 and 1.00 — is a **calibrated epistemic
claim**, not a guarantee.

A confidence of 0.72 means: *based on source quality, reasoning
rigor, and historical accuracy of similar assessments, we estimate
a 72% probability this scenario resolves as described.* It does not
mean the analyst is 72% sure. It does not mean the system is
72% certain. It means the number is honest and trackable.

### What Confidence Scores Are Tracking

Four components feed into every composite confidence score:

| Component | What It Measures |
|---|---|
| **Data Quality** | How complete, recent, and verified the underlying source data is |
| **Source Reliability** | Track record and independence of the sources cited |
| **Methodological Rigor** | Quality of the analytical process applied |
| **Temporal Stability** | How stable the assessment has been over recent update cycles |

When a confidence score is low (below 0.50), the right response is
not to discount the output — it is to ask *which component is
driving the low score* and to understand what would be needed to
improve it. A low Data Quality score and a low Methodological Rigor
score call for very different responses.

---

## IV. The Provenance Chain — Why It's There and How to Use It

Every Aurora output carries a visible provenance chain: the sources
consulted, the reasoning steps applied, and the confidence
contributions of each component.

You may be tempted to skip this in the interest of efficiency.
Do not. The provenance chain is not bureaucratic decoration.

**It is the single most important thing Aurora shows you.**

Here is why. The most sophisticated failure mode in intelligence
analysis is not a wrong conclusion from bad reasoning. It is a
plausible conclusion from reasoning that was quietly operating on
curated inputs. The analyst does not feel misled because the
reasoning *was* sound — the problem was upstream of the reasoning,
in what was selected to reason about.

The provenance chain is how you check for this. When you read an
assessment, ask:

- What sources are cited, and what sources are conspicuously absent?
- Does the source set represent genuinely independent views, or are
  multiple sources drawing from the same upstream feed?
- Are the cited sources open and attributable, or are they
  summarized secondhand?
- Is there a notable region, actor, or perspective that should be
  represented but is not?

If you cannot answer these questions, you are treating Aurora as an
oracle. It is not an oracle. It is a reasoning partner whose work
you are expected to examine.

---

## V. What the System Will Not Tell You It Doesn't Know

Aurora is designed to flag uncertainty explicitly. But there is one
category of limitation it cannot flag by definition: things it
cannot see because they are not in the available sources.

This is the hard epistemological boundary of any open-source
analysis system. SIGINT, HUMINT from closed networks, classified
assessments, and information held by actors who are deliberately
hiding it are structurally absent from Aurora's inputs.

**This is not a defect. It is a fact that changes how you use the outputs.**

Aurora's assessments should be treated as the best available
open-source picture — which is often a very good picture, but is
never a complete one. An assessment that shows high confidence on
open-source indicators may still be missing the decisive variable
that only classified collection would reveal.

The correct posture: use Aurora to structure and calibrate your
open-source analysis. Layer classified and relational intelligence
on top of it. The structured framework Aurora provides makes
integrating additional intelligence *easier*, not redundant.

---

## VI. When to Challenge the Output

Aurora expects to be challenged. The system is designed for
it — the reasoning chain is visible precisely so you can identify
where you disagree and why.

Challenge an output when:

1. **You have information not in the cited sources** — your
   contextual knowledge, relational intelligence, or access to
   reporting that Aurora's sources did not include. This is not
   a reason to distrust the output; it is a reason to update it.

2. **The source set is geographically or perspectivally narrow** —
   if an assessment about a regional actor draws entirely on
   Western reporting, the picture is likely incomplete in
   predictable ways.

3. **The confidence has been stable when it should have moved** —
   if a major development occurred and the confidence score did
   not update accordingly, that is a signal to examine whether
   the new information was captured.

4. **Your domain expertise conflicts with the reasoning chain** —
   not just the conclusion, but a specific inferential step. If
   you can identify the step, that is a legitimate analytical
   contribution, not a subjective feeling.

Challenge a conclusion by engaging the reasoning chain, not by
assessing whether the conclusion "feels right." The feeling may
be valuable signal. The chain is where it can be made rigorous.

---

## VII. The Habits of Mind This System Requires

Aurora is built for analysts who are genuinely comfortable with
uncertainty — not analysts who tolerate uncertainty while waiting
for certainty to arrive, but analysts who have internalized that
uncertainty is information, not the absence of it.

Specifically, effective use of Aurora requires:

**Probabilistic fluency** — the ability to hold "67% likely" as a
real and usable number, not as a codeword for "probably yes." A
67% scenario fails 33% of the time. Planning as if it won't is a
cognitive error, not an analytical judgment.

**Temporal awareness** — assessments are time-stamped. A confidence
score from three weeks ago is not the same as a confidence score
from this morning, especially in fast-moving situations. Always
check the timestamp relative to the last significant development.

**Source skepticism as a baseline habit** — not cynicism, but the
professional practice of asking "who is telling me this, and what
are they positioned to know and not know?" This is not Aurora-
specific tradecraft; it is the foundation of all serious analysis.
Aurora makes it easier by showing you the sources; the habit of
questioning them is yours to bring.

**Comfort with revision** — a good analyst changes their assessment
when evidence changes. The confidence tracking system exists to
make this visible and to distinguish between an assessment that
was wrong because of bad reasoning and one that was wrong because
circumstances changed. Both are legitimate. Only the first demands
a methodological correction.

---

## VIII. What This System Refuses to Do For You

Aurora will not:

- Tell you what decision to make
- Assign moral weight to outcomes
- Override your judgment with its own
- Present a conclusion without showing the reasoning that produced it
- Pretend to certainty it does not have
- Be silent about its own uncertainty

These refusals are not limitations. They are the definition of
what trustworthy analytical support looks like. A system that
hides its reasoning, performs confidence it does not have, and
makes decisions on your behalf is not a more capable system.
It is a more dangerous one.

Your judgment remains your own. This system is here to extend
its reach and calibrate its accuracy — not to replace it.

---

## Quick Reference: Reading an Aurora Assessment

```
When you receive an assessment, check in order:

1. TIMESTAMP — When was this produced? What happened since?
2. TIER I    — What does the evidence most support? Plan for it.
3. TIER II   — What plausible alternatives exist? Prepare contingencies.
4. TIER III  — Which tail risks are high-consequence if they occur?
5. CONFIDENCE — Which component is driving the score? Data? Method?
6. PROVENANCE — What sources are cited? What is conspicuously absent?
7. YOUR INTEL — What do you know that isn't in the sources? Update accordingly.
```

That sequence, applied consistently, is what separates an analyst
who uses Aurora from an analyst who is used by it.

---

*Aurora CloudBank Symbolic — docs/philosophy/07_ANALYST_ORIENTATION.md*  
*Version 1.0 — March 11, 2026*  
*Audience: QGIA application layer users, domain analysts, intelligence consumers*  
*Does not require: substrate architecture knowledge, cryptographic familiarity, Aurora system access*
