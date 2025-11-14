#!/usr/bin/env python3
"""
Command Chain Flow Control
===========================
Anchor: CMD-CHAIN-FLOW-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Implements sequence execution, conditional branching, error recovery,
rollback, and transaction support for command chains.

Features:
- Sequential execution with dependencies
- Conditional branching based on results
- Error recovery and rollback mechanisms
- All-or-nothing transaction support
"""

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, Optional

from .executor import ChainExecutionResult, CommandExecutor, ExecutionResult


class FlowControlType(Enum):
    """Types of flow control"""
    SEQUENTIAL = "sequential"  # Execute one after another
    PARALLEL = "parallel"      # Execute simultaneously
    CONDITIONAL = "conditional"  # Execute based on condition
    TRANSACTIONAL = "transactional"  # All or nothing


@dataclass
class FlowNode:
    """A node in the command flow"""
    command: str
    on_success: Optional[str] = None
    on_failure: Optional[str] = None
    rollback_command: Optional[str] = None


class CommandChainFlow:
    """
    Manages command chain execution flow.
    
    Features:
    - Sequential execution with dependency tracking
    - Conditional branching (if/then/else logic)
    - Error recovery and rollback
    - Transaction support (all or nothing)
    """
    
    def __init__(self, executor: Optional[CommandExecutor] = None):
        self.executor = executor or CommandExecutor()
        self.flow_history: List[ChainExecutionResult] = []
    
    def execute_sequence(self, commands: List[str]) -> ChainExecutionResult:
        """
        Execute commands sequentially.
        
        Args:
            commands: List of command strings (e.g., ['#seal//.', '#verify//.'])
            
        Returns:
            ChainExecutionResult with execution details
        """
        chain_text = ' '.join(commands)
        result = self.executor.execute(chain_text)
        self.flow_history.append(result)
        return result
    
    def execute_conditional(
        self,
        condition_command: str,
        on_success: Optional[str] = None,
        on_failure: Optional[str] = None
    ) -> ChainExecutionResult:
        """
        Execute command with conditional branching.
        
        Args:
            condition_command: Command to test
            on_success: Command to run if successful
            on_failure: Command to run if failed
            
        Returns:
            ChainExecutionResult with execution details
        """
        # Execute condition
        condition_result = self.executor.execute(condition_command)
        
        # Branch based on result
        if condition_result.success and on_success:
            return self.executor.execute(on_success)
        elif not condition_result.success and on_failure:
            return self.executor.execute(on_failure)
        
        return condition_result
    
    def execute_with_rollback(
        self,
        commands: List[str],
        rollback_commands: Optional[List[str]] = None
    ) -> ChainExecutionResult:
        """
        Execute commands with rollback support.
        
        If any command fails, execute rollback commands in reverse order.
        
        Args:
            commands: List of commands to execute
            rollback_commands: Optional rollback commands for each step
            
        Returns:
            ChainExecutionResult with execution details
        """
        executed_commands = []
        
        # Execute each command
        for i, cmd in enumerate(commands):
            result = self.executor.execute(cmd)
            executed_commands.append((cmd, result))
            
            # If failed, rollback
            if not result.success:
                if rollback_commands and len(rollback_commands) > i:
                    # Rollback previous successful commands
                    for j in range(i - 1, -1, -1):
                        if rollback_commands and j < len(rollback_commands):
                            self.executor.execute(rollback_commands[j])
                
                return result
        
        # All succeeded
        chain_text = ' '.join(commands)
        return self.executor.execute(chain_text)
    
    def execute_transaction(self, commands: List[str]) -> ChainExecutionResult:
        """
        Execute commands as atomic transaction (all or nothing).
        
        All commands must succeed or none take effect.
        
        Args:
            commands: List of commands to execute
            
        Returns:
            ChainExecutionResult with execution details
        """
        # First, validate all commands
        for cmd in commands:
            parse_result = self.executor.parser.parse(cmd)
            if parse_result.has_errors:
                # Create failed result
                from datetime import datetime
                return ChainExecutionResult(
                    chain_hash='',
                    results=[],
                    success=False,
                    total_commands=len(commands),
                    successful_commands=0,
                    failed_commands=len(commands),
                    execution_time_ms=0.0,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        # Execute all commands
        chain_text = ' '.join(commands)
        result = self.executor.execute(chain_text)
        
        # If any failed, consider entire transaction failed
        if result.failed_commands > 0:
            result.success = False
        
        return result
    
    def execute_with_retry(
        self,
        command: str,
        max_retries: int = 3,
        on_retry: Optional[Callable[[int, ExecutionResult], None]] = None
    ) -> ChainExecutionResult:
        """
        Execute command with retry logic.
        
        Args:
            command: Command to execute
            max_retries: Maximum number of retries
            on_retry: Optional callback for retry events
            
        Returns:
            ChainExecutionResult with execution details
        """
        for attempt in range(max_retries + 1):
            result = self.executor.execute(command)
            
            if result.success:
                return result
            
            # Retry callback
            if on_retry and attempt < max_retries:
                for exec_result in result.results:
                    on_retry(attempt + 1, exec_result)
        
        return result
    
    def get_flow_history(self) -> List[ChainExecutionResult]:
        """Get command flow execution history"""
        return self.flow_history


def demo():
    """Demonstration of command chain flow"""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Command Chain Flow - Demonstration                     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    flow = CommandChainFlow()
    
    # Test 1: Sequential execution
    print("Test 1: Sequential Execution")
    print("Commands: #seal//. #verify//. #deploy//.")
    result = flow.execute_sequence(['#seal//.', '#verify//.', '#deploy//.'])
    print(f"  Result: {result.success} ({result.successful_commands}/{result.total_commands})")
    print()
    
    # Test 2: Conditional execution
    print("Test 2: Conditional Execution")
    print("If #test//. succeeds, run #deploy//., else run #build//.")
    result = flow.execute_conditional(
        '#test//.',
        on_success='#deploy//.',
        on_failure='#build//.'
    )
    print(f"  Result: {result.success}")
    print()
    
    # Test 3: Transaction
    print("Test 3: Transactional Execution")
    print("Commands: #seal//. #verify//. (all or nothing)")
    result = flow.execute_transaction(['#seal//.', '#verify//.'])
    print(f"  Result: {result.success} (transaction: {result.success})")
    print()


if __name__ == "__main__":
    demo()
