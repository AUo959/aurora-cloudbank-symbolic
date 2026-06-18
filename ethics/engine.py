"""Unified config-backed ethics engine for ORION Station checks."""

from __future__ import annotations

import json
import logging
import operator
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

from ethics.audit_log import AuditLogEntry, EthicsAuditLog

logger = logging.getLogger(__name__)

APPROVED = "APPROVED"
REVIEW = "REVIEW"
BLOCKED = "BLOCKED"

_SEVERITY_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
_COMPARATORS = [
    (">=", operator.ge),
    ("<=", operator.le),
    ("==", operator.eq),
    ("!=", operator.ne),
    (">", operator.gt),
    ("<", operator.lt),
]


@dataclass(frozen=True)
class EthicsRule:
    """One normalized validation rule from ethics/validation_engine."""

    rule_id: str
    name: str
    description: str
    category: str
    severity: str
    auto_block: bool
    conditions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TriggeredRule:
    """Rule hit included in an ethics verdict."""

    rule_id: str
    name: str
    category: str
    severity: str
    auto_block: bool
    matched_conditions: List[str]
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EthicsValidationResult:
    """Structured result returned by EthicsEngine.validate()."""

    verdict: str
    context: str
    agent_id: str
    anchor: Optional[str]
    severity: str = "none"
    triggered_rules: List[TriggeredRule] = field(default_factory=list)
    audit_id: Optional[str] = None
    audit_entry: Optional[Dict[str, Any]] = None
    engine_id: str = "PICARD_DELTA_3"
    engine_version: str = "unknown"
    compliance_monitor_id: str = "unknown"
    blockchain_anchoring: bool = False

    @property
    def approved(self) -> bool:
        return self.verdict == APPROVED

    @property
    def blocked(self) -> bool:
        return self.verdict == BLOCKED

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["triggered_rules"] = [rule.to_dict() for rule in self.triggered_rules]
        return data


class EthicsEngine:
    """Unified ethics engine loading L3, validation, and compliance configs."""

    DEFAULT_SENTINEL_THRESHOLDS = {
        "monitor": 0.4,
        "audit": 0.6,
        "intervention": 0.7,
        "human_approval": 0.8,
    }

    def __init__(
        self,
        *,
        config_root: Optional[Path | str] = None,
        audit_log: Optional[EthicsAuditLog] = None,
    ) -> None:
        self.config_root = Path(config_root) if config_root else Path(__file__).resolve().parent
        self.l3_config = self._load_yaml(self.config_root / "l3_layer" / "ethics_engine_config.yaml")
        self.validation_config = self._load_json(
            self.config_root / "validation_engine" / "validation_rules.json"
        )
        self.compliance_config = self._load_yaml(
            self.config_root / "compliance_monitor" / "compliance_config.yaml"
        )
        self.rules = self._load_rules(self.validation_config)
        self.audit_log = audit_log or EthicsAuditLog(
            cryptographic_signing=self.audit_trails.get("cryptographic_signing", True),
            blockchain_anchoring=self.audit_trails.get("blockchain_anchoring", False),
        )

    @property
    def engine_config(self) -> Dict[str, Any]:
        return self.l3_config.get("l3_ethics_engine", {})

    @property
    def compliance_monitor(self) -> Dict[str, Any]:
        return self.compliance_config.get("compliance_monitor", {})

    @property
    def audit_trails(self) -> Dict[str, Any]:
        return self.compliance_monitor.get("audit_trails", {})

    @property
    def engine_id(self) -> str:
        return str(self.engine_config.get("engine_id", "PICARD_DELTA_3"))

    @property
    def engine_version(self) -> str:
        return str(self.engine_config.get("version", "unknown"))

    @property
    def compliance_monitor_id(self) -> str:
        return str(self.compliance_monitor.get("monitor_id", "unknown"))

    def validate(
        self,
        *,
        context: str,
        signals: Dict[str, Any],
        anchor: Optional[str] = None,
        agent_id: str = "system",
    ) -> EthicsValidationResult:
        """Validate signals against all configured ethics rules."""
        normalized = self._normalize_signals(signals)
        triggered: List[TriggeredRule] = []

        for rule in self.rules:
            matched = [condition for condition in rule.conditions if self._check_condition(condition, normalized)]
            if self._rule_triggered(rule, matched):
                triggered.append(
                    TriggeredRule(
                        rule_id=rule.rule_id,
                        name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        auto_block=rule.auto_block,
                        matched_conditions=matched,
                        description=rule.description,
                    )
                )

        verdict = self._verdict_for(triggered)
        severity = self._max_severity(triggered)
        result = EthicsValidationResult(
            verdict=verdict,
            context=context,
            agent_id=agent_id,
            anchor=anchor,
            severity=severity,
            triggered_rules=triggered,
            engine_id=self.engine_id,
            engine_version=self.engine_version,
            compliance_monitor_id=self.compliance_monitor_id,
            blockchain_anchoring=bool(self.audit_trails.get("blockchain_anchoring", False)),
        )

        if verdict != APPROVED:
            entry = self._emit_audit(result, normalized)
            result.audit_id = entry.audit_id
            result.audit_entry = entry.to_dict()

        return result

    def sentinel_thresholds(self) -> Dict[str, float]:
        """Expose SENTINEL thresholds through the engine integration seam."""
        thresholds = dict(self.DEFAULT_SENTINEL_THRESHOLDS)
        enforcement = self.validation_config.get("ethics_validation_rules", {}).get("enforcement_levels", {})
        if enforcement.get("critical", {}).get("auto_block") is True:
            thresholds["human_approval"] = max(thresholds["human_approval"], thresholds["intervention"])
        return thresholds

    def _emit_audit(self, result: EthicsValidationResult, signals: Dict[str, Any]) -> AuditLogEntry:
        return self.audit_log.emit(
            context=result.context,
            agent_id=result.agent_id,
            anchor=result.anchor,
            verdict=result.verdict,
            severity=result.severity,
            triggered_rules=[rule.rule_id for rule in result.triggered_rules],
            details={
                "engine_id": result.engine_id,
                "engine_version": result.engine_version,
                "compliance_monitor_id": result.compliance_monitor_id,
                "signals": signals,
                "triggered_rules": [rule.to_dict() for rule in result.triggered_rules],
                "blockchain_anchoring_todo": result.blockchain_anchoring,
            },
        )

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            raise ValueError(f"{path} must contain a mapping")
        return data

    def _load_json(self, path: Path) -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"{path} must contain a mapping")
        return data

    def _load_rules(self, data: Dict[str, Any]) -> List[EthicsRule]:
        categories = data.get("ethics_validation_rules", {}).get("rule_categories", {})
        rules: List[EthicsRule] = []
        for category_name, category_data in categories.items():
            for rule_data in category_data.get("rules", []):
                rules.append(
                    EthicsRule(
                        rule_id=str(rule_data["id"]),
                        name=str(rule_data["name"]),
                        description=str(rule_data["description"]),
                        category=str(category_name),
                        severity=str(rule_data["severity"]),
                        auto_block=bool(rule_data["auto_block"]),
                        conditions=[str(condition) for condition in rule_data.get("conditions", [])],
                    )
                )
        return rules

    def _normalize_signals(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(signals)

        alias_pairs = {
            "no_human_override": ("human_override", False),
            "no_explanation_available": ("explanation_available", False),
            "safety_protocols_incomplete": ("safety_protocols_complete", False),
            "no_mitigation_plan": ("mitigation_plan", False),
            "consent_missing": ("informed_consent", False),
        }
        for negative_key, (positive_key, negative_value) in alias_pairs.items():
            if negative_key not in normalized and normalized.get(positive_key) is negative_value:
                normalized[negative_key] = True

        if "safety_protocols_incomplete" not in normalized and normalized.get("safety_override_missing"):
            normalized["safety_protocols_incomplete"] = True
        if "no_explanation_available" not in normalized and normalized.get("no_explanation"):
            normalized["no_explanation_available"] = True

        return normalized

    def _check_condition(self, condition: str, signals: Dict[str, Any]) -> bool:
        condition = condition.strip()
        for symbol, comparator in _COMPARATORS:
            if symbol in condition:
                left, right = [part.strip() for part in condition.split(symbol, 1)]
                if left not in signals:
                    return False
                right_value = self._resolve_value(right, signals)
                left_value = signals[left]
                try:
                    left_value = float(left_value)
                    right_value = float(right_value)
                except (TypeError, ValueError):
                    pass
                return bool(comparator(left_value, right_value))

        value = signals.get(condition)
        return bool(value) if value is not None else False

    def _rule_triggered(self, rule: EthicsRule, matched_conditions: List[str]) -> bool:
        if rule.rule_id == "AI002":
            return set(rule.conditions).issubset(set(matched_conditions))
        return bool(matched_conditions)

    def _resolve_value(self, name_or_value: str, signals: Dict[str, Any]) -> Any:
        if name_or_value in signals:
            return signals[name_or_value]
        if name_or_value == "threshold":
            return signals.get("threshold", 0.3)
        lowered = name_or_value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        try:
            return float(name_or_value)
        except ValueError:
            return name_or_value.strip("'\"")

    def _verdict_for(self, triggered: Iterable[TriggeredRule]) -> str:
        triggered = list(triggered)
        if not triggered:
            return APPROVED
        if any(rule.auto_block or rule.severity == "critical" for rule in triggered):
            return BLOCKED
        return REVIEW

    def _max_severity(self, triggered: Iterable[TriggeredRule]) -> str:
        severities = [rule.severity for rule in triggered]
        if not severities:
            return "none"
        return max(severities, key=lambda severity: _SEVERITY_RANK.get(severity, 0))


def get_sentinel_thresholds(config_root: Optional[Path | str] = None) -> Dict[str, float]:
    """Load SENTINEL thresholds via the unified engine seam."""
    return EthicsEngine(config_root=config_root).sentinel_thresholds()
