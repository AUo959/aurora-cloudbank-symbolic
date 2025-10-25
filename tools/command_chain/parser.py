#!/usr/bin/env python3
"""
Command Chain Parser
====================
Anchor: CMD-CHAIN-PARSER-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Parses command syntax: #command//.
Safety: Commands without //. terminator are NOT executed.
Instead, system provides helpful guidance.

Pattern Examples:
  ✅ Valid:   #seal//.
  ✅ Valid:   #verify//. #deploy//.
  ❌ Naked:   #seal (missing terminator)
  ❌ Naked:   #verify (missing terminator)
"""

import hashlib
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Command:
    """Represents a parsed command"""
    name: str
    raw: str
    is_valid: bool
    position: int
    error_message: Optional[str] = None


@dataclass
class ParseResult:
    """Result of parsing command chain"""
    commands: List[Command]
    naked_commands: List[Command]
    has_errors: bool
    error_messages: List[str]
    raw_input: str


class CommandChainParser:
    """
    Parses command chains with safety validation.
    
    Command Syntax:
    - Valid: #command//.
    - Naked: #command (no terminator) - triggers helpful error
    
    Safety Features:
    - Commands without //. terminator are NEVER executed
    - Helpful guidance provided for malformed commands
    - Command validation with DLP tracking
    """
    
    # Valid command pattern: #word//.
    VALID_COMMAND_PATTERN = r'#([a-zA-Z_][a-zA-Z0-9_]*)//\.'
    
    # Naked command pattern: #word (no //. terminator)
    NAKED_COMMAND_PATTERN = r'#([a-zA-Z_][a-zA-Z0-9_]*)(?!//\.)'
    
    # Supported commands (extensible)
    SUPPORTED_COMMANDS = {
        'seal', 'verify', 'deploy', 'snapshot', 'restore',
        'status', 'sync', 'test', 'build', 'clean',
        'anchor', 'validate', 'export', 'import', 'commit'
    }
    
    def __init__(self):
        self.valid_pattern = re.compile(self.VALID_COMMAND_PATTERN)
        self.naked_pattern = re.compile(self.NAKED_COMMAND_PATTERN)
    
    def parse(self, input_text: str) -> ParseResult:
        """
        Parse input text for command chains.
        
        Args:
            input_text: Text potentially containing commands
            
        Returns:
            ParseResult with commands and validation status
        """
        commands = []
        naked_commands = []
        error_messages = []
        
        # Find all valid commands
        for match in self.valid_pattern.finditer(input_text):
            cmd_name = match.group(1)
            cmd = Command(
                name=cmd_name,
                raw=match.group(0),
                is_valid=True,
                position=match.start()
            )
            
            # Validate command is supported
            if cmd_name not in self.SUPPORTED_COMMANDS:
                cmd.is_valid = False
                cmd.error_message = f"Unknown command: {cmd_name}"
                error_messages.append(cmd.error_message)
            
            commands.append(cmd)
        
        # Find all naked commands (missing terminator)
        for match in self.naked_pattern.finditer(input_text):
            cmd_name = match.group(1)
            
            # Skip if this position is already a valid command
            if any(c.position == match.start() for c in commands):
                continue
            
            cmd = Command(
                name=cmd_name,
                raw=match.group(0),
                is_valid=False,
                position=match.start(),
                error_message=self._generate_naked_command_message(cmd_name)
            )
            naked_commands.append(cmd)
            error_messages.append(cmd.error_message)
        
        has_errors = len(error_messages) > 0
        
        return ParseResult(
            commands=commands,
            naked_commands=naked_commands,
            has_errors=has_errors,
            error_messages=error_messages,
            raw_input=input_text
        )
    
    def _generate_naked_command_message(self, cmd_name: str) -> str:
        """
        Generate helpful error message for naked commands.
        
        Args:
            cmd_name: Name of the command without terminator
            
        Returns:
            Helpful error message guiding user
        """
        message = f"""
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️  Incomplete Command Detected                                 ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Found: #{cmd_name}                                               ║
║  Status: Not quite ready for launch                             ║
║                                                                  ║
║  Commands need their safety terminator. You know, like how      ║
║  you wouldn't press a big red button without the safety cover.  ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  The Fix (it's easier than you think)                           ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  What you typed:  #{cmd_name}                                     ║
║  What I need:     #{cmd_name}//.                                  ║
║                                                                  ║
║  That's it. Just add //. at the end.                            ║
║  Think of it as the "yes, I really mean this" button.           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        return message.strip()
    
    def validate_command_chain(self, input_text: str) -> Tuple[bool, List[str]]:
        """
        Validate entire command chain.
        
        Args:
            input_text: Command chain to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        result = self.parse(input_text)
        return (not result.has_errors, result.error_messages)
    
    def extract_valid_commands(self, input_text: str) -> List[str]:
        """
        Extract only valid, executable commands.
        
        Args:
            input_text: Text containing commands
            
        Returns:
            List of valid command names
        """
        result = self.parse(input_text)
        return [cmd.name for cmd in result.commands if cmd.is_valid]
    
    def generate_command_hash(self, commands: List[str]) -> str:
        """
        Generate SHA-256 hash of command chain for DLP tracking.
        
        Args:
            commands: List of command names
            
        Returns:
            SHA-256 hash of command chain
        """
        chain_str = "//".join(commands)
        return hashlib.sha256(chain_str.encode()).hexdigest()
    
    def format_command_chain(self, commands: List[str]) -> str:
        """
        Format command list as proper command chain.
        
        Args:
            commands: List of command names
            
        Returns:
            Properly formatted command chain string
        """
        return " ".join(f"#{cmd}//." for cmd in commands)
    
    def get_supported_commands(self) -> List[str]:
        """Return list of supported commands"""
        return sorted(self.SUPPORTED_COMMANDS)
    
    def add_command(self, command_name: str) -> bool:
        """
        Add new command to supported commands.
        
        Args:
            command_name: Name of command to add
            
        Returns:
            True if added successfully
        """
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', command_name):
            return False
        
        self.SUPPORTED_COMMANDS.add(command_name)
        return True


def demo():
    """Demonstration of command chain parser"""
    parser = CommandChainParser()
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Command Chain Parser - Safety Demonstration            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    # Test cases
    test_cases = [
        "Please run #seal//. and then #verify//.?",
        "I want to #deploy but forgot the terminator",
        "#snapshot//. #restore//. #validate//.?",
        "Can you #seal this for me?",
        "Execute #build//. #test//. #deploy//.?",
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"Input: {test_input}")
        print()
        
        result = parser.parse(test_input)
        
        if result.commands:
            print(f"✅ Valid Commands Found: {len(result.commands)}")
            for cmd in result.commands:
                print(f"   • {cmd.raw} → {cmd.name}")
        
        if result.naked_commands:
            print(f"⚠️  Naked Commands Found: {len(result.naked_commands)}")
            for cmd in result.naked_commands:
                print(cmd.error_message)
        
        if not result.commands and not result.naked_commands:
            print("ℹ️  No commands detected in input")
        
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    demo()
