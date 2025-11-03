/**
 * Aurora CloudBank GitHub Actions Bot Helper
 * 
 * Centralized helper for all automated bot workflows
 * Handles comment management, deduplication, and spam prevention
 * 
 * Version: 1.0.0
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class AuroraBot {
  constructor(github, context, config = null) {
    this.github = github;
    this.context = context;
    this.config = config || this.loadConfig();
    this.workflowName = process.env.GITHUB_WORKFLOW || 'unknown';
  }

  /**
   * Load bot configuration from .github/bot-config.yml
   */
  loadConfig() {
    try {
      const configPath = path.join(__dirname, '../bot-config.yml');
      const configContent = fs.readFileSync(configPath, 'utf8');
      return yaml.load(configContent);
    } catch (error) {
      console.warn('Failed to load bot config, using defaults:', error.message);
      return this.getDefaultConfig();
    }
  }

  /**
   * Get default configuration if config file is missing
   */
  getDefaultConfig() {
    return {
      global: {
        deduplication: true,
        comment_throttle: 60,
        max_comments_per_pr: 5
      },
      spam_prevention: {
        enabled: true,
        rate_limiting: { enabled: true, max_per_workflow: 2 }
      }
    };
  }

  /**
   * Check if we should post a comment based on spam prevention rules
   */
  async shouldPostComment(prNumber, commentIdentifier) {
    if (!this.config.spam_prevention?.enabled) {
      return true;
    }

    // Check rate limiting
    const rateLimitOk = await this.checkRateLimit(prNumber);
    if (!rateLimitOk) {
      console.log('⚠️ Rate limit exceeded, skipping comment');
      return false;
    }

    // Check for duplicate content
    if (this.config.spam_prevention.detect_duplicates?.enabled) {
      const isDuplicate = await this.isDuplicateComment(prNumber, commentIdentifier);
      if (isDuplicate) {
        console.log('⚠️ Duplicate comment detected, skipping');
        return false;
      }
    }

    return true;
  }

  /**
   * Check if rate limit allows posting
   */
  async checkRateLimit(prNumber) {
    const rateLimitConfig = this.config.spam_prevention?.rate_limiting;
    if (!rateLimitConfig?.enabled) {
      return true;
    }

    // Get existing comments
    const comments = await this.getBotComments(prNumber);
    
    // Count comments from this workflow
    const workflowComments = comments.filter(c => 
      c.body.includes(this.workflowName) ||
      c.body.includes(this.getBotSignature())
    );

    const maxPerWorkflow = rateLimitConfig.max_per_workflow || 2;
    if (workflowComments.length >= maxPerWorkflow) {
      console.log(`Rate limit: ${workflowComments.length}/${maxPerWorkflow} comments from this workflow`);
      return false;
    }

    // Check total bot comments
    const maxTotal = this.config.global?.max_comments_per_pr || 10;
    if (comments.length >= maxTotal) {
      console.log(`Total bot comment limit reached: ${comments.length}/${maxTotal}`);
      return false;
    }

    // Check cooldown period
    if (workflowComments.length > 0) {
      const cooldown = rateLimitConfig.cooldown || 30; // minutes
      const lastComment = workflowComments[workflowComments.length - 1];
      const lastCommentTime = new Date(lastComment.created_at);
      const now = new Date();
      const minutesSince = (now - lastCommentTime) / 1000 / 60;

      if (minutesSince < cooldown) {
        console.log(`Cooldown active: ${minutesSince.toFixed(1)}/${cooldown} minutes`);
        return false;
      }
    }

    return true;
  }

  /**
   * Check if this comment is a duplicate
   */
  async isDuplicateComment(prNumber, commentIdentifier) {
    const comments = await this.getBotComments(prNumber);
    
    const timeWindow = this.config.spam_prevention?.detect_duplicates?.time_window || 24; // hours
    const now = new Date();
    
    // Look for comments with same identifier within time window
    const recentSimilar = comments.filter(c => {
      const commentAge = (now - new Date(c.created_at)) / 1000 / 60 / 60; // hours
      return commentAge < timeWindow && c.body.includes(commentIdentifier);
    });

    return recentSimilar.length > 0;
  }

  /**
   * Get all bot comments on a PR
   */
  async getBotComments(prNumber) {
    try {
      const { data: comments } = await this.github.rest.issues.listComments({
        owner: this.context.repo.owner,
        repo: this.context.repo.repo,
        issue_number: prNumber
      });

      const botSignature = this.getBotSignature();
      return comments.filter(c => 
        c.body.includes(botSignature) ||
        c.body.includes('Aurora CloudBank Automation') ||
        c.body.includes('🤖')
      );
    } catch (error) {
      console.error('Failed to fetch comments:', error.message);
      return [];
    }
  }

  /**
   * Post or update a comment
   */
  async postComment(prNumber, commentBody, options = {}) {
    const {
      identifier = null,
      updateExisting = this.config.spam_prevention?.consolidation?.update_existing ?? true,
      onlyOnIssues = false
    } = options;

    // Check if we should skip this comment
    if (onlyOnIssues && !this.hasIssues(commentBody)) {
      console.log('No issues found, skipping comment');
      return null;
    }

    // Check spam prevention
    const shouldPost = await this.shouldPostComment(prNumber, identifier);
    if (!shouldPost) {
      return null;
    }

    // Add bot signature
    const fullComment = this.addSignature(commentBody, identifier);

    // Try to update existing comment if enabled
    if (updateExisting && identifier) {
      const updated = await this.updateExistingComment(prNumber, identifier, fullComment);
      if (updated) {
        console.log('✅ Updated existing comment');
        return updated;
      }
    }

    // Post new comment
    try {
      const { data: comment } = await this.github.rest.issues.createComment({
        owner: this.context.repo.owner,
        repo: this.context.repo.repo,
        issue_number: prNumber,
        body: fullComment
      });

      console.log('✅ Posted new comment');
      
      // Cleanup old comments if enabled
      if (this.config.spam_prevention?.consolidation?.cleanup_old) {
        await this.cleanupOldComments(prNumber, identifier);
      }

      return comment;
    } catch (error) {
      console.error('Failed to post comment:', error.message);
      return null;
    }
  }

  /**
   * Update an existing comment if found
   */
  async updateExistingComment(prNumber, identifier, newBody) {
    const comments = await this.getBotComments(prNumber);
    const existing = comments.find(c => c.body.includes(identifier));

    if (!existing) {
      return null;
    }

    try {
      const { data: updated } = await this.github.rest.issues.updateComment({
        owner: this.context.repo.owner,
        repo: this.context.repo.repo,
        comment_id: existing.id,
        body: newBody
      });
      return updated;
    } catch (error) {
      console.error('Failed to update comment:', error.message);
      return null;
    }
  }

  /**
   * Cleanup old bot comments
   */
  async cleanupOldComments(prNumber, currentIdentifier) {
    const maxRetained = this.config.spam_prevention?.consolidation?.max_retained || 3;
    const comments = await this.getBotComments(prNumber);

    // Sort by creation date, newest first
    const sortedComments = comments.sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    );

    // Keep the most recent N comments
    const toDelete = sortedComments.slice(maxRetained);

    for (const comment of toDelete) {
      try {
        await this.github.rest.issues.deleteComment({
          owner: this.context.repo.owner,
          repo: this.context.repo.repo,
          comment_id: comment.id
        });
        console.log(`🗑️ Deleted old comment: ${comment.id}`);
      } catch (error) {
        console.warn(`Failed to delete comment ${comment.id}:`, error.message);
      }
    }
  }

  /**
   * Add bot signature to comment
   */
  addSignature(commentBody, identifier = null) {
    const signature = this.getBotSignature();
    const workflowInfo = `<!-- workflow: ${this.workflowName} -->`;
    const identifierTag = identifier ? `<!-- identifier: ${identifier} -->` : '';
    
    return `${commentBody}\n\n---\n\n${signature}\n${workflowInfo}\n${identifierTag}`;
  }

  /**
   * Get bot signature
   */
  getBotSignature() {
    return this.config.global?.bot_signature || '🤖 *Aurora CloudBank Automation*';
  }

  /**
   * Check if comment body contains issues/findings
   */
  hasIssues(commentBody) {
    const issueIndicators = [
      '❌', '⚠️', '🔴',
      'FAILED', 'NEEDS WORK', 'violation', 'error', 'critical', 'high priority'
    ];
    return issueIndicators.some(indicator => commentBody.includes(indicator));
  }

  /**
   * Format comment based on template
   */
  formatComment(data, template = 'standard') {
    const templateConfig = this.config.templates?.[template] || this.config.templates?.standard;
    const sections = templateConfig?.sections || ['status', 'summary', 'recommendations'];
    const maxLength = templateConfig?.max_length || 1500;

    let comment = '';

    // Build comment from sections
    if (sections.includes('status') && data.status) {
      comment += `## ${data.statusEmoji || '📊'} ${data.title}\n\n`;
      comment += `**Status:** ${data.status}\n\n`;
    }

    if (sections.includes('summary') && data.summary) {
      comment += `### Summary\n${data.summary}\n\n`;
    }

    if (sections.includes('critical_issues') && data.criticalIssues?.length > 0) {
      comment += `### 🚨 Critical Issues\n`;
      data.criticalIssues.forEach(issue => {
        comment += `- ${issue}\n`;
      });
      comment += '\n';
    }

    if (sections.includes('key_findings') && data.findings?.length > 0) {
      comment += `### Key Findings\n`;
      const topFindings = data.findings.slice(0, 5);
      topFindings.forEach(finding => {
        comment += `- ${finding}\n`;
      });
      if (data.findings.length > 5) {
        comment += `\n<details>\n<summary>Show ${data.findings.length - 5} more findings</summary>\n\n`;
        data.findings.slice(5).forEach(finding => {
          comment += `- ${finding}\n`;
        });
        comment += `</details>\n`;
      }
      comment += '\n';
    }

    if (sections.includes('recommendations') && data.recommendations?.length > 0) {
      comment += `### 💡 Recommendations\n`;
      data.recommendations.forEach(rec => {
        comment += `- ${rec}\n`;
      });
      comment += '\n';
    }

    if (sections.includes('action_items') && data.actionItems?.length > 0) {
      comment += `### 🎯 Action Items\n`;
      data.actionItems.forEach((item, index) => {
        comment += `${index + 1}. ${item}\n`;
      });
      comment += '\n';
    }

    if (sections.includes('next_steps') && data.nextSteps) {
      comment += `### Next Steps\n${data.nextSteps}\n\n`;
    }

    // Truncate if too long
    if (comment.length > maxLength) {
      comment = comment.substring(0, maxLength - 100) + '\n\n*[Truncated for length]*\n';
    }

    return comment;
  }

  /**
   * Manage labels with cleanup
   */
  async manageLabels(prNumber, newLabels, prefix = null, cleanupOld = true) {
    const labelConfig = this.config.labeling;
    if (!labelConfig?.enabled) {
      return;
    }

    // Cleanup old labels with same prefix
    if (cleanupOld && prefix) {
      try {
        const { data: issue } = await this.github.rest.issues.get({
          owner: this.context.repo.owner,
          repo: this.context.repo.repo,
          issue_number: prNumber
        });

        const oldLabels = issue.labels
          .map(l => l.name)
          .filter(name => name.startsWith(`${prefix}:`));

        for (const label of oldLabels) {
          await this.github.rest.issues.removeLabel({
            owner: this.context.repo.owner,
            repo: this.context.repo.repo,
            issue_number: prNumber,
            name: label
          }).catch(() => {}); // Ignore errors
        }
      } catch (error) {
        console.warn('Failed to cleanup old labels:', error.message);
      }
    }

    // Add new labels
    if (newLabels.length > 0) {
      try {
        await this.github.rest.issues.addLabels({
          owner: this.context.repo.owner,
          repo: this.context.repo.repo,
          issue_number: prNumber,
          labels: newLabels
        });
        console.log(`✅ Added labels: ${newLabels.join(', ')}`);
      } catch (error) {
        console.warn('Failed to add labels:', error.message);
      }
    }
  }
}

module.exports = AuroraBot;
