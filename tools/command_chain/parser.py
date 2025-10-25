#!/usr/bin/env python3
"""
Command Chain Parser
====================
Anchor: CMD-CHAIN-PARSER-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Parses unified command syntax: #command//.
Supports word commands, numeric codes, and system verbs.
Safety: Commands without //. terminator are NOT executed.
Instead, system provides helpful guidance.

Pattern Examples:
  ✅ Valid:   #seal//.
  ✅ Valid:   #001//. (numeric alias)
  ✅ Valid:   #BUP//. (system verb)
  ✅ Valid:   #verify//. #deploy//.
  ❌ Naked:   #seal (missing terminator)
  ❌ Naked:   #001 (missing terminator)
  ❌ Naked:   #BUP (missing terminator)

Aurora Codex v2.5 Standardization:
  All commands now use consistent #COMMAND//. syntax
  - User macros: #001//., #025//., #999//.
  - System verbs: #BUP//., #RESUME//., #THREADSYNC//.
  - Operations: #seal//., #deploy//., #test//.
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

    Command Syntax (Aurora Codex v2.5 Unified Standard):
    - Valid: #command//.
    - Supports: Word commands, numeric codes, system verbs
    - Examples: #seal//., #001//., #BUP//.
    - Naked: #command (no terminator) - triggers helpful error

    Safety Features:
    - Commands without //. terminator are NEVER executed
    - Helpful guidance provided for malformed commands
    - Command validation with DLP tracking
    """
    
    # Valid command pattern: #word//. or #NNN//.
    # Supports: #seal//., #001//., #BUP//., etc.
    VALID_COMMAND_PATTERN = r'#([a-zA-Z0-9_]+)//\.'
    
    # Naked command pattern: #word or #NNN (no //. terminator)
    NAKED_COMMAND_PATTERN = r'#([a-zA-Z0-9_]+)(?!//\.)'
    
    # Supported commands (extensible)
    SUPPORTED_COMMANDS = {
        # Core operations
        'seal', 'verify', 'deploy', 'snapshot', 'restore',
        'status', 'sync', 'test', 'build', 'clean',
        'anchor', 'validate', 'export', 'import', 'commit',
        
        # Numeric aliases (Aurora Codex v2.5)
        '001', '002', '003', '004', '005', '006', '007', '008',
        '025', '080', '717', '808', '999',
        
        # System verbs (standardized to # prefix)
        'THREADSYNC', 'TAGTRACE', 'TAGPATCH', 'SYNCANCHORS', 'RESTOREMAP',
        'REBUILDRECOVERY', 'LOCKMEM', 'T1', 'EXPORTTHREAD',
        'DIAGNOW', 'RESETCORE', 'SENTRYSTAT', 'SUP', 'OPTISEED',
        'PULSEWALK', 'CLEANDEPLOY', 'SANDDROP', 'THREADWAKE',
        'RESUME', 'BUP',
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
        Generate natural, contextual error message for naked commands.
        
        Guidelines maintained:
        - Clever and almost sarcastic
        - Helpful without being preachy
        - Enhances rather than hinders
        - Conversational and in rhythm
        
        Args:
            cmd_name: Name of the command without terminator
            
        Returns:
            Contextual error message
        """
        # Natural variations that flow with context - no template bank
        import random
        
        # Command-specific context awareness
        is_destructive = cmd_name in ('deploy', 'clean', 'restore', 'commit')
        is_critical = cmd_name in ('seal', 'validate', 'verify', 'anchor')
        
        # Build message naturally based on command context
        if is_destructive:
            opener = f"Whoa there! #{cmd_name} needs confirmation first."
            safety_note = "You wouldn't hit 'delete all' without a safety check, right?"
        elif is_critical:
            opener = f"Hold up - #{cmd_name} is missing something important."
            safety_note = "Critical commands need the full handshake."
        else:
            opener = f"Almost there! #{cmd_name} is incomplete."
            safety_note = "Commands need their safety terminator to execute."
        
        # Natural flow, not template
        fix_lead = random.choice([
            "The fix?",
            "Easy fix:",
            "Just add:",
            "Here's what you need:",
        ])
        
        confirmation = random.choice([
            "That //. at the end? Think of it as the 'I'm sure' button.",
            "The //. terminator means 'yes, really execute this.'",
            "Those three characters (//.) are your commit gesture.",
            "The //. is your safety cover - lift it to press the button.",
        ])
        
        # Compose naturally
        message = f"""
{opener}

{safety_note}

{fix_lead}
  What you typed:  #{cmd_name}
  What it needs:   #{cmd_name}//.

{confirmation}
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
