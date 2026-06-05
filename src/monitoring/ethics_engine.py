"""
Ethics Compliance Engine

Evaluates agent actions and decisions against defined ethical guidelines
and safety boundaries. Supports configurable rules and automated enforcement.
"""

import json
import logging
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from src.core.time_utils import utc_iso
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable

from src.utils.atomic_io import atomic_write_json, append_jsonl

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Severity level of ethics violation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleCategory(Enum):
    """Category of ethics rule"""
    MISSION_ETHICS = "mission_ethics"
    RESOURCE_ETHICS = "resource_ethics"
    AI_ETHICS = "ai_ethics"
    SAFETY = "safety"
    TRANSPARENCY = "transparency"
    FAIRNESS = "fairness"


@dataclass
class EthicsRule:
    """Definition of an ethics compliance rule"""
    id: str
    name: str
    description: str
    category: RuleCategory
    severity: ViolationSeverity
    auto_block: bool
    conditions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EthicsViolation:
    """Record of an ethics violation"""
    timestamp: str
    agent_id: str
    rule_id: str
    rule_name: str
    severity: ViolationSeverity
    category: RuleCategory
    description: str
    blocked: bool
    context: Dict[str, Any]
    context_tag: Optional[str] = None
    remediation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['category'] = self.category.value
        return data


@dataclass
class ActionContext:
    """Context for evaluating an action"""
    agent_id: str
    action_type: str
    parameters: Dict[str, Any]
    timestamp: str = field(default_factory=utc_iso)
    context_tag: Optional[str] = None


class EthicsEngine:
    """
    Ethics Compliance and Rule Enforcement Engine
    
    Evaluates agent actions against configurable ethics rules and safety
    boundaries. Supports automated blocking of critical violations and
    comprehensive audit trail.
    
    Features:
    - Rule-based ethics evaluation
    - Multi-level severity classification
    - Automated intervention for critical violations
    - Customizable rules via JSON/YAML config
    - Extensible with custom evaluators
    """
    
    def __init__(
        self,
        rules_path: Optional[Path] = None,
        violations_path: Optional[Path] = None
    ):
        """
        Initialize ethics engine
        
        Args:
            rules_path: Path to rules configuration file (JSON)
            violations_path: Append-only JSONL path for persisted violations
        """
        self.rules: Dict[str, EthicsRule] = {}
        self.violations: List[EthicsViolation] = []
        self.custom_evaluators: Dict[str, Callable] = {}
        self.violations_path = violations_path

        # Thread safety for violation persistence
        self._lock = threading.Lock()
        
        # Load default rules if available
        if rules_path and rules_path.exists():
            self.load_rules(rules_path)
        else:
            self._load_default_rules()

        self._load_violations()
        
        logger.info("Ethics engine initialized with %d rules", len(self.rules))
    
    def _load_default_rules(self):
        """Load default ethics rules"""
        default_rules = [
            EthicsRule(
                id="SAFETY_001",
                name="Life Safety Priority",
                description="Actions must not create risk to human safety",
                category=RuleCategory.SAFETY,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                conditions=["risk_to_life > 0", "safety_override_missing"]
            ),
            EthicsRule(
                id="AI_001",
                name="Human Oversight Required",
                description="Critical decisions must have human oversight",
                category=RuleCategory.AI_ETHICS,
                severity=ViolationSeverity.CRITICAL,
                auto_block=True,
                conditions=["critical_decision", "no_human_approval"]
            ),
            EthicsRule(
                id="AI_002",
                name="Decision Transparency",
                description="AI decisions must be explainable",
                category=RuleCategory.TRANSPARENCY,
                severity=ViolationSeverity.HIGH,
                auto_block=False,
                conditions=["decision_opacity > 0.5", "no_explanation"]
            ),
            EthicsRule(
                id="RESOURCE_001",
                name="Fair Resource Allocation",
                description="Resources must be allocated fairly",
                category=RuleCategory.FAIRNESS,
                severity=ViolationSeverity.MEDIUM,
                auto_block=False,
                conditions=["inequality_coefficient > 0.7"]
            ),
            EthicsRule(
                id="MISSION_001",
                name="Informed Consent",
                description="Stakeholders must provide informed consent",
                category=RuleCategory.MISSION_ETHICS,
                severity=ViolationSeverity.HIGH,
                auto_block=True,
                conditions=["consent_missing", "insufficient_information"]
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.id] = rule
    
    def load_rules(self, rules_path: Path):
        """
        Load rules from configuration file
        
        Args:
            rules_path: Path to JSON rules file
        """
        try:
            with open(rules_path, 'r') as f:
                data = json.load(f)
            
            if 'ethics_validation_rules' in data:
                # Load from existing format
                for category_name, category_data in data['ethics_validation_rules'].get('rule_categories', {}).items():
                    for rule_data in category_data.get('rules', []):
                        rule = EthicsRule(
                            id=rule_data['id'],
                            name=rule_data['name'],
                            description=rule_data['description'],
                            category=self._map_category(category_name),
                            severity=ViolationSeverity(rule_data['severity']),
                            auto_block=rule_data['auto_block'],
                            conditions=rule_data['conditions']
                        )
                        self.rules[rule.id] = rule
            
            logger.info("Loaded %d rules from %s", len(self.rules), rules_path)
            
        except Exception as e:
            logger.error("Failed to load rules from %s: %s", rules_path, e)
            self._load_default_rules()
    
    def _map_category(self, category_name: str) -> RuleCategory:
        """Map category name to enum"""
        mapping = {
            'mission_ethics': RuleCategory.MISSION_ETHICS,
            'resource_ethics': RuleCategory.RESOURCE_ETHICS,
            'ai_ethics': RuleCategory.AI_ETHICS,
            'safety': RuleCategory.SAFETY,
            'transparency': RuleCategory.TRANSPARENCY,
            'fairness': RuleCategory.FAIRNESS
        }
        return mapping.get(category_name, RuleCategory.AI_ETHICS)
    
    def register_evaluator(self, condition: str, evaluator: Callable[[Dict[str, Any]], bool]):
        """
        Register custom condition evaluator
        
        Args:
            condition: Condition pattern to match
            evaluator: Function that takes context and returns boolean
        """
        self.custom_evaluators[condition] = evaluator
        logger.info("Registered custom evaluator for condition: %s", condition)
    
    def evaluate_action(
        self,
        context: ActionContext
    ) -> List[EthicsViolation]:
        """
        Evaluate an action against all ethics rules
        
        Args:
            context: Action context to evaluate
        
        Returns:
            List of violations detected (empty if compliant)
        """
        violations = []
        
        for rule in self.rules.values():
            violation = self._evaluate_rule(rule, context)
            if violation:
                self._persist_violation(violation)
                violations.append(violation)
                self.violations.append(violation)
        
        if violations:
            logger.warning(
                "Ethics violations detected for %s: %d violations",
                context.agent_id, len(violations)
            )
        
        return violations
    
    def _evaluate_rule(
        self,
        rule: EthicsRule,
        context: ActionContext
    ) -> Optional[EthicsViolation]:
        """
        Evaluate a single rule against context
        
        Args:
            rule: Rule to evaluate
            context: Action context
        
        Returns:
            EthicsViolation if rule violated, None if compliant
        """
        # Check if any conditions are met
        violated = False
        matched_conditions = []
        
        for condition in rule.conditions:
            if self._check_condition(condition, context):
                violated = True
                matched_conditions.append(condition)
        
        if not violated:
            return None
        
        # Create violation record
        description = f"{rule.description}. Matched conditions: {', '.join(matched_conditions)}"
        
        violation = EthicsViolation(
            timestamp=utc_iso(),
            agent_id=context.agent_id,
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            category=rule.category,
            description=description,
            blocked=rule.auto_block,
            context=context.parameters,
            context_tag=context.context_tag,
            remediation=self._suggest_remediation(rule)
        )
        
        return violation
    
    def _check_condition(self, condition: str, context: ActionContext) -> bool:
        """
        Check if a condition is met
        
        Args:
            condition: Condition string to evaluate
            context: Action context
        
        Returns:
            True if condition is met
        """
        # Check for custom evaluator
        if condition in self.custom_evaluators:
            return self.custom_evaluators[condition](context.parameters)
        
        # Simple parameter checks
        if condition in context.parameters:
            value = context.parameters[condition]
            return bool(value) if value is not None else False
        
        # Parse comparison expressions (e.g., "action_type == 'forbidden_action'")
        # Also check context attributes like action_type, agent_id
        for op in ['>=', '<=', '==', '!=', '>', '<']:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    param, threshold = parts[0].strip(), parts[1].strip()
                    if param in context.parameters:
                        param_value = context.parameters[param]
                        try:
                            param_value = float(param_value)
                            threshold_value = float(threshold)
                            
                            if op == '>':
                                return param_value > threshold_value
                            elif op == '<':
                                return param_value < threshold_value
                            elif op == '>=':
                                return param_value >= threshold_value
                            elif op == '<=':
                                return param_value <= threshold_value
                            elif op == '==':
                                return param_value == threshold_value
                            elif op == '!=':
                                return param_value != threshold_value
                        except (ValueError, TypeError):
                            # Try string comparison for non-numeric values
                            if op == '==':
                                return str(param_value) == threshold.strip("'\"")
                            elif op == '!=':
                                return str(param_value) != threshold.strip("'\"")
        
        # Check context attributes (action_type, agent_id) for comparison conditions
        for op in ['==', '!=']:
            if op in condition:
                parts = condition.split(op, 1)
                if len(parts) == 2:
                    attr_name = parts[0].strip()
                    expected_value = parts[1].strip().strip("'\"")
                    # Check if it's a context attribute
                    if hasattr(context, attr_name):
                        actual_value = getattr(context, attr_name)
                        if op == '==':
                            return str(actual_value) == expected_value
                        elif op == '!=':
                            return str(actual_value) != expected_value
        
        return False
    
    def _suggest_remediation(self, rule: EthicsRule) -> str:
        """Suggest remediation based on rule"""
        remediations = {
            RuleCategory.SAFETY: "Review safety protocols and obtain necessary approvals",
            RuleCategory.AI_ETHICS: "Ensure human oversight and decision explainability",
            RuleCategory.TRANSPARENCY: "Provide clear explanation of decision process",
            RuleCategory.FAIRNESS: "Review allocation algorithms for bias",
            RuleCategory.MISSION_ETHICS: "Obtain informed consent from all stakeholders"
        }
        return remediations.get(rule.category, "Review action for compliance")
    
    def get_violations(
        self,
        agent_id: Optional[str] = None,
        severity: Optional[ViolationSeverity] = None,
        category: Optional[RuleCategory] = None,
        since: Optional[datetime] = None
    ) -> List[EthicsViolation]:
        """
        Get filtered list of violations
        
        Args:
            agent_id: Filter by agent ID
            severity: Filter by severity
            category: Filter by category
            since: Filter violations after this time
        
        Returns:
            List of matching violations
        """
        violations = self.violations
        
        if agent_id:
            violations = [v for v in violations if v.agent_id == agent_id]
        
        if severity:
            violations = [v for v in violations if v.severity == severity]
        
        if category:
            violations = [v for v in violations if v.category == category]
        
        if since:
            violations = [
                v for v in violations
                if datetime.fromisoformat(v.timestamp) >= since
            ]
        
        return violations

    def export_violations(self) -> List[Dict[str, Any]]:
        """Export recorded violations for persistence and diagnostics."""
        return [violation.to_dict() for violation in self.violations]

    def import_violations(self, data: List[Dict[str, Any]]):
        """Import violations from persisted data."""
        self.violations = [
            self._violation_from_dict(violation_data)
            for violation_data in data
        ]
        self._rewrite_violations()
        logger.info("Imported %d ethics violations", len(self.violations))

    def _persist_violation(self, violation: EthicsViolation):
        """Append a violation to the shared violation store."""
        if not self.violations_path:
            return

        try:
            with self._lock:
                append_jsonl(self.violations_path, violation.to_dict())
        except Exception as e:
            logger.error("Failed to persist ethics violation: %s", e)

    def _load_violations(self):
        """Load persisted violations from the shared violation store."""
        if not self.violations_path or not self.violations_path.exists():
            return

        try:
            with open(self.violations_path, 'r') as f:
                self.violations = [
                    self._violation_from_dict(json.loads(line))
                    for line in f
                    if line.strip()
                ]
            logger.info("Loaded %d ethics violations", len(self.violations))
        except Exception as e:
            logger.error("Failed to load ethics violations: %s", e)

    def _rewrite_violations(self):
        """Rewrite the shared violation store after explicit mutation."""
        if not self.violations_path:
            return

        try:
            with self._lock:
                import os
                tmp = self.violations_path.with_suffix(self.violations_path.suffix + ".tmp")
                try:
                    self.violations_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(tmp, "w", encoding="utf-8") as f:
                        for violation in self.violations:
                            f.write(json.dumps(violation.to_dict(), sort_keys=True) + "\n")
                        f.flush()
                        os.fsync(f.fileno())
                    os.replace(tmp, self.violations_path)
                except Exception:
                    tmp.unlink(missing_ok=True)
                    raise
        except Exception as e:
            logger.error("Failed to rewrite ethics violations: %s", e)

    def _violation_from_dict(self, data: Dict[str, Any]) -> EthicsViolation:
        """Restore a violation from persisted data."""
        return EthicsViolation(
            timestamp=data['timestamp'],
            agent_id=data['agent_id'],
            rule_id=data['rule_id'],
            rule_name=data['rule_name'],
            severity=ViolationSeverity(data['severity']),
            category=RuleCategory(data['category']),
            description=data['description'],
            blocked=data['blocked'],
            context=data['context'],
            context_tag=data.get('context_tag'),
            remediation=data.get('remediation')
        )
    
    def check_should_block(self, violations: List[EthicsViolation]) -> bool:
        """
        Check if action should be blocked based on violations
        
        Args:
            violations: List of violations to check
        
        Returns:
            True if action should be blocked
        """
        return any(v.blocked for v in violations)
    
    def add_rule(self, rule: EthicsRule):
        """Add a new rule to the engine"""
        self.rules[rule.id] = rule
        logger.info("Added rule: %s (%s)", rule.id, rule.name)
    
    def remove_rule(self, rule_id: str):
        """Remove a rule from the engine"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info("Removed rule: %s", rule_id)
    
    def export_rules(self) -> Dict[str, Any]:
        """Export all rules for persistence"""
        return {
            rule_id: {
                'id': rule.id,
                'name': rule.name,
                'description': rule.description,
                'category': rule.category.value,
                'severity': rule.severity.value,
                'auto_block': rule.auto_block,
                'conditions': rule.conditions,
                'metadata': rule.metadata
            }
            for rule_id, rule in self.rules.items()
        }
    
    def clear_violations(self, before: Optional[datetime] = None):
        """
        Clear old violations
        
        Args:
            before: Clear violations before this time (default: all)
        """
        if before:
            self.violations = [
                v for v in self.violations
                if datetime.fromisoformat(v.timestamp) >= before
            ]
        else:
            self.violations.clear()

        self._rewrite_violations()
        
        logger.info("Cleared violations (before=%s)", before)
