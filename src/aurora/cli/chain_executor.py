"""
Branched Chain Executor for Aurora Advanced CLI Extensions
Supports parallel execution, rollback, checkpoints, and extended notation
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed


class ExecutionMode(Enum):
    """Chain execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    STAGED = "staged"
    ADAPTIVE = "adaptive"


class ExecutionStatus(Enum):
    """Execution status tracking"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


@dataclass
class ExecutionCheckpoint:
    """Checkpoint for chain execution state"""
    checkpoint_id: str
    timestamp: float
    execution_state: Dict[str, Any]
    completed_steps: List[str]
    current_step: Optional[str]
    execution_metadata: Dict[str, Any]


@dataclass
class BranchDefinition:
    """Definition of an execution branch"""
    branch_id: str
    start_step: int
    end_step: int
    execution_mode: ExecutionMode
    dependencies: List[str]
    priority: int
    timeout: Optional[float]
    retry_count: int


class BranchedChainExecutor:
    """Advanced chain executor with branching, parallel execution, and rollback capabilities"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.execution_history: List[Dict[str, Any]] = []
        self.checkpoints: Dict[str, ExecutionCheckpoint] = {}
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        
        # Extended notation parser
        self.notation_patterns = {
            'simple': r'(\d{3})//(\d{3})//',
            'branched': r'(\d{3})//(\d{3})//\[([^\]]+)\]',
            'conditional': r'(\d{3})//(\d{3})//\?([^?]+)\?',
            'looped': r'(\d{3})//(\d{3})//\*(\d+)',
            'parallel': r'(\d{3})//(\d{3})//\|\|',
            'staged': r'(\d{3})//(\d{3})//>>(\d+)',
        }
        
        # Execution statistics
        self.execution_stats = {
            'total_executions': 0,
            'parallel_executions': 0,
            'rollbacks_performed': 0,
            'checkpoints_created': 0,
            'average_execution_time': 0.0
        }
    
    def execute_branched_chain(self, chain_notation: str, 
                              symbolic_engine=None,
                              execution_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute chain with branched notation support"""
        execution_start = time.time()
        execution_id = f"exec_{int(execution_start)}"
        
        # Parse extended notation
        parsed_notation = self._parse_extended_notation(chain_notation)
        
        # Create execution plan
        execution_plan = self._create_execution_plan(parsed_notation, execution_context)
        
        # Create initial checkpoint
        initial_checkpoint = self._create_checkpoint(execution_id, "initial", execution_plan)
        
        # Execute according to plan
        try:
            execution_result = self._execute_plan(execution_plan, symbolic_engine, execution_id)
            execution_result['status'] = ExecutionStatus.COMPLETED
        except Exception as e:
            execution_result = {
                'status': ExecutionStatus.FAILED,
                'error': str(e),
                'execution_id': execution_id
            }
        
        # Record execution
        execution_record = {
            'execution_id': execution_id,
            'chain_notation': chain_notation,
            'execution_plan': execution_plan,
            'result': execution_result,
            'execution_time': time.time() - execution_start,
            'timestamp': execution_start
        }
        
        self.execution_history.append(execution_record)
        
        # Update statistics
        self._update_execution_stats(execution_record)
        
        return execution_result
    
    def _parse_extended_notation(self, notation: str) -> Dict[str, Any]:
        """Parse extended chain notation beyond 001//999// format"""
        import re
        
        parsed = {
            'original_notation': notation,
            'notation_type': 'unknown',
            'components': {},
            'execution_hints': {}
        }
        
        # Try each notation pattern
        for pattern_name, pattern in self.notation_patterns.items():
            match = re.match(pattern, notation)
            if match:
                parsed['notation_type'] = pattern_name
                
                if pattern_name == 'simple':
                    start, end = match.groups()
                    parsed['components'] = {
                        'start': int(start),
                        'end': int(end),
                        'mode': ExecutionMode.SEQUENTIAL
                    }
                
                elif pattern_name == 'branched':
                    start, end, branch_spec = match.groups()
                    parsed['components'] = {
                        'start': int(start),
                        'end': int(end),
                        'branches': self._parse_branch_specification(branch_spec)
                    }
                    parsed['execution_hints']['mode'] = ExecutionMode.PARALLEL
                
                elif pattern_name == 'conditional':
                    start, end, condition = match.groups()
                    parsed['components'] = {
                        'start': int(start),
                        'end': int(end),
                        'condition': condition
                    }
                    parsed['execution_hints']['conditional'] = True
                
                elif pattern_name == 'looped':
                    start, end, iterations = match.groups()
                    parsed['components'] = {
                        'start': int(start),
                        'end': int(end),
                        'iterations': int(iterations)
                    }
                    parsed['execution_hints']['looped'] = True
                
                elif pattern_name == 'parallel':
                    start, end = match.groups()
                    parsed['components'] = {
                        'start': int(start),
                        'end': int(end),
                        'mode': ExecutionMode.PARALLEL
                    }
                
                elif pattern_name == 'staged':
                    start, end, stages = match.groups()
                    parsed['components'] = {
                        'start': int(start),
                        'end': int(end),
                        'stages': int(stages),
                        'mode': ExecutionMode.STAGED
                    }
                
                break
        
        # Fallback to simple notation if no pattern matches
        if parsed['notation_type'] == 'unknown':
            # Try to extract basic start//end pattern
            basic_match = re.search(r'(\d+)//(\d+)', notation)
            if basic_match:
                start, end = basic_match.groups()
                parsed['notation_type'] = 'simple'
                parsed['components'] = {
                    'start': int(start),
                    'end': int(end),
                    'mode': ExecutionMode.SEQUENTIAL
                }
        
        return parsed
    
    def _parse_branch_specification(self, branch_spec: str) -> List[BranchDefinition]:
        """Parse branch specification string"""
        branches = []
        
        # Split by commas for multiple branches
        branch_parts = branch_spec.split(',')
        
        for i, part in enumerate(branch_parts):
            part = part.strip()
            
            # Parse branch range (e.g., "5-10", "1-3:parallel", "7-12:priority=2")
            if '-' in part:
                range_spec, *options = part.split(':')
                start_str, end_str = range_spec.split('-')
                
                branch = BranchDefinition(
                    branch_id=f"branch_{i}",
                    start_step=int(start_str),
                    end_step=int(end_str),
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    dependencies=[],
                    priority=1,
                    timeout=None,
                    retry_count=0
                )
                
                # Parse options
                for option in options:
                    if option == 'parallel':
                        branch.execution_mode = ExecutionMode.PARALLEL
                    elif option.startswith('priority='):
                        branch.priority = int(option.split('=')[1])
                    elif option.startswith('timeout='):
                        branch.timeout = float(option.split('=')[1])
                    elif option.startswith('retry='):
                        branch.retry_count = int(option.split('=')[1])
                
                branches.append(branch)
        
        return branches
    
    def _create_execution_plan(self, parsed_notation: Dict[str, Any], 
                              execution_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create detailed execution plan from parsed notation"""
        plan = {
            'plan_id': f"plan_{int(time.time())}",
            'notation_info': parsed_notation,
            'execution_steps': [],
            'execution_mode': ExecutionMode.SEQUENTIAL,
            'context': execution_context or {},
            'checkpoints': [],
            'rollback_points': []
        }
        
        components = parsed_notation['components']
        execution_hints = parsed_notation.get('execution_hints', {})
        
        # Generate execution steps based on notation type
        if parsed_notation['notation_type'] == 'simple':
            plan['execution_steps'] = self._generate_sequential_steps(
                components['start'], components['end']
            )
            plan['execution_mode'] = components.get('mode', ExecutionMode.SEQUENTIAL)
        
        elif parsed_notation['notation_type'] == 'branched':
            plan['execution_steps'] = self._generate_branched_steps(components['branches'])
            plan['execution_mode'] = ExecutionMode.PARALLEL
        
        elif parsed_notation['notation_type'] == 'conditional':
            plan['execution_steps'] = self._generate_conditional_steps(
                components['start'], components['end'], components['condition']
            )
        
        elif parsed_notation['notation_type'] == 'looped':
            plan['execution_steps'] = self._generate_looped_steps(
                components['start'], components['end'], components['iterations']
            )
        
        elif parsed_notation['notation_type'] == 'parallel':
            plan['execution_steps'] = self._generate_parallel_steps(
                components['start'], components['end']
            )
            plan['execution_mode'] = ExecutionMode.PARALLEL
        
        elif parsed_notation['notation_type'] == 'staged':
            plan['execution_steps'] = self._generate_staged_steps(
                components['start'], components['end'], components['stages']
            )
            plan['execution_mode'] = ExecutionMode.STAGED
        
        # Add checkpoints at strategic points
        plan['checkpoints'] = self._plan_checkpoints(plan['execution_steps'])
        
        return plan
    
    def _generate_sequential_steps(self, start: int, end: int) -> List[Dict[str, Any]]:
        """Generate sequential execution steps"""
        steps = []
        for i in range(start, end + 1):
            steps.append({
                'step_id': f"step_{i}",
                'step_number': i,
                'execution_type': 'sequential',
                'dependencies': [f"step_{i-1}"] if i > start else [],
                'parallel_group': None
            })
        return steps
    
    def _generate_branched_steps(self, branches: List[BranchDefinition]) -> List[Dict[str, Any]]:
        """Generate steps for branched execution"""
        steps = []
        
        for branch in branches:
            for i in range(branch.start_step, branch.end_step + 1):
                steps.append({
                    'step_id': f"{branch.branch_id}_step_{i}",
                    'step_number': i,
                    'execution_type': 'branched',
                    'branch_id': branch.branch_id,
                    'execution_mode': branch.execution_mode,
                    'priority': branch.priority,
                    'timeout': branch.timeout,
                    'retry_count': branch.retry_count,
                    'dependencies': branch.dependencies,
                    'parallel_group': branch.branch_id
                })
        
        return steps
    
    def _generate_conditional_steps(self, start: int, end: int, condition: str) -> List[Dict[str, Any]]:
        """Generate conditional execution steps"""
        steps = []
        
        # Add condition evaluation step
        steps.append({
            'step_id': f"condition_eval",
            'step_number': start - 1,
            'execution_type': 'condition',
            'condition': condition,
            'dependencies': []
        })
        
        # Add conditional steps
        for i in range(start, end + 1):
            steps.append({
                'step_id': f"conditional_step_{i}",
                'step_number': i,
                'execution_type': 'conditional',
                'condition_dependency': 'condition_eval',
                'dependencies': [f"conditional_step_{i-1}"] if i > start else ['condition_eval']
            })
        
        return steps
    
    def _generate_looped_steps(self, start: int, end: int, iterations: int) -> List[Dict[str, Any]]:
        """Generate looped execution steps"""
        steps = []
        
        for iteration in range(iterations):
            for i in range(start, end + 1):
                steps.append({
                    'step_id': f"loop_{iteration}_step_{i}",
                    'step_number': i,
                    'execution_type': 'looped',
                    'iteration': iteration,
                    'total_iterations': iterations,
                    'dependencies': self._calculate_loop_dependencies(iteration, i, start, end)
                })
        
        return steps
    
    def _generate_parallel_steps(self, start: int, end: int) -> List[Dict[str, Any]]:
        """Generate parallel execution steps"""
        steps = []
        parallel_group = f"parallel_group_{start}_{end}"
        
        for i in range(start, end + 1):
            steps.append({
                'step_id': f"parallel_step_{i}",
                'step_number': i,
                'execution_type': 'parallel',
                'parallel_group': parallel_group,
                'dependencies': []  # No dependencies within parallel group
            })
        
        return steps
    
    def _generate_staged_steps(self, start: int, end: int, stages: int) -> List[Dict[str, Any]]:
        """Generate staged execution steps"""
        steps = []
        steps_per_stage = max(1, (end - start + 1) // stages)
        
        for stage in range(stages):
            stage_start = start + stage * steps_per_stage
            stage_end = min(start + (stage + 1) * steps_per_stage - 1, end)
            
            for i in range(stage_start, stage_end + 1):
                steps.append({
                    'step_id': f"stage_{stage}_step_{i}",
                    'step_number': i,
                    'execution_type': 'staged',
                    'stage': stage,
                    'total_stages': stages,
                    'dependencies': self._calculate_stage_dependencies(stage, i, stage_start)
                })
        
        return steps
    
    def _calculate_loop_dependencies(self, iteration: int, step: int, loop_start: int, loop_end: int) -> List[str]:
        """Calculate dependencies for looped steps"""
        dependencies = []
        
        if iteration > 0:
            # Depend on completion of previous iteration
            dependencies.append(f"loop_{iteration-1}_step_{loop_end}")
        
        if step > loop_start:
            # Depend on previous step in same iteration
            dependencies.append(f"loop_{iteration}_step_{step-1}")
        
        return dependencies
    
    def _calculate_stage_dependencies(self, stage: int, step: int, stage_start: int) -> List[str]:
        """Calculate dependencies for staged steps"""
        dependencies = []
        
        if stage > 0:
            # Depend on completion of previous stage
            dependencies.append(f"stage_{stage-1}_complete")
        
        if step > stage_start:
            # Depend on previous step in same stage
            dependencies.append(f"stage_{stage}_step_{step-1}")
        
        return dependencies
    
    def _plan_checkpoints(self, execution_steps: List[Dict[str, Any]]) -> List[str]:
        """Plan checkpoint locations in execution"""
        checkpoints = []
        
        # Add checkpoint at start
        checkpoints.append("execution_start")
        
        # Add checkpoints at regular intervals
        step_count = len(execution_steps)
        if step_count > 10:
            checkpoint_interval = step_count // 4  # 4 checkpoints
            for i in range(checkpoint_interval, step_count, checkpoint_interval):
                checkpoints.append(f"checkpoint_{i}")
        
        # Add checkpoint at end
        checkpoints.append("execution_complete")
        
        return checkpoints
    
    def _execute_plan(self, execution_plan: Dict[str, Any], symbolic_engine, execution_id: str) -> Dict[str, Any]:
        """Execute the planned chain execution"""
        execution_mode = execution_plan['execution_mode']
        execution_steps = execution_plan['execution_steps']
        
        if execution_mode == ExecutionMode.SEQUENTIAL:
            return self._execute_sequential(execution_steps, symbolic_engine, execution_id)
        elif execution_mode == ExecutionMode.PARALLEL:
            return self._execute_parallel(execution_steps, symbolic_engine, execution_id)
        elif execution_mode == ExecutionMode.STAGED:
            return self._execute_staged(execution_steps, symbolic_engine, execution_id)
        else:
            return self._execute_adaptive(execution_steps, symbolic_engine, execution_id)
    
    def _execute_sequential(self, steps: List[Dict[str, Any]], symbolic_engine, execution_id: str) -> Dict[str, Any]:
        """Execute steps sequentially"""
        results = []
        
        for step in steps:
            step_result = self._execute_single_step(step, symbolic_engine, execution_id)
            results.append(step_result)
            
            # Create checkpoint if needed
            if step['step_id'] in self.checkpoints:
                self._create_checkpoint(execution_id, step['step_id'], {'completed_steps': results})
        
        return {
            'execution_mode': 'sequential',
            'steps_completed': len(results),
            'results': results,
            'execution_id': execution_id
        }
    
    def _execute_parallel(self, steps: List[Dict[str, Any]], symbolic_engine, execution_id: str) -> Dict[str, Any]:
        """Execute steps in parallel"""
        results = []
        
        # Group steps by parallel group
        parallel_groups = {}
        for step in steps:
            group = step.get('parallel_group', 'default')
            if group not in parallel_groups:
                parallel_groups[group] = []
            parallel_groups[group].append(step)
        
        # Execute each group in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_step = {}
            
            for group_name, group_steps in parallel_groups.items():
                for step in group_steps:
                    future = executor.submit(self._execute_single_step, step, symbolic_engine, execution_id)
                    future_to_step[future] = step
            
            # Collect results as they complete
            for future in as_completed(future_to_step):
                step = future_to_step[future]
                try:
                    step_result = future.result()
                    results.append(step_result)
                except Exception as e:
                    results.append({
                        'step_id': step['step_id'],
                        'status': 'failed',
                        'error': str(e)
                    })
        
        return {
            'execution_mode': 'parallel',
            'parallel_groups': len(parallel_groups),
            'steps_completed': len(results),
            'results': sorted(results, key=lambda x: x.get('step_number', 0)),
            'execution_id': execution_id
        }
    
    def _execute_staged(self, steps: List[Dict[str, Any]], symbolic_engine, execution_id: str) -> Dict[str, Any]:
        """Execute steps in stages"""
        results = []
        
        # Group steps by stage
        stages = {}
        for step in steps:
            stage = step.get('stage', 0)
            if stage not in stages:
                stages[stage] = []
            stages[stage].append(step)
        
        # Execute stages sequentially
        for stage_num in sorted(stages.keys()):
            stage_steps = stages[stage_num]
            stage_results = []
            
            # Execute steps within stage (can be parallel)
            for step in stage_steps:
                step_result = self._execute_single_step(step, symbolic_engine, execution_id)
                stage_results.append(step_result)
            
            results.extend(stage_results)
            
            # Create checkpoint after each stage
            checkpoint_id = f"stage_{stage_num}_complete"
            self._create_checkpoint(execution_id, checkpoint_id, {'completed_stages': stage_num + 1})
        
        return {
            'execution_mode': 'staged',
            'stages_completed': len(stages),
            'steps_completed': len(results),
            'results': results,
            'execution_id': execution_id
        }
    
    def _execute_adaptive(self, steps: List[Dict[str, Any]], symbolic_engine, execution_id: str) -> Dict[str, Any]:
        """Execute steps with adaptive mode selection"""
        # Analyze steps to determine best execution strategy
        total_steps = len(steps)
        parallel_groups = len(set(step.get('parallel_group') for step in steps if step.get('parallel_group')))
        
        if parallel_groups > 1 and total_steps > 5:
            return self._execute_parallel(steps, symbolic_engine, execution_id)
        elif total_steps > 20:
            return self._execute_staged(steps, symbolic_engine, execution_id)
        else:
            return self._execute_sequential(steps, symbolic_engine, execution_id)
    
    def _execute_single_step(self, step: Dict[str, Any], symbolic_engine, execution_id: str) -> Dict[str, Any]:
        """Execute a single step"""
        step_start = time.time()
        
        try:
            step_number = step['step_number']
            
            # Use symbolic engine if available
            if symbolic_engine and hasattr(symbolic_engine, 'execute_chain'):
                # Execute single step through engine
                chain_results = symbolic_engine.execute_chain(step_number, step_number)
                if chain_results:
                    result = chain_results[0]
                else:
                    result = {'step': step_number, 'status': 'completed'}
            else:
                # Fallback execution
                result = {
                    'step': step_number,
                    'status': 'completed',
                    'execution_time': time.time() - step_start
                }
            
            # Add step metadata
            result.update({
                'step_id': step['step_id'],
                'execution_type': step.get('execution_type', 'unknown'),
                'execution_id': execution_id
            })
            
            return result
            
        except Exception as e:
            return {
                'step_id': step['step_id'],
                'step_number': step['step_number'],
                'status': 'failed',
                'error': str(e),
                'execution_time': time.time() - step_start,
                'execution_id': execution_id
            }
    
    def _create_checkpoint(self, execution_id: str, checkpoint_name: str, 
                          execution_state: Dict[str, Any]) -> ExecutionCheckpoint:
        """Create execution checkpoint"""
        checkpoint_id = f"{execution_id}_{checkpoint_name}"
        
        checkpoint = ExecutionCheckpoint(
            checkpoint_id=checkpoint_id,
            timestamp=time.time(),
            execution_state=execution_state,
            completed_steps=execution_state.get('completed_steps', []),
            current_step=execution_state.get('current_step'),
            execution_metadata={
                'execution_id': execution_id,
                'checkpoint_name': checkpoint_name
            }
        )
        
        self.checkpoints[checkpoint_id] = checkpoint
        self.execution_stats['checkpoints_created'] += 1
        
        return checkpoint
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Rollback execution to a specific checkpoint"""
        if checkpoint_id not in self.checkpoints:
            return {'error': f'Checkpoint {checkpoint_id} not found'}
        
        checkpoint = self.checkpoints[checkpoint_id]
        
        # Record rollback
        rollback_record = {
            'rollback_id': f"rollback_{int(time.time())}",
            'checkpoint_id': checkpoint_id,
            'rollback_timestamp': time.time(),
            'restored_state': checkpoint.execution_state
        }
        
        self.execution_stats['rollbacks_performed'] += 1
        
        return {
            'status': 'rolled_back',
            'checkpoint_id': checkpoint_id,
            'rollback_record': rollback_record,
            'restored_state': checkpoint.execution_state
        }
    
    def _update_execution_stats(self, execution_record: Dict[str, Any]):
        """Update execution statistics"""
        self.execution_stats['total_executions'] += 1
        
        execution_mode = execution_record['execution_plan']['execution_mode']
        if execution_mode == ExecutionMode.PARALLEL:
            self.execution_stats['parallel_executions'] += 1
        
        # Update average execution time
        total_executions = self.execution_stats['total_executions']
        current_avg = self.execution_stats['average_execution_time']
        new_time = execution_record['execution_time']
        
        self.execution_stats['average_execution_time'] = (
            (current_avg * (total_executions - 1) + new_time) / total_executions
        )
    
    def get_executor_statistics(self) -> Dict[str, Any]:
        """Get comprehensive executor statistics"""
        return {
            'execution_statistics': self.execution_stats.copy(),
            'active_executions': len(self.active_executions),
            'total_checkpoints': len(self.checkpoints),
            'execution_history_size': len(self.execution_history),
            'supported_notations': list(self.notation_patterns.keys()),
            'max_workers': self.max_workers
        }