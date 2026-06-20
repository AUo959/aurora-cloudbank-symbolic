"""Deterministic ORD dispatch policy engine.

Status: draft_policy_library
Anchor: EOS_SEED_ORION
Ethics: Picard_Delta_3

This module intentionally removes environment-specific dependencies from the
recovered ORD prototype. It exposes a pure policy surface suitable for unit
tests, receipts, and later adapter injection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional
from urllib.parse import urlsplit

from modules.ord.ord_threshold_registry import ThresholdRegistry, load_default_registry


class DroneType(Enum):
    GAMMA_SWARM = "ORD-1 Gamma Swarm"
    DELTA_SCOUT = "ORD-2 Delta Scout"
    SHADOWFAX = "ORD-3 Shadowfax"
    WISP = "ORD-4 Wisp"


class SensitivityClass(Enum):
    STANDARD = "STANDARD"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


@dataclass(frozen=True)
class MissionBrief:
    mission_id: str
    tool_name: str
    risk_level: float
    destination: str
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransportRequirement:
    encryption: str
    tamper_evident: bool
    sensitivity: SensitivityClass
    quantum_seal_required: bool


@dataclass(frozen=True)
class DispatchOrder:
    mission_id: str
    drones_required: List[DroneType]
    deployment_phase: Dict[str, List[DroneType]]
    priority: int
    transport_requirement: Optional[TransportRequirement]
    special_instructions: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DispatchPolicy:
    threshold_registry: ThresholdRegistry = field(default_factory=load_default_registry)
    write_tools: List[str] = field(default_factory=lambda: [
        "create_branch", "create_or_update_file", "push_files",
        "create_issue", "create_pull_request", "add_issue_comment",
        "update_issue", "update_pull_request",
    ])
    destructive_tools: List[str] = field(default_factory=lambda: [
        "delete_file", "merge_pull_request", "close_issue",
    ])
    data_extraction_tools: List[str] = field(default_factory=lambda: [
        "fetch_url", "get_file_contents", "search_files",
    ])
    sensitive_tools: List[str] = field(default_factory=lambda: [
        "push_files", "create_or_update_file",
    ])
    trusted_domains: List[str] = field(default_factory=lambda: [
        "api.github.com", "github.com", "api.anthropic.com", "claude.ai",
    ])
    internal_patterns: List[str] = field(default_factory=lambda: [
        "localhost", "127.0.0.1", "aurora-internal", "orion-station",
    ])


class OrdPolicyEngine:
    def __init__(self, policy: Optional[DispatchPolicy] = None) -> None:
        self.policy = policy or DispatchPolicy()
        self.registry = self.policy.threshold_registry

    def create_dispatch_order(self, mission: MissionBrief) -> DispatchOrder:
        drones_required: List[DroneType] = []
        pre_flight: List[DroneType] = []
        post_flight: List[DroneType] = []
        special_instructions: Dict[str, Any] = {
            "threshold_registry": {
                "registry_id": self.registry.registry_id,
                "version": self.registry.version,
            }
        }

        is_external = not self._is_internal_destination(mission.destination)
        is_trusted = self._is_trusted_destination(mission.destination)

        if self._requires_reconnaissance(mission.tool_name, is_external, is_trusted, mission.risk_level):
            self._append_unique(drones_required, DroneType.DELTA_SCOUT)
            self._append_unique(pre_flight, DroneType.DELTA_SCOUT)
            special_instructions["delta_scout"] = {
                "full_scan": mission.risk_level >= self.registry.quantum_seal_threshold,
                "ssl_verify": True,
                "latency_threshold_ms": 5000,
                "threat_abort_threshold": self.registry.quantum_seal_threshold,
            }

        if self._requires_inspection(mission.tool_name, is_external, mission.risk_level):
            self._append_unique(drones_required, DroneType.SHADOWFAX)
            self._append_unique(post_flight, DroneType.SHADOWFAX)
            special_instructions["shadowfax"] = {
                "drift_threshold": self.registry.drift_threshold,
                "ethics_scan": True,
                "structure_validation": True,
                "quarantine_on_drift": mission.risk_level >= self.registry.quantum_seal_threshold,
            }

        if self._requires_sanitization(mission.tool_name, is_trusted, mission.risk_level):
            self._append_unique(drones_required, DroneType.GAMMA_SWARM)
            self._append_unique(post_flight, DroneType.GAMMA_SWARM)
            special_instructions["gamma_swarm"] = {
                "strip_scripts": True,
                "redact_pii": self._pii_detection_enabled(mission.tool_name),
                "fix_malformed": True,
                "aggressive_mode": not is_trusted,
            }

        transport_requirement = None
        if self._requires_secure_transport(mission.tool_name, mission.risk_level, mission.parameters):
            self._append_unique(drones_required, DroneType.WISP)
            self._append_unique(post_flight, DroneType.WISP)
            transport_requirement = TransportRequirement(
                encryption="AES-256",
                tamper_evident=True,
                quantum_seal_required=mission.risk_level >= self.registry.quantum_seal_threshold,
                sensitivity=self.classify_data_sensitivity(mission.tool_name, mission.parameters),
            )
            special_instructions["wisp"] = {
                "encryption": transport_requirement.encryption,
                "tamper_evident": transport_requirement.tamper_evident,
                "quantum_seal": transport_requirement.quantum_seal_required,
                "data_sensitivity": transport_requirement.sensitivity.value,
            }

        return DispatchOrder(
            mission_id=mission.mission_id,
            drones_required=drones_required,
            deployment_phase={"pre_flight": pre_flight, "post_flight": post_flight},
            priority=self._compute_priority(mission.risk_level, mission.tool_name),
            transport_requirement=transport_requirement,
            special_instructions=special_instructions,
        )

    def classify_data_sensitivity(self, tool_name: str, parameters: Mapping[str, Any]) -> SensitivityClass:
        registry_label = self.registry.sensitivity_for_value(parameters)
        if registry_label == SensitivityClass.RESTRICTED.value:
            return SensitivityClass.RESTRICTED
        if tool_name in self.policy.sensitive_tools:
            return SensitivityClass.CONFIDENTIAL
        return SensitivityClass.STANDARD

    def _is_internal_destination(self, destination: str) -> bool:
        scheme, hostname = self._destination_authority(destination)
        internal_names = {pattern.lower() for pattern in self.policy.internal_patterns}
        return scheme in internal_names or hostname in internal_names

    def _is_trusted_destination(self, destination: str) -> bool:
        _, hostname = self._destination_authority(destination)
        return any(
            hostname == domain.lower() or hostname.endswith(f".{domain.lower()}")
            for domain in self.policy.trusted_domains
        )

    def _requires_reconnaissance(self, tool_name: str, is_external: bool, is_trusted: bool, risk_level: float) -> bool:
        return (
            is_external
            or (is_external and not is_trusted)
            or tool_name in self.policy.write_tools
            or tool_name in self.policy.destructive_tools
            or risk_level >= self.registry.reconnaissance_threshold
        )

    def _requires_inspection(self, tool_name: str, is_external: bool, risk_level: float) -> bool:
        return (
            is_external
            or tool_name in self.policy.write_tools
            or risk_level >= self.registry.inspection_threshold
        )

    def _requires_sanitization(self, tool_name: str, is_trusted: bool, risk_level: float) -> bool:
        return tool_name in self.policy.data_extraction_tools and (
            not is_trusted or risk_level >= self.registry.inspection_threshold
        )

    def _requires_secure_transport(self, tool_name: str, risk_level: float, parameters: Mapping[str, Any]) -> bool:
        return (
            risk_level >= self.registry.secure_transport_threshold
            or tool_name in self.policy.sensitive_tools
            or self.registry.sensitivity_for_value(parameters) == SensitivityClass.RESTRICTED.value
        )

    def _pii_detection_enabled(self, tool_name: str) -> bool:
        return tool_name in self.policy.data_extraction_tools

    def _compute_priority(self, risk_level: float, tool_name: str) -> int:
        base = 1
        if tool_name in self.policy.destructive_tools:
            base += 4
        elif tool_name in self.policy.write_tools:
            base += 2
        base += min(5, int(risk_level * 5))
        return max(1, min(10, base))

    @staticmethod
    def _append_unique(items: List[DroneType], item: DroneType) -> None:
        if item not in items:
            items.append(item)

    @staticmethod
    def _destination_authority(destination: str) -> tuple[str, str]:
        parsed = urlsplit(destination)
        scheme = parsed.scheme.lower()
        hostname = (parsed.hostname or "").lower()
        if hostname:
            return scheme, hostname

        raw = destination.strip().lower()
        if "://" not in raw:
            authority = raw.split("/", 1)[0]
            authority = authority.split("?", 1)[0]
            authority = authority.split("#", 1)[0]
            authority = authority.split(":", 1)[0]
            return "", authority

        return scheme, ""


__all__ = [
    "DispatchOrder",
    "DispatchPolicy",
    "DroneType",
    "MissionBrief",
    "OrdPolicyEngine",
    "SensitivityClass",
    "TransportRequirement",
]
