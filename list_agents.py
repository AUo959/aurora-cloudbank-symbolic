#!/usr/bin/env python3
"""List all crew agents by ID."""

# Import and initialize all agents
from src.agents.crew import (
    get_all_crew_agents,
    get_thorne, get_markov, get_roberts, get_qin, get_chen, get_noor,
    get_velin, get_shepard, get_lin, get_vu, get_sato, get_vell,
    get_porter, get_tanaka_j, get_feldman, get_patel, get_sorensen,
    get_vasquez, get_martinez, get_patel_ryan, get_okada, get_zhao,
    get_menon, get_kale, get_rivas, get_koss, get_kyros, get_drev,
    get_park, get_suresh, get_halden, get_vatra,
    get_nguyen, get_lee, get_el_sayegh,
)

# Initialize all agents
for getter in [
    get_thorne, get_markov, get_roberts, get_qin, get_chen, get_noor,
    get_velin, get_shepard, get_lin, get_vu, get_sato, get_vell,
    get_porter, get_tanaka_j, get_feldman, get_patel, get_sorensen,
    get_vasquez, get_martinez, get_patel_ryan, get_okada, get_zhao,
    get_menon, get_kale, get_rivas, get_koss, get_kyros, get_drev,
    get_park, get_suresh, get_halden, get_vatra,
    get_nguyen, get_lee, get_el_sayegh,
]:
    getter()

agents = get_all_crew_agents()
print(f'Total agents: {len(agents)}\n')

print('By agent_id:')
for surname, agent in sorted(agents.items(), key=lambda x: x[1].agent_id):
    print(f'{agent.agent_id:12} {agent.full_name:30} ({surname})')

# Check for duplicates
ids = [agent.agent_id for agent in agents.values()]
duplicates = set([id for id in ids if ids.count(id) > 1])
if duplicates:
    print(f'\n⚠️  DUPLICATE IDs FOUND: {duplicates}')
    for dup_id in duplicates:
        print(f'  {dup_id}:')
        for surname, agent in agents.items():
            if agent.agent_id == dup_id:
                print(f'    - {agent.full_name} ({surname})')
