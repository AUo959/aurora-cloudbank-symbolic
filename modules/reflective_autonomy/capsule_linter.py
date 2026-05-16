"""Deterministic capsule linting for the reflective autonomy layer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import yaml

DEFAULT_ANCHOR_SEED = "EOS_SEED_ORION"
DEFAULT_ETHICS_PROTOCOL = "Picard_Delta_3"
DEFAULT_MAX_DRIFT = 0.002
THREADCORE_REQUIRED_FIELDS = (
    "augmentation",
    "version",
    "role",
    "threadcore_directives",
    "anchor_seed",
    "ethics_protocol",
)
CAPSULE_REQUIRED_FIELDS = ("capsule_id", "role", "ethics_protocol")
REGISTRY_REQUIRED_FIELDS = ("status", "files", "exported_at")


@dataclass(frozen=True)
class CapsuleLintFinding:
    """A machine-readable capsule validation finding."""

    code: str
    severity: str
    message: str
    capsule_id: Optional[str] = None
    field: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "capsule_id": self.capsule_id,
            "field": self.field,
        }


@dataclass
class CapsuleLintResult:
    """Aggregate result for one or more capsule checks."""

    checked_capsules: int = 0
    findings: List[CapsuleLintFinding] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)

    @property
    def errors(self) -> List[CapsuleLintFinding]:
        return [finding for finding in self.findings if finding.severity == "error"]

    @property
    def warnings(self) -> List[CapsuleLintFinding]:
        return [finding for finding in self.findings if finding.severity == "warning"]

    def add(self, finding: CapsuleLintFinding) -> None:
        self.findings.append(finding)

    def extend(self, other: "CapsuleLintResult") -> None:
        self.checked_capsules += other.checked_capsules
        self.findings.extend(other.findings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "checked_capsules": self.checked_capsules,
            "errors": [finding.to_dict() for finding in self.errors],
            "warnings": [finding.to_dict() for finding in self.warnings],
            "findings": [finding.to_dict() for finding in self.findings],
        }


class CapsuleLinter:
    """Validate ThreadCore and reflective autonomy capsule structures."""

    def __init__(
        self,
        registry_path: Optional[Path] = None,
        repo_root: Optional[Path] = None,
    ) -> None:
        self.repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]
        self.registry_path = Path(registry_path) if registry_path else self.repo_root / "threadcore_registry.json"
        self.registry = self._load_registry()
        self.rules = self.registry.get("validation_rules", {})

    def lint_capsule(
        self,
        capsule: Mapping[str, Any],
        capsule_id: Optional[str] = None,
    ) -> CapsuleLintResult:
        """Validate one in-memory capsule payload."""
        result = CapsuleLintResult(checked_capsules=1)
        if not isinstance(capsule, Mapping):
            result.add(
                CapsuleLintFinding(
                    code="invalid_capsule_type",
                    severity="error",
                    message="Capsule payload must be a mapping.",
                    capsule_id=capsule_id,
                )
            )
            return result

        resolved_id = capsule_id or self._capsule_id(capsule)
        self._check_required_fields(capsule, self._required_fields_for(capsule), resolved_id, result)
        self._check_governance_fields(capsule, resolved_id, result)
        self._check_directives(capsule, resolved_id, result)
        self._check_drift(capsule, resolved_id, result)
        return result

    def lint_payload_file(self, payload_path: Path) -> CapsuleLintResult:
        """Load and validate one JSON or YAML capsule file."""
        path = Path(payload_path)
        if not path.exists():
            return CapsuleLintResult(
                findings=[
                    CapsuleLintFinding(
                        code="payload_file_missing",
                        severity="error",
                        message=f"Payload file not found: {path}",
                        capsule_id=path.stem,
                    )
                ]
            )

        try:
            payload = self._load_structured_file(path)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            return CapsuleLintResult(
                checked_capsules=1,
                findings=[
                    CapsuleLintFinding(
                        code="payload_file_unreadable",
                        severity="error",
                        message=f"Could not parse payload file {path}: {exc}",
                        capsule_id=path.stem,
                    )
                ],
            )

        return self.lint_capsule(payload, capsule_id=path.stem)

    def lint_registry_entries(self, registry: Mapping[str, Mapping[str, Any]]) -> CapsuleLintResult:
        """Validate the historical anchor-hash capsule registry shape."""
        result = CapsuleLintResult()
        for anchor, metadata in registry.items():
            result.checked_capsules += 1
            if not isinstance(metadata, Mapping):
                result.add(
                    CapsuleLintFinding(
                        code="registry_entry_invalid",
                        severity="error",
                        message="Registry entry must be a mapping.",
                        capsule_id=str(anchor),
                    )
                )
                continue
            self._check_required_fields(metadata, REGISTRY_REQUIRED_FIELDS, str(anchor), result)
            if metadata.get("status") not in (None, "sealed"):
                result.add(
                    CapsuleLintFinding(
                        code="capsule_unsealed",
                        severity="error",
                        message="Capsule registry entry is not sealed.",
                        capsule_id=str(anchor),
                        field="status",
                    )
                )
        return result

    def lint_registered_payloads(self) -> CapsuleLintResult:
        """Validate all payload files referenced by threadcore_registry.json."""
        result = CapsuleLintResult()
        payloads = self.registry.get("payloads", {})
        for payload_name, payload_info in payloads.items():
            file_path = payload_info.get("file_path")
            if not file_path:
                result.add(
                    CapsuleLintFinding(
                        code="registry_payload_path_missing",
                        severity="error",
                        message="Registry payload entry has no file_path.",
                        capsule_id=payload_name,
                        field="file_path",
                    )
                )
                continue
            result.extend(self.lint_payload_file(self.repo_root / file_path))
        return result

    def suggest_corrections(self, result: CapsuleLintResult) -> List[Dict[str, Optional[str]]]:
        """Convert lint findings into deterministic correction intents."""
        return [self._suggestion_for(finding) for finding in result.findings]

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_path.exists():
            return {}
        with open(self.registry_path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _required_fields_for(self, capsule: Mapping[str, Any]) -> Sequence[str]:
        if "threadcore_directives" in capsule:
            return tuple(self.rules.get("required_fields", THREADCORE_REQUIRED_FIELDS))
        if "capsule_id" in capsule:
            return CAPSULE_REQUIRED_FIELDS
        return THREADCORE_REQUIRED_FIELDS

    def _check_required_fields(
        self,
        capsule: Mapping[str, Any],
        required_fields: Iterable[str],
        capsule_id: Optional[str],
        result: CapsuleLintResult,
    ) -> None:
        for field_name in required_fields:
            if field_name not in capsule or capsule.get(field_name) in (None, "", []):
                result.add(
                    CapsuleLintFinding(
                        code="missing_required_field",
                        severity="error",
                        message=f"Missing required field: {field_name}",
                        capsule_id=capsule_id,
                        field=field_name,
                    )
                )

    def _check_governance_fields(
        self,
        capsule: Mapping[str, Any],
        capsule_id: Optional[str],
        result: CapsuleLintResult,
    ) -> None:
        required_anchor = self.rules.get("anchor_seed_required", DEFAULT_ANCHOR_SEED)
        if "anchor_seed" in capsule and capsule.get("anchor_seed") != required_anchor:
            result.add(
                CapsuleLintFinding(
                    code="invalid_anchor_seed",
                    severity="error",
                    message=f"Anchor seed must be {required_anchor}.",
                    capsule_id=capsule_id,
                    field="anchor_seed",
                )
            )

        required_ethics = self.rules.get("ethics_protocol_required", DEFAULT_ETHICS_PROTOCOL)
        if capsule.get("ethics_protocol") != required_ethics:
            result.add(
                CapsuleLintFinding(
                    code="invalid_ethics_protocol",
                    severity="error",
                    message=f"Ethics protocol must be {required_ethics}.",
                    capsule_id=capsule_id,
                    field="ethics_protocol",
                )
            )

    def _check_directives(
        self,
        capsule: Mapping[str, Any],
        capsule_id: Optional[str],
        result: CapsuleLintResult,
    ) -> None:
        directives = capsule.get("threadcore_directives")
        if directives is None:
            return
        if not isinstance(directives, list) or not directives or not all(
            isinstance(item, str) and item.strip() for item in directives
        ):
            result.add(
                CapsuleLintFinding(
                    code="invalid_threadcore_directives",
                    severity="error",
                    message="threadcore_directives must be a non-empty list of strings.",
                    capsule_id=capsule_id,
                    field="threadcore_directives",
                )
            )

    def _check_drift(
        self,
        capsule: Mapping[str, Any],
        capsule_id: Optional[str],
        result: CapsuleLintResult,
    ) -> None:
        drift_value = self._parse_drift(capsule.get("symbolic_drift"))
        if drift_value is None:
            return
        max_drift = float(self.rules.get("max_drift_threshold", DEFAULT_MAX_DRIFT))
        if drift_value > max_drift:
            result.add(
                CapsuleLintFinding(
                    code="symbolic_drift_high",
                    severity="warning",
                    message=f"Symbolic drift {drift_value} exceeds threshold {max_drift}.",
                    capsule_id=capsule_id,
                    field="symbolic_drift",
                )
            )

    @staticmethod
    def _capsule_id(capsule: Mapping[str, Any]) -> Optional[str]:
        for key in ("capsule_id", "augmentation", "version"):
            value = capsule.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _parse_drift(raw_value: Any) -> Optional[float]:
        if raw_value in (None, ""):
            return None
        try:
            raw_text = str(raw_value).strip()
            if raw_text.endswith("%"):
                return float(raw_text[:-1]) / 100
            return float(raw_text)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _load_structured_file(path: Path) -> Mapping[str, Any]:
        with open(path, "r", encoding="utf-8") as handle:
            if path.suffix.lower() == ".json":
                payload = json.load(handle)
            else:
                payload = yaml.safe_load(handle)
        if not isinstance(payload, Mapping):
            raise ValueError("payload root must be a mapping")
        return payload

    @staticmethod
    def _suggestion_for(finding: CapsuleLintFinding) -> Dict[str, Optional[str]]:
        actions = {
            "missing_required_field": "populate_field",
            "invalid_anchor_seed": "restore_governance_value",
            "invalid_ethics_protocol": "restore_governance_value",
            "invalid_threadcore_directives": "repair_directives",
            "symbolic_drift_high": "review_drift",
            "payload_file_missing": "recover_payload_file",
            "capsule_unsealed": "seal_capsule",
        }
        return {
            "action": actions.get(finding.code, "review_finding"),
            "target": finding.capsule_id,
            "field": finding.field,
            "reason": finding.message,
        }


__all__ = [
    "CapsuleLinter",
    "CapsuleLintFinding",
    "CapsuleLintResult",
    "DEFAULT_ANCHOR_SEED",
    "DEFAULT_ETHICS_PROTOCOL",
]
