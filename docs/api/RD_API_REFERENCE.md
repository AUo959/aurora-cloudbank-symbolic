# R&D Productization Pipeline API Reference

**Version:** 1.0.0 (HR Module v3.0 "Helios")  
**Base Path:** `/rd`  
**Ethics Framework:** [Connection as Universal Constant](../../modules/hr/ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md)

---

## Overview

The R&D Productization Pipeline API provides endpoints for managing research-to-production transitions, calculating production readiness, and analyzing team coherence using Vector Symbolic Architecture (VSA).

**Core Principle:** All metrics follow the **Inquiry-First Mandate** - they exist to facilitate conversation, not replace human judgment.

---

## Authentication & Rate Limiting

- **Authentication:** Bearer token via `Authorization` header (mocked in test environments)
- **CSRF Protection:** Required for all state-changing operations (POST/PUT/DELETE)
- **Rate Limits:**
  - GET endpoints: 60-120 requests/minute
  - POST endpoints: 30-45 requests/minute

---

## Ethics Framework Integration

### Required Reading

Before using coherence metrics, review the [Ethics Framework](../../modules/hr/ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md) which establishes:

1. **What Coherence Observes:** Behavioral-symbolic alignment patterns, NOT:
   - Individual worth or capability
   - Personality compatibility
   - Future performance predictions
   - Personal relationship quality

2. **Prohibited Uses:**
   - ❌ Deterministic staffing decisions
   - ❌ Performance evaluation inputs
   - ❌ Predictive labeling ("low collaborator")
   - ❌ Automated exclusion from opportunities

3. **Mandated Human Oversight:**
   - All high-stakes decisions require HR Director review
   - 30-day appeal window for affected parties
   - Documented rationale beyond metrics required

### Data Dignity Principles

**Consent Architecture (to be implemented in v3.1):**
- **Tier 1 (Default):** Aggregated, anonymized data
- **Tier 2 (Consent Required):** Individual profiles visible to self and HR
- **Tier 3 (Explicit Request):** Data shared with project leads

**Withdrawal Rights:**
- Crew members can opt out of coherence tracking without penalty
- Systems function gracefully with partial data
- Withdrawal does not affect job security or advancement

---

## Endpoints

### Health Check

**GET** `/rd/health`

Check RD API availability and basic system metrics.

**Response:**
```json
{
  "status": "healthy",
  "active_projects": 5,
  "timestamp": "2025-11-12T10:30:00Z"
}
```

---

### Project Management

#### List Projects

**GET** `/rd/projects`

Retrieve all active R&D projects.

**Response:**
```json
{
  "success": true,
  "count": 3,
  "projects": [...],
  "context_tag": "rd_list_projects"
}
```

#### Create Project

**POST** `/rd/projects`

Initialize new R&D project.

**Request Body Format:**
```json
{
  "body": {
    "project_id": "rdp-quantum-cache",
    "name": "Quantum Cache Optimization",
    "project_type": "module",
    "lead_researcher": "T-42",
    "team_members": ["T-17", "T-89"],
    "key_technologies": ["python", "quantum-algorithms"]
  }
}
```

**Note:** Request body must be wrapped in `{"body": {...}}` due to FastAPI + SlowAPI rate limiter integration.

**Response:**
```json
{
  "success": true,
  "project": {...},
  "context_tag": "rd_create_project"
}
```

#### Advance Project Stage

**POST** `/rd/projects/{project_id}/advance`

Move project to next development stage.

**Request Body:**
```json
{
  "body": {
    "new_stage": "proof_of_concept",
    "milestone": "Initial prototype validated"
  }
}
```

**Available Stages:**
- `research` (0% → 15%)
- `proof_of_concept` (15% → 30%)
- `prototype` (30% → 50%)
- `alpha` (50% → 70%)
- `beta` (70% → 85%)
- `production` (85% → 100%)
- `maintenance` (100%)

---

### Production Readiness

#### Update Readiness Score

**POST** `/rd/projects/{project_id}/readiness`

Calculate production readiness based on quality metrics.

**Request Body:**
```json
{
  "body": {
    "code_quality": 0.92,
    "documentation": 0.88,
    "test_coverage": 0.85,
    "performance": 0.90,
    "security": 0.95
  }
}
```

**Response:**
```json
{
  "success": true,
  "production_readiness": 0.9000,
  "context_tag": "rd_update_readiness",
  "inquiry_prompts": {
    "status": "production-ready",
    "questions_to_ask": [
      "Have all stakeholders reviewed deployment procedures?",
      "Is the monitoring/alerting infrastructure in place?",
      "Are rollback procedures documented and tested?"
    ]
  }
}
```

**Ethics Note:** Readiness scores reflect technical maturity, not team capability. Use inquiry prompts to guide deployment conversations.

---

### Team Coherence Analytics

#### Update Team Coherence

**POST** `/rd/projects/{project_id}/coherence`

Calculate team coherence using VSA vectors.

**Request Body:**
```json
{
  "body": {
    "team_vectors": {
      "T-42": [0.8, 0.7, 0.9, 0.6, 0.85],
      "T-17": [0.75, 0.72, 0.88, 0.65, 0.82],
      "T-89": [0.78, 0.68, 0.91, 0.62, 0.87]
    }
  }
}
```

**VSA Vector Dimensions:**
1. Focus (task orientation)
2. Empathy (interpersonal awareness)
3. Resilience (stress recovery)
4. Synthesis (pattern integration)
5. Ethical Rigor (decision-making alignment)

**Response:**
```json
{
  "success": true,
  "team_coherence": 0.8234,
  "context_tag": "rd_update_coherence",
  "guidance": {
    "interpretation": "Strong team alignment detected",
    "inquiry_prompts": [
      "How can we document and share these successful collaboration patterns?",
      "Are there opportunities to mentor other teams?"
    ],
    "watch_for": "Groupthink risk - ensure diverse perspectives are still valued"
  },
  "ethics_note": "Coherence measures behavioral-symbolic alignment, not team quality. Low coherence can indicate healthy diversity or coordination challenges - human judgment required to distinguish."
}
```

**Interpretation Guidelines:**

| Score Range | Interpretation | Action |
|-------------|----------------|--------|
| ≥ 0.75 | Strong alignment | Document patterns, watch for groupthink |
| 0.55 - 0.74 | Healthy diversity | Monitor communication channels |
| < 0.55 | Coordination friction | Investigate root causes, consider alignment session |

---

### Organization-Wide Coherence

#### Full Coherence Analysis

**GET** `/rd/coherence/full`

Calculate average coherence across all team members in the organization.

**Response:**
```json
{
  "success": true,
  "vector_count": 35,
  "pairwise_samples": 595,
  "average_coherence": 0.6845,
  "context_tag": "rd_full_coherence",
  "interpretation": {
    "system_health": "Moderate alignment - typical for diverse teams",
    "recommended_action": "Identify specific low-coherence pairs for targeted support",
    "what_this_means": "This aggregate metric reflects overall behavioral-symbolic alignment across the organization. Low scores suggest coordination friction, NOT individual performance issues.",
    "next_steps": "Use /coherence/mediation endpoint to identify specific pairs needing support"
  }
}
```

**System Health Thresholds:**
- **≥ 0.70:** Strong overall alignment - healthy team dynamics
- **0.55 - 0.69:** Moderate alignment - typical for diverse teams
- **< 0.55:** Low alignment - systemic coordination challenges detected

#### Coherence Mediation

**GET** `/rd/coherence/mediation?threshold=0.55&limit=25`

Identify low-coherence pairs with conversation starters and anchor recommendations.

**Query Parameters:**
- `threshold` (default: 0.55): Coherence score below which pairs are flagged
- `limit` (default: 25): Maximum pairs to return

**Response:**
```json
{
  "success": true,
  "threshold": 0.55,
  "pair_count": 3,
  "pairs": [
    {
      "member_a": "T-42",
      "member_b": "T-89",
      "coherence": 0.3421,
      "recommended_anchor": "T1:focused_alignment_breath",
      "conversation_starters": [
        "What recent project challenges might be affecting team dynamics?",
        "Are there unaddressed communication preference mismatches?",
        "Would a facilitated alignment session help clarify shared goals?"
      ],
      "mediation_recommended": true,
      "urgency": "high"
    }
  ],
  "ethics_context": {
    "what_this_observes": "Behavioral-symbolic alignment patterns between team members, NOT compatibility or relationship quality",
    "what_this_cannot_tell": "Individual worth, future performance, or personal connection depth",
    "inquiry_first_mandate": "These metrics exist to facilitate conversation, not replace human judgment",
    "escalation_path": "For persistent low coherence (< 0.35 for 30+ days), contact HR Director for facilitated mediation",
    "data_dignity_note": "All crew members can request exclusion from coherence tracking without penalty"
  }
}
```

**Urgency Levels:**

| Coherence Score | Urgency | Mediation | Action |
|-----------------|---------|-----------|--------|
| < 0.35 | High | Recommended | Facilitated alignment session |
| 0.35 - 0.55 | Medium | Optional | Anchor protocol alignment |
| ≥ 0.55 | Low | Not needed | Monitor and document successes |

**Anchor Protocol Recommendations:**

Anchors are stress recovery and communication preference protocols stored in crew profiles:
- **T1 anchors:** Temporal protocols (breathing exercises, focus restoration)
- **SRB anchors:** Spatial-relational boundaries (workspace preferences, communication channels)

---

### Pipeline Reporting

#### Generate Pipeline Report

**GET** `/rd/report`

Aggregate metrics across all active projects.

**Response:**
```json
{
  "success": true,
  "aggregate_metrics": {
    "total_projects": 8,
    "by_stage": {...},
    "average_readiness": 0.7234,
    "average_coherence": 0.6891
  },
  "bottlenecks": [...],
  "pipeline_health": "healthy",
  "context_tag": "rd_pipeline_report"
}
```

#### Team Member Capacity

**GET** `/rd/capacity/{team_member}`

Estimate parallel project capacity for a team member.

**Response:**
```json
{
  "success": true,
  "team_member": "T-42",
  "active_projects": 3,
  "capacity_score": 0.75,
  "recommendation": "At moderate capacity",
  "context_tag": "rd_capacity_estimate"
}
```

---

## Error Handling

All endpoints return structured errors:

```json
{
  "detail": "Project 'rdp-invalid' not found"
}
```

**HTTP Status Codes:**
- `200 OK`: Successful operation
- `400 Bad Request`: Invalid input (e.g., score out of range)
- `404 Not Found`: Project/resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

---

## Best Practices

### Using Coherence Metrics Ethically

1. **Always Start with Conversation**
   - Use coherence scores as conversation starters, not verdicts
   - Review inquiry prompts before taking action
   - Involve team members in interpreting their own data

2. **Context Matters**
   - Low coherence may indicate:
     - Healthy cognitive diversity (positive)
     - Communication breakdown (needs attention)
     - Recent team changes (temporary, resolves with time)
   - High coherence may indicate:
     - Strong collaboration (positive)
     - Groupthink risk (needs monitoring)

3. **Human Oversight Required**
   - Never make staffing decisions based solely on coherence scores
   - Consult HR Director for persistent low coherence (< 0.35 for 30+ days)
   - Document reasoning beyond metrics for all high-stakes decisions

4. **Respect Data Dignity**
   - Honor opt-out requests immediately
   - Use minimum data necessary for decision
   - Provide transparency when coherence data informs decisions

### Integration Patterns

**Daily Standup Augmentation:**
```python
# Get team coherence for context
coherence = api.post(f"/rd/projects/{project_id}/coherence", 
                     json={"body": {"team_vectors": current_vectors}})

if coherence["team_coherence"] < 0.55:
    # Use inquiry prompts to guide standup discussion
    for prompt in coherence["guidance"]["inquiry_prompts"]:
        print(f"Discussion topic: {prompt}")
```

**Pre-Project Risk Assessment:**
```python
# Check if potential team members have low coherence
mediation = api.get("/rd/coherence/mediation?threshold=0.50")

# Review pairs before finalizing team assignments
for pair in mediation["pairs"]:
    if pair["mediation_recommended"]:
        schedule_alignment_session(pair["member_a"], pair["member_b"])
```

---

## Version History

- **v1.0.0** (2025-11-12): Initial release with Ethics Framework integration
  - Inquiry-first mandate implemented
  - Contextual interpretation added to all coherence endpoints
  - Misuse prevention language embedded
  - Data dignity principles documented

---

## Support & Feedback

**HR Director:** Helena Vu  
**Technical Issues:** Open issue at [aurora-cloudbank-symbolic/issues](https://github.com/AUo959/aurora-cloudbank-symbolic/issues)  
**Ethics Concerns:** Contact HR directly via secure channel

**Anonymous Feedback:** Available through HR portal (Tier 1 consent - aggregated only)
