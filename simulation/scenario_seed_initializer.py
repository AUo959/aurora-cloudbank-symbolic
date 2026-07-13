"""Adapter for root L2 scenario seed uptake packets.

This module consumes the root control-plane ``simulation_initializer`` payload
shape and turns it into a validated CloudBank-side initialization object. It
does not execute a simulation, promote canon, or convert observation categories
into required outcomes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


REQUIRED_RUNTIME_FREEDOMS = frozenset(
    {
        "agent_policy_variation",
        "knob_sweep_or_sensitivity_run",
        "exogenous_pressure_variation",
        "multi_outcome_branch_observation",
        "post_run_narrative_rendering",
    }
)

PROHIBITED_SEMANTIC_KEYS = frozenset(
    {
        "forced_winner",
        "scripted_outcome",
        "single_required_ending",
        "required_ending",
        "canonical_outcome",
        "canon_fact_by_seed",
        "runtime_mutation_by_seed",
    }
)


class ScenarioSeedInitializationError(ValueError):
    """Raised when an uptake packet cannot initialize a scenario seed."""


@dataclass(frozen=True)
class ScenarioSeedSimulationInitializer:
    """Validated simulation initializer state derived from a root packet."""

    source_card_id: str
    seed: int
    ticks: int
    anchor_seed: str
    roles: tuple[str, ...]
    pressure_axes: tuple[str, ...]
    knobs: dict[str, str]
    runtime_freedoms: tuple[str, ...]
    expected_end_state_handling: str

    def to_initial_state(self) -> dict[str, Any]:
        """Return the narrow runtime initialization shape."""

        return {
            "source_card_id": self.source_card_id,
            "seed": self.seed,
            "ticks": self.ticks,
            "anchor_seed": self.anchor_seed,
            "initial_condition_vector": {
                "roles": list(self.roles),
                "pressure": list(self.pressure_axes),
                "knobs": dict(self.knobs),
            },
            "runtime_freedoms": list(self.runtime_freedoms),
            "expected_end_state_handling": self.expected_end_state_handling,
        }


def initialize_from_uptake_packet(packet: Mapping[str, Any]) -> ScenarioSeedSimulationInitializer:
    """Build a CloudBank initializer from a root uptake packet.

    ``packet`` may be the whole uptake packet or the nested
    ``consumer_payloads.simulation_initializer`` object. Whole packets must
    preserve the root boundary assertions that prohibit nested writes and direct
    canon promotion.
    """

    source_card_id = _source_card_id(packet)
    simulation_payload = _simulation_payload(packet)
    _assert_boundary(packet)
    _reject_prohibited_keys(simulation_payload)

    vector = _mapping(simulation_payload.get("initial_condition_vector"), "initial_condition_vector")
    roles = _string_tuple(vector.get("roles"), "initial_condition_vector.roles", minimum=4)
    pressure = _string_tuple(vector.get("pressure"), "initial_condition_vector.pressure", minimum=2)
    knobs = _string_mapping(vector.get("knobs"), "initial_condition_vector.knobs", minimum=5)
    runtime_freedoms = _string_tuple(
        simulation_payload.get("runtime_freedoms"),
        "runtime_freedoms",
        minimum=len(REQUIRED_RUNTIME_FREEDOMS),
    )

    missing_freedoms = REQUIRED_RUNTIME_FREEDOMS.difference(runtime_freedoms)
    if missing_freedoms:
        raise ScenarioSeedInitializationError(
            "runtime_freedoms missing required freedom(s): " + ", ".join(sorted(missing_freedoms))
        )

    expected_handling = _string(simulation_payload.get("expected_end_state_handling"), "expected_end_state_handling")
    if "observation categories" not in expected_handling:
        raise ScenarioSeedInitializationError(
            "expected_end_state_handling must preserve observation-category semantics"
        )

    return ScenarioSeedSimulationInitializer(
        source_card_id=source_card_id,
        seed=_positive_int(simulation_payload.get("seed"), "seed"),
        ticks=_positive_int(simulation_payload.get("ticks"), "ticks"),
        anchor_seed=_string(simulation_payload.get("anchor_seed"), "anchor_seed"),
        roles=roles,
        pressure_axes=pressure,
        knobs=knobs,
        runtime_freedoms=runtime_freedoms,
        expected_end_state_handling=expected_handling,
    )


def _source_card_id(packet: Mapping[str, Any]) -> str:
    value = packet.get("source_card_id")
    if isinstance(value, str) and value:
        return value
    return _string(packet.get("source_card_id", "unknown"), "source_card_id")


def _simulation_payload(packet: Mapping[str, Any]) -> Mapping[str, Any]:
    consumer_payloads = packet.get("consumer_payloads")
    if isinstance(consumer_payloads, Mapping):
        return _mapping(consumer_payloads.get("simulation_initializer"), "consumer_payloads.simulation_initializer")
    return packet


def _assert_boundary(packet: Mapping[str, Any]) -> None:
    boundary = packet.get("boundary_assertions")
    if boundary is None:
        return
    boundary_map = _mapping(boundary, "boundary_assertions")
    if boundary_map.get("writes_nested_repos") is not False:
        raise ScenarioSeedInitializationError("packet must not authorize nested repo writes")
    if boundary_map.get("canonrec_promotion") != "not_authorized_by_this_packet":
        raise ScenarioSeedInitializationError("packet must not authorize CanonRec promotion")


def _reject_prohibited_keys(value: Any) -> None:
    keys = _iter_keys(value)
    prohibited = PROHIBITED_SEMANTIC_KEYS.intersection(keys)
    if prohibited:
        raise ScenarioSeedInitializationError(
            "simulation_initializer contains prohibited semantic key(s): " + ", ".join(sorted(prohibited))
        )


def _iter_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            keys.add(str(key))
            keys.update(_iter_keys(item))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            keys.update(_iter_keys(item))
    return keys


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ScenarioSeedInitializationError(f"{field} must be an object")
    return value


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScenarioSeedInitializationError(f"{field} must be a non-empty string")
    return value


def _positive_int(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ScenarioSeedInitializationError(f"{field} must be a positive integer")
    return value


def _string_tuple(value: Any, field: str, minimum: int) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise ScenarioSeedInitializationError(f"{field} must be a list of strings")
    result = tuple(_string(item, field) for item in value)
    if len(result) < minimum:
        raise ScenarioSeedInitializationError(f"{field} must contain at least {minimum} item(s)")
    return result


def _string_mapping(value: Any, field: str, minimum: int) -> dict[str, str]:
    mapping = _mapping(value, field)
    result = {_string(key, field): _string(item, field) for key, item in mapping.items()}
    if len(result) < minimum:
        raise ScenarioSeedInitializationError(f"{field} must contain at least {minimum} item(s)")
    return result
