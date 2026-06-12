"""ORD-Series Drone Fleet — governance-backed policy family.

The station's autonomous MCP validation layer (L1 Orion Station, security /
validation infrastructure):

- ORD-1 Gamma Swarm — response sanitization & error correction
- ORD-2 Delta Scout — pre-flight reconnaissance & threat assessment
- ORD-3 Shadowfax  — response inspection & quarantine decisions

This package is the policy layer (threshold registry, dispatch policy
engine, inspection policy, audit receipts). The fleet entity layer lives in
``src/entities/fleet`` (drone registry accessors). Specs: ``docs/ord/``.

Recovered from the ORION_ORD Promotion Workbench v0.5.0 (2026-03-10)
salvage; integrated 2026-06-12.
"""

from modules.ord.ord_inspection_policy import (
    InspectionInput,
    InspectionReport,
    OrdInspectionPolicy,
    QuarantineDecision,
    SanitizationAction,
)
from modules.ord.ord_policy_engine import (
    DispatchOrder,
    DispatchPolicy,
    DroneType,
    MissionBrief,
    OrdPolicyEngine,
    SensitivityClass,
    TransportRequirement,
)
from modules.ord.ord_receipts import canonical_json, canonical_sha256
from modules.ord.ord_threshold_registry import (
    EscalationRule,
    ThresholdRegistry,
    load_default_registry,
)

__all__ = [
    "DispatchOrder",
    "DispatchPolicy",
    "DroneType",
    "EscalationRule",
    "InspectionInput",
    "InspectionReport",
    "MissionBrief",
    "OrdInspectionPolicy",
    "OrdPolicyEngine",
    "QuarantineDecision",
    "SanitizationAction",
    "SensitivityClass",
    "ThresholdRegistry",
    "TransportRequirement",
    "canonical_json",
    "canonical_sha256",
    "load_default_registry",
]
