"""
Symbolic Thread Manager for Aurora Memory Sealing Integration
Manages thread preservation, rehydration, and validation cycles
"""

import time
import hashlib
import pickle
from typing import Dict, List, Any, Optional, Tuple, Set
from enum import Enum

try:
    from ...core.native_symbolic_anchor import NativeMemorySealer
except ImportError:
    try:
        from src.core.native_symbolic_anchor import NativeMemorySealer
    except ImportError:
        # Fallback implementation
        class NativeMemorySealer:
            def __init__(self):
                self.sealed_states = {}
                self.integrity_checks = {}
            
            def seal_state(self, state_id, state_data):
                state_str = str(state_data)
                integrity_hash = hashlib.sha256(state_str.encode()).hexdigest()
                self.sealed_states[state_id] = {
                    'state_id': state_id,
                    'data': state_data,
                    'seal_timestamp': time.time(),
                    'integrity_hash': integrity_hash
                }
                return integrity_hash
            
            def unseal_state(self, state_id):
                if state_id not in self.sealed_states:
                    return None
                return self.sealed_states[state_id]['data']
            
            def verify_integrity(self, state_id):
                return state_id in self.sealed_states


class ThreadState(Enum):
    """Thread lifecycle states"""
    ACTIVE = "active"
    PRESERVED = "preserved"
    SEALED = "sealed"
    REHYDRATING = "rehydrating"
    CORRUPTED = "corrupted"
    ARCHIVED = "archived"


class ThreadPriority(Enum):
    """Thread preservation priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    ARCHIVAL = "archival"


class SymbolicThread:
    """Represents a symbolic computation thread with preservation capabilities"""
    
    def __init__(self, thread_id: str, thread_type: str = "symbolic", priority: ThreadPriority = ThreadPriority.NORMAL):
        self.thread_id = thread_id
        self.thread_type = thread_type
        self.priority = priority
        self.state = ThreadState.ACTIVE
        
        # Thread data
        self.thread_data: Dict[str, Any] = {}
        self.execution_context: Dict[str, Any] = {}
        self.computation_history: List[Dict[str, Any]] = []
        
        # Preservation metadata
        self.creation_timestamp = time.time()
        self.last_activity_timestamp = time.time()
        self.preservation_timestamp: Optional[float] = None
        self.rehydration_timestamp: Optional[float] = None
        
        # Integrity tracking
        self.integrity_hash: Optional[str] = None
        self.validation_history: List[Dict[str, Any]] = []
        
        # Dependencies and relationships
        self.dependencies: Set[str] = set()
        self.dependents: Set[str] = set()
        
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity_timestamp = time.time()
    
    def add_computation(self, computation_data: Dict[str, Any]):
        """Add computation step to thread history"""
        self.computation_history.append({
            'timestamp': time.time(),
            'data': computation_data,
            'step_id': len(self.computation_history)
        })
        self.update_activity()
    
    def add_dependency(self, thread_id: str):
        """Add dependency on another thread"""
        self.dependencies.add(thread_id)
    
    def add_dependent(self, thread_id: str):
        """Add dependent thread"""
        self.dependents.add(thread_id)
    
    def calculate_integrity_hash(self) -> str:
        """Calculate integrity hash for thread data"""
        thread_snapshot = {
            'thread_id': self.thread_id,
            'thread_type': self.thread_type,
            'thread_data': self.thread_data,
            'execution_context': self.execution_context,
            'computation_history': self.computation_history,
            'dependencies': sorted(list(self.dependencies)),
            'dependents': sorted(list(self.dependents))
        }
        
        thread_bytes = pickle.dumps(thread_snapshot, protocol=pickle.HIGHEST_PROTOCOL)
        return hashlib.sha256(thread_bytes).hexdigest()
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get thread metadata"""
        return {
            'thread_id': self.thread_id,
            'thread_type': self.thread_type,
            'priority': self.priority.value,
            'state': self.state.value,
            'creation_timestamp': self.creation_timestamp,
            'last_activity_timestamp': self.last_activity_timestamp,
            'preservation_timestamp': self.preservation_timestamp,
            'rehydration_timestamp': self.rehydration_timestamp,
            'computation_steps': len(self.computation_history),
            'dependencies_count': len(self.dependencies),
            'dependents_count': len(self.dependents),
            'integrity_hash': self.integrity_hash
        }


class SymbolicThreadManager:
    """Advanced thread manager with preservation and rehydration capabilities"""
    
    def __init__(self, memory_sealer: Optional[NativeMemorySealer] = None):
        self.memory_sealer = memory_sealer or NativeMemorySealer()
        
        # Thread management
        self.active_threads: Dict[str, SymbolicThread] = {}
        self.preserved_threads: Dict[str, Dict[str, Any]] = {}
        self.thread_registry: Dict[str, Dict[str, Any]] = {}
        
        # Preservation policies
        self.preservation_policies = {
            'max_active_threads': 100,
            'max_preserved_threads': 1000,
            'auto_preserve_threshold': 3600,  # 1 hour inactive
            'priority_preservation_multiplier': {
                ThreadPriority.CRITICAL: 10.0,
                ThreadPriority.HIGH: 5.0,
                ThreadPriority.NORMAL: 1.0,
                ThreadPriority.LOW: 0.5,
                ThreadPriority.ARCHIVAL: 0.1
            }
        }
        
        # Validation settings
        self.validation_settings = {
            'auto_validate_interval': 300,  # 5 minutes
            'integrity_check_enabled': True,
            'dependency_validation_enabled': True,
            'corruption_recovery_enabled': True
        }
        
        # Statistics and monitoring
        self.statistics = {
            'threads_created': 0,
            'threads_preserved': 0,
            'threads_rehydrated': 0,
            'threads_corrupted': 0,
            'validation_cycles_performed': 0,
            'integrity_failures': 0
        }
        
        # Last validation timestamp
        self.last_validation_timestamp = time.time()
    
    def create_thread(self, thread_id: str, thread_type: str = "symbolic", 
                     priority: ThreadPriority = ThreadPriority.NORMAL,
                     initial_data: Dict[str, Any] = None) -> SymbolicThread:
        """Create a new symbolic thread"""
        if thread_id in self.active_threads or thread_id in self.preserved_threads:
            raise ValueError(f"Thread '{thread_id}' already exists")
        
        thread = SymbolicThread(thread_id, thread_type, priority)
        
        if initial_data:
            thread.thread_data.update(initial_data)
        
        self.active_threads[thread_id] = thread
        self.thread_registry[thread_id] = thread.get_metadata()
        
        self.statistics['threads_created'] += 1
        
        # Check if we need to auto-preserve threads due to capacity
        self._check_auto_preservation()
        
        return thread
    
    def get_thread(self, thread_id: str) -> Optional[SymbolicThread]:
        """Get an active thread"""
        return self.active_threads.get(thread_id)
    
    def preserve_thread(self, thread_id: str, force: bool = False) -> bool:
        """Preserve a thread to sealed storage"""
        if thread_id not in self.active_threads:
            return False
        
        thread = self.active_threads[thread_id]
        
        # Check dependencies unless forced
        if not force and thread.dependents:
            # Don't preserve if other active threads depend on this one
            active_dependents = [dep for dep in thread.dependents if dep in self.active_threads]
            if active_dependents:
                return False
        
        # Prepare thread for preservation
        thread.state = ThreadState.PRESERVED
        thread.preservation_timestamp = time.time()
        thread.integrity_hash = thread.calculate_integrity_hash()
        
        # Create preservation package
        preservation_package = {
            'thread_metadata': thread.get_metadata(),
            'thread_data': thread.thread_data,
            'execution_context': thread.execution_context,
            'computation_history': thread.computation_history,
            'dependencies': list(thread.dependencies),
            'dependents': list(thread.dependents),
            'preservation_reason': 'manual' if force else 'auto',
            'preservation_timestamp': thread.preservation_timestamp
        }
        
        # Seal the thread using memory sealer
        seal_id = f"thread_{thread_id}_{int(thread.preservation_timestamp)}"
        integrity_hash = self.memory_sealer.seal_state(seal_id, preservation_package)
        
        # Store preservation metadata
        self.preserved_threads[thread_id] = {
            'seal_id': seal_id,
            'integrity_hash': integrity_hash,
            'preservation_timestamp': thread.preservation_timestamp,
            'thread_metadata': thread.get_metadata(),
            'preservation_package_size': len(str(preservation_package))
        }
        
        # Update registry
        self.thread_registry[thread_id] = thread.get_metadata()
        
        # Remove from active threads
        del self.active_threads[thread_id]
        
        self.statistics['threads_preserved'] += 1
        
        return True
    
    def rehydrate_thread(self, thread_id: str) -> Optional[SymbolicThread]:
        """Rehydrate a preserved thread back to active state"""
        if thread_id not in self.preserved_threads:
            return None
        
        preservation_info = self.preserved_threads[thread_id]
        seal_id = preservation_info['seal_id']
        
        # Unseal the preservation package
        try:
            preservation_package = self.memory_sealer.unseal_state(seal_id)
            if preservation_package is None:
                raise ValueError(f"Failed to unseal thread '{thread_id}'")
        except Exception as e:
            self.statistics['integrity_failures'] += 1
            return None
        
        # Verify integrity
        if not self._verify_preservation_integrity(preservation_package, preservation_info):
            self.statistics['integrity_failures'] += 1
            return None
        
        # Reconstruct thread
        metadata = preservation_package['thread_metadata']
        thread = SymbolicThread(
            thread_id, 
            metadata['thread_type'], 
            ThreadPriority(metadata['priority'])
        )
        
        # Restore thread state
        thread.thread_data = preservation_package['thread_data']
        thread.execution_context = preservation_package['execution_context']
        thread.computation_history = preservation_package['computation_history']
        thread.dependencies = set(preservation_package['dependencies'])
        thread.dependents = set(preservation_package['dependents'])
        
        # Update timestamps
        thread.creation_timestamp = metadata['creation_timestamp']
        thread.last_activity_timestamp = metadata['last_activity_timestamp']
        thread.preservation_timestamp = metadata['preservation_timestamp']
        thread.rehydration_timestamp = time.time()
        thread.state = ThreadState.REHYDRATING
        
        # Add to active threads
        self.active_threads[thread_id] = thread
        
        # Clean up preservation
        del self.preserved_threads[thread_id]
        
        # Update registry
        self.thread_registry[thread_id] = thread.get_metadata()
        
        # Mark as active
        thread.state = ThreadState.ACTIVE
        thread.update_activity()
        
        self.statistics['threads_rehydrated'] += 1
        
        return thread
    
    def _verify_preservation_integrity(self, preservation_package: Dict[str, Any], 
                                     preservation_info: Dict[str, Any]) -> bool:
        """Verify integrity of preserved thread package"""
        try:
            # Verify package structure
            required_keys = ['thread_metadata', 'thread_data', 'execution_context', 
                           'computation_history', 'dependencies', 'dependents']
            if not all(key in preservation_package for key in required_keys):
                return False
            
            # Verify metadata consistency
            package_metadata = preservation_package['thread_metadata']
            stored_metadata = preservation_info['thread_metadata']
            
            critical_fields = ['thread_id', 'thread_type', 'creation_timestamp']
            for field in critical_fields:
                if package_metadata.get(field) != stored_metadata.get(field):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _check_auto_preservation(self):
        """Check if auto-preservation is needed"""
        # Check capacity limits
        if len(self.active_threads) > self.preservation_policies['max_active_threads']:
            self._auto_preserve_threads()
        
        # Check inactive threads
        current_time = time.time()
        threshold = self.preservation_policies['auto_preserve_threshold']
        
        inactive_threads = []
        for thread_id, thread in self.active_threads.items():
            time_inactive = current_time - thread.last_activity_timestamp
            priority_multiplier = self.preservation_policies['priority_preservation_multiplier'][thread.priority]
            adjusted_threshold = threshold * priority_multiplier
            
            if time_inactive > adjusted_threshold:
                inactive_threads.append((thread_id, time_inactive, thread.priority))
        
        # Preserve inactive threads (lowest priority first)
        inactive_threads.sort(key=lambda x: (x[2].value, -x[1]))  # Sort by priority, then by inactivity time
        
        for thread_id, _, _ in inactive_threads[:10]:  # Preserve up to 10 threads at once
            if self.preserve_thread(thread_id):
                break  # Stop if preservation fails
    
    def _auto_preserve_threads(self):
        """Auto-preserve threads based on priority and activity"""
        if len(self.active_threads) <= self.preservation_policies['max_active_threads']:
            return
        
        # Calculate preservation scores
        current_time = time.time()
        thread_scores = []
        
        for thread_id, thread in self.active_threads.items():
            time_inactive = current_time - thread.last_activity_timestamp
            priority_score = {
                ThreadPriority.CRITICAL: 1000,
                ThreadPriority.HIGH: 100,
                ThreadPriority.NORMAL: 10,
                ThreadPriority.LOW: 1,
                ThreadPriority.ARCHIVAL: 0.1
            }[thread.priority]
            
            # Lower score = higher preservation priority
            preservation_score = priority_score - (time_inactive / 3600)  # Reduce score for longer inactivity
            thread_scores.append((thread_id, preservation_score, thread.priority))
        
        # Sort by preservation score (lowest first)
        thread_scores.sort(key=lambda x: x[1])
        
        # Preserve threads until we're under the limit
        threads_to_preserve = len(self.active_threads) - self.preservation_policies['max_active_threads']
        preserved_count = 0
        
        for thread_id, score, priority in thread_scores:
            if preserved_count >= threads_to_preserve:
                break
            
            # Don't auto-preserve critical threads unless absolutely necessary
            if priority == ThreadPriority.CRITICAL and preserved_count < threads_to_preserve * 0.8:
                continue
            
            if self.preserve_thread(thread_id):
                preserved_count += 1
    
    def perform_validation_cycle(self) -> Dict[str, Any]:
        """Perform comprehensive thread validation cycle"""
        validation_start_time = time.time()
        validation_results = {
            'timestamp': validation_start_time,
            'active_threads_validated': 0,
            'preserved_threads_validated': 0,
            'integrity_failures': 0,
            'dependency_issues': 0,
            'corruption_detected': 0,
            'corruption_recovered': 0,
            'validation_duration': 0.0
        }
        
        # Validate active threads
        for thread_id, thread in list(self.active_threads.items()):
            try:
                # Integrity check
                if self.validation_settings['integrity_check_enabled']:
                    current_hash = thread.calculate_integrity_hash()
                    if thread.integrity_hash and thread.integrity_hash != current_hash:
                        validation_results['integrity_failures'] += 1
                        thread.validation_history.append({
                            'timestamp': validation_start_time,
                            'type': 'integrity_failure',
                            'expected_hash': thread.integrity_hash,
                            'actual_hash': current_hash
                        })
                    
                    thread.integrity_hash = current_hash
                
                # Dependency validation
                if self.validation_settings['dependency_validation_enabled']:
                    invalid_dependencies = []
                    for dep_id in thread.dependencies:
                        if dep_id not in self.active_threads and dep_id not in self.preserved_threads:
                            invalid_dependencies.append(dep_id)
                    
                    if invalid_dependencies:
                        validation_results['dependency_issues'] += 1
                        # Clean up invalid dependencies
                        for dep_id in invalid_dependencies:
                            thread.dependencies.discard(dep_id)
                
                validation_results['active_threads_validated'] += 1
                
            except Exception as e:
                validation_results['corruption_detected'] += 1
                if self.validation_settings['corruption_recovery_enabled']:
                    # Attempt corruption recovery
                    if self._attempt_corruption_recovery(thread_id, thread):
                        validation_results['corruption_recovered'] += 1
                    else:
                        thread.state = ThreadState.CORRUPTED
        
        # Validate preserved threads
        for thread_id, preservation_info in list(self.preserved_threads.items()):
            try:
                # Verify seal integrity
                seal_id = preservation_info['seal_id']
                if not self.memory_sealer.verify_integrity(seal_id):
                    validation_results['corruption_detected'] += 1
                    validation_results['integrity_failures'] += 1
                
                validation_results['preserved_threads_validated'] += 1
                
            except Exception:
                validation_results['corruption_detected'] += 1
        
        validation_results['validation_duration'] = time.time() - validation_start_time
        self.last_validation_timestamp = validation_start_time
        self.statistics['validation_cycles_performed'] += 1
        
        return validation_results
    
    def _attempt_corruption_recovery(self, thread_id: str, corrupted_thread: SymbolicThread) -> bool:
        """Attempt to recover a corrupted thread"""
        try:
            # If thread was previously preserved, try to rehydrate from preserved state
            if thread_id in self.preserved_threads:
                preserved_thread = self.rehydrate_thread(thread_id)
                if preserved_thread:
                    # Copy current computation history to recovered thread
                    if len(corrupted_thread.computation_history) > len(preserved_thread.computation_history):
                        additional_computations = corrupted_thread.computation_history[len(preserved_thread.computation_history):]
                        preserved_thread.computation_history.extend(additional_computations)
                    
                    self.active_threads[thread_id] = preserved_thread
                    return True
            
            # If recovery fails, try to preserve current state before marking as corrupted
            try:
                self.preserve_thread(thread_id, force=True)
                return True
            except Exception:
                pass
            
            return False
            
        except Exception:
            return False
    
    def get_thread_statistics(self) -> Dict[str, Any]:
        """Get comprehensive thread management statistics"""
        current_time = time.time()
        
        # Calculate activity statistics
        active_by_priority = {}
        active_by_type = {}
        
        for thread in self.active_threads.values():
            priority_key = thread.priority.value
            type_key = thread.thread_type
            
            active_by_priority[priority_key] = active_by_priority.get(priority_key, 0) + 1
            active_by_type[type_key] = active_by_type.get(type_key, 0) + 1
        
        # Calculate average inactivity time
        if self.active_threads:
            avg_inactivity = sum(
                current_time - thread.last_activity_timestamp 
                for thread in self.active_threads.values()
            ) / len(self.active_threads)
        else:
            avg_inactivity = 0.0
        
        return {
            'active_threads': len(self.active_threads),
            'preserved_threads': len(self.preserved_threads),
            'total_threads_registered': len(self.thread_registry),
            'active_by_priority': active_by_priority,
            'active_by_type': active_by_type,
            'average_inactivity_time': avg_inactivity,
            'last_validation_timestamp': self.last_validation_timestamp,
            'time_since_last_validation': current_time - self.last_validation_timestamp,
            'preservation_policies': self.preservation_policies,
            'validation_settings': self.validation_settings,
            'statistics': self.statistics.copy()
        }
    
    def cleanup_archived_threads(self, max_age_days: int = 30) -> int:
        """Clean up old archived threads"""
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 3600
        
        threads_cleaned = 0
        
        # Clean up old preserved threads
        for thread_id in list(self.preserved_threads.keys()):
            preservation_info = self.preserved_threads[thread_id]
            age = current_time - preservation_info['preservation_timestamp']
            
            if age > max_age_seconds:
                # Remove from memory sealer
                try:
                    seal_id = preservation_info['seal_id']
                    # Note: NativeMemorySealer doesn't have delete method in current implementation
                    # This would need to be added to the native implementation
                except Exception:
                    pass
                
                # Remove from preserved threads
                del self.preserved_threads[thread_id]
                threads_cleaned += 1
        
        return threads_cleaned