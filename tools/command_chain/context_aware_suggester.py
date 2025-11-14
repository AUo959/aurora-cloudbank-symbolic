#!/usr/bin/env python3
"""
Context-Aware Command Suggester
================================
Anchor: CMD-CHAIN-SUGGESTER-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Intelligent system that:
1. Monitors conversation context and repo state
2. Auto-executes commands behind the scenes when optimal
3. Suggests command chains to user with symbolic aliases
4. Routes commands smartly: transparent vs user-facing

Philosophy:
- Commands work FOR the user, not just BY the user
- Suggest when helpful, execute when transparent
- Use symbolic aliases (#001//., #QUICKFIX//.) for clarity
- Context-aware: same intent, different commands based on state

Pattern:
  Detect Context → Analyze Intent → Auto-Execute OR Suggest → Track Results
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ExecutionMode(Enum):
    """How to execute a command"""
    AUTO_BEHIND_SCENES = "auto"      # Execute transparently, report results
    SUGGEST_TO_USER = "suggest"      # Offer as option with symbolic alias
    ASK_PERMISSION = "ask"           # Ask before executing
    BOTH = "both"                    # Execute + tell user what was done


class ContextTrigger(Enum):
    """What triggered the command suggestion"""
    USER_REQUEST = "user_request"           # User explicitly asked
    CODE_QUALITY_ISSUE = "code_quality"     # Detected linting/format issues
    TEST_FAILURE = "test_failure"           # Tests failed
    GIT_STATE_CHANGE = "git_change"         # Git status changed
    DEPLOYMENT_READY = "deploy_ready"       # Ready to deploy
    PERFORMANCE_ISSUE = "performance"       # Performance degradation
    SECURITY_RISK = "security"              # Security vulnerability
    DOCUMENTATION_GAP = "docs_missing"      # Missing documentation
    DEPENDENCY_UPDATE = "deps_outdated"     # Dependencies need update


@dataclass
class CommandSuggestion:
    """A suggested command or command chain"""
    commands: List[str]                    # Command chain
    symbolic_alias: str                    # User-friendly alias (#QUICKFIX//.)
    reason: str                            # Why this is suggested
    execution_mode: ExecutionMode          # How to execute
    trigger: ContextTrigger                # What triggered it
    confidence: float                      # 0.0-1.0 confidence score
    expected_outcome: str                  # What will happen
    estimated_time: str                    # How long it takes


class ContextAwareSuggester:
    """
    Intelligent command suggestion and auto-execution system.
    
    Monitors conversation context and repo state to:
    - Auto-execute optimal commands behind the scenes
    - Suggest command chains when user would benefit
    - Use symbolic aliases for clarity
    - Route smartly based on operation type
    """
    
    def __init__(self):
        self.conversation_history = []
        self.repo_state = {}
        self.last_commands_executed = []
        self.suggestion_history = []
        
        # Define which commands should auto-execute vs suggest
        self.auto_execute_commands = {
            'CONTEXT', 'STATUS', 'ANALYZE', 'CHECK',  # Read-only operations
            'FIND', 'GREP', 'TREE', 'IMPORTS',        # Discovery operations
            'DIFF', 'TRACE', 'SEARCH',                # Analysis operations
        }
        
        self.suggest_only_commands = {
            'COMMIT', 'PUSH', 'DEPLOY', 'MERGE',      # Critical operations
            'CLEAN', 'REBASE', 'HOTFIX',              # Destructive operations
            'SHIPIT', 'AUDIT', 'POLISH',              # Major workflows
        }
        
        self.ask_permission_commands = {
            'REBASE', 'MERGE', 'DEPLOY', 'HOTFIX',    # Risky operations
        }
    
    def analyze_user_intent(self, user_message: str) -> List[CommandSuggestion]:
        """
        Analyze user's message and suggest optimal commands.
        
        Returns list of suggestions with symbolic aliases.
        """
        suggestions = []
        message_lower = user_message.lower()
        
        # Pattern 1: Testing intent
        if any(word in message_lower for word in ['test', 'run tests', 'check tests']):
            if 'fast' in message_lower or 'quick' in message_lower:
                suggestions.append(CommandSuggestion(
                    commands=['#TESTFAST//.'],
                    symbolic_alias='#TESTFAST//.',
                    reason='User wants quick test feedback',
                    execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                    trigger=ContextTrigger.USER_REQUEST,
                    confidence=0.9,
                    expected_outcome='Run unit tests only (< 10s)',
                    estimated_time='< 10s'
                ))
            elif 'failed' in message_lower or 'broken' in message_lower:
                suggestions.append(CommandSuggestion(
                    commands=['#TESTLAST//.'],
                    symbolic_alias='#TESTLAST//.',
                    reason='Re-run failed tests only',
                    execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                    trigger=ContextTrigger.TEST_FAILURE,
                    confidence=0.85,
                    expected_outcome='Re-run last failed tests',
                    estimated_time='< 30s'
                ))
            else:
                suggestions.append(CommandSuggestion(
                    commands=['#TESTUNIT//.'],
                    symbolic_alias='#TESTUNIT//.',
                    reason='Run full unit test suite',
                    execution_mode=ExecutionMode.SUGGEST_TO_USER,
                    trigger=ContextTrigger.USER_REQUEST,
                    confidence=0.8,
                    expected_outcome='Run all unit tests with verbose output',
                    estimated_time='< 60s'
                ))
        
        # Pattern 2: Code quality intent
        if any(word in message_lower for word in ['format', 'lint', 'clean up', 'fix style']):
            suggestions.append(CommandSuggestion(
                commands=['#FMT//.', '#LINTFIX//.'],
                symbolic_alias='#QUICKFIX//.',
                reason='Fix formatting and linting issues',
                execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                trigger=ContextTrigger.CODE_QUALITY_ISSUE,
                confidence=0.95,
                expected_outcome='Auto-format with black+isort, fix linting',
                estimated_time='< 5s'
            ))
        
        # Pattern 3: Git status intent
        if any(word in message_lower for word in ['status', 'what changed', 'git', 'changes']):
            suggestions.append(CommandSuggestion(
                commands=['#STATUS//.'],
                symbolic_alias='#STATUS//.',
                reason='Check current git state',
                execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                trigger=ContextTrigger.GIT_STATE_CHANGE,
                confidence=0.9,
                expected_outcome='Show git status with tracking info',
                estimated_time='< 1s'
            ))
        
        # Pattern 4: Ready to commit
        if any(word in message_lower for word in ['ready to commit', 'commit', 'save changes']):
            # Check if we should run validation first
            suggestions.append(CommandSuggestion(
                commands=['#VALIDATE//.', '#COMMIT//.'],
                symbolic_alias='#COMMIT//.',
                reason='Validate before committing',
                execution_mode=ExecutionMode.SUGGEST_TO_USER,
                trigger=ContextTrigger.USER_REQUEST,
                confidence=0.85,
                expected_outcome='Run pre-commit checks then commit',
                estimated_time='< 30s'
            ))
        
        # Pattern 5: Ready to deploy
        if any(word in message_lower for word in ['deploy', 'ship', 'release', 'publish']):
            suggestions.append(CommandSuggestion(
                commands=['#SHIPIT//.'],
                symbolic_alias='#SHIPIT//.',
                reason='Full CI pipeline before deployment',
                execution_mode=ExecutionMode.SUGGEST_TO_USER,
                trigger=ContextTrigger.DEPLOYMENT_READY,
                confidence=0.9,
                expected_outcome='Run complete CI: test + lint + security + build + validate',
                estimated_time='< 2min'
            ))
        
        # Pattern 6: Security/audit intent
        if any(word in message_lower for word in ['security', 'audit', 'vulnerabilities', 'safe']):
            suggestions.append(CommandSuggestion(
                commands=['#AUDIT//.'],
                symbolic_alias='#AUDIT//.',
                reason='Security and dependency audit',
                execution_mode=ExecutionMode.SUGGEST_TO_USER,
                trigger=ContextTrigger.SECURITY_RISK,
                confidence=0.85,
                expected_outcome='Run safety + bandit + dependency checks',
                estimated_time='< 1min'
            ))
        
        # Pattern 7: Documentation intent
        if any(word in message_lower for word in ['document', 'readme', 'docs', 'documentation']):
            suggestions.append(CommandSuggestion(
                commands=['#README//.'],
                symbolic_alias='#README//.',
                reason='Generate/update documentation',
                execution_mode=ExecutionMode.SUGGEST_TO_USER,
                trigger=ContextTrigger.DOCUMENTATION_GAP,
                confidence=0.8,
                expected_outcome='Auto-generate README sections',
                estimated_time='< 10s'
            ))
        
        # Pattern 8: Finding/searching intent
        if any(word in message_lower for word in ['find', 'search', 'where is', 'locate']):
            if 'file' in message_lower:
                suggestions.append(CommandSuggestion(
                    commands=['#FIND//.'],
                    symbolic_alias='#FIND//.',
                    reason='Search for files by pattern',
                    execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                    trigger=ContextTrigger.USER_REQUEST,
                    confidence=0.9,
                    expected_outcome='Find files matching pattern',
                    estimated_time='< 2s'
                ))
            else:
                suggestions.append(CommandSuggestion(
                    commands=['#GREP//.'],
                    symbolic_alias='#GREP//.',
                    reason='Search code content',
                    execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                    trigger=ContextTrigger.USER_REQUEST,
                    confidence=0.85,
                    expected_outcome='Search code with regex + context',
                    estimated_time='< 3s'
                ))
        
        # Pattern 9: Before committing workflow
        if any(word in message_lower for word in ['before commit', 'pre-commit', 'ready to commit']):
            suggestions.append(CommandSuggestion(
                commands=['#QUICKFIX//.'],
                symbolic_alias='#QUICKFIX//.',
                reason='Quick QA pipeline before commit',
                execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                trigger=ContextTrigger.USER_REQUEST,
                confidence=0.9,
                expected_outcome='Format + lint fix + fast tests',
                estimated_time='< 15s'
            ))
        
        return suggestions
    
    def detect_repo_state_triggers(self) -> List[CommandSuggestion]:
        """
        Analyze current repo state and suggest proactive commands.
        
        This runs automatically to detect optimization opportunities.
        """
        suggestions = []
        
        # Check if there are uncommitted changes
        # (In real implementation, would check actual git status)
        if self.repo_state.get('has_uncommitted_changes'):
            suggestions.append(CommandSuggestion(
                commands=['#STATUS//.'],
                symbolic_alias='#STATUS//.',
                reason='Uncommitted changes detected',
                execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                trigger=ContextTrigger.GIT_STATE_CHANGE,
                confidence=0.7,
                expected_outcome='Show current changes',
                estimated_time='< 1s'
            ))
        
        # Check if tests are failing
        if self.repo_state.get('tests_failing'):
            suggestions.append(CommandSuggestion(
                commands=['#TESTLAST//.'],
                symbolic_alias='#TESTLAST//.',
                reason='Failed tests detected',
                execution_mode=ExecutionMode.SUGGEST_TO_USER,
                trigger=ContextTrigger.TEST_FAILURE,
                confidence=0.8,
                expected_outcome='Re-run failed tests to verify fixes',
                estimated_time='< 30s'
            ))
        
        # Check if formatting issues exist
        if self.repo_state.get('format_issues'):
            suggestions.append(CommandSuggestion(
                commands=['#FMT//.'],
                symbolic_alias='#FMT//.',
                reason='Code formatting inconsistencies detected',
                execution_mode=ExecutionMode.AUTO_BEHIND_SCENES,
                trigger=ContextTrigger.CODE_QUALITY_ISSUE,
                confidence=0.85,
                expected_outcome='Auto-format all Python files',
                estimated_time='< 5s'
            ))
        
        return suggestions
    
    def format_suggestion_for_user(self, suggestion: CommandSuggestion) -> str:
        """
        Format a suggestion as user-friendly text with symbolic alias.
        
        Returns string like:
        "💡 I can run #QUICKFIX//. to format + lint + test (< 15s)"
        """
        emoji_map = {
            ExecutionMode.AUTO_BEHIND_SCENES: "⚡",
            ExecutionMode.SUGGEST_TO_USER: "💡",
            ExecutionMode.ASK_PERMISSION: "🤔",
            ExecutionMode.BOTH: "✨"
        }
        
        emoji = emoji_map.get(suggestion.execution_mode, "💡")
        
        if suggestion.execution_mode == ExecutionMode.AUTO_BEHIND_SCENES:
            return f"{emoji} Running {suggestion.symbolic_alias} behind the scenes: {suggestion.expected_outcome}"
        elif suggestion.execution_mode == ExecutionMode.SUGGEST_TO_USER:
            return f"{emoji} Suggested: {suggestion.symbolic_alias} - {suggestion.reason}\n   → {suggestion.expected_outcome} ({suggestion.estimated_time})"
        elif suggestion.execution_mode == ExecutionMode.ASK_PERMISSION:
            return f"{emoji} Should I run {suggestion.symbolic_alias}? {suggestion.reason}\n   → {suggestion.expected_outcome} ({suggestion.estimated_time})"
        else:
            return f"{emoji} {suggestion.symbolic_alias}: {suggestion.expected_outcome}"
    
    def should_auto_execute(self, suggestion: CommandSuggestion) -> bool:
        """
        Determine if command should auto-execute behind the scenes.
        
        Criteria:
        - High confidence (> 0.8)
        - Non-destructive operation
        - Fast execution (< 30s)
        - Read-only or safe operation
        """
        if suggestion.execution_mode == ExecutionMode.SUGGEST_TO_USER:
            return False
        
        if suggestion.execution_mode == ExecutionMode.ASK_PERMISSION:
            return False
        
        if suggestion.confidence < 0.8:
            return False
        
        # Check if any commands are in suggest-only list
        for cmd in suggestion.commands:
            cmd_name = cmd.replace('#', '').replace('//.', '').strip()
            if cmd_name in self.suggest_only_commands:
                return False
        
        return suggestion.execution_mode == ExecutionMode.AUTO_BEHIND_SCENES
    
    def generate_command_chain_suggestion(
        self,
        user_intent: str,
        available_commands: List[str]
    ) -> Optional[CommandSuggestion]:
        """
        Generate optimal command chain based on user's intent.
        
        Example:
        Intent: "make sure everything is good before deploying"
        Chain: #TESTUNIT//. #LINTCHECK//. #SECURITY//. #AUDIT//.
        Alias: #SHIPIT//.
        """
        intent_lower = user_intent.lower()
        
        # Map common intents to command chains
        intent_chains = {
            'quick fix': (['#FMT//.', '#LINTFIX//.', '#TESTFAST//.'], '#QUICKFIX//.'),
            'ready to ship': (['#TESTUNIT//.', '#LINTCHECK//.', '#SECURITY//.', '#AUDIT//.'], '#SHIPIT//.'),
            'clean up': (['#FMT//.', '#CLEAN//.', '#OPTIMIZE//.'], '#CLEANUP//.'),
            'full check': (['#CHECK//.', '#TESTUNIT//.', '#SECURITY//.'], '#VALIDATE//.'),
            'audit security': (['#SECURITY//.', '#AUDIT//.'], '#AUDIT//.'),
        }
        
        for intent_key, (chain, alias) in intent_chains.items():
            if intent_key in intent_lower:
                return CommandSuggestion(
                    commands=chain,
                    symbolic_alias=alias,
                    reason=f'Optimal chain for: {intent_key}',
                    execution_mode=ExecutionMode.SUGGEST_TO_USER,
                    trigger=ContextTrigger.USER_REQUEST,
                    confidence=0.85,
                    expected_outcome=f'Execute {len(chain)}-step workflow',
                    estimated_time='< 2min'
                )
        
        return None
    
    def track_execution(self, command: str, success: bool, output: str):
        """Track command execution for learning and optimization"""
        self.last_commands_executed.append({
            'command': command,
            'success': success,
            'output': output,
            'timestamp': 'now'  # Would use actual timestamp
        })
    
    def get_suggestion_prompt(self, suggestions: List[CommandSuggestion]) -> str:
        """
        Generate user-facing prompt with command suggestions.
        
        Returns formatted text with symbolic aliases and options.
        """
        if not suggestions:
            return ""
        
        lines = ["\n💡 Command Suggestions:"]
        
        for i, sugg in enumerate(suggestions, 1):
            if sugg.execution_mode == ExecutionMode.AUTO_BEHIND_SCENES:
                lines.append(f"   ⚡ Auto-executing {sugg.symbolic_alias}: {sugg.expected_outcome}")
            else:
                lines.append(f"   {i}. {sugg.symbolic_alias} - {sugg.reason}")
                lines.append(f"      → {sugg.expected_outcome} ({sugg.estimated_time})")
        
        lines.append("\nYou can:")
        lines.append("- Reference by alias: 'Run #QUICKFIX//.'")
        lines.append("- Reference by number: 'Run option 1'")
        lines.append("- Compose chains: '#FMT//. #TESTFAST//. #COMMIT//.'")
        
        return "\n".join(lines)


def demo():
    """Demonstration of context-aware suggestion system"""
    suggester = ContextAwareSuggester()
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  Context-Aware Command Suggester - Demo                 ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    
    test_messages = [
        "Let's run tests quickly",
        "I want to format and lint the code",
        "What's our git status?",
        "Ready to deploy this",
        "Can you check for security issues?",
        "I need to find a specific file",
    ]
    
    for msg in test_messages:
        print(f"User: '{msg}'")
        suggestions = suggester.analyze_user_intent(msg)
        
        if suggestions:
            for sugg in suggestions:
                print(f"  {suggester.format_suggestion_for_user(sugg)}")
                if suggester.should_auto_execute(sugg):
                    print(f"    [Auto-executing behind the scenes...]")
        else:
            print("  [No specific command suggestions]")
        print()


if __name__ == "__main__":
    demo()
