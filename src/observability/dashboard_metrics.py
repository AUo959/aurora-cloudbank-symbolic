"""Read-only dashboard snapshot assembled from the running process."""
from datetime import datetime, timezone

import psutil

from src.agents.crew.base_agent import get_all_crew_agents
from src.monitoring.metrics_pusher import get_pusher

try:
    from modules.aumemmanager.api_integration import memory_manager
except ImportError:
    memory_manager = None

try:
    from modules.quantum_simulator.api import active_simulations
    from modules.quantum_simulator.scenario_cache import get_cache
except ImportError:
    active_simulations = None
    get_cache = None


def _memory_metrics() -> dict:
    names = ("total_memories", "active_memories", "compressed_memories", "archived_memories")
    memory = memory_manager.get_metrics() if memory_manager is not None else {}
    return {name: memory.get(name) for name in names} | {"cache_hit_rate": None}


def _quantum_metrics() -> dict:
    if active_simulations is None or get_cache is None:
        return {"simulations_running": None, "total_simulations": None, "average_speedup": None}
    simulations = list(active_simulations.values())
    cache = get_cache()
    retained_ids = set(active_simulations).union(
        item.simulation_id for item in cache.list_scenarios(limit=cache.max_cache_size)
    )
    return {
        "simulations_running": sum(item.status in ("running", "pending") for item in simulations),
        "total_simulations": len(retained_ids),
        "average_speedup": None,
    }


def collect_dashboard_metrics() -> dict:
    """Return live counters, with null for measurements we do not collect."""
    agents = list(get_all_crew_agents().values())
    request_metrics = get_pusher().get_metrics()
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "memory": _memory_metrics(),
        "quantum": _quantum_metrics(),
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
