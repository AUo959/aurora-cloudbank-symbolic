"""A two-choice, synthetic L2 corridor crisis for cross-scale acceptance.

No character, institution, event or territory here is asserted to be canon.
"""
from __future__ import annotations

from .kernel import CausalEngine
from .model import Actor, Corridor, Site, Universe


def fixture() -> Universe:
    return Universe(
        time_s=0,
        sites={
            "union_depot": Site("union_depot", "fixture_union",
                                {"rations": 20, "energy_j": 100000}),
            "frontier_port": Site("frontier_port", "fixture_frontier",
                                  {"rations": 3, "energy_j": 10000}),
        },
        actors={
            "governor": Actor("governor", "union_depot", ("union_depot",)),
            "observer": Actor("observer", "frontier_port"),
            "local_dissenter": Actor("local_dissenter", "union_depot"),
        },
        corridors={
            "corridor_a": Corridor(
                "corridor_a", "union_depot", "frontier_port",
                distance_km=1200, cargo_speed_km_s=100,
                signal_speed_km_s=300, capacity_units_per_window=6,
                window_seconds=60,
                shipment_energy_j_per_unit_km=1,
                signal_energy_j_per_km=1,
            )
        },
    )


def run_experiment(*, governor_choice: str = "dispatch") -> dict:
    if governor_choice not in ("dispatch", "hold"):
        raise ValueError("unsupported experimental choice")
    engine = CausalEngine(fixture(), run_id=f"synthetic-corridor-{governor_choice}")
    engine.disrupt_route("corridor_a", 4, cause="fixture:corridor-disruption")
    if governor_choice == "dispatch":
        engine.dispatch("governor", "corridor_a", "rations", 3,
                        cause="actor:governor-choice")
    engine.send_report("governor", "observer", "corridor_a",
                       f"Governor chose: {governor_choice}",
                       cause="actor:governor-report")
    at_departure = {
        "origin": engine.site_view("union_depot"),
        "destination": engine.site_view("frontier_port"),
        "origin_polity": engine.polity_view("fixture_union"),
        "destination_polity": engine.polity_view("fixture_frontier"),
        "observer": engine.actor_view("observer"),
    }
    engine.advance_to(3)
    before_signal = engine.actor_view("observer")
    engine.advance_to(4)
    after_signal = engine.actor_view("observer")
    engine.advance_to(12)
    after_cargo = {
        "origin": engine.site_view("union_depot"),
        "destination": engine.site_view("frontier_port"),
        "origin_polity": engine.polity_view("fixture_union"),
        "destination_polity": engine.polity_view("fixture_frontier"),
        "observer": engine.actor_view("observer"),
    }
    return {
        "choice": governor_choice,
        "departure": at_departure,
        "before_signal": before_signal,
        "after_signal": after_signal,
        "arrival": after_cargo,
        "evidence": engine.evidence(),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment(), indent=2, sort_keys=True))
