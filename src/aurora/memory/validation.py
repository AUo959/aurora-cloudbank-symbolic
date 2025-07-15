"""
Thread Validation Cycles for Aurora Memory Sealing
Comprehensive validation system for thread integrity and consistency
"""

import time
import hashlib
from typing import Dict, List, Any, Optional, Set, Callable
from enum import Enum
from dataclasses import dataclass
from .thread_manager import SymbolicThreadManager, SymbolicThread, ThreadState


class ValidationLevel(Enum):
    """Validation depth levels"""
    BASIC = "basic"          # Quick integrity checks
    STANDARD = "standard"    # Standard validation with dependencies
    COMPREHENSIVE = "comprehensive"  # Full validation with deep checks
    FORENSIC = "forensic"    # Detailed forensic analysis


class ValidationResult(Enum):
    """Validation result types"""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    issue_type: str
    severity: ValidationResult
    thread_id: str
    message: str
    timestamp: float
    details: Dict[str, Any]
    recommended_action: str


class ThreadValidationCycles:
    """Advanced thread validation system with multiple validation levels"""
    
    def __init__(self, thread_manager: SymbolicThreadManager):
        self.thread_manager = thread_manager
        
        # Validation configuration
        self.validation_config = {
            'default_level': ValidationLevel.STANDARD,
            'auto_cycle_interval': 300,  # 5 minutes
            'critical_failure_threshold': 3,
            'warning_accumulation_threshold': 10,
            'forensic_trigger_threshold': 5  # Critical failures before forensic analysis
        }
        
        # Validation history and tracking
        self.validation_history: List[Dict[str, Any]] = []
        self.validation_issues: List[ValidationIssue] = []
        self.validation_statistics = {
            'cycles_performed': 0,
            'issues_detected': 0,
            'issues_resolved': 0,
            'critical_failures': 0,
            'last_cycle_timestamp': 0.0,
            'average_cycle_duration': 0.0
        }
        
        # Custom validation rules
        self.custom_validators: List[Callable] = []
        self.validation_plugins: Dict[str, Callable] = {}
        
        # Issue tracking
        self.persistent_issues: Dict[str, List[ValidationIssue]] = {}
        self.resolved_issues: List[ValidationIssue] = []
        
        # Auto-repair capabilities
        self.auto_repair_enabled = True
        self.repair_strategies = {
            'integrity_failure': self._repair_integrity_failure,
            'dependency_issue': self._repair_dependency_issue,
            'memory_leak': self._repair_memory_leak,
            'corruption': self._repair_corruption
        }
    
    def perform_validation_cycle(self, level: ValidationLevel = None, 
                                target_threads: List[str] = None) -> Dict[str, Any]:
        """Perform a comprehensive validation cycle"""
        cycle_start_time = time.time()
        level = level or self.validation_config['default_level']
        
        validation_cycle_id = f"validation_{int(cycle_start_time)}"
        
        # Initialize cycle results
        cycle_results = {
            'cycle_id': validation_cycle_id,
            'timestamp': cycle_start_time,
            'level': level.value,
            'target_threads': target_threads or 'all',
            'threads_validated': 0,
            'issues_found': 0,
            'issues_resolved': 0,
            'duration': 0.0,
            'validation_details': {},
            'recommendations': []
        }
        
        # Determine threads to validate
        if target_threads:
            threads_to_validate = {tid: t for tid, t in self.thread_manager.active_threads.items() 
                                 if tid in target_threads}
        else:
            threads_to_validate = self.thread_manager.active_threads.copy()
        
        # Perform validation based on level
        if level == ValidationLevel.BASIC:
            cycle_results.update(self._perform_basic_validation(threads_to_validate))
        elif level == ValidationLevel.STANDARD:
            cycle_results.update(self._perform_standard_validation(threads_to_validate))
        elif level == ValidationLevel.COMPREHENSIVE:
            cycle_results.update(self._perform_comprehensive_validation(threads_to_validate))
        elif level == ValidationLevel.FORENSIC:
            cycle_results.update(self._perform_forensic_validation(threads_to_validate))
        
        # Run custom validators
        custom_results = self._run_custom_validators(threads_to_validate)
        cycle_results['custom_validation'] = custom_results
        
        # Process validation issues
        new_issues = self._process_validation_issues(cycle_results)
        
        # Attempt auto-repair if enabled
        if self.auto_repair_enabled and new_issues:
            repair_results = self._attempt_auto_repair(new_issues)
            cycle_results['repair_results'] = repair_results
        
        # Update statistics and history
        cycle_results['duration'] = time.time() - cycle_start_time
        self._update_validation_statistics(cycle_results)
        self.validation_history.append(cycle_results)
        
        # Maintain history limits
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-500:]
        
        return cycle_results
    
    def _perform_basic_validation(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Perform basic validation checks"""
        results = {
            'validation_type': 'basic',
            'checks_performed': [],
            'issues': []
        }
        
        for thread_id, thread in threads.items():
            thread_issues = []
            
            # Check 1: Thread state consistency
            if thread.state not in [ThreadState.ACTIVE, ThreadState.REHYDRATING]:
                thread_issues.append(ValidationIssue(
                    issue_type='state_inconsistency',
                    severity=ValidationResult.WARNING,
                    thread_id=thread_id,
                    message=f'Thread has unexpected state: {thread.state.value}',
                    timestamp=time.time(),
                    details={'current_state': thread.state.value, 'expected_states': ['active', 'rehydrating']},
                    recommended_action='Verify thread lifecycle management'
                ))
            
            # Check 2: Basic integrity hash
            try:
                current_hash = thread.calculate_integrity_hash()
                if thread.integrity_hash and thread.integrity_hash != current_hash:
                    thread_issues.append(ValidationIssue(
                        issue_type='integrity_mismatch',
                        severity=ValidationResult.FAIL,
                        thread_id=thread_id,
                        message='Thread integrity hash mismatch detected',
                        timestamp=time.time(),
                        details={'expected_hash': thread.integrity_hash[:16], 'actual_hash': current_hash[:16]},
                        recommended_action='Perform comprehensive validation or restore from backup'
                    ))
                thread.integrity_hash = current_hash
            except Exception as e:
                thread_issues.append(ValidationIssue(
                    issue_type='integrity_calculation_error',
                    severity=ValidationResult.CRITICAL,
                    thread_id=thread_id,
                    message=f'Failed to calculate integrity hash: {str(e)}',
                    timestamp=time.time(),
                    details={'error': str(e)},
                    recommended_action='Investigate thread corruption'
                ))
            
            # Check 3: Basic timestamp validation
            current_time = time.time()
            if thread.last_activity_timestamp > current_time:
                thread_issues.append(ValidationIssue(
                    issue_type='timestamp_future',
                    severity=ValidationResult.WARNING,
                    thread_id=thread_id,
                    message='Thread last activity timestamp is in the future',
                    timestamp=time.time(),
                    details={'last_activity': thread.last_activity_timestamp, 'current_time': current_time},
                    recommended_action='Synchronize system time or update thread timestamp'
                ))
            
            results['issues'].extend(thread_issues)
            results['checks_performed'].extend(['state_consistency', 'integrity_hash', 'timestamp_validation'])
        
        results['threads_validated'] = len(threads)
        results['issues_found'] = len(results['issues'])
        
        return results
    
    def _perform_standard_validation(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Perform standard validation with dependency checks"""
        # Start with basic validation
        results = self._perform_basic_validation(threads)
        results['validation_type'] = 'standard'
        
        for thread_id, thread in threads.items():
            thread_issues = []
            
            # Check 4: Dependency validation
            for dep_id in thread.dependencies:
                if dep_id not in self.thread_manager.active_threads and dep_id not in self.thread_manager.preserved_threads:
                    thread_issues.append(ValidationIssue(
                        issue_type='missing_dependency',
                        severity=ValidationResult.FAIL,
                        thread_id=thread_id,
                        message=f'Thread depends on non-existent thread: {dep_id}',
                        timestamp=time.time(),
                        details={'missing_dependency': dep_id, 'total_dependencies': len(thread.dependencies)},
                        recommended_action='Remove invalid dependency or restore missing thread'
                    ))
            
            # Check 5: Circular dependency detection
            if self._detect_circular_dependency(thread_id, thread.dependencies, set()):
                thread_issues.append(ValidationIssue(
                    issue_type='circular_dependency',
                    severity=ValidationResult.CRITICAL,
                    thread_id=thread_id,
                    message='Circular dependency detected in thread graph',
                    timestamp=time.time(),
                    details={'dependencies': list(thread.dependencies)},
                    recommended_action='Break circular dependency chain'
                ))
            
            # Check 6: Data consistency
            if len(thread.computation_history) > 1000:  # Arbitrary large number
                thread_issues.append(ValidationIssue(
                    issue_type='excessive_computation_history',
                    severity=ValidationResult.WARNING,
                    thread_id=thread_id,
                    message=f'Thread has excessive computation history: {len(thread.computation_history)} entries',
                    timestamp=time.time(),
                    details={'history_size': len(thread.computation_history)},
                    recommended_action='Consider archiving or truncating computation history'
                ))
            
            results['issues'].extend(thread_issues)
        
        results['checks_performed'].extend(['dependency_validation', 'circular_dependency', 'data_consistency'])
        results['issues_found'] = len(results['issues'])
        
        return results
    
    def _perform_comprehensive_validation(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Perform comprehensive validation with deep analysis"""
        # Start with standard validation
        results = self._perform_standard_validation(threads)
        results['validation_type'] = 'comprehensive'
        
        for thread_id, thread in threads.items():
            thread_issues = []
            
            # Check 7: Memory usage analysis
            thread_memory_estimate = self._estimate_thread_memory_usage(thread)
            if thread_memory_estimate > 10 * 1024 * 1024:  # 10MB threshold
                thread_issues.append(ValidationIssue(
                    issue_type='high_memory_usage',
                    severity=ValidationResult.WARNING,
                    thread_id=thread_id,
                    message=f'Thread using high memory: ~{thread_memory_estimate / 1024 / 1024:.1f}MB',
                    timestamp=time.time(),
                    details={'memory_estimate_bytes': thread_memory_estimate},
                    recommended_action='Optimize thread data or consider preservation'
                ))
            
            # Check 8: Activity pattern analysis
            activity_analysis = self._analyze_activity_pattern(thread)
            if activity_analysis['anomaly_detected']:
                thread_issues.append(ValidationIssue(
                    issue_type='activity_anomaly',
                    severity=ValidationResult.WARNING,
                    thread_id=thread_id,
                    message=f'Anomalous activity pattern detected: {activity_analysis["anomaly_type"]}',
                    timestamp=time.time(),
                    details=activity_analysis,
                    recommended_action='Investigate thread activity or adjust thresholds'
                ))
            
            # Check 9: Data validation
            data_validation = self._validate_thread_data(thread)
            if not data_validation['valid']:
                thread_issues.append(ValidationIssue(
                    issue_type='data_validation_failure',
                    severity=ValidationResult.FAIL,
                    thread_id=thread_id,
                    message=f'Thread data validation failed: {data_validation["error"]}',
                    timestamp=time.time(),
                    details=data_validation,
                    recommended_action='Restore thread data from backup or reinitialize'
                ))
            
            # Check 10: Performance metrics
            performance_metrics = self._calculate_thread_performance_metrics(thread)
            if performance_metrics['performance_score'] < 0.5:
                thread_issues.append(ValidationIssue(
                    issue_type='poor_performance',
                    severity=ValidationResult.WARNING,
                    thread_id=thread_id,
                    message=f'Thread performance below threshold: {performance_metrics["performance_score"]:.2f}',
                    timestamp=time.time(),
                    details=performance_metrics,
                    recommended_action='Optimize thread operations or consider refactoring'
                ))
            
            results['issues'].extend(thread_issues)
        
        results['checks_performed'].extend(['memory_analysis', 'activity_analysis', 'data_validation', 'performance_metrics'])
        results['issues_found'] = len(results['issues'])
        
        return results
    
    def _perform_forensic_validation(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Perform forensic-level validation for detailed investigation"""
        # Start with comprehensive validation
        results = self._perform_comprehensive_validation(threads)
        results['validation_type'] = 'forensic'
        
        # Additional forensic analysis
        forensic_analysis = {
            'thread_relationship_map': self._build_thread_relationship_map(threads),
            'computation_flow_analysis': self._analyze_computation_flows(threads),
            'timeline_reconstruction': self._reconstruct_thread_timelines(threads),
            'anomaly_detection': self._perform_anomaly_detection(threads)
        }
        
        results['forensic_analysis'] = forensic_analysis
        results['checks_performed'].extend(['relationship_mapping', 'flow_analysis', 'timeline_reconstruction', 'anomaly_detection'])
        
        return results
    
    def _detect_circular_dependency(self, thread_id: str, dependencies: Set[str], visited: Set[str]) -> bool:
        """Detect circular dependencies in thread graph"""
        if thread_id in visited:
            return True
        
        visited.add(thread_id)
        
        for dep_id in dependencies:
            if dep_id in self.thread_manager.active_threads:
                dep_thread = self.thread_manager.active_threads[dep_id]
                if self._detect_circular_dependency(dep_id, dep_thread.dependencies, visited.copy()):
                    return True
        
        return False
    
    def _estimate_thread_memory_usage(self, thread: SymbolicThread) -> int:
        """Estimate memory usage of a thread"""
        # Simple estimation based on data size
        import sys
        
        total_size = 0
        total_size += sys.getsizeof(thread.thread_data)
        total_size += sys.getsizeof(thread.execution_context)
        total_size += sys.getsizeof(thread.computation_history)
        total_size += sum(sys.getsizeof(item) for item in thread.computation_history)
        
        return total_size
    
    def _analyze_activity_pattern(self, thread: SymbolicThread) -> Dict[str, Any]:
        """Analyze thread activity patterns for anomalies"""
        if len(thread.computation_history) < 5:
            return {'anomaly_detected': False, 'reason': 'insufficient_data'}
        
        # Calculate activity intervals
        intervals = []
        for i in range(1, len(thread.computation_history)):
            interval = thread.computation_history[i]['timestamp'] - thread.computation_history[i-1]['timestamp']
            intervals.append(interval)
        
        if not intervals:
            return {'anomaly_detected': False, 'reason': 'no_intervals'}
        
        # Simple anomaly detection based on variance
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((interval - avg_interval) ** 2 for interval in intervals) / len(intervals)
        
        # Detect anomalies
        anomaly_threshold = avg_interval * 3  # 3x average interval
        large_gaps = [i for i in intervals if i > anomaly_threshold]
        
        return {
            'anomaly_detected': len(large_gaps) > len(intervals) * 0.2,  # More than 20% large gaps
            'anomaly_type': 'irregular_activity' if large_gaps else 'none',
            'average_interval': avg_interval,
            'variance': variance,
            'large_gaps_count': len(large_gaps),
            'total_intervals': len(intervals)
        }
    
    def _validate_thread_data(self, thread: SymbolicThread) -> Dict[str, Any]:
        """Validate thread data integrity and structure"""
        try:
            # Check required fields exist
            if not hasattr(thread, 'thread_id') or not thread.thread_id:
                return {'valid': False, 'error': 'Missing thread_id'}
            
            if not hasattr(thread, 'thread_type') or not thread.thread_type:
                return {'valid': False, 'error': 'Missing thread_type'}
            
            # Check timestamp validity
            current_time = time.time()
            if thread.creation_timestamp > current_time:
                return {'valid': False, 'error': 'Creation timestamp in future'}
            
            # Check data structure integrity
            if not isinstance(thread.thread_data, dict):
                return {'valid': False, 'error': 'thread_data is not a dictionary'}
            
            if not isinstance(thread.computation_history, list):
                return {'valid': False, 'error': 'computation_history is not a list'}
            
            return {'valid': True, 'checks_passed': 5}
            
        except Exception as e:
            return {'valid': False, 'error': f'Validation exception: {str(e)}'}
    
    def _calculate_thread_performance_metrics(self, thread: SymbolicThread) -> Dict[str, Any]:
        """Calculate performance metrics for a thread"""
        if not thread.computation_history:
            return {'performance_score': 1.0, 'reason': 'no_computations'}
        
        # Simple performance calculation based on computation frequency
        current_time = time.time()
        thread_age = current_time - thread.creation_timestamp
        
        if thread_age <= 0:
            return {'performance_score': 1.0, 'reason': 'new_thread'}
        
        computation_rate = len(thread.computation_history) / thread_age
        
        # Normalize to 0-1 score (assuming 1 computation per second is optimal)
        performance_score = min(computation_rate, 1.0)
        
        return {
            'performance_score': performance_score,
            'computation_rate': computation_rate,
            'thread_age': thread_age,
            'total_computations': len(thread.computation_history)
        }
    
    def _build_thread_relationship_map(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Build a comprehensive map of thread relationships"""
        relationship_map = {
            'nodes': [],
            'edges': [],
            'clusters': [],
            'isolated_threads': []
        }
        
        # Add nodes
        for thread_id, thread in threads.items():
            relationship_map['nodes'].append({
                'id': thread_id,
                'type': thread.thread_type,
                'priority': thread.priority.value,
                'state': thread.state.value,
                'dependency_count': len(thread.dependencies),
                'dependent_count': len(thread.dependents)
            })
        
        # Add edges (dependencies)
        for thread_id, thread in threads.items():
            for dep_id in thread.dependencies:
                relationship_map['edges'].append({
                    'from': dep_id,
                    'to': thread_id,
                    'type': 'dependency'
                })
        
        # Identify isolated threads
        connected_threads = set()
        for edge in relationship_map['edges']:
            connected_threads.add(edge['from'])
            connected_threads.add(edge['to'])
        
        relationship_map['isolated_threads'] = [
            thread_id for thread_id in threads.keys() 
            if thread_id not in connected_threads
        ]
        
        return relationship_map
    
    def _analyze_computation_flows(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Analyze computation flows across threads"""
        flow_analysis = {
            'total_computations': 0,
            'computation_by_thread': {},
            'temporal_distribution': {},
            'flow_patterns': []
        }
        
        all_computations = []
        
        for thread_id, thread in threads.items():
            thread_computations = len(thread.computation_history)
            flow_analysis['total_computations'] += thread_computations
            flow_analysis['computation_by_thread'][thread_id] = thread_computations
            
            for comp in thread.computation_history:
                all_computations.append({
                    'thread_id': thread_id,
                    'timestamp': comp['timestamp'],
                    'step_id': comp['step_id']
                })
        
        # Sort by timestamp for temporal analysis
        all_computations.sort(key=lambda x: x['timestamp'])
        
        # Analyze temporal distribution
        if all_computations:
            start_time = all_computations[0]['timestamp']
            end_time = all_computations[-1]['timestamp']
            duration = end_time - start_time
            
            if duration > 0:
                # Divide into time buckets
                bucket_count = min(10, len(all_computations))
                bucket_size = duration / bucket_count
                
                for i in range(bucket_count):
                    bucket_start = start_time + i * bucket_size
                    bucket_end = bucket_start + bucket_size
                    
                    bucket_computations = [
                        comp for comp in all_computations 
                        if bucket_start <= comp['timestamp'] < bucket_end
                    ]
                    
                    flow_analysis['temporal_distribution'][f'bucket_{i}'] = {
                        'start_time': bucket_start,
                        'end_time': bucket_end,
                        'computation_count': len(bucket_computations),
                        'threads_active': len(set(comp['thread_id'] for comp in bucket_computations))
                    }
        
        return flow_analysis
    
    def _reconstruct_thread_timelines(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Reconstruct detailed timelines for forensic analysis"""
        timeline_reconstruction = {
            'thread_timelines': {},
            'global_timeline': [],
            'timeline_gaps': [],
            'concurrency_analysis': {}
        }
        
        all_events = []
        
        for thread_id, thread in threads.items():
            thread_timeline = []
            
            # Add creation event
            thread_timeline.append({
                'timestamp': thread.creation_timestamp,
                'event_type': 'thread_created',
                'thread_id': thread_id
            })
            
            # Add computation events
            for comp in thread.computation_history:
                thread_timeline.append({
                    'timestamp': comp['timestamp'],
                    'event_type': 'computation',
                    'thread_id': thread_id,
                    'step_id': comp['step_id']
                })
            
            # Add preservation/rehydration events
            if thread.preservation_timestamp:
                thread_timeline.append({
                    'timestamp': thread.preservation_timestamp,
                    'event_type': 'thread_preserved',
                    'thread_id': thread_id
                })
            
            if thread.rehydration_timestamp:
                thread_timeline.append({
                    'timestamp': thread.rehydration_timestamp,
                    'event_type': 'thread_rehydrated',
                    'thread_id': thread_id
                })
            
            timeline_reconstruction['thread_timelines'][thread_id] = sorted(thread_timeline, key=lambda x: x['timestamp'])
            all_events.extend(thread_timeline)
        
        # Create global timeline
        timeline_reconstruction['global_timeline'] = sorted(all_events, key=lambda x: x['timestamp'])
        
        return timeline_reconstruction
    
    def _perform_anomaly_detection(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Perform advanced anomaly detection across threads"""
        anomaly_analysis = {
            'anomalies_detected': [],
            'patterns_identified': [],
            'risk_assessment': {},
            'recommendations': []
        }
        
        # Detect threads with unusual dependency patterns
        dependency_counts = [len(thread.dependencies) for thread in threads.values()]
        if dependency_counts:
            avg_dependencies = sum(dependency_counts) / len(dependency_counts)
            std_dev = (sum((x - avg_dependencies) ** 2 for x in dependency_counts) / len(dependency_counts)) ** 0.5
            
            for thread_id, thread in threads.items():
                if len(thread.dependencies) > avg_dependencies + 2 * std_dev:
                    anomaly_analysis['anomalies_detected'].append({
                        'type': 'excessive_dependencies',
                        'thread_id': thread_id,
                        'dependency_count': len(thread.dependencies),
                        'average': avg_dependencies,
                        'threshold': avg_dependencies + 2 * std_dev
                    })
        
        return anomaly_analysis
    
    def _run_custom_validators(self, threads: Dict[str, SymbolicThread]) -> Dict[str, Any]:
        """Run custom validation rules"""
        custom_results = {
            'validators_run': len(self.custom_validators),
            'plugin_results': {},
            'custom_issues': []
        }
        
        # Run custom validators
        for validator in self.custom_validators:
            try:
                validator_result = validator(threads)
                if isinstance(validator_result, list):
                    custom_results['custom_issues'].extend(validator_result)
            except Exception as e:
                custom_results['custom_issues'].append(ValidationIssue(
                    issue_type='custom_validator_error',
                    severity=ValidationResult.WARNING,
                    thread_id='system',
                    message=f'Custom validator failed: {str(e)}',
                    timestamp=time.time(),
                    details={'error': str(e)},
                    recommended_action='Check custom validator implementation'
                ))
        
        # Run validation plugins
        for plugin_name, plugin_func in self.validation_plugins.items():
            try:
                plugin_result = plugin_func(threads)
                custom_results['plugin_results'][plugin_name] = plugin_result
            except Exception as e:
                custom_results['plugin_results'][plugin_name] = {
                    'error': str(e),
                    'status': 'failed'
                }
        
        return custom_results
    
    def _process_validation_issues(self, cycle_results: Dict[str, Any]) -> List[ValidationIssue]:
        """Process and categorize validation issues"""
        new_issues = cycle_results.get('issues', [])
        
        for issue in new_issues:
            # Add to persistent issues if not already resolved
            thread_id = issue.thread_id
            if thread_id not in self.persistent_issues:
                self.persistent_issues[thread_id] = []
            
            # Check if this is a recurring issue
            similar_issues = [
                existing for existing in self.persistent_issues[thread_id]
                if existing.issue_type == issue.issue_type
            ]
            
            if not similar_issues:
                self.persistent_issues[thread_id].append(issue)
                self.validation_issues.append(issue)
        
        return new_issues
    
    def _attempt_auto_repair(self, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """Attempt automatic repair of validation issues"""
        repair_results = {
            'repairs_attempted': 0,
            'repairs_successful': 0,
            'repairs_failed': 0,
            'repair_details': []
        }
        
        for issue in issues:
            if issue.issue_type in self.repair_strategies:
                repair_results['repairs_attempted'] += 1
                
                try:
                    repair_strategy = self.repair_strategies[issue.issue_type]
                    repair_result = repair_strategy(issue)
                    
                    if repair_result['success']:
                        repair_results['repairs_successful'] += 1
                        # Mark issue as resolved
                        self.resolved_issues.append(issue)
                        if issue in self.validation_issues:
                            self.validation_issues.remove(issue)
                    else:
                        repair_results['repairs_failed'] += 1
                    
                    repair_results['repair_details'].append({
                        'issue_type': issue.issue_type,
                        'thread_id': issue.thread_id,
                        'repair_result': repair_result
                    })
                    
                except Exception as e:
                    repair_results['repairs_failed'] += 1
                    repair_results['repair_details'].append({
                        'issue_type': issue.issue_type,
                        'thread_id': issue.thread_id,
                        'repair_result': {'success': False, 'error': str(e)}
                    })
        
        return repair_results
    
    def _repair_integrity_failure(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Repair integrity failure"""
        thread_id = issue.thread_id
        if thread_id not in self.thread_manager.active_threads:
            return {'success': False, 'reason': 'thread_not_found'}
        
        thread = self.thread_manager.active_threads[thread_id]
        
        # Recalculate integrity hash
        try:
            new_hash = thread.calculate_integrity_hash()
            thread.integrity_hash = new_hash
            return {'success': True, 'action': 'recalculated_hash', 'new_hash': new_hash[:16]}
        except Exception as e:
            return {'success': False, 'reason': f'hash_calculation_failed: {str(e)}'}
    
    def _repair_dependency_issue(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Repair dependency issues"""
        thread_id = issue.thread_id
        if thread_id not in self.thread_manager.active_threads:
            return {'success': False, 'reason': 'thread_not_found'}
        
        thread = self.thread_manager.active_threads[thread_id]
        
        # Remove invalid dependencies
        initial_dep_count = len(thread.dependencies)
        valid_dependencies = set()
        
        for dep_id in thread.dependencies:
            if (dep_id in self.thread_manager.active_threads or 
                dep_id in self.thread_manager.preserved_threads):
                valid_dependencies.add(dep_id)
        
        thread.dependencies = valid_dependencies
        removed_count = initial_dep_count - len(valid_dependencies)
        
        return {
            'success': True,
            'action': 'cleaned_dependencies',
            'removed_count': removed_count,
            'remaining_count': len(valid_dependencies)
        }
    
    def _repair_memory_leak(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Repair memory leak issues"""
        thread_id = issue.thread_id
        if thread_id not in self.thread_manager.active_threads:
            return {'success': False, 'reason': 'thread_not_found'}
        
        thread = self.thread_manager.active_threads[thread_id]
        
        # Truncate computation history if too large
        if len(thread.computation_history) > 500:
            original_size = len(thread.computation_history)
            thread.computation_history = thread.computation_history[-250:]  # Keep last 250 entries
            
            return {
                'success': True,
                'action': 'truncated_history',
                'original_size': original_size,
                'new_size': len(thread.computation_history)
            }
        
        return {'success': False, 'reason': 'no_action_needed'}
    
    def _repair_corruption(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Repair corruption issues"""
        thread_id = issue.thread_id
        
        # Attempt to preserve the thread before further corruption
        try:
            if self.thread_manager.preserve_thread(thread_id, force=True):
                return {
                    'success': True,
                    'action': 'preserved_corrupted_thread',
                    'thread_id': thread_id
                }
        except Exception as e:
            return {'success': False, 'reason': f'preservation_failed: {str(e)}'}
        
        return {'success': False, 'reason': 'preservation_not_possible'}
    
    def _update_validation_statistics(self, cycle_results: Dict[str, Any]):
        """Update validation statistics"""
        self.validation_statistics['cycles_performed'] += 1
        self.validation_statistics['issues_detected'] += cycle_results.get('issues_found', 0)
        self.validation_statistics['last_cycle_timestamp'] = cycle_results['timestamp']
        
        # Update average cycle duration
        duration = cycle_results['duration']
        cycles = self.validation_statistics['cycles_performed']
        prev_avg = self.validation_statistics['average_cycle_duration']
        self.validation_statistics['average_cycle_duration'] = (prev_avg * (cycles - 1) + duration) / cycles
        
        # Count critical failures
        critical_issues = [
            issue for issue in cycle_results.get('issues', [])
            if issue.severity == ValidationResult.CRITICAL
        ]
        self.validation_statistics['critical_failures'] += len(critical_issues)
    
    def add_custom_validator(self, validator_func: Callable):
        """Add a custom validation function"""
        self.custom_validators.append(validator_func)
    
    def add_validation_plugin(self, name: str, plugin_func: Callable):
        """Add a validation plugin"""
        self.validation_plugins[name] = plugin_func
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        current_time = time.time()
        
        # Categorize current issues
        issues_by_severity = {}
        issues_by_type = {}
        
        for issue in self.validation_issues:
            severity = issue.severity.value
            issue_type = issue.issue_type
            
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        
        return {
            'report_timestamp': current_time,
            'validation_statistics': self.validation_statistics.copy(),
            'current_issues': {
                'total_issues': len(self.validation_issues),
                'by_severity': issues_by_severity,
                'by_type': issues_by_type
            },
            'persistent_issues': {
                'threads_with_issues': len(self.persistent_issues),
                'total_persistent_issues': sum(len(issues) for issues in self.persistent_issues.values())
            },
            'resolved_issues': len(self.resolved_issues),
            'system_health': {
                'auto_repair_enabled': self.auto_repair_enabled,
                'custom_validators': len(self.custom_validators),
                'validation_plugins': len(self.validation_plugins),
                'last_validation_age': current_time - self.validation_statistics['last_cycle_timestamp']
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate system recommendations based on validation history"""
        recommendations = []
        
        # Check validation frequency
        if self.validation_statistics['last_cycle_timestamp'] > 0:
            time_since_last = time.time() - self.validation_statistics['last_cycle_timestamp']
            if time_since_last > self.validation_config['auto_cycle_interval'] * 2:
                recommendations.append("Consider running validation cycle - significant time since last validation")
        
        # Check issue accumulation
        if len(self.validation_issues) > self.validation_config['warning_accumulation_threshold']:
            recommendations.append("High number of unresolved validation issues - consider manual intervention")
        
        # Check critical failures
        if self.validation_statistics['critical_failures'] > self.validation_config['critical_failure_threshold']:
            recommendations.append("Multiple critical failures detected - perform forensic validation")
        
        # Check auto-repair effectiveness
        total_issues = self.validation_statistics['issues_detected']
        resolved_issues = len(self.resolved_issues)
        if total_issues > 0 and resolved_issues / total_issues < 0.7:
            recommendations.append("Auto-repair effectiveness below 70% - review repair strategies")
        
        return recommendations