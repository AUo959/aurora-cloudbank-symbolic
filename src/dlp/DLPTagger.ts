/**
 * Aurora/GUMAS DLP Tagging System
 * Data Loss Prevention with classification and lifecycle management
 * Operator: AUo959
 */

export type DataClassification = 'public' | 'internal' | 'restricted' | 'confidential';

export interface RetentionPolicy {
  id: string;
  classification: DataClassification;
  retentionDays: number;
  autoArchive: boolean;
  autoDelete: boolean;
  complianceRequirements: string[];
  operatorId: string;
}

export interface AccessControl {
  roleId: string;
  permissions: ('read' | 'write' | 'delete' | 'export')[];
  restrictions: string[];
  validUntil?: Date;
  operatorId: string;
}

export interface DLPTag {
  id: string;
  classification: DataClassification;
  sensitivity: number; // 1-10 scale
  retentionPolicy: RetentionPolicy;
  accessControls: AccessControl[];
  metadata: Record<string, any>;
  createdAt: Date;
  lastModified: Date;
  operatorId: string;
}

export interface ComplianceReport {
  reportId: string;
  period: { start: Date; end: Date };
  summary: {
    totalItems: number;
    byClassification: Record<DataClassification, number>;
    violations: ComplianceViolation[];
    retentionActions: RetentionAction[];
  };
  auroraGumasCompliance: boolean;
  generatedAt: Date;
  operatorId: string;
}

export interface ComplianceViolation {
  id: string;
  type: 'access' | 'retention' | 'export' | 'classification';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  itemId: string;
  detectedAt: Date;
  resolved: boolean;
}

export interface RetentionAction {
  id: string;
  action: 'archive' | 'delete' | 'extend' | 'review';
  itemId: string;
  reason: string;
  executedAt: Date;
  operatorId: string;
}

/**
 * DLP Tagging with automated lifecycle management
 */
export class DLPTagger {
  private readonly operatorId = 'AUo959';
  private tags: Map<string, DLPTag> = new Map();
  private retentionPolicies: Map<string, RetentionPolicy> = new Map();
  private accessControls: Map<string, AccessControl> = new Map();
  private complianceHistory: ComplianceReport[] = [];

  constructor() {
    this.initializeDefaultPolicies();
  }

  /**
   * Create DLP tag for data item
   */
  createTag(
    itemId: string,
    classification: DataClassification,
    sensitivity: number,
    metadata: Record<string, any> = {}
  ): DLPTag {
    const retentionPolicy = this.getRetentionPolicy(classification);
    const accessControls = this.getDefaultAccessControls(classification);

    const tag: DLPTag = {
      id: itemId,
      classification,
      sensitivity: Math.max(1, Math.min(10, sensitivity)),
      retentionPolicy,
      accessControls,
      metadata: {
        ...metadata,
        auroraCompliant: true,
        gumasStandards: '2024.1'
      },
      createdAt: new Date(),
      lastModified: new Date(),
      operatorId: this.operatorId
    };

    this.tags.set(itemId, tag);
    return tag;
  }

  /**
   * Update data classification
   */
  updateClassification(itemId: string, newClassification: DataClassification): boolean {
    const tag = this.tags.get(itemId);
    if (!tag) return false;

    tag.classification = newClassification;
    tag.retentionPolicy = this.getRetentionPolicy(newClassification);
    tag.accessControls = this.getDefaultAccessControls(newClassification);
    tag.lastModified = new Date();

    return true;
  }

  /**
   * Check access permissions for role
   */
  checkAccess(itemId: string, roleId: string, permission: 'read' | 'write' | 'delete' | 'export'): boolean {
    const tag = this.tags.get(itemId);
    if (!tag) return false;

    const applicableControls = tag.accessControls.filter(ac => 
      ac.roleId === roleId || ac.roleId === 'all'
    );

    if (applicableControls.length === 0) return false;

    return applicableControls.some(ac => {
      // Check if access is still valid
      if (ac.validUntil && ac.validUntil < new Date()) return false;
      
      // Check if permission is granted
      return ac.permissions.includes(permission);
    });
  }

  /**
   * Execute retention policy actions
   */
  executeRetentionActions(): RetentionAction[] {
    const actions: RetentionAction[] = [];
    const now = new Date();

    for (const [itemId, tag] of this.tags) {
      const daysSinceCreation = Math.floor(
        (now.getTime() - tag.createdAt.getTime()) / (1000 * 60 * 60 * 24)
      );

      if (daysSinceCreation >= tag.retentionPolicy.retentionDays) {
        let action: RetentionAction;

        if (tag.retentionPolicy.autoDelete) {
          action = {
            id: this.generateActionId(),
            action: 'delete',
            itemId,
            reason: 'Retention period expired - auto-delete enabled',
            executedAt: now,
            operatorId: this.operatorId
          };
          this.tags.delete(itemId);
        } else if (tag.retentionPolicy.autoArchive) {
          action = {
            id: this.generateActionId(),
            action: 'archive',
            itemId,
            reason: 'Retention period expired - auto-archive enabled',
            executedAt: now,
            operatorId: this.operatorId
          };
        } else {
          action = {
            id: this.generateActionId(),
            action: 'review',
            itemId,
            reason: 'Retention period expired - manual review required',
            executedAt: now,
            operatorId: this.operatorId
          };
        }

        actions.push(action);
      }
    }

    return actions;
  }

  /**
   * Generate compliance report
   */
  generateComplianceReport(startDate: Date, endDate: Date): ComplianceReport {
    const violations: ComplianceViolation[] = this.detectViolations();
    const retentionActions = this.executeRetentionActions();

    const byClassification: Record<DataClassification, number> = {
      public: 0,
      internal: 0,
      restricted: 0,
      confidential: 0
    };

    for (const tag of this.tags.values()) {
      byClassification[tag.classification]++;
    }

    const report: ComplianceReport = {
      reportId: this.generateReportId(),
      period: { start: startDate, end: endDate },
      summary: {
        totalItems: this.tags.size,
        byClassification,
        violations,
        retentionActions
      },
      auroraGumasCompliance: violations.filter(v => v.severity === 'critical').length === 0,
      generatedAt: new Date(),
      operatorId: this.operatorId
    };

    this.complianceHistory.push(report);
    return report;
  }

  /**
   * Get tag by item ID
   */
  getTag(itemId: string): DLPTag | undefined {
    return this.tags.get(itemId);
  }

  /**
   * Get all tags by classification
   */
  getTagsByClassification(classification: DataClassification): DLPTag[] {
    return Array.from(this.tags.values()).filter(tag => tag.classification === classification);
  }

  /**
   * Export compliance history
   */
  exportComplianceHistory(): ComplianceReport[] {
    return [...this.complianceHistory];
  }

  private initializeDefaultPolicies(): void {
    // Public data policy
    this.retentionPolicies.set('public', {
      id: 'policy_public',
      classification: 'public',
      retentionDays: 365,
      autoArchive: true,
      autoDelete: false,
      complianceRequirements: ['Aurora/GUMAS-2024.1'],
      operatorId: this.operatorId
    });

    // Internal data policy
    this.retentionPolicies.set('internal', {
      id: 'policy_internal',
      classification: 'internal',
      retentionDays: 1095, // 3 years
      autoArchive: true,
      autoDelete: false,
      complianceRequirements: ['Aurora/GUMAS-2024.1', 'Internal-Security'],
      operatorId: this.operatorId
    });

    // Restricted data policy
    this.retentionPolicies.set('restricted', {
      id: 'policy_restricted',
      classification: 'restricted',
      retentionDays: 2555, // 7 years
      autoArchive: false,
      autoDelete: false,
      complianceRequirements: ['Aurora/GUMAS-2024.1', 'Internal-Security', 'Restricted-Access'],
      operatorId: this.operatorId
    });

    // Confidential data policy
    this.retentionPolicies.set('confidential', {
      id: 'policy_confidential',
      classification: 'confidential',
      retentionDays: 3650, // 10 years
      autoArchive: false,
      autoDelete: false,
      complianceRequirements: ['Aurora/GUMAS-2024.1', 'Internal-Security', 'Restricted-Access', 'Confidential-Handling'],
      operatorId: this.operatorId
    });
  }

  private getRetentionPolicy(classification: DataClassification): RetentionPolicy {
    const policy = this.retentionPolicies.get(classification);
    if (!policy) {
      throw new Error(`No retention policy found for classification: ${classification}`);
    }
    return policy;
  }

  private getDefaultAccessControls(classification: DataClassification): AccessControl[] {
    const baseControls: Record<DataClassification, AccessControl[]> = {
      public: [{
        roleId: 'all',
        permissions: ['read'],
        restrictions: [],
        operatorId: this.operatorId
      }],
      internal: [{
        roleId: 'internal',
        permissions: ['read', 'write'],
        restrictions: ['no-external-export'],
        operatorId: this.operatorId
      }],
      restricted: [{
        roleId: 'restricted',
        permissions: ['read'],
        restrictions: ['no-external-export', 'audit-trail-required'],
        operatorId: this.operatorId
      }],
      confidential: [{
        roleId: 'confidential',
        permissions: ['read'],
        restrictions: ['no-external-export', 'audit-trail-required', 'two-factor-auth'],
        operatorId: this.operatorId
      }]
    };

    return baseControls[classification] || [];
  }

  private detectViolations(): ComplianceViolation[] {
    const violations: ComplianceViolation[] = [];
    
    // Check for expired access controls
    for (const tag of this.tags.values()) {
      for (const ac of tag.accessControls) {
        if (ac.validUntil && ac.validUntil < new Date()) {
          violations.push({
            id: this.generateViolationId(),
            type: 'access',
            severity: 'medium',
            description: 'Expired access control found',
            itemId: tag.id,
            detectedAt: new Date(),
            resolved: false
          });
        }
      }
    }

    return violations;
  }

  private generateActionId(): string {
    return `action_${Date.now()}_${this.operatorId}`;
  }

  private generateReportId(): string {
    return `report_${Date.now()}_${this.operatorId}`;
  }

  private generateViolationId(): string {
    return `violation_${Date.now()}_${this.operatorId}`;
  }
}