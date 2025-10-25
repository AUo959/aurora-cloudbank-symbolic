#!/usr/bin/env python3
"""
Command Chain Parser Tests
===========================
Anchor: CMD-CHAIN-TEST-001
Team: AUo959-team

Comprehensive test suite for command chain parser.
"""

import sys
from pathlib import Path

import pytest

from tools.command_chain.parser import Command, CommandChainParser, ParseResult

# Add project root to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestCommandChainParser:
    """Test command chain parser functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = CommandChainParser()
    
    def test_valid_single_command(self):
        """Test parsing single valid command"""
        result = self.parser.parse("#seal//.")
        
        assert len(result.commands) == 1
        assert result.commands[0].name == "seal"
        assert result.commands[0].is_valid is True
        assert len(result.naked_commands) == 0
        assert result.has_errors is False
    
    def test_valid_multiple_commands(self):
        """Test parsing multiple valid commands"""
        result = self.parser.parse("#seal//. #verify//. #deploy//.")
        
        assert len(result.commands) == 3
        assert [c.name for c in result.commands] == ["seal", "verify", "deploy"]
        assert all(c.is_valid for c in result.commands)
        assert len(result.naked_commands) == 0
        assert result.has_errors is False
    
    def test_naked_command_single(self):
        """Test detection of single naked command"""
        result = self.parser.parse("#seal")
        
        assert len(result.commands) == 0
        assert len(result.naked_commands) == 1
        assert result.naked_commands[0].name == "seal"
        assert result.naked_commands[0].is_valid is False
        assert result.has_errors is True
        # Dynamic message - just check it exists and has key info
        assert "#seal" in result.naked_commands[0].error_message
        assert "//." in result.naked_commands[0].error_message
    
    def test_naked_command_multiple(self):
        """Test detection of multiple naked commands"""
        result = self.parser.parse("#seal #verify #deploy")
        
        assert len(result.commands) == 0
        assert len(result.naked_commands) == 3
        assert [c.name for c in result.naked_commands] == ["seal", "verify", "deploy"]
        assert all(not c.is_valid for c in result.naked_commands)
        assert result.has_errors is True
    
    def test_mixed_valid_and_naked(self):
        """Test parsing mix of valid and naked commands"""
        result = self.parser.parse("#seal//. #verify #deploy//.")
        
        assert len(result.commands) == 2
        assert len(result.naked_commands) == 1
        assert [c.name for c in result.commands] == ["seal", "deploy"]
        assert result.naked_commands[0].name == "verify"
        assert result.has_errors is True
    
    def test_commands_in_text(self):
        """Test parsing commands embedded in text"""
        result = self.parser.parse("Please run #seal//. and then #verify//. for me")
        
        assert len(result.commands) == 2
        assert [c.name for c in result.commands] == ["seal", "verify"]
        assert len(result.naked_commands) == 0
        assert result.has_errors is False
    
    def test_naked_command_in_text(self):
        """Test detecting naked command in text"""
        result = self.parser.parse("Can you #seal this for me?")
        
        assert len(result.commands) == 0
        assert len(result.naked_commands) == 1
        assert result.naked_commands[0].name == "seal"
        assert result.has_errors is True
    
    def test_no_commands(self):
        """Test input with no commands"""
        result = self.parser.parse("This is regular text without commands")
        
        assert len(result.commands) == 0
        assert len(result.naked_commands) == 0
        assert result.has_errors is False
    
    def test_unsupported_command(self):
        """Test unsupported command with proper terminator"""
        result = self.parser.parse("#invalid_cmd//.")
        
        assert len(result.commands) == 1
        assert result.commands[0].is_valid is False
        assert "Unknown command" in result.commands[0].error_message
        assert result.has_errors is True
    
    def test_validate_command_chain_valid(self):
        """Test validating valid command chain"""
        is_valid, errors = self.parser.validate_command_chain("#seal//. #verify//.")
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_command_chain_invalid(self):
        """Test validating invalid command chain"""
        is_valid, errors = self.parser.validate_command_chain("#seal #verify")
        
        assert is_valid is False
        assert len(errors) == 2
    
    def test_extract_valid_commands(self):
        """Test extracting only valid commands"""
        commands = self.parser.extract_valid_commands("#seal//. #verify #deploy//.")
        
        assert commands == ["seal", "deploy"]
    
    def test_generate_command_hash(self):
        """Test generating command chain hash"""
        cmd_hash = self.parser.generate_command_hash(["seal", "verify", "deploy"])
        
        assert len(cmd_hash) == 64  # SHA-256 produces 64 hex characters
        assert cmd_hash.isalnum()  # Should be hexadecimal
    
    def test_format_command_chain(self):
        """Test formatting command chain"""
        chain = self.parser.format_command_chain(["seal", "verify", "deploy"])
        
        assert chain == "#seal//. #verify//. #deploy//."
    
    def test_get_supported_commands(self):
        """Test getting supported commands list"""
        commands = self.parser.get_supported_commands()
        
        assert isinstance(commands, list)
        assert len(commands) > 0
        assert "seal" in commands
        assert "verify" in commands
        assert "deploy" in commands
    
    def test_add_command(self):
        """Test adding new command"""
        initial_count = len(self.parser.SUPPORTED_COMMANDS)
        
        # Add valid command
        result = self.parser.add_command("newcmd")
        assert result is True
        assert "newcmd" in self.parser.SUPPORTED_COMMANDS
        assert len(self.parser.SUPPORTED_COMMANDS) == initial_count + 1
        
        # Try to add invalid command
        result = self.parser.add_command("invalid-name")
        assert result is False
    
    def test_error_message_format(self):
        """Test that error messages contain essential elements"""
        result = self.parser.parse("#seal")
        
        error_msg = result.naked_commands[0].error_message
        
        # Check for essential elements (dynamic content)
        assert "#seal" in error_msg
        assert "//." in error_msg
        assert "What you typed" in error_msg or "What it needs" in error_msg
        
        # Should be natural and conversational
        assert len(error_msg) > 50  # Substantial message
        assert len(error_msg) < 500  # Not overwhelming
    
    def test_command_position_tracking(self):
        """Test that command positions are tracked"""
        result = self.parser.parse("Hello #seal//. world #verify//.")
        
        assert len(result.commands) == 2
        assert result.commands[0].position == 6  # Position of first #
        assert result.commands[1].position == 21  # Position of second #
    
    def test_complex_chain_with_punctuation(self):
        """Test parsing commands with surrounding punctuation"""
        result = self.parser.parse("Run #seal//.? Then #verify//., finally #deploy//.!")
        
        assert len(result.commands) == 3
        assert all(c.is_valid for c in result.commands)
        assert len(result.naked_commands) == 0
    
    def test_case_sensitivity(self):
        """Test that command names are case-sensitive"""
        # Lowercase should work
        result1 = self.parser.parse("#seal//.")
        assert len(result1.commands) == 1
        assert result1.commands[0].is_valid is True
        
        # Uppercase won't match supported commands
        result2 = self.parser.parse("#SEAL//.")
        assert len(result2.commands) == 1
        assert result2.commands[0].is_valid is False
    
    def test_command_with_underscores(self):
        """Test commands with underscores in name"""
        # Add command with underscore
        self.parser.add_command("test_cmd")
        
        result = self.parser.parse("#test_cmd//.")
        assert len(result.commands) == 1
        assert result.commands[0].name == "test_cmd"
        assert result.commands[0].is_valid is True
    
    def test_hash_consistency(self):
        """Test that hash generation is consistent"""
        commands = ["seal", "verify", "deploy"]
        
        hash1 = self.parser.generate_command_hash(commands)
        hash2 = self.parser.generate_command_hash(commands)
        
        assert hash1 == hash2
    
    def test_hash_uniqueness(self):
        """Test that different chains produce different hashes"""
        hash1 = self.parser.generate_command_hash(["seal", "verify"])
        hash2 = self.parser.generate_command_hash(["verify", "seal"])
        hash3 = self.parser.generate_command_hash(["seal", "deploy"])
        
        assert hash1 != hash2  # Order matters
        assert hash1 != hash3  # Commands matter
        assert hash2 != hash3


class TestCommandDataclass:
    """Test Command dataclass"""
    
    def test_command_creation(self):
        """Test creating Command object"""
        cmd = Command(
            name="seal",
            raw="#seal//.",
            is_valid=True,
            position=0
        )
        
        assert cmd.name == "seal"
        assert cmd.raw == "#seal//."
        assert cmd.is_valid is True
        assert cmd.position == 0
        assert cmd.error_message is None
    
    def test_command_with_error(self):
        """Test Command with error message"""
        cmd = Command(
            name="seal",
            raw="#seal",
            is_valid=False,
            position=0,
            error_message="Missing terminator"
        )
        
        assert cmd.error_message == "Missing terminator"


class TestParseResultDataclass:
    """Test ParseResult dataclass"""
    
    def test_parse_result_creation(self):
        """Test creating ParseResult object"""
        result = ParseResult(
            commands=[],
            naked_commands=[],
            has_errors=False,
            error_messages=[],
            raw_input="test"
        )
        
        assert result.commands == []
        assert result.naked_commands == []
        assert result.has_errors is False
        assert result.error_messages == []
        assert result.raw_input == "test"


@pytest.mark.integration
class TestCommandChainIntegration:
    """Integration tests for command chain parser"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = CommandChainParser()
    
    def test_end_to_end_valid_chain(self):
        """Test complete workflow with valid chain"""
        input_text = "Execute #seal//. #verify//. #deploy//."
        
        # Parse
        result = self.parser.parse(input_text)
        assert not result.has_errors
        
        # Extract
        commands = self.parser.extract_valid_commands(input_text)
        assert commands == ["seal", "verify", "deploy"]
        
        # Hash
        cmd_hash = self.parser.generate_command_hash(commands)
        assert len(cmd_hash) == 64
        
        # Format
        chain = self.parser.format_command_chain(commands)
        assert chain == "#seal//. #verify//. #deploy//."
    
    def test_end_to_end_naked_detection(self):
        """Test complete workflow with naked commands"""
        input_text = "Please #seal and #verify"
        
        # Parse
        result = self.parser.parse(input_text)
        assert result.has_errors
        assert len(result.naked_commands) == 2
        
        # Validate
        is_valid, errors = self.parser.validate_command_chain(input_text)
        assert not is_valid
        assert len(errors) == 2
        
        # Each error should be helpful and contain essential info
        for error in errors:
            assert "//." in error
            assert len(error) > 50  # Substantial guidance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
