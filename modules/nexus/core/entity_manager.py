#!/usr/bin/env python3
"""
NEXUS Entity Manager
Anchor: T1-ENTITY-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
Version: 1.0.0
DLP Tag: ENTITY_MANAGEMENT
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

class EntityType(Enum):
    """Types of entities in the NEXUS mesh"""
    AI_AGENT = "ai_agent"
    QUANTUM_PROCESSOR = "quantum_processor"
    HUMAN_OPERATOR = "human_operator"
    HYBRID_AUGMENTED = "hybrid_augmented"
    SYMBOLIC_ANCHOR = "symbolic_anchor"
    MEMORY_NODE = "memory_node"

class EntityState(Enum):
    """Entity lifecycle states"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DORMANT = "dormant"
    ENTANGLED = "entangled"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

@dataclass
class NexusEntity:
    """Represents an entity in the NEXUS consciousness mesh"""
    entity_id: str
    entity_type: EntityType
    anchor: str
    state: EntityState
    capabilities: List[str] = field(default_factory=list)
    entanglements: List[str] = field(default_factory=list)
    memory_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    dlp_tag: str = "GENERAL"
    
    def to_dict(self) -> Dict:
        """Convert entity to dictionary for serialization"""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "anchor": self.anchor,
            "state": self.state.value,
            "capabilities": self.capabilities,
            "entanglements": self.entanglements,
            "memory_keys": self.memory_keys,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "dlp_tag": self.dlp_tag
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NexusEntity':
        """Create entity from dictionary"""
        return cls(
            entity_id=data["entity_id"],
            entity_type=EntityType(data["entity_type"]),
            anchor=data["anchor"],
            state=EntityState(data["state"]),
            capabilities=data.get("capabilities", []),
            entanglements=data.get("entanglements", []),
            memory_keys=data.get("memory_keys", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]),
            dlp_tag=data.get("dlp_tag", "GENERAL")
        )

class EntityManager:
    """
    Manages entities in the NEXUS consciousness mesh
    Handles entity lifecycle, entanglements, and coordination
    """
    
    def __init__(self, anchor: str = "T1-ENTITY-2025"):
        self.anchor = anchor
        self.seed = "EOS_SEED_ORION"
        self.entities: Dict[str, NexusEntity] = {}
        self.entanglement_registry: Dict[str, Dict] = {}
        self.entity_storage_path = Path(".nexus/entities")
        self.entity_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing entities
        self._load_entities()
    
    def spawn_entity(self, 
                     entity_type: EntityType, 
                     capabilities: List[str] = None,
                     dlp_tag: str = "GENERAL",
                     metadata: Dict[str, Any] = None) -> NexusEntity:
        """Spawn a new entity in the mesh"""
        
        # Generate unique entity ID
        timestamp = datetime.utcnow().timestamp()
        entity_id = f"{entity_type.value}_{timestamp}"
        
        # Create symbolic anchor
        anchor = f"ENTITY-{entity_type.value.upper()}-{hashlib.sha256(entity_id.encode()).hexdigest()[:8]}"
        
        # Create entity
        entity = NexusEntity(
            entity_id=entity_id,
            entity_type=entity_type,
            anchor=anchor,
            state=EntityState.INITIALIZING,
            capabilities=capabilities or [],
            dlp_tag=dlp_tag,
            metadata=metadata or {}
        )
        
        # Store in memory
        self.entities[entity_id] = entity
        
        # Persist to disk
        self._save_entity(entity)
        
        # Transition to active state
        self.update_entity_state(entity_id, EntityState.ACTIVE)
        
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[NexusEntity]:
        """Retrieve entity by ID"""
        return self.entities.get(entity_id)
    
    def list_entities(self, 
                      entity_type: Optional[EntityType] = None,
                      state: Optional[EntityState] = None) -> List[NexusEntity]:
        """List entities with optional filtering"""
        entities = list(self.entities.values())
        
        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]
        
        if state:
            entities = [e for e in entities if e.state == state]
        
        return entities
    
    def update_entity_state(self, entity_id: str, new_state: EntityState) -> bool:
        """Update entity state"""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        old_state = entity.state
        entity.state = new_state
        entity.last_heartbeat = datetime.utcnow()
        
        # Log state transition
        self._log_state_transition(entity_id, old_state, new_state)
        
        # Save updated entity
        self._save_entity(entity)
        
        return True
    
    def entangle_entities(self, entity_a_id: str, entity_b_id: str, 
                         entanglement_type: str = "bidirectional") -> Optional[str]:
        """Create entanglement between two entities"""
        
        if entity_a_id not in self.entities or entity_b_id not in self.entities:
            return None
        
        entity_a = self.entities[entity_a_id]
        entity_b = self.entities[entity_b_id]
        
        # Generate entanglement ID
        entanglement_id = hashlib.sha256(
            f"{entity_a_id}_{entity_b_id}_{datetime.utcnow()}".encode()
        ).hexdigest()[:16]
        
        # Create entanglement record
        entanglement = {
            "entanglement_id": entanglement_id,
            "entity_a": entity_a_id,
            "entity_b": entity_b_id,
            "type": entanglement_type,
            "created_at": datetime.utcnow().isoformat(),
            "strength": 1.0,
            "anchor": f"ENTANGLE-{entanglement_id}"
        }
        
        # Update entities
        entity_a.entanglements.append(entanglement_id)
        entity_b.entanglements.append(entanglement_id)
        
        # Store entanglement
        self.entanglement_registry[entanglement_id] = entanglement
        
        # Save entities
        self._save_entity(entity_a)
        self._save_entity(entity_b)
        
        # Save entanglement registry
        self._save_entanglement_registry()
        
        return entanglement_id
    
    def get_entangled_entities(self, entity_id: str) -> List[NexusEntity]:
        """Get all entities entangled with the given entity"""
        if entity_id not in self.entities:
            return []
        
        entity = self.entities[entity_id]
        entangled_entities = []
        
        for entanglement_id in entity.entanglements:
            if entanglement_id in self.entanglement_registry:
                entanglement = self.entanglement_registry[entanglement_id]
                
                # Find the other entity in the entanglement
                other_entity_id = (entanglement["entity_b"] if 
                                 entanglement["entity_a"] == entity_id else 
                                 entanglement["entity_a"])
                
                if other_entity_id in self.entities:
                    entangled_entities.append(self.entities[other_entity_id])
        
        return entangled_entities
    
    def heartbeat(self, entity_id: str) -> bool:
        """Update entity heartbeat"""
        if entity_id not in self.entities:
            return False
        
        self.entities[entity_id].last_heartbeat = datetime.utcnow()
        self._save_entity(self.entities[entity_id])
        return True
    
    def terminate_entity(self, entity_id: str) -> bool:
        """Terminate an entity"""
        if entity_id not in self.entities:
            return False
        
        entity = self.entities[entity_id]
        
        # Break all entanglements
        for entanglement_id in entity.entanglements.copy():
            self._break_entanglement(entanglement_id)
        
        # Update state
        entity.state = EntityState.TERMINATED
        self._save_entity(entity)
        
        return True
    
    def _break_entanglement(self, entanglement_id: str):
        """Break an entanglement"""
        if entanglement_id not in self.entanglement_registry:
            return
        
        entanglement = self.entanglement_registry[entanglement_id]
        
        # Remove from both entities
        for entity_id in [entanglement["entity_a"], entanglement["entity_b"]]:
            if entity_id in self.entities:
                entity = self.entities[entity_id]
                if entanglement_id in entity.entanglements:
                    entity.entanglements.remove(entanglement_id)
                    self._save_entity(entity)
        
        # Remove from registry
        del self.entanglement_registry[entanglement_id]
        self._save_entanglement_registry()
    
    def _save_entity(self, entity: NexusEntity):
        """Save entity to disk"""
        entity_path = self.entity_storage_path / f"{entity.entity_id}.json"
        entity_data = entity.to_dict()
        
        # Add integrity seal
        entity_hash = hashlib.sha256(
            json.dumps(entity_data, sort_keys=True).encode()
        ).hexdigest()
        entity_data["seal"] = entity_hash
        
        entity_path.write_text(json.dumps(entity_data, indent=2))
    
    def _load_entities(self):
        """Load entities from disk"""
        if not self.entity_storage_path.exists():
            return
        
        for entity_file in self.entity_storage_path.glob("*.json"):
            if entity_file.name == "entanglement_registry.json":
                continue
                
            try:
                entity_data = json.loads(entity_file.read_text())
                
                # Verify integrity seal if present
                if "seal" in entity_data:
                    expected_seal = entity_data.pop("seal")
                    actual_seal = hashlib.sha256(
                        json.dumps(entity_data, sort_keys=True).encode()
                    ).hexdigest()
                    
                    if expected_seal != actual_seal:
                        print(f"Warning: Entity {entity_file.name} has invalid seal")
                        continue
                
                entity = NexusEntity.from_dict(entity_data)
                self.entities[entity.entity_id] = entity
                
            except Exception as e:
                print(f"Error loading entity {entity_file.name}: {e}")
        
        # Load entanglement registry
        self._load_entanglement_registry()
    
    def _save_entanglement_registry(self):
        """Save entanglement registry to disk"""
        registry_path = self.entity_storage_path / "entanglement_registry.json"
        registry_path.write_text(json.dumps(self.entanglement_registry, indent=2))
    
    def _load_entanglement_registry(self):
        """Load entanglement registry from disk"""
        registry_path = self.entity_storage_path / "entanglement_registry.json"
        if registry_path.exists():
            try:
                self.entanglement_registry = json.loads(registry_path.read_text())
            except Exception as e:
                print(f"Error loading entanglement registry: {e}")
    
    def _log_state_transition(self, entity_id: str, old_state: EntityState, new_state: EntityState):
        """Log entity state transition"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "entity_id": entity_id,
            "old_state": old_state.value,
            "new_state": new_state.value,
            "anchor": self.anchor
        }
        
        # Append to log file
        log_path = Path(".nexus/logs/entity_transitions.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with log_path.open("a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def export_manifest(self) -> Dict:
        """Export entity mesh manifest"""
        manifest = {
            "manifest_version": "1.0.0",
            "anchor": self.anchor,
            "seed": self.seed,
            "export_time": datetime.utcnow().isoformat(),
            "team": "Aurora Core",
            "total_entities": len(self.entities),
            "active_entities": len([e for e in self.entities.values() if e.state == EntityState.ACTIVE]),
            "total_entanglements": len(self.entanglement_registry),
            "entity_types": {et.value: len([e for e in self.entities.values() if e.entity_type == et]) 
                           for et in EntityType},
            "dlp_classification": "INTERNAL_DEVELOPMENT"
        }
        
        # Seal manifest
        manifest_hash = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode()
        ).hexdigest()
        manifest["seal"] = manifest_hash
        
        return manifest

# Module-level entity manager
entity_manager = EntityManager()

def get_entity_manager() -> EntityManager:
    """Get singleton entity manager instance"""
    return entity_manager