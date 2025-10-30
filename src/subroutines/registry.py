"""
Subroutine Registry System
===========================
Anchor: SUBROUTINE-REG-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Official subroutine authoring and tracking system for Aurora's neural net.
Provides versioning, provenance, dependency management, and execution monitoring.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class SubroutineStatus(Enum):
    """Subroutine lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class SubroutineCategory(Enum):
    """Subroutine functional categories"""
    VALIDATION = "validation"
    MONITORING = "monitoring"
    PROCESSING = "processing"
    INTEGRATION = "integration"
    UTILITY = "utility"
    EXECUTIVE = "executive"


@dataclass
class SubroutineAuthor:
    """Subroutine author information"""
    name: str
    team: str
    email: Optional[str] = None
    role: Optional[str] = None


@dataclass
class SubroutineDependency:
    """Subroutine dependency specification"""
    subroutine_id: str
    version_constraint: str  # e.g., ">=1.0.0", "^2.1.0"
    required: bool = True


@dataclass
class SubroutineExecution:
    """Record of subroutine execution"""
    execution_id: str
    timestamp: str
    inputs_hash: str
    outputs_hash: str
    success: bool
    duration_ms: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Subroutine:
    """
    Official Aurora subroutine specification.
    
    Represents a tracked, versioned, and monitored computational unit
    in Aurora's neural net.
    """
    # Core Identity
    id: str
    name: str
    version: str
    description: str
    
    # Authoring & Provenance
    author: SubroutineAuthor
    created_at: str
    updated_at: str
    status: SubroutineStatus
    category: SubroutineCategory
    
    # Code & Implementation
    module_path: str  # Python module path, e.g., "src.subroutines.reality_sim_monitor"
    class_name: str  # Class name, e.g., "RealitySimMonitor"
    entry_point: str  # Method name, e.g., "enforce_principles"
    
    # Dependencies & Integration
    dependencies: List[SubroutineDependency] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)  # e.g., ["telemetry", "registry"]
    
    # Documentation
    documentation_url: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    
    # Execution History
    executions: List[SubroutineExecution] = field(default_factory=list)
    total_executions: int = 0
    success_count: int = 0
    failure_count: int = 0
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # DLP Anchor
    dlp_anchor: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': {
                'name': self.author.name,
                'team': self.author.team,
                'email': self.author.email,
                'role': self.author.role
            },
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status.value,
            'category': self.category.value,
            'module_path': self.module_path,
            'class_name': self.class_name,
            'entry_point': self.entry_point,
            'dependencies': [
                {
                    'subroutine_id': dep.subroutine_id,
                    'version_constraint': dep.version_constraint,
                    'required': dep.required
                }
                for dep in self.dependencies
            ],
            'integrations': self.integrations,
            'documentation_url': self.documentation_url,
            'examples': self.examples,
            'total_executions': self.total_executions,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': self.success_rate,
            'tags': self.tags,
            'metadata': self.metadata,
            'dlp_anchor': self.dlp_anchor
        }

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_executions == 0:
            return 0.0
        return self.success_count / self.total_executions

    def record_execution(
        self,
        execution_id: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a subroutine execution"""
        execution = SubroutineExecution(
            execution_id=execution_id,
            timestamp=datetime.utcnow().isoformat(),
            inputs_hash=self._hash_data(inputs),
            outputs_hash=self._hash_data(outputs) if success else "",
            success=success,
            duration_ms=duration_ms,
            error=error,
            metadata=metadata or {}
        )
        
        self.executions.append(execution)
        self.total_executions += 1
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.updated_at = datetime.utcnow().isoformat()

    @staticmethod
    def _hash_data(data: Dict[str, Any]) -> str:
        """Generate hash of data for provenance"""
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]


class SubroutineRegistry:
    """
    Central registry for Aurora subroutines.
    
    Manages subroutine lifecycle, versioning, dependencies, and execution tracking.
    Integrates with DLP tracker for audit trails.
    """

    def __init__(self):
        self._subroutines: Dict[str, Subroutine] = {}
        self._by_category: Dict[SubroutineCategory, List[str]] = {
            category: [] for category in SubroutineCategory
        }
        self._execution_count = 0
        
        # Register built-in subroutines
        self._register_builtin_subroutines()

    def _register_builtin_subroutines(self):
        """Register Aurora's built-in subroutines"""
        # Register Reality Sim Monitor
        reality_sim = Subroutine(
            id="reality_sim_monitor",
            name="Reality Sim Monitor",
            version="1.0.0",
            description="Executive subroutine ensuring simulations align with reality maxim",
            author=SubroutineAuthor(
                name="AUo959-team",
                team="Aurora Core",
                role="System Architect"
            ),
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            status=SubroutineStatus.ACTIVE,
            category=SubroutineCategory.EXECUTIVE,
            module_path="src.subroutines.reality_sim_monitor",
            class_name="RealitySimMonitor",
            entry_point="enforce_principles",
            integrations=["telemetry", "registry", "audit_log"],
            tags=["reality", "validation", "provenance", "metrics"],
            dlp_anchor="SUBROUTINE-REALITY-SIM-001"
        )
        self.register(reality_sim)

    def register(self, subroutine: Subroutine) -> bool:
        """
        Register a new subroutine in the system.
        
        Args:
            subroutine: Subroutine specification
            
        Returns:
            True if registered successfully
        """
        if subroutine.id in self._subroutines:
            logger.warning("Subroutine already registered: %s", subroutine.id)
            return False
        
        # Validate dependencies
        for dep in subroutine.dependencies:
            if dep.required and dep.subroutine_id not in self._subroutines:
                logger.error(
                    "Missing required dependency '%s' for subroutine '%s'",
                    dep.subroutine_id,
                    subroutine.id
                )
                if dep.required:
                    return False
        
        self._subroutines[subroutine.id] = subroutine
        self._by_category[subroutine.category].append(subroutine.id)
        
        logger.info(
            "Registered subroutine '%s' v%s by %s",
            subroutine.id,
            subroutine.version,
            subroutine.author.name
        )
        return True

    def get(self, subroutine_id: str) -> Optional[Subroutine]:
        """Get subroutine by ID"""
        return self._subroutines.get(subroutine_id)

    def list_all(self) -> List[Subroutine]:
        """List all registered subroutines"""
        return list(self._subroutines.values())

    def list_by_category(self, category: SubroutineCategory) -> List[Subroutine]:
        """List subroutines by category"""
        ids = self._by_category.get(category, [])
        return [self._subroutines[sid] for sid in ids if sid in self._subroutines]

    def list_by_status(self, status: SubroutineStatus) -> List[Subroutine]:
        """List subroutines by status"""
        return [s for s in self._subroutines.values() if s.status == status]

    def update_status(self, subroutine_id: str, status: SubroutineStatus) -> bool:
        """Update subroutine status"""
        subroutine = self.get(subroutine_id)
        if not subroutine:
            logger.error("Subroutine not found: %s", subroutine_id)
            return False
        
        old_status = subroutine.status
        subroutine.status = status
        subroutine.updated_at = datetime.utcnow().isoformat()
        
        logger.info(
            "Updated subroutine '%s' status: %s -> %s",
            subroutine_id,
            old_status.value,
            status.value
        )
        return True

    def record_execution(
        self,
        subroutine_id: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record a subroutine execution"""
        subroutine = self.get(subroutine_id)
        if not subroutine:
            logger.error("Cannot record execution for unknown subroutine: %s", subroutine_id)
            return False
        
        self._execution_count += 1
        execution_id = f"{subroutine_id}_exec_{self._execution_count}"
        
        subroutine.record_execution(
            execution_id=execution_id,
            inputs=inputs,
            outputs=outputs,
            success=success,
            duration_ms=duration_ms,
            error=error,
            metadata=metadata
        )
        
        logger.info(
            "Recorded execution for '%s': success=%s, duration=%.2fms",
            subroutine_id,
            success,
            duration_ms
        )
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'total_subroutines': len(self._subroutines),
            'by_category': {
                cat.value: len(ids)
                for cat, ids in self._by_category.items()
            },
            'by_status': {
                status.value: len(self.list_by_status(status))
                for status in SubroutineStatus
            },
            'total_executions': self._execution_count,
            'active_subroutines': len(self.list_by_status(SubroutineStatus.ACTIVE))
        }

    def export_registry(self) -> Dict[str, Any]:
        """Export full registry state"""
        return {
            'registry_version': '1.0.0',
            'exported_at': datetime.utcnow().isoformat(),
            'subroutines': [s.to_dict() for s in self._subroutines.values()],
            'stats': self.get_stats()
        }

    def search(
        self,
        query: str,
        category: Optional[SubroutineCategory] = None,
        status: Optional[SubroutineStatus] = None,
        tags: Optional[List[str]] = None
    ) -> List[Subroutine]:
        """
        Search subroutines by query, category, status, or tags.
        
        Args:
            query: Search query (matches name, description, id)
            category: Filter by category
            status: Filter by status
            tags: Filter by tags (any match)
            
        Returns:
            List of matching subroutines
        """
        results = list(self._subroutines.values())
        
        # Filter by category
        if category:
            results = [s for s in results if s.category == category]
        
        # Filter by status
        if status:
            results = [s for s in results if s.status == status]
        
        # Filter by tags
        if tags:
            results = [
                s for s in results
                if any(tag in s.tags for tag in tags)
            ]
        
        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if (
                    query_lower in s.id.lower()
                    or query_lower in s.name.lower()
                    or query_lower in s.description.lower()
                )
            ]
        
        return results


# Global singleton
_registry: Optional[SubroutineRegistry] = None


def get_subroutine_registry() -> SubroutineRegistry:
    """Get global subroutine registry instance"""
    global _registry
    if _registry is None:
        _registry = SubroutineRegistry()
    return _registry
