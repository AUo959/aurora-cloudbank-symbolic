"""
Scenario Cache

Caching layer for simulation results with symbolic nodes and expiration.

Anchor: T1-QSS-002
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .schemas import ScenarioListItem, SimulationResult


class ScenarioCache:
    """
    Cache for simulation results with expiration and persistence.

    Provides fast access to recent simulation results and supports
    symbolic node storage for scenario genealogy tracking.
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_cache_size: int = 1000,
        default_ttl_hours: int = 24,
    ):
        """
        Initialize scenario cache.

        Args:
            cache_dir: Directory for persistent storage (None = memory only)
            max_cache_size: Maximum number of cached results
            default_ttl_hours: Default time-to-live for cache entries (hours)
        """
        self.cache_dir = cache_dir
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_cache_size = max_cache_size
        self.default_ttl_hours = default_ttl_hours

        # In-memory cache: {simulation_id: CacheEntry}
        self._cache: Dict[str, "CacheEntry"] = {}

        # Symbolic nodes for scenario relationships: {simulation_id: parent_ids}
        self._symbolic_nodes: Dict[str, List[str]] = {}

        # Load from disk if persistence enabled
        if self.cache_dir:
            self._load_from_disk()

    def set(
        self,
        result: SimulationResult,
        ttl_hours: Optional[int] = None,
        parent_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Cache simulation result.

        Args:
            result: SimulationResult to cache
            ttl_hours: Time-to-live in hours (None = use default)
            parent_ids: List of parent simulation IDs for genealogy
        """
        ttl = ttl_hours or self.default_ttl_hours
        expiration = datetime.now(timezone.utc) + timedelta(hours=ttl)

        entry = CacheEntry(
            result=result,
            created_at=datetime.now(timezone.utc),
            expires_at=expiration,
            access_count=0,
            last_accessed=datetime.now(timezone.utc),
        )

        self._cache[result.simulation_id] = entry

        # Store symbolic node relationships
        if parent_ids:
            self._symbolic_nodes[result.simulation_id] = parent_ids

        # Enforce cache size limit
        self._evict_if_needed()

        # Persist to disk if enabled
        if self.cache_dir:
            self._save_to_disk(result.simulation_id)

    def get(self, simulation_id: str) -> Optional[SimulationResult]:
        """
        Retrieve cached simulation result.

        Args:
            simulation_id: Simulation identifier

        Returns:
            SimulationResult if cached and not expired, else None
        """
        entry = self._cache.get(simulation_id)
        if not entry:
            # Try loading from disk if persistence enabled
            if self.cache_dir:
                entry = self._load_entry_from_disk(simulation_id)
                if entry:
                    self._cache[simulation_id] = entry

        if not entry:
            return None

        # Check expiration
        if datetime.now(timezone.utc) > entry.expires_at:
            self.delete(simulation_id)
            return None

        # Update access stats
        entry.access_count += 1
        entry.last_accessed = datetime.now(timezone.utc)

        return entry.result

    def delete(self, simulation_id: str) -> bool:
        """
        Delete cached simulation result.

        Args:
            simulation_id: Simulation identifier

        Returns:
            True if deleted, False if not found
        """
        if simulation_id in self._cache:
            del self._cache[simulation_id]

            # Remove symbolic node relationships
            if simulation_id in self._symbolic_nodes:
                del self._symbolic_nodes[simulation_id]

            # Delete from disk
            if self.cache_dir:
                cache_file = self.cache_dir / f"{simulation_id}.json"
                if cache_file.exists():
                    cache_file.unlink()

            return True

        return False

    def list_scenarios(
        self,
        scenario_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[ScenarioListItem]:
        """
        List cached scenarios with optional filtering.

        Args:
            scenario_type: Filter by scenario type (None = all)
            status: Filter by status (None = all)
            limit: Maximum number of results

        Returns:
            List of ScenarioListItem summaries
        """
        items = []

        for simulation_id, entry in self._cache.items():
            result = entry.result

            # Apply filters
            if scenario_type and result.scenario_type.value != scenario_type:
                continue
            if status and result.status != status:
                continue

            # Check expiration
            if datetime.now(timezone.utc) > entry.expires_at:
                continue

            items.append(
                ScenarioListItem(
                    simulation_id=result.simulation_id,
                    scenario_name=result.scenario_name,
                    scenario_type=result.scenario_type,
                    status=result.status,
                    start_time=result.start_time,
                    execution_time_seconds=result.execution_time_seconds,
                    tags=result.tags,
                )
            )

            if len(items) >= limit:
                break

        # Sort by start time (most recent first)
        items.sort(key=lambda x: x.start_time, reverse=True)

        return items

    def clear_expired(self) -> int:
        """
        Remove all expired cache entries.

        Returns:
            Number of entries removed
        """
        now = datetime.now(timezone.utc)
        expired_ids = [
            sim_id for sim_id, entry in self._cache.items() if now > entry.expires_at
        ]

        for sim_id in expired_ids:
            self.delete(sim_id)

        return len(expired_ids)

    def clear_all(self) -> int:
        """
        Clear entire cache.

        Returns:
            Number of entries removed
        """
        count = len(self._cache)

        self._cache.clear()
        self._symbolic_nodes.clear()

        # Clear disk cache
        if self.cache_dir:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()

        return count

    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics.

        Returns:
            Dict with cache metrics
        """
        now = datetime.now(timezone.utc)
        active_entries = [
            entry for entry in self._cache.values() if now <= entry.expires_at
        ]

        total_accesses = sum(entry.access_count for entry in active_entries)
        avg_access_count = total_accesses / len(active_entries) if active_entries else 0

        return {
            "total_entries": len(self._cache),
            "active_entries": len(active_entries),
            "expired_entries": len(self._cache) - len(active_entries),
            "total_accesses": total_accesses,
            "avg_access_count": avg_access_count,
            "max_cache_size": self.max_cache_size,
            "cache_utilization": len(self._cache) / self.max_cache_size,
            "symbolic_nodes": len(self._symbolic_nodes),
        }

    def get_scenario_genealogy(self, simulation_id: str) -> List[str]:
        """
        Get genealogy (parent chain) for a scenario.

        Args:
            simulation_id: Simulation identifier

        Returns:
            List of parent simulation IDs (oldest first)
        """
        genealogy = []
        current_id = simulation_id

        visited = set()  # Prevent cycles

        while current_id in self._symbolic_nodes and current_id not in visited:
            visited.add(current_id)
            parents = self._symbolic_nodes[current_id]

            if not parents:
                break

            # Take first parent (could extend to handle multiple parents)
            current_id = parents[0]
            genealogy.insert(0, current_id)

        return genealogy

    def _evict_if_needed(self) -> None:
        """Evict least recently accessed entries if cache is full."""
        if len(self._cache) <= self.max_cache_size:
            return

        # Sort by last access time (oldest first)
        entries_by_access = sorted(
            self._cache.items(), key=lambda x: x[1].last_accessed
        )

        # Remove oldest until under limit
        num_to_remove = len(self._cache) - self.max_cache_size
        for i in range(num_to_remove):
            sim_id, _ = entries_by_access[i]
            self.delete(sim_id)

    def _save_to_disk(self, simulation_id: str) -> None:
        """Save cache entry to disk."""
        if not self.cache_dir:
            return

        entry = self._cache.get(simulation_id)
        if not entry:
            return

        cache_file = self.cache_dir / f"{simulation_id}.json"

        data = {
            "result": entry.result.model_dump(mode="json"),
            "created_at": entry.created_at.isoformat(),
            "expires_at": entry.expires_at.isoformat(),
            "access_count": entry.access_count,
            "last_accessed": entry.last_accessed.isoformat(),
            "symbolic_parents": self._symbolic_nodes.get(simulation_id, []),
        }

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

    def _load_entry_from_disk(self, simulation_id: str) -> Optional["CacheEntry"]:
        """Load cache entry from disk."""
        if not self.cache_dir:
            return None

        cache_file = self.cache_dir / f"{simulation_id}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)

            result = SimulationResult(**data["result"])
            entry = CacheEntry(
                result=result,
                created_at=datetime.fromisoformat(data["created_at"]),
                expires_at=datetime.fromisoformat(data["expires_at"]),
                access_count=data["access_count"],
                last_accessed=datetime.fromisoformat(data["last_accessed"]),
            )

            # Restore symbolic node relationships
            if "symbolic_parents" in data:
                self._symbolic_nodes[simulation_id] = data["symbolic_parents"]

            return entry

        except Exception as e:
            print(f"Warning: Failed to load cache entry {simulation_id}: {e}")
            return None

    def _load_from_disk(self) -> None:
        """Load all cache entries from disk."""
        if not self.cache_dir:
            return

        for cache_file in self.cache_dir.glob("*.json"):
            simulation_id = cache_file.stem
            entry = self._load_entry_from_disk(simulation_id)
            if entry:
                self._cache[simulation_id] = entry


class CacheEntry:
    """Cache entry with metadata."""

    def __init__(
        self,
        result: SimulationResult,
        created_at: datetime,
        expires_at: datetime,
        access_count: int,
        last_accessed: datetime,
    ):
        """
        Initialize cache entry.

        Args:
            result: Simulation result
            created_at: Creation timestamp
            expires_at: Expiration timestamp
            access_count: Number of accesses
            last_accessed: Last access timestamp
        """
        self.result = result
        self.created_at = created_at
        self.expires_at = expires_at
        self.access_count = access_count
        self.last_accessed = last_accessed


# Global cache instance
_cache: Optional[ScenarioCache] = None


def get_cache() -> ScenarioCache:
    """
    Get global scenario cache instance.

    Returns:
        ScenarioCache singleton
    """
    global _cache
    if _cache is None:
        # Default to memory-only cache (can be reconfigured)
        _cache = ScenarioCache(cache_dir=None, max_cache_size=1000, default_ttl_hours=24)
    return _cache


def initialize_cache(
    cache_dir: Optional[Path] = None,
    max_cache_size: int = 1000,
    default_ttl_hours: int = 24,
) -> ScenarioCache:
    """
    Initialize global scenario cache with custom settings.

    Args:
        cache_dir: Directory for persistent storage
        max_cache_size: Maximum number of cached results
        default_ttl_hours: Default TTL in hours

    Returns:
        Initialized ScenarioCache
    """
    global _cache
    _cache = ScenarioCache(
        cache_dir=cache_dir, max_cache_size=max_cache_size, default_ttl_hours=default_ttl_hours
    )
    return _cache
