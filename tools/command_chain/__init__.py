"""
Command Chain Parser Package
=============================
Anchor: CMD-CHAIN-PKG-001
Team: AUo959-team

Provides command chain parsing with safety validation.
Commands require //. terminator to execute.
"""

from tools.command_chain.parser import (
    CommandChainParser,
    Command,
    ParseResult
)

__version__ = "1.0.0"
__all__ = ["CommandChainParser", "Command", "ParseResult"]
