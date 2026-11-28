"""Deterministic Phase-11 control inputs.

Each variant is derived from the frozen control files by a fixed, declared
edit. Substitutions enter only as CanonRec-facing data (source set, identity
mapping, composition) and are resolved by the unchanged pinned CanonRec
resolver and T0 constructor. No engine code branches on the variant.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from simulation.runtime.canonrec_tactical.resolver import CanonRecTacticalResolver
from simulation.runtime.gumas_battle_orchestrator import (
    authority_doctrine_binding,
    initialize_run_context,
)
from simulation.runtime.gumas_movement_geometry.kernel import initialize_motion_state
from simulation.runtime.gumas_physical_t0.constructor import construct_t0_state

from .constants import (
    CLASS_SUBSTITUTION,
    POLITY_SUBSTITUTION,
    VARIANT_CLASS,
    VARIANT_CONTROL,
    VARIANT_POLITY,
    VARIANTS,
)
from .identity import Phase11Error, json_diff_paths, sha256_canonical

ROOT = Path(__file__).resolve().parents[3]
BASELINE = ROOT / (
    "simulation/baselines/gumas/GUMAS__BASELINE__FLASH_REBELLION_PLANETOID_EQUAL_FLEETS__v1.2__2026-08-11.json"
)
CALIBRATION = ROOT / (
    "simulation/calibration/gumas/GUMAS__CALIBRATION__CANONREC_TO_PHYSICAL_TACTICAL_STATE__v1.0__2026-08-13.json"
)
SOURCE_SET = ROOT / (
    "simulation/canon_snapshots/canonrec/CANONREC__SOURCE_SET__GUMAS_RUN0_PHASE2__v1.0__2026-08-12.json"
)

# Machine-checkable allowed-delta matrix over the three input documents.
# Any differing path outside a variant's allowed prefixes fails closed.
ALLOWED_INPUT_DELTAS: dict[str, dict[str, tuple[str, ...]]] = {
    VARIANT_CONTROL: {"baseline": (), "calibration": (), "source_set": ()},
    VARIANT_CLASS: {
        "baseline": ("/fleet_template/composition",),
        "calibration": (
            "/identity_mapping/baseline_class_to_canonrec/CLASS-BASTION-01",
            "/authority_boundary/control_manifest_sha256",
        ),
        "source_set": (),
    },
    VARIANT_POLITY: {
        "baseline": (),
        "calibration": (
            "/identity_mapping/organization_id",
            "/authority_boundary/control_manifest_sha256",
        ),
        "source_set": ("/sources",),
    },
}


@dataclass(frozen=True)
class ControlInputs:
    variant: str
    baseline: dict[str, Any]
    calibration: dict[str, Any]
    source_set: dict[str, Any]
    manifest: dict[str, Any]
    t0: dict[str, Any]
    initial_state: dict[str, Any]
    run_context: dict[str, Any]

    def identities(self) -> dict[str, str]:
        """The four identity layers the Phase-11 contract keeps separate."""
        return {
            "baseline_sha256": sha256_canonical(self.baseline),
            "calibration_sha256": sha256_canonical(self.calibration),
            "source_set_sha256": sha256_canonical(self.source_set),
            "canonrec_commit": str(self.source_set["canonrec_commit"]),
            "resolved_manifest_sha256": str(self.manifest["manifest_sha256"]),
            "authority_resolution_sha256": str(self.manifest["authority"]["resolution_sha256"]),
            "t0_sha256": str(self.t0["t0_sha256"]),
            "initial_state_sha256": str(self.initial_state["state_sha256"]),
            "t0_roster_sha256": str(self.run_context["t0_roster_sha256"]),
            "run_identity_sha256": str(self.run_context["run_identity_sha256"]),
        }


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def control_documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return _load(BASELINE), _load(CALIBRATION), _load(SOURCE_SET)


def _resolver_roster(baseline: Mapping[str, Any], calibration: Mapping[str, Any]) -> list[dict[str, Any]]:
    mapping = calibration["identity_mapping"]["baseline_class_to_canonrec"]
    return [
        {"class_id": mapping[item["class_id"]], "count": int(item["count"])}
        for item in baseline["fleet_template"]["composition"]
    ]


def derive_documents(variant: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Apply the declared variant edit to deep copies of the control documents.

    The calibration's ``control_manifest_sha256`` pin is re-bound later, after
    the pinned resolver has produced the variant manifest.
    """
    if variant not in VARIANTS:
        raise Phase11Error(f"unknown control variant: {variant}")
    baseline, calibration, source_set = (copy.deepcopy(doc) for doc in control_documents())
    if variant == VARIANT_CLASS:
        spec = CLASS_SUBSTITUTION
        composition = baseline["fleet_template"]["composition"]
        target = [item for item in composition if item["class_id"] == spec["remove_baseline_class_id"]]
        if len(target) != 1 or int(target[0]["count"]) <= int(spec["remove_count"]):
            raise Phase11Error("class substitution target is absent or too small")
        target[0]["count"] = int(target[0]["count"]) - int(spec["remove_count"])
        if any(item["class_id"] == spec["add"]["class_id"] for item in composition):
            raise Phase11Error("class substitution addition already present")
        composition.append(dict(spec["add"]))
        mapping = calibration["identity_mapping"]["baseline_class_to_canonrec"]
        mapping[spec["add"]["class_id"]] = spec["add_canonrec_class_id"]
    elif variant == VARIANT_POLITY:
        spec = POLITY_SUBSTITUTION
        if spec["source"] in source_set["sources"]:
            raise Phase11Error("polity substitution source already pinned")
        source_set["sources"].append(dict(spec["source"]))
        calibration["identity_mapping"]["organization_id"] = spec["authority_id"]
    return baseline, calibration, source_set


def check_input_deltas(variant: str, documents: Mapping[str, Mapping[str, Any]]) -> dict[str, list[str]]:
    """Fail closed unless every differing input path is allowed for the variant."""
    control = dict(zip(("baseline", "calibration", "source_set"), control_documents()))
    allowed = ALLOWED_INPUT_DELTAS[variant]
    observed: dict[str, list[str]] = {}
    for name in ("baseline", "calibration", "source_set"):
        paths = json_diff_paths(control[name], documents[name])
        for path in paths:
            if not any(path == prefix or path.startswith(prefix + "/") for prefix in allowed[name]):
                raise Phase11Error(f"forbidden {variant} input delta: {name}{path}")
        observed[name] = paths
    if variant != VARIANT_CONTROL and not any(observed.values()):
        raise Phase11Error(f"{variant} produced no input delta")
    return observed


def resolve_inputs(canonrec_root: Path, variant: str) -> ControlInputs:
    """Resolve one variant through the pinned CanonRec resolver and T0 constructor."""
    baseline, calibration, source_set = derive_documents(variant)
    resolver = CanonRecTacticalResolver(canonrec_root, source_set)
    manifest = resolver.resolve_roster(
        calibration["identity_mapping"]["organization_id"],
        _resolver_roster(baseline, calibration),
    )
    if variant == VARIANT_CONTROL:
        if manifest["manifest_sha256"] != calibration["authority_boundary"]["control_manifest_sha256"]:
            raise Phase11Error("control manifest differs from the accepted pin")
    else:
        calibration["authority_boundary"]["control_manifest_sha256"] = manifest["manifest_sha256"]
    check_input_deltas(
        variant,
        {"baseline": baseline, "calibration": calibration, "source_set": source_set},
    )
    t0 = construct_t0_state(baseline, calibration, manifest)
    initial_state = initialize_motion_state(t0)
    binding = authority_doctrine_binding(manifest)
    doctrine = {str(side): copy.deepcopy(binding) for side in sorted(baseline["sides"])}
    run_context = initialize_run_context(t0, initial_state, baseline, authority_doctrine_by_side=doctrine)
    return ControlInputs(
        variant=variant,
        baseline=baseline,
        calibration=calibration,
        source_set=source_set,
        manifest=manifest,
        t0=t0,
        initial_state=initial_state,
        run_context=run_context,
    )
