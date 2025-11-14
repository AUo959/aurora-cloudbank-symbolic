# Consent Architecture Design (v3.1 Implementation Plan)

**Status:** Design Specification (Implementation: v3.1, Q1 2026)  
**Version:** 1.0.0  
**Ethics Framework:** [Connection as Universal Constant](ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md)

---

## Overview

This document specifies the 3-tier consent architecture for HR Module v3.1+, enabling crew members to control their coherence data with granular precision while maintaining operational effectiveness.

**Design Principles:**
1. **Informed Consent:** Crew understand what data is collected and how it's used
2. **Granular Control:** Three consent tiers balance privacy and functionality
3. **Reversible Decisions:** All consent can be withdrawn at any time
4. **Default Privacy:** Most restrictive tier by default (opt-in model)
5. **No Penalty:** Consent choices do not affect career advancement

---

## Three-Tier System

### Tier 1: Basic Coordination (Default)

**What Crew Consents To:**
- VSA vector created from behavioral observations
- Team-level coherence calculation (aggregated only)
- No individual coherence scores visible to managers
- Data retained for **90 days** maximum
- Used only for anonymous team health dashboards

**What Crew Can See:**
- Their own VSA vector components
- Aggregate team coherence (not pairwise)
- Historical trends for their team

**What Managers See:**
- Team-level coherence scores (no individual breakdowns)
- Trend lines (improving/declining)
- **No individual crew vectors**

**Use Cases:**
- Organization-wide health monitoring
- Anonymous research (de-identified data)
- General team effectiveness dashboards

**Example:**
```json
{
  "crew_id": "T-42",
  "consent_tier": 1,
  "data_retention": "90_days",
  "visible_to_managers": false,
  "visible_to_hr": true,
  "pairwise_coherence": false
}
```

---

### Tier 2: Project Optimization (Opt-In)

**What Crew Consents To:**
- All Tier 1 permissions, PLUS:
- Individual coherence scores visible to **project leads only**
- Pairwise coherence calculation for active project teams
- Data retained for **1 year** or project completion (whichever comes first)
- Used for proactive coordination support

**What Crew Can See:**
- Own coherence scores with current team members
- Suggested anchor protocol alignments
- Historical project coherence data

**What Managers See:**
- Individual coherence scores for their direct reports
- Low-coherence pair identification (for mediation)
- Anchor protocol recommendations
- **No access to vectors of crew outside their reporting chain**

**Use Cases:**
- Proactive conflict mediation
- Team formation for high-stakes projects
- Coordination support for low-coherence pairs
- Anchor protocol optimization

**Example:**
```json
{
  "crew_id": "T-42",
  "consent_tier": 2,
  "data_retention": "1_year_or_project_end",
  "visible_to_managers": true,
  "scope": ["project_alpha", "project_beta"],
  "pairwise_coherence": true,
  "mediation_eligible": true
}
```

---

### Tier 3: Full Research Participation (Opt-In)

**What Crew Consents To:**
- All Tier 2 permissions, PLUS:
- Long-term VSA vector evolution tracking (5+ years)
- De-identified data used in external research
- Participation in coherence algorithm validation studies
- Data may inform future HR technology development

**What Crew Can See:**
- Complete VSA vector history with timestamps
- Coherence evolution charts over career
- Research study results (anonymized)
- Contributions to algorithm improvements

**What Researchers See:**
- De-identified VSA vectors and coherence scores
- Longitudinal behavioral pattern data
- Algorithm performance metrics
- **No names, employee IDs, or identifying information**

**Use Cases:**
- Longitudinal behavioral research
- Algorithm validation and improvement
- External academic partnerships
- Future HR technology development

**Example:**
```json
{
  "crew_id": "T-42",
  "consent_tier": 3,
  "data_retention": "5_years_active_plus_2_archive",
  "research_participation": true,
  "deidentified_external_use": true,
  "longitudinal_tracking": true,
  "algorithm_improvement": true
}
```

---

## Consent Transitions

### Upgrading Consent Tiers

**Tier 1 → Tier 2:**
- Crew initiates via HR portal or direct HR request
- HR provides detailed explanation of new permissions
- 48-hour cooling-off period (optional, crew can waive)
- Historical Tier 1 data **not retroactively applied** to Tier 2 use cases
- New data collection starts at transition timestamp

**Tier 2 → Tier 3:**
- Requires HR Director approval (to ensure informed consent)
- Detailed research protocol explanation provided
- Mandatory 7-day consideration period
- Crew acknowledges long-term data retention implications
- Opt-out path clearly documented

---

### Downgrading Consent Tiers

**Tier 3 → Tier 2 or Tier 1:**
- Immediate processing (no approval required)
- Research data de-identified and decoupled from crew ID
- Future data collection follows new tier rules
- Historical data **not deleted** (anonymization prevents re-identification)

**Tier 2 → Tier 1:**
- Immediate processing
- Individual coherence scores **deleted within 48 hours**
- Pairwise coherence calculations disabled
- Managers lose access to individual crew data
- Aggregate contributions remain (cannot be extracted)

**Complete Opt-Out (All Tiers → Tier 0):**
- 48-hour processing timeline
- All coherence data deleted (VSA vectors, scores, history)
- Aggregate contributions removed where technically feasible
- "COHERENCE_OPT_OUT" flag set permanently
- **Cannot opt back in for 6 months** (prevents consent fatigue abuse)

---

## Data Retention and Deletion

### Tier 1: 90-Day Rolling Window

**Retention Policy:**
- VSA vectors deleted after 90 days
- Aggregate statistics retained indefinitely (cannot be re-identified)
- No individual historical tracking

**Deletion Mechanism:**
```python
# Automated cleanup job runs daily
def cleanup_tier1_data():
    cutoff_date = datetime.now() - timedelta(days=90)
    db.execute("""
        DELETE FROM vsa_vectors 
        WHERE consent_tier = 1 
        AND last_updated < ?
    """, [cutoff_date])
```

---

### Tier 2: 1-Year or Project Completion

**Retention Policy:**
- Data retained for active projects + 1 year
- Upon project closure, data enters 30-day grace period (allows final analysis)
- After grace period, individual data deleted, aggregates retained
- If crew leaves project mid-cycle, their data deleted 30 days post-departure

**Deletion Trigger:**
```python
def check_tier2_retention(project_id, crew_id):
    project_status = get_project_status(project_id)
    crew_participation = get_participation_end_date(project_id, crew_id)
    
    if project_status == "completed":
        grace_end = project.completion_date + timedelta(days=30)
        if datetime.now() > grace_end:
            delete_individual_data(crew_id, project_id)
    
    elif crew_participation:
        grace_end = crew_participation + timedelta(days=30)
        if datetime.now() > grace_end:
            delete_individual_data(crew_id, project_id)
```

---

### Tier 3: 5 Years Active + 2 Years Archive

**Retention Policy:**
- Active employment: Data retained up to 5 years rolling
- Upon departure: Data enters 2-year archive (de-identified)
- After 7 years total, converted to research-only dataset (irreversibly anonymized)
- Crew can request deletion during active or archive phase

**Long-Term Storage:**
```python
def archive_tier3_data(crew_id):
    # Move to archive with de-identification
    archive_id = generate_pseudonym()  # One-way hash
    
    db.execute("""
        INSERT INTO research_archive (
            pseudonym, vsa_vector_history, coherence_data
        ) SELECT ?, vsa_vectors, coherence_scores
        FROM crew_data WHERE crew_id = ?
    """, [archive_id, crew_id])
    
    # Delete original identifiable data
    db.execute("DELETE FROM crew_data WHERE crew_id = ?", [crew_id])
```

---

## Consent Workflow Implementation

### Initial Consent Collection

**Onboarding Process:**

1. **Education Phase (Week 1)**
   - New hire orientation includes coherence system overview
   - Ethics framework introduction
   - Video: "How Coherence Metrics Work"
   - Q&A session with HR representative

2. **Decision Phase (Week 2)**
   - Crew receives consent tier comparison document
   - Interactive demo of what data looks like at each tier
   - Optional 1-on-1 with HR Director
   - 7-day minimum consideration period

3. **Consent Capture (Week 3+)**
   - Digital consent form with explicit checkboxes per tier
   - Mandatory acknowledgment of prohibited uses
   - Confirmation of withdrawal rights
   - Signed consent stored in secure HR system

**Consent Form Example:**
```
[ ] I consent to Tier 1 (Basic Coordination)
    I understand my VSA vector will be used for anonymous team health monitoring only.
    
[ ] I consent to Tier 2 (Project Optimization) - Requires Tier 1
    I understand project leads can see my individual coherence scores for coordination support.
    
[ ] I consent to Tier 3 (Full Research Participation) - Requires Tier 1 & 2
    I understand my data may be used in long-term research and algorithm development (de-identified).
    
I acknowledge:
- [ ] I can withdraw consent at any time
- [ ] Consent choices do not affect my job security or career advancement
- [ ] Coherence data will never be used in performance reviews, hiring, or layoffs
- [ ] I have reviewed the Ethics Framework: Connection as Universal Constant

Signature: _______________  Date: _______________
```

---

### Ongoing Consent Management

**Annual Review:**
- Every crew member receives consent status summary
- Option to adjust tier level or opt out entirely
- Reminder of current data holdings and use cases
- Links to updated ethics documentation

**Trigger-Based Reviews:**
- Role change (promotion, transfer, new project)
- Organizational policy updates
- Major algorithm changes
- Crew request for review

---

## Technical Infrastructure

### Database Schema

```sql
CREATE TABLE consent_records (
    crew_id VARCHAR(10) PRIMARY KEY,
    consent_tier INT CHECK (consent_tier IN (0, 1, 2, 3)),
    consent_date TIMESTAMP NOT NULL,
    last_review_date TIMESTAMP,
    next_review_date TIMESTAMP,
    withdrawal_effective_date TIMESTAMP NULL,
    withdrawal_reason TEXT NULL,
    cooling_off_end_date TIMESTAMP NULL,
    signature_hash VARCHAR(64) NOT NULL,
    version VARCHAR(10) NOT NULL  -- Ethics framework version
);

CREATE TABLE consent_audit_log (
    log_id SERIAL PRIMARY KEY,
    crew_id VARCHAR(10),
    action VARCHAR(50),  -- 'tier_upgrade', 'tier_downgrade', 'opt_out', 'annual_review'
    old_tier INT,
    new_tier INT,
    timestamp TIMESTAMP DEFAULT NOW(),
    initiated_by VARCHAR(50),  -- 'crew', 'hr', 'system'
    notes TEXT
);

CREATE TABLE data_retention_schedule (
    crew_id VARCHAR(10),
    data_type VARCHAR(50),  -- 'vsa_vector', 'coherence_score', 'aggregate'
    retention_until TIMESTAMP,
    deletion_status VARCHAR(20) DEFAULT 'pending',
    deletion_completed TIMESTAMP NULL
);
```

---

### API Endpoints (v3.1)

**Consent Management:**

```
POST /consent/enroll
    Body: { crew_id, tier, signature_hash, version }
    Returns: { consent_id, effective_date, next_review_date }

GET /consent/status/{crew_id}
    Returns: { current_tier, effective_date, data_holdings_summary, next_review_date }

PUT /consent/update
    Body: { crew_id, new_tier, reason }
    Returns: { transition_status, effective_date, data_actions }

DELETE /consent/withdraw/{crew_id}
    Returns: { withdrawal_confirmed, data_deletion_timeline, cooling_off_end }
```

**Data Subject Rights:**

```
GET /data/export/{crew_id}
    Returns: Complete data package (GDPR-compliant JSON export)
    Includes: VSA vectors, coherence scores, consent history, audit log

GET /data/retention/{crew_id}
    Returns: Scheduled deletion dates for all data types

POST /data/delete-request
    Body: { crew_id, reason_optional }
    Returns: { request_id, processing_timeline, confirmation_email }
```

---

## Prohibited Actions

### What the System CANNOT Do (by Design)

1. **Default to Tier 2 or 3**
   - All new crew members start at Tier 1 (or Tier 0 if no consent provided)
   - Requires explicit opt-in for higher tiers

2. **Silent Tier Upgrades**
   - System cannot automatically upgrade consent tiers
   - Policy changes require re-consent collection

3. **Coercive Consent**
   - Managers cannot see crew consent tier choices
   - HR cannot correlate career advancement with tier participation

4. **Retroactive Data Use**
   - Tier 1 data collected before Tier 2 upgrade cannot be used for Tier 2 purposes
   - Historical data use locked to consent tier active at collection time

5. **Delayed Opt-Out Processing**
   - Maximum 48-hour processing for Tier 2→1 or complete opt-out
   - No "waiting periods" except cooling-off protections

---

## Edge Cases and Solutions

### Case 1: Crew Member Leaves During Project

**Scenario:** Tier 2 crew member leaves organization mid-project.

**Solution:**
- Immediate data anonymization (within 48 hours)
- Project coherence calculations continue with "departed member" placeholder
- Historical coherence data retained at aggregate level only
- Individual VSA vector deleted per retention policy

---

### Case 2: Consent Tier Mismatch in Team

**Scenario:** Project team has mix of Tier 1 and Tier 2 members.

**Solution:**
- Team-level coherence calculated using Tier 1 permissions only
- Tier 2 members can opt to share pairwise coherence within Tier 2 subgroup
- Managers see aggregated team score, not Tier 1 member individual data
- System flags "partial visibility" to prevent misinterpretation

---

### Case 3: Research Algorithm Change

**Scenario:** v4.0 introduces new coherence algorithm. Does this require re-consent?

**Decision Tree:**
```
Algorithm change affects:
- Data collection method? → YES: Re-consent required
- Calculation method only? → NO: Re-consent not required (disclose in annual review)
- Data use cases? → YES: Re-consent required
- Accuracy/precision? → NO: Disclose in annual review, crew can opt-out if concerned
```

---

### Case 4: Legal Data Preservation

**Scenario:** Crew member under investigation opts out. Can HR retain data for legal hold?

**Solution:**
- **Yes, for legal hold only** (documented, time-limited)
- Data frozen but not used for operational purposes
- Crew notified of legal hold and retention reason
- Data deleted immediately upon legal hold release
- External legal counsel approval required

---

## Compliance and Auditing

### Regular Audits

**Quarterly:**
- Data retention schedule adherence
- Consent tier accuracy in database
- Deletion job execution logs

**Annual:**
- Full consent record review (random sample)
- Crew feedback survey on consent process
- External audit of de-identification effectiveness (Tier 3)

### Compliance Metrics

**Key Performance Indicators:**
```
- Consent collection rate: Target 100% within 30 days of hire
- Opt-out rate: Baseline < 5% (higher rates trigger investigation)
- Data deletion SLA: 48-hour target, 100% within 7 days
- Consent tier distribution: Monitor for coercion patterns
- Annual review completion: Target 95%
```

---

## Training Requirements

### HR Staff (Mandatory)

- Ethics framework deep dive (4 hours)
- Consent collection procedures (2 hours)
- Data subject rights handling (2 hours)
- Edge case decision-making (2 hours)

### Managers (Mandatory)

- Coherence interpretation ethics (2 hours)
- Consent tier awareness (no access to crew choices) (1 hour)
- Prohibited uses refresher (1 hour)

### All Crew (Mandatory)

- Consent system overview (30 minutes, onboarding)
- Annual refresher (15 minutes)

---

## Implementation Roadmap (v3.1)

### Phase 1: Database Schema (Months 1-2)
- Create consent_records table
- Create audit_log table
- Create retention_schedule table
- Migration scripts for existing data

### Phase 2: API Development (Months 2-4)
- Consent management endpoints
- Data export endpoints
- Deletion request handlers
- Audit logging middleware

### Phase 3: UI/UX (Months 4-6)
- Crew consent portal
- Manager visibility restrictions
- HR admin dashboard
- Consent workflow automation

### Phase 4: Training & Rollout (Months 6-8)
- Staff training materials
- Crew education campaign
- Consent collection from existing crew
- Monitoring and adjustment

### Phase 5: Audit & Iteration (Months 9-12)
- First quarterly audit
- Crew feedback collection
- Policy adjustments
- External compliance review

---

## Success Criteria

**Technical:**
- ✅ 100% consent records captured within 30 days of hire
- ✅ 48-hour data deletion SLA met 99%+ of time
- ✅ Zero unauthorized data access incidents
- ✅ De-identification effectiveness verified by external audit

**Organizational:**
- ✅ < 10% opt-out rate (indicates trust in system)
- ✅ 95%+ crew report understanding consent choices (survey)
- ✅ Zero consent-related ethics violations
- ✅ Manager feedback: "Consent system does not impede coordination"

**Cultural:**
- ✅ Crew perceive consent system as empowering, not bureaucratic
- ✅ Ethics framework cited positively in external reviews
- ✅ Consent architecture becomes model for other organizational data systems

---

## Frequently Asked Questions

### For Crew Members

**Q: What happens if I choose Tier 1?**
A: Your data is only used for anonymous team health dashboards. Managers never see your individual coherence scores. This is the default and most private option.

**Q: Can I be denied a project assignment for choosing Tier 1?**
A: Absolutely not. Consent tier cannot influence project assignments, promotions, or any career decisions. This is a strict ethics violation.

**Q: How do I know my data is actually deleted?**
A: You can request deletion confirmation logs via the HR portal. We provide timestamped proof of deletion within 7 days.

---

### For Managers

**Q: Can I see which of my team members chose Tier 2 vs. Tier 1?**
A: No. Consent tier choices are confidential. You only see data crew members explicitly consented to share.

**Q: What if I need coherence data for team planning but crew members are mostly Tier 1?**
A: You can encourage Tier 2 participation by explaining benefits, but you cannot require it or penalize Tier 1 choices. Use aggregate team coherence for planning.

---

### For HR Staff

**Q: Can we fast-track consent collection during onboarding?**
A: No. Minimum 7-day consideration period for Tier 3, recommended 48 hours for Tier 2. Rushing consent violates informed consent principles.

**Q: What if external auditors request crew data?**
A: Legal holds are permitted, but require external legal counsel approval and crew notification. Data cannot be used for operational purposes during legal hold.

---

## References

- **Ethics Framework:** [Connection as Universal Constant](ETHICS_FRAMEWORK_CONNECTION_AS_CONSTANT.md)
- **GDPR Compliance:** Regulation (EU) 2016/679 (Articles 6, 7, 17)
- **CCPA Compliance:** California Civil Code §1798.100-1798.199
- **Research Ethics:** Belmont Report (1979) - Respect for Persons, Beneficence, Justice

---

## Revision History

- **v1.0.0** (2025-11-12): Initial design specification
  - Three-tier consent system defined
  - Data retention policies established
  - Implementation roadmap created
  - Edge cases documented

---

**Next Review:** Q4 2025 (Pre-implementation validation)  
**Owner:** Helena Vu, HR Director  
**Technical Lead:** Aurora Symbolic Systems Team
