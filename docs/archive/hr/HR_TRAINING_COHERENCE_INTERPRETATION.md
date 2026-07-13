# HR Training Guide: Interpreting Coherence Metrics

**Target Audience:** HR Directors, Team Leads, Project Managers  
**Version:** 1.0.0 (HR Module v3.0 "Helios")  
**Prerequisites:** Review [Ethics Framework](../hr/ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md) first

---

## Purpose

This guide helps HR professionals and team leads interpret coherence metrics ethically and effectively, ensuring metrics facilitate conversation rather than replace human judgment.

---

## Core Concepts

### What Coherence Actually Measures

**Coherence scores reflect behavioral-symbolic alignment patterns** - how similarly team members approach:
- Task focus and prioritization
- Interpersonal communication
- Stress recovery preferences
- Pattern recognition and synthesis
- Ethical decision-making frameworks

**Coherence does NOT measure:**
- Individual intelligence or capability ❌
- Personality compatibility ❌
- Friendship potential ❌
- Future performance ❌
- Personal connection depth ❌

### The VSA Vector Components

Each team member has a 5-dimensional behavioral signature:

1. **Focus (0.0 - 1.0):** Task orientation and concentration patterns
2. **Empathy (0.0 - 1.0):** Interpersonal awareness and communication style
3. **Resilience (0.0 - 1.0):** Stress recovery and adaptation capacity
4. **Synthesis (0.0 - 1.0):** Pattern integration and systems thinking
5. **Ethical Rigor (0.0 - 1.0):** Decision-making alignment with values

**Example Vector:**
```
T-42: [0.85, 0.72, 0.90, 0.68, 0.88]
      [Focus, Empathy, Resilience, Synthesis, Ethics]
```

**Interpretation:** High focus and resilience, moderate synthesis, strong ethical alignment. This person likely excels in structured high-pressure work but may need support in ambiguous problem spaces.

---

## Interpreting Coherence Scores

### Team-Level Coherence

**Formula:** Average pairwise cosine similarity of all team member vectors.

| Score | Interpretation | What It Means | Action |
|-------|----------------|---------------|--------|
| **0.80 - 1.00** | Very High Alignment | Team thinks very similarly | 🚨 **Watch for groupthink!** Ensure diverse perspectives are valued. May need "devil's advocate" practices. |
| **0.70 - 0.79** | Strong Alignment | Healthy collaboration patterns | ✅ Document what's working. Consider mentoring other teams. |
| **0.55 - 0.69** | Moderate Alignment | **Normal for diverse teams** | ✅ Monitor communication channels. This is healthy! |
| **0.40 - 0.54** | Low Alignment | Coordination friction likely | ⚠️ Investigate root causes. Anchor protocol mismatches? Role confusion? |
| **< 0.40** | Very Low Alignment | Significant challenges | 🚨 Recommend facilitated alignment session. Check for unresolved conflicts. |

### Organization-Wide Coherence

**Healthy Range:** 0.55 - 0.70

- **Too high (> 0.75):** May indicate lack of cognitive diversity - consider diversifying hiring
- **Too low (< 0.50):** Systemic coordination challenges - review communication infrastructure

---

## Conversation Frameworks

### Script: Discussing Low Coherence (< 0.40)

**DON'T SAY:**
- ❌ "Your coherence score is too low - you're not compatible."
- ❌ "The system says you shouldn't work together."
- ❌ "Your personality doesn't match the team."

**DO SAY:**
- ✅ "The behavioral alignment metrics suggest there might be coordination friction. Let's explore what's happening."
- ✅ "Have you noticed any communication challenges? The data suggests there might be some mismatches we can address."
- ✅ "What would make collaboration easier for you both?"

### Sample Conversation Starters (by Urgency)

#### High Urgency (< 0.35)

1. "What recent project challenges might be affecting team dynamics?"
2. "Are there unresolved conflicts that need attention?"
3. "Would it help to clarify roles and responsibilities?"
4. "Let's look at your preferred communication channels - are they aligned?"

**Goal:** Identify specific, actionable coordination issues.

#### Medium Urgency (0.35 - 0.55)

1. "How are communication channels working for everyone?"
2. "Do you feel heard in decision-making processes?"
3. "Would shared anchor protocols help? (e.g., preferred focus times, stress recovery methods)"
4. "Are there workflow bottlenecks we can address?"

**Goal:** Proactive maintenance before issues escalate.

#### Low Urgency (> 0.55)

1. "What collaboration patterns are working well?"
2. "Are there opportunities to document successful practices?"
3. "How can we support the team's continued success?"

**Goal:** Positive reinforcement and knowledge sharing.

---

## Case Studies: Ethical Interpretation

### Case Study 1: Low Coherence, High Performance

**Scenario:**
- Team coherence: 0.42 (low)
- Project status: Ahead of schedule, high quality
- Team member feedback: Positive

**Analysis:**
Low coherence indicates **cognitive diversity** (positive!). Different problem-solving approaches create robust solutions.

**Action:**
✅ Continue monitoring, but **no intervention needed**.  
✅ Document as example of "diversity as strength."

**DON'T:** Assume low coherence = problem. Context matters!

---

### Case Study 2: High Coherence, Missed Risks

**Scenario:**
- Team coherence: 0.88 (very high)
- Project status: On track
- Recent incident: Security vulnerability missed in review

**Analysis:**
High coherence may indicate **groupthink** - everyone thinking similarly missed the edge case.

**Action:**
⚠️ Implement structured dissent practices (pre-mortems, designated skeptic).  
⚠️ Consider adding team member with different background/perspective.

**DON'T:** Celebrate high coherence without checking for blind spots.

---

### Case Study 3: Declining Coherence Over Time

**Scenario:**
- Initial coherence: 0.72 (healthy)
- Current coherence: 0.38 (low)
- Timeline: Declined over 6 weeks

**Analysis:**
Something **changed** - possible causes:
- New team member integration challenges
- Unresolved conflict
- Scope creep causing stress
- External pressures (personal life, org changes)

**Action:**
🚨 Prioritize 1-on-1s to understand root cause.  
🚨 Review recent team changes and stressors.  
🚨 Consider facilitated retrospective.

**DON'T:** Wait - declining coherence indicates growing friction.

---

## Anchor Protocol Recommendations

### What Are Anchor Protocols?

Personal preferences for communication, focus, and stress recovery stored in crew profiles.

**T1 Anchors (Temporal):**
- Preferred focus times (morning person vs. night owl)
- Meeting frequency preferences
- Response time expectations
- Stress recovery activities (breathing exercises, walks, meditation)

**SRB Anchors (Spatial-Relational Boundaries):**
- Workspace preferences (open vs. private)
- Communication channels (email vs. chat vs. face-to-face)
- Collaboration style (synchronous vs. asynchronous)
- Boundary signals ("do not disturb" protocols)

### Using Anchor Recommendations

When coherence mediation suggests an anchor protocol:

1. **Review both parties' anchors** (with their consent)
2. **Identify mismatches** (e.g., one prefers morning sync, other prefers async evening)
3. **Negotiate shared protocols** (e.g., async updates with weekly sync)
4. **Document agreement** (shared team norms document)

**Example:**
```
Member A prefers: Morning standups, quick Slack responses
Member B prefers: Async updates, email for non-urgent items

Shared protocol: Daily async standup at 9am, urgent items via Slack
```

---

## Escalation Guidelines

### When to Involve HR Director

**Immediate Escalation:**
- Coherence < 0.35 for **30+ consecutive days**
- Team member reports feeling discriminated against due to coherence data
- Manager makes staffing decision based solely on coherence score
- Suspected misuse of coherence data (performance reviews, hiring decisions)

**Scheduled Review:**
- Organization-wide coherence < 0.50 for **90+ days**
- Multiple teams experiencing persistent low coherence
- Requests for coherence data opt-out increasing

### When NOT to Escalate

- Single instance of low coherence (monitor first)
- High coherence with positive team dynamics (healthy!)
- Temporary coherence fluctuations during team transitions

---

## Prohibited Uses: What NOT to Do

### ❌ NEVER Use Coherence Scores For:

1. **Performance Reviews**
   - Coherence measures collaboration patterns, not individual capability

2. **Hiring Decisions**
   - Pre-employment coherence prediction is unreliable and unethical

3. **Promotion Criteria**
   - Leadership requires skills beyond behavioral alignment

4. **Automated Team Assignments**
   - Human judgment required to distinguish diversity from dysfunction

5. **Punitive Actions**
   - Low coherence may indicate system issues, not individual fault

### Real-World Example of Misuse

**WRONG Scenario:**
> "Manager denies promotion because applicant has low coherence with leadership team."

**Why This Is Unethical:**
- Low coherence may indicate **valuable diversity**, not incompatibility
- Leadership roles benefit from diverse perspectives
- Violates Data Dignity Principle: metrics facilitate conversation, not replace judgment

**Correct Approach:**
> "Manager reviews coherence data, identifies potential coordination challenges, and discusses strategies with applicant: 'The metrics suggest communication style differences with the leadership team. Let's discuss how we can set you up for success in cross-functional collaboration.'"

---

## Data Dignity: Handling Opt-Out Requests

### Crew Member Rights

All crew members can:
1. **Request exclusion** from coherence tracking
2. **Withdraw consent** at any time
3. **View their own VSA vectors** and coherence scores
4. **Appeal** any decision informed by coherence data

### Processing Opt-Out Requests

**Timeline:** 48 hours maximum

**Procedure:**
1. Confirm request in writing (email acceptable)
2. Remove VSA vector from active datasets
3. Mark profile with "COHERENCE_OPT_OUT" flag
4. Notify affected project leads (for capacity planning)
5. Confirm completion to crew member

**Important:**
- ✅ Opt-out does NOT affect job security
- ✅ Opt-out does NOT prevent career advancement
- ✅ Opt-out DOES mean reduced coordination data for team optimization
- ✅ Document opt-out reason (optional, crew member's choice)

---

## FAQ for HR Practitioners

### Q: What if a manager insists on using coherence for performance reviews?

**A:** Escalate immediately. This is a prohibited use per Ethics Framework Section 4.2. Document the request and refer manager to HR Director for retraining.

---

### Q: Can we use coherence data in layoff decisions?

**A:** **Absolutely not.** This violates Data Dignity Principles. Layoff criteria must be based on business needs, role requirements, and documented performance - never behavioral alignment metrics.

---

### Q: A team has 0.95 coherence - should we celebrate?

**A:** Celebrate with caution. While high coherence indicates strong collaboration, scores above 0.90 warrant a groupthink check:
- Are dissenting opinions welcomed?
- Has the team missed any obvious issues recently?
- Is there cognitive diversity in problem-solving approaches?

---

### Q: What if coherence data contradicts my observations?

**A:** **Trust your judgment first.** Metrics are instruments, not oracles. Possible explanations:
- VSA vectors need updating (behaviors have changed)
- Your observations capture nuances the metrics miss
- Metrics detect patterns not yet visible to humans

Use coherence as **additional data point**, not sole decision factor.

---

### Q: How often should VSA vectors be updated?

**A:** Recommended frequency:
- **Baseline:** Annual review for all crew
- **Triggered updates:** After major life events, role changes, extended leave
- **Team updates:** When coherence data seems misaligned with observations

---

## Training Exercises

### Exercise 1: Interpreting Ambiguous Scores

**Scenario:** Team coherence is 0.52. Is this good or bad?

**Answer:** **Context-dependent!**
- If trending down from 0.70 → investigate
- If steady at 0.52 with high performance → likely healthy diversity
- If new team, still forming → normal transition phase

**Key Learning:** No score is inherently "good" or "bad" - always consider context.

---

### Exercise 2: Prohibited Use Recognition

Which of these are prohibited uses?

1. "Use coherence to identify teams needing communication support" ✅ Allowed
2. "Deny promotion due to low coherence with leadership" ❌ Prohibited
3. "Include coherence score in performance review" ❌ Prohibited
4. "Suggest anchor protocol alignment for low-coherence pair" ✅ Allowed
5. "Automatically reassign low-coherence team members" ❌ Prohibited

---

## Additional Resources

- **Ethics Framework:** [Connection as Universal Constant](../hr/ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md)
- **API Documentation:** [R&D Productization Pipeline API](../api/RD_API_REFERENCE.md)
- **VSA Theory:** *Geometric Algebra for Behavioral Modeling* (internal research paper)
- **HR Policy Manual:** Section 7.3 - "Algorithmic Decision-Making Guidelines"

---

## Revision History

- **v1.0.0** (2025-11-12): Initial release
  - Conversation frameworks added
  - Case studies included
  - Prohibited uses documented
  - FAQ section established

---

**Questions?** Contact HR Director Helena Vu or file anonymous feedback via HR portal.
