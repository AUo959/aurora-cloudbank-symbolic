"""Phase 6 vector and EchoChain binding verification."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

import yaml

PHASE6_ANCHOR = "T6-EMERGENCE-2025"
SEED_ANCHOR = "EOS_SEED_ORION"
ETHICS_PROTOCOL = "Picard_Delta_3"
VECTOR_STATE = "QEM-SN1-ACTIVE::BASELINE_V1"
LOCKPOINT_REFERENCE = "SN1_LOCKPOINT_20250406T1432Z"
ECHOCHAIN_LOOPSET = "LOOPSET_001"
ECHOCHAIN_LINKS = ("NESTED_001_ECHO", "DRIFTTRACE::REI")
CONTRACT_PATH = Path(__file__).with_name("vector_binding.yaml")


@dataclass
class VectorBindingReceipt:
    """Verification receipt for the Phase 6 vector binding contract."""

    valid: bool
    contract_path: str
    checked_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    bindings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "contract_path": self.contract_path,
            "checked_files": self.checked_files,
            "errors": self.errors,
            "bindings": self.bindings,
        }


def load_vector_binding_contract(contract_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load the machine-readable Phase 6 vector binding contract."""
    path = Path(contract_path) if contract_path else CONTRACT_PATH
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError("Vector binding contract root must be a mapping.")
    return payload


def verify_phase6_vector_binding(
    repo_root: Optional[Path] = None,
    contract_path: Optional[Path] = None,
) -> VectorBindingReceipt:
    """Verify that Phase 6 vector identifiers are bound to runtime evidence."""
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    path = Path(contract_path) if contract_path else CONTRACT_PATH
    errors: List[str] = []
    checked_files: List[str] = []

    try:
        contract = load_vector_binding_contract(path)
        checked_files.append(_display_path(root, path))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return VectorBindingReceipt(
            valid=False,
            contract_path=str(path),
            errors=[f"Cannot load vector binding contract: {exc}"],
        )

    _expect(contract, "phase_anchor", PHASE6_ANCHOR, errors)
    _expect(contract, "seed_anchor", SEED_ANCHOR, errors)
    _expect(contract, "ethics_protocol", ETHICS_PROTOCOL, errors)
    _expect(contract, "vector_state", VECTOR_STATE, errors)
    _expect(contract, "lockpoint_reference", LOCKPOINT_REFERENCE, errors)
    _expect(contract.get("echochain", {}), "loopset", ECHOCHAIN_LOOPSET, errors)
    _expect_sequence(contract.get("echochain", {}), "linked", ECHOCHAIN_LINKS, errors)

    runtime_bindings = contract.get("runtime_bindings", {})
    if not isinstance(runtime_bindings, Mapping):
        errors.append("runtime_bindings must be a mapping.")
        runtime_bindings = {}

    checked_files.extend(_verify_runtime_bindings(root, runtime_bindings, errors))
    _verify_protocol_archive(root, runtime_bindings.get("protocol_archive"), errors, checked_files)

    bindings = {
        "phase_anchor": PHASE6_ANCHOR,
        "seed_anchor": SEED_ANCHOR,
        "ethics_protocol": ETHICS_PROTOCOL,
        "vector_state": VECTOR_STATE,
        "lockpoint_reference": LOCKPOINT_REFERENCE,
        "echochain": {
            "loopset": ECHOCHAIN_LOOPSET,
            "linked": list(ECHOCHAIN_LINKS),
        },
    }
    return VectorBindingReceipt(
        valid=not errors,
        contract_path=str(path),
        checked_files=checked_files,
        errors=errors,
        bindings=bindings,
    )


def startup_assert_phase6_vector_binding(repo_root: Optional[Path] = None) -> VectorBindingReceipt:
    """Raise if Phase 6 vector binding evidence is incomplete."""
    receipt = verify_phase6_vector_binding(repo_root=repo_root)
    if not receipt.valid:
        raise RuntimeError("; ".join(receipt.errors))
    return receipt


def _expect(source: Mapping[str, Any], key: str, expected: str, errors: List[str]) -> None:
    actual = source.get(key)
    if actual != expected:
        errors.append(f"{key} must be {expected}; found {actual!r}.")


def _expect_sequence(
    source: Mapping[str, Any],
    key: str,
    expected: Tuple[str, ...],
    errors: List[str],
) -> None:
    actual = source.get(key)
    if list(actual or []) != list(expected):
        errors.append(f"{key} must be {list(expected)!r}; found {actual!r}.")


def _verify_runtime_bindings(
    repo_root: Path,
    runtime_bindings: Mapping[str, Any],
    errors: List[str],
) -> List[str]:
    checked_files: List[str] = []
    for binding_name, binding_ref in runtime_bindings.items():
        if binding_name == "protocol_archive":
            continue
        if not isinstance(binding_ref, str):
            errors.append(f"{binding_name} binding must be a dotted Python reference.")
            continue
        module_path = _dotted_reference_to_path(repo_root, binding_ref)
        checked_files.append(_display_path(repo_root, module_path))
        if not module_path.exists():
            errors.append(f"{binding_name} binding path is missing: {_display_path(repo_root, module_path)}")
    return checked_files


def _verify_protocol_archive(
    repo_root: Path,
    protocol_archive: Any,
    errors: List[str],
    checked_files: List[str],
) -> None:
    if not isinstance(protocol_archive, str):
        errors.append("protocol_archive binding must be a repo-relative path.")
        return
    archive_path = repo_root / protocol_archive
    checked_files.append(_display_path(repo_root, archive_path))
    if not archive_path.exists():
        errors.append(f"protocol_archive is missing: {protocol_archive}")
        return
    with archive_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not _contains_value(payload, PHASE6_ANCHOR):
        errors.append(f"protocol_archive does not contain anchor {PHASE6_ANCHOR}.")


def _dotted_reference_to_path(repo_root: Path, dotted_reference: str) -> Path:
    parts = dotted_reference.split(".")
    module_parts = parts[:-1] if parts and parts[-1][:1].isupper() else parts
    return repo_root.joinpath(*module_parts).with_suffix(".py")


def _contains_value(payload: Any, expected: str) -> bool:
    if payload == expected:
        return True
    if isinstance(payload, Mapping):
        return any(_contains_value(value, expected) for value in payload.values())
    if isinstance(payload, list):
        return any(_contains_value(value, expected) for value in payload)
    return False


def _display_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


__all__ = [
    "ECHOCHAIN_LINKS",
    "ECHOCHAIN_LOOPSET",
    "ETHICS_PROTOCOL",
    "LOCKPOINT_REFERENCE",
    "PHASE6_ANCHOR",
    "SEED_ANCHOR",
    "VECTOR_STATE",
    "VectorBindingReceipt",
    "load_vector_binding_contract",
    "startup_assert_phase6_vector_binding",
    "verify_phase6_vector_binding",
]
