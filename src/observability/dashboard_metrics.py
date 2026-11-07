"""Read-only dashboard snapshot assembled from the running process."""
from datetime import datetime, timezone

import psutil

from modules.aumemmanager.api_integration import memory_manager
from modules.quantum_simulator.api import active_simulations
from modules.quantum_simulator.scenario_cache import get_cache
from src.agents.crew.base_agent import get_all_crew_agents
from src.monitoring.metrics_pusher import get_pusher


def collect_dashboard_metrics() -> dict:
    """Return live counters, with null for measurements we do not collect."""
    memory = memory_manager.get_metrics()
    agents = list(get_all_crew_agents().values())
    request_metrics = get_pusher().get_metrics()
    simulations = list(active_simulations.values())
    cache = get_cache()
    retained_ids = set(active_simulations).union(
        item.simulation_id for item in cache.list_scenarios(limit=cache.max_cache_size)
    )
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "memory": {
            name: memory[name] for name in (
                "total_memories", "active_memories", "compressed_memories", "archived_memories"
            )
        } | {"cache_hit_rate": None},
        "quantum": {
            "simulations_running": sum(item.status in ("running", "pending") for item in simulations),
            "total_simulations": len(retained_ids),
            "average_speedup": None,
        },
        "agents": {
            "total_agents": len(agents),
            "active_agents": sum(agent.status != "offline" for agent in agents),
            "total_tasks": sum(
                len(agent.active_tasks) + agent.stats["tasks_completed"] + agent.stats["tasks_failed"]
                for agent in agents
            ),
            "completed_tasks": sum(agent.stats["tasks_completed"] for agent in agents),
        },
        "system": {
            "cpu_usage": psutil.cpu_percent(interval=None),
            "memory_usage": psutil.virtual_memory().percent,
            "api_requests_per_minute": int(request_metrics.get("request_count", 0)),
            "average_response_time_ms": request_metrics.get("avg_latency_ms"),
        },
        "context_tag": "dashboard_metrics_snapshot",
    }
