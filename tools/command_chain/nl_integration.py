#!/usr/bin/env python3
"""
Natural Language Integration
=============================
Anchor: CMD-CHAIN-NL-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Parse commands from natural language chat messages.
Extract command chains from longer text.
Suggest command syntax based on intent.
Auto-format naked commands.

Features:
- Extract commands from conversational text
- Suggest commands based on natural language intent
- Auto-format incomplete commands
- Intent recognition and mapping
"""

import re
from dataclasses import dataclass
from typing import Dict, List

from .parser import CommandChainParser, ParseResult


@dataclass
class IntentMatch:
    """A matched intent with suggested command"""
    intent: str
    confidence: float
    suggested_command: str
    explanation: str


class NaturalLanguageIntegration:
    """
    Integrates command parsing with natural language.

    Features:
    - Extract commands from chat messages
    - Intent recognition
    - Command suggestion based on natural language
    - Auto-formatting for naked commands
    """

    # Intent patterns mapping natural language to commands
    INTENT_PATTERNS = {
        'seal': [
            r'\b(seal|lock|secure|finalize)\b',
            r'\bseal\s+(state|memory|system)\b',
        ],
        'verify': [
            r'\b(verify|check|validate|confirm|test)\b',
            r'\b(is|check)\s+(it|this)\s+(valid|correct|ok)\b',
        ],
        'deploy': [
            r'\b(deploy|launch|release|publish|ship)\b',
            r'\bpush\s+to\s+(production|prod)\b',
        ],
        'build': [
            r'\b(build|compile|make|construct)\b',
            r'\brun\s+(the\s+)?build\b',
        ],
        'test': [
            r'\b(test|run tests|execute tests)\b',
            r'\brun\s+test\s+suite\b',
        ],
        'status': [
            r'\b(status|state|health|check)\b',
            r'\b(what\'?s|how\'?s)\s+(the\s+)?(status|state)\b',
            r'\bhow\s+are\s+(things|we)\s+doing\b',
        ],
        'snapshot': [
            r'\b(snapshot|backup|save|checkpoint)\b',
            r'\bcreate\s+a\s+(backup|snapshot)\b',
        ],
        'restore': [
            r'\b(restore|recover|rollback|revert)\b',
            r'\bgo\s+back\s+to\b',
        ],
        '001': [
            r'\bimplement\s+(suggestion|option)\s+1\b',
            r'\bdo\s+(the\s+)?first\s+(one|suggestion)\b',
        ],
        '005': [
            r'\bimplement\s+all\b',
            r'\bdo\s+everything\b',
            r'\brun\s+all\s+suggestions\b',
        ],
        'BUP': [
            r'\b(reboot|restart|boot|initialize)\b',
            r'\bboot\s+up\b',
        ],
        'RESUME': [
            r'\b(resume|continue|proceed)\b',
            r'\bpick\s+up\s+where\b',
        ],
    }

    def __init__(self):
        self.parser = CommandChainParser()

    def extract_commands(self, text: str) -> ParseResult:
        """
        Extract commands from natural language text.

        Args:
            text: Natural language text that may contain commands

        Returns:
            ParseResult with found commands
        """
        return self.parser.parse(text)

    def suggest_commands(self, text: str, max_suggestions: int = 3) -> List[IntentMatch]:
        """
        Suggest commands based on natural language intent.

        Args:
            text: Natural language text describing intent
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of IntentMatch objects with suggestions
        """
        text_lower = text.lower()
        matches = []

        for command, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    # Calculate confidence based on pattern specificity
                    confidence = 0.7 if len(pattern) > 20 else 0.5

                    matches.append(IntentMatch(
                        intent=command,
                        confidence=confidence,
                        suggested_command=f'#{command}//.',
                        explanation=f'Detected intent to {command}'
                    ))
                    break  # Only match once per command

        # Sort by confidence and return top matches
        matches.sort(key=lambda x: x.confidence, reverse=True)
        return matches[:max_suggestions]

    def auto_format(self, text: str) -> str:
        """
        Auto-format naked commands found in text.

        Converts: "I want to #deploy" -> "I want to #deploy//."

        Args:
            text: Text potentially containing naked commands

        Returns:
            Text with auto-formatted commands
        """
        # Find naked commands
        result = self.parser.parse(text)

        if not result.naked_commands:
            return text

        # Replace naked commands with formatted versions
        formatted_text = text
        for cmd in result.naked_commands:
            # Replace #command with #command//.
            naked_pattern = f'#{cmd.name}(?!//\\.)'
            formatted_pattern = f'#{cmd.name}//.'
            formatted_text = re.sub(naked_pattern, formatted_pattern, formatted_text)

        return formatted_text

    def extract_and_suggest(self, text: str) -> Dict:
        """
        Extract commands and provide suggestions for natural language.

        Args:
            text: Text to analyze

        Returns:
            Dict with extracted commands and suggestions
        """
        # Extract existing commands
        extracted = self.extract_commands(text)

        # Get intent suggestions
        suggestions = self.suggest_commands(text)

        return {
            'extracted_commands': [cmd.name for cmd in extracted.commands],
            'naked_commands': [cmd.name for cmd in extracted.naked_commands],
            'has_errors': extracted.has_errors,
            'suggestions': [
                {
                    'intent': s.intent,
                    'confidence': s.confidence,
                    'command': s.suggested_command,
                    'explanation': s.explanation
                }
                for s in suggestions
            ]
        }

    def parse_conversation(self, messages: List[str]) -> List[ParseResult]:
        """
        Parse multiple conversation messages for commands.

        Args:
            messages: List of conversation messages

        Returns:
            List of ParseResult objects, one per message
        """
        return [self.extract_commands(msg) for msg in messages]

    def format_command_help(self, naked_command: str) -> str:
        """
        Generate helpful message for naked command.

        Args:
            naked_command: Name of naked command (without #)

        Returns:
            Helpful formatting message
        """
        return (
            f"Almost there! To execute #{naked_command}, add the safety "
            f"terminator: #{naked_command}//.\n\n"
            f"This ensures you really mean to run the command."
        )


def demo():
    """Demonstration of natural language integration"""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Natural Language Integration - Demonstration           ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    nl = NaturalLanguageIntegration()

    # Test 1: Extract commands from conversation
    print("Test 1: Extract Commands from Text")
    text = "Please run #seal//. and then #verify//. the results"
    result = nl.extract_commands(text)
    print(f"Input: {text}")
    print(f"Extracted: {[c.name for c in result.commands]}")
    print()

    # Test 2: Suggest commands from intent
    print("Test 2: Suggest Commands from Intent")
    text = "I need to deploy the system and verify everything is ok"
    suggestions = nl.suggest_commands(text)
    print(f"Input: {text}")
    print("Suggestions:")
    for s in suggestions:
        print(f"  • {s.suggested_command} ({s.confidence:.0%} confidence)")
    print()

    # Test 3: Auto-format naked commands
    print("Test 3: Auto-format Naked Commands")
    text = "Can you #deploy for me?"
    formatted = nl.auto_format(text)
    print(f"Original:  {text}")
    print(f"Formatted: {formatted}")
    print()

    # Test 4: Extract and suggest combined
    print("Test 4: Extract and Suggest Combined")
    text = "Please #seal and then verify the deployment"
    analysis = nl.extract_and_suggest(text)
    print(f"Input: {text}")
    print(f"Naked commands: {analysis['naked_commands']}")
    print(f"Suggestions: {[s['command'] for s in analysis['suggestions']]}")
    print()


if __name__ == "__main__":
    demo()
