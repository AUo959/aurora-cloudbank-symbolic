# Aurora CloudBank GitHub Actions Bot Refinement Guide

## Overview

This guide documents the comprehensive refinement of Aurora CloudBank's GitHub Actions bot ecosystem. The bots now operate with **intelligence, restraint, and actionable focus** rather than verbose spam.

## Core Philosophy

> **"Speak when you have something valuable to say, not just because you can."**

Our bots follow these principles:

1. **Actionable over Verbose**: Every comment must contain specific, actionable guidance
2. **Signal over Noise**: Comment only on issues, failures, or important state changes
3. **Update over Duplicate**: Update existing comments instead of creating new ones
4. **Consolidated over Scattered**: Combine related information in single comments
5. **Silent Labels**: Update labels without notification spam

## Architecture

### Centralized Configuration

**File**: `.github/bot-config.yml`

All bot behavior is controlled through a single configuration file, making it easy to:
- Enable/disable specific features
- Adjust spam prevention thresholds
- Customize comment templates
- Configure rate limiting

### Smart Bot Helper

**File**: `.github/scripts/bot-helper.js`

The `AuroraBot` class provides centralized intelligence for all workflows:

```javascript
const bot = new AuroraBot(github, context);

// Smart comment posting with spam prevention
await bot.postComment(prNumber, commentBody, {
  identifier: 'unique-id',
  updateExisting: true,
  onlyOnIssues: true
});

// Intelligent label management
await bot.manageLabels(prNumber, ['eval: excellent'], 'eval', true);

// Template-based comment formatting
const comment = bot.formatComment(data, 'actionable');
```

## Bot Behaviors

### 1. PR Evaluation (`pr_evaluation.yml`)

**When it runs**: PR opened, new commits pushed

**Smart behavior**:
- ✅ **High scores (≥0.9)**: Minimal success message only
- ⚠️ **Low scores (<0.7)**: Actionable comment with critical issues
- 🔄 **Updates existing comment** instead of creating duplicates
- 🎯 **Shows only critical issues** and top recommendations
- 📦 **Collapses detailed results** in expandable sections

**Example comments**:

**Good PR (≥0.9 score)**:
```
✅ PR Evaluation: PASSED (Score: 0.92/1.00)

🤖 Aurora CloudBank Automation
```

**PR needing work (<0.7 score)**:
```
## ⚠️ PR Evaluation

**Status:** ⚠️ NEEDS WORK (0.65/1.00)

### 🚨 Critical Issues
- **Code Quality**: Flake8 violations in 3 files
- **Test Coverage**: Coverage dropped by 5%

### 💡 Recommendations
- Fix E501 line length violations
- Add tests for new functions
- Update documentation

### Next Steps
Address the critical issues above before merging.

---
🤖 Aurora CloudBank Automation
<!-- workflow: PR Evaluation -->
<!-- identifier: pr-evaluation -->
```

### 2. Selective Integration Analysis (`pr-selective-integration.yml`)

**When it runs**: PR opened (once only, not on every commit)

**Smart behavior**:
- ✅ **Direct merge strategy**: No comment (already covered by evaluation)
- 🔄 **Alternative strategies**: Actionable comment explaining what happens next
- 📋 **Conditional labels**: Only added if score < 0.9 or non-standard strategy
- 🎯 **Focus on integration plan** not philosophy lectures

**Only comments when**:
- Strategy is NOT "direct_merge"
- OR score < 0.9
- OR there are specific integration concerns

### 3. CI Status Automation (`ci-status-project-automation.yml`)

**When it runs**: Check suites complete, PR updated

**Smart behavior**:
- ✅ **CI passes**: Silent label update only (no comment spam)
- ⚠️ **CI fails**: Comment only if ≥3 checks fail OR critical checks fail
- 🔄 **Updates existing comment** instead of creating new ones
- 🎯 **Shows only failed checks** with actionable steps
- 🏷️ **Labels updated silently** without notification noise

**Example comment (only on significant failures)**:
```
## ⚠️ CI Status Update

**Status:** ⚠️ Checks Failed

### 🚨 Critical Issues
- **Security Scan**
- **Unit Tests**
- **Integration Tests**

### 🎯 Action Items
1. Check the Details link for each failed check
2. Fix the issues locally and test
3. Push your fixes to trigger a new CI run

### Next Steps
Review failed checks and push fixes. CI will re-run automatically.

---
🤖 Aurora CloudBank Automation
<!-- workflow: CI Status Project Automation -->
<!-- identifier: ci-status -->
```

### 4. Code Quality Analysis (`code-quality.yml`)

**When it runs**: Push to main/develop, PRs

**Smart behavior**:
- ✅ **No violations**: No comment, silent pass
- ⚠️ **Has violations**: Comment only if severity ≥ high
- 🎯 **Show only critical/high** violations
- 📊 **Severity breakdown** for quick assessment
- 🔄 **Update existing comment**

**Only comments when**:
- Critical violations exist
- OR High-severity violations exist
- OR total violations > threshold

### 5. Auto-Labeling (`auto-labeler.yml`)

**When it runs**: PRs and issues opened/updated

**Smart behavior**:
- 🏷️ **All label operations are SILENT**
- 📁 Path-based labels added automatically
- 🏷️ Size labels based on changes
- 🎯 Content labels based on PR description
- 🔕 **NO COMMENTS OR NOTIFICATIONS**

### 6. Assignment Automation (`auto-assign-and-review.yml`)

**When it runs**: PRs and issues opened

**Smart behavior**:
- 👤 **Auto-assign silently** (no comment)
- 👥 **Add reviewers silently** (no notification)
- 🔕 **NO COMMENTS** unless assignment fails

## Spam Prevention System

### Rate Limiting

- **Max 2 comments per workflow per PR**
- **Max 10 total bot comments per PR**
- **30-minute cooldown** between comments from same workflow

### Deduplication

- **90% similarity threshold** for duplicate detection
- **24-hour time window** for checking duplicates
- **Identifier-based tracking** for related comments

### Comment Consolidation

- **Update existing comments** instead of creating new ones
- **Delete old comments** beyond retention limit (keep 3 most recent)
- **Combine pending comments** from same workflow

### Content Aggregation

- **60-second debounce** before posting (allows batching)
- **Combine multiple pending updates** into single comment
- **Group related findings** by file or category

## Comment Templates

### Minimal Template (≤500 chars)
- Status indicator
- Critical issues only
- Next steps

### Standard Template (≤1500 chars)
- Status with details
- Summary
- Key findings (top 5)
- Recommendations

### Actionable Template (≤1000 chars)
- Status
- Action items (numbered list)
- Blocking issues
- Fix suggestions

### Detailed Template (≤5000 chars)
- Comprehensive status
- Full summary
- All findings (with collapsible sections)
- All recommendations
- Resource links

## Configuration Examples

### Enable Only Critical Notifications

```yaml
# .github/bot-config.yml
pr_evaluation:
  comments:
    only_on_issues: true
    score_threshold: 0.7  # Only comment if score < 0.7
    template: minimal

ci_status_automation:
  comments:
    only_on_state_change: true
    failure_threshold: 3  # Need 3+ failures to comment

code_review:
  comments:
    only_on_violations: true
    min_severity: "high"  # Only high/critical violations
```

### Disable Specific Bot Features

```yaml
# .github/bot-config.yml
selective_integration:
  enabled: false  # Disable selective integration analysis

labeling:
  silent: true  # All labeling is silent (no notifications)
```

### Adjust Rate Limits

```yaml
# .github/bot-config.yml
spam_prevention:
  rate_limiting:
    max_per_workflow: 1  # More restrictive
    cooldown: 60  # 1 hour cooldown
```

## Migration from Old System

### Before Refinement

**Problems**:
- ❌ 5-10 bot comments per PR
- ❌ Duplicate information across comments
- ❌ Verbose philosophy lectures on every PR
- ❌ Comments on successful checks
- ❌ Label changes trigger notifications
- ❌ No deduplication or rate limiting

**Example spam** (old system):
```
Comment 1: "CI Status: Pending..."
Comment 2: "PR Evaluation: Running..."
Comment 3: "Selective Integration: Analyzing..."
Comment 4: "CI Status: One check failed..."
Comment 5: "CI Status: Another check failed..."
Comment 6: "PR Evaluation: Results ready..."
Comment 7: "Selective Integration: Philosophy explanation..."
Comment 8: "Code Quality: Minor issues..."
Comment 9: "Labels updated: ci:pending..."
Comment 10: "Labels updated: eval:good..."
```

### After Refinement

**Benefits**:
- ✅ 0-2 bot comments per PR (only when needed)
- ✅ Actionable, specific guidance
- ✅ Silent label updates
- ✅ Update existing comments
- ✅ Intelligent spam prevention

**Example refined** (new system):
```
Comment 1: "⚠️ CI Status Update
3 checks failed: Security Scan, Unit Tests, Linting
Action items:
1. Fix security issues in secure_helpers.py
2. Add tests for new functions
3. Run flake8 locally before pushing"

[That's it - one actionable comment]
[Labels updated silently]
[Subsequent updates edit the same comment]
```

## Best Practices for Bot Comments

### ✅ DO

- **Be specific**: "Fix E501 in line 42" not "Fix linting issues"
- **Be actionable**: "Add test for calculateTotal()" not "Improve test coverage"
- **Show severity**: Use 🚨 for critical, ⚠️ for warnings, ℹ️ for info
- **Link to fixes**: Provide URLs to failed check details
- **Update existing**: Edit previous comment instead of new one
- **Use collapsible sections**: `<details>` for additional info

### ❌ DON'T

- **Lecture about philosophy** unless strategy is non-standard
- **Comment on success** (use silent labels instead)
- **Repeat information** already in other comments
- **Show all findings** (prioritize critical/high only)
- **Create duplicate comments** on same issue
- **Notify for label changes** (always silent)

## Monitoring and Tuning

### Check Bot Activity

```bash
# Count bot comments on recent PRs
gh pr list --state all --limit 50 --json number,comments \
  | jq '.[] | select(.comments > 5) | {pr: .number, comments: .comments}'

# Find PRs with excessive bot comments
gh pr list --state all --limit 50 --json number,body \
  | jq '.[] | select(.body | contains("🤖")) | .number'
```

### Adjust Thresholds

If bots are still too chatty:
1. Increase `score_threshold` (comment on fewer PRs)
2. Increase `failure_threshold` (comment on more failures only)
3. Increase `cooldown` period (slower response)
4. Decrease `max_comments_per_pr` (stricter limit)

If bots are too quiet:
1. Decrease `score_threshold` (comment on more PRs)
2. Set `only_on_issues: false` (comment even on success)
3. Decrease `failure_threshold` (comment on single failures)

## Testing Bot Changes

### Test in Sandbox PR

1. Create test PR with known issues
2. Check bot comments are:
   - Actionable and specific
   - Non-duplicate
   - Properly formatted
   - Under rate limits
3. Push fixes and verify:
   - Existing comments updated (not new ones)
   - Labels updated silently
   - No spam on success

### Validate Configuration

```bash
# Check YAML syntax
yamllint .github/bot-config.yml

# Test bot helper
node .github/scripts/bot-helper.js --test

# Dry-run workflow
gh workflow run pr_evaluation.yml --ref test-branch
```

## Troubleshooting

### Bot Not Commenting

**Check**:
1. `enabled: true` in bot-config.yml
2. Score below `score_threshold`
3. Rate limit not exceeded
4. Identifier not duplicate

**Fix**: Lower thresholds or check rate limiting

### Too Many Comments

**Check**:
1. `update_existing: true` working?
2. `only_on_issues: true` enabled?
3. Rate limits properly configured?

**Fix**: Enable consolidation and stricter limits

### Comments Still Verbose

**Check**:
1. Using correct template (`minimal` or `actionable`)
2. `collapse_detailed_results: true` enabled?
3. `show_critical_issues_only: true` enabled?

**Fix**: Switch to `actionable` template and enable collapsing

## Future Enhancements

### Planned Features

1. **ML-based duplicate detection**: Semantic similarity instead of text matching
2. **User preference learning**: Adapt verbosity based on user feedback
3. **Smart batching**: Group multiple updates into single summary comment
4. **Workflow dependency awareness**: Don't comment if another workflow already covered it
5. **Context-aware commenting**: Check PR conversation before adding comment

### Experimental Features

- **Reaction-based feedback**: Let users 👍/👎 bot comments to tune behavior
- **Personalization**: Different verbosity levels for different users
- **Smart summarization**: AI-generated concise summaries of multiple issues
- **Proactive suggestions**: Suggest fixes before CI runs

## Support

### Questions?

- **Config issues**: Check `.github/bot-config.yml` syntax
- **Bot helper bugs**: Review `.github/scripts/bot-helper.js` logs
- **Workflow problems**: Check GitHub Actions run logs

### Contributing

To improve bot behavior:
1. Update `.github/bot-config.yml` for configuration changes
2. Modify `.github/scripts/bot-helper.js` for logic changes
3. Refactor workflow `.yml` files to use new helper
4. Test thoroughly on sandbox PR
5. Document changes in this guide

---

**Last Updated**: November 3, 2025  
**Version**: 1.0.0  
**Status**: Active and maintained
