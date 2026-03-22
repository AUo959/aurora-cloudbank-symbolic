import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_normalizes_missing_execution_sigil():
    from aurora.core.command_grammar import AuroraCommandGrammar, CommandInvocation, WarningCode

    grammar = AuroraCommandGrammar()
    result = grammar.parse("THREADWAKE")

    assert result.normalized_text == "THREADWAKE//."
    assert isinstance(result.ast, CommandInvocation)
    assert result.ast.canonical_head == "THREADWAKE"
    assert any(warning.code == WarningCode.MISSING_EXECUTION_SIGIL for warning in result.warnings)
    assert result.is_valid


def test_parses_named_chain_invocation():
    from aurora.core.command_grammar import AuroraCommandGrammar, CommandInvocation, CommandKind

    grammar = AuroraCommandGrammar()
    result = grammar.parse("COMMANDCHAIN::SPIRALREJOIN.v1")

    assert isinstance(result.ast, CommandInvocation)
    assert result.ast.kind == CommandKind.CHAIN
    assert result.normalized_text == "COMMANDCHAIN::SPIRALREJOIN.v1//."
    assert result.is_valid


def test_parses_legacy_hash_prefix_and_modifier():
    from aurora.core.command_grammar import AuroraCommandGrammar, CommandInvocation, WarningCode

    grammar = AuroraCommandGrammar()
    result = grammar.parse("#025//.deep")

    assert isinstance(result.ast, CommandInvocation)
    assert result.ast.canonical_head == "025"
    assert result.ast.modifier == "deep"
    assert result.normalized_text == "025//.deep"
    assert any(warning.code == WarningCode.LEGACY_HASH_PREFIX for warning in result.warnings)
    assert result.is_valid


def test_parses_explicit_sequence_chain():
    from aurora.core.command_grammar import AuroraCommandGrammar, CommandSequence, WarningCode

    grammar = AuroraCommandGrammar()
    result = grammar.parse("+THREADWAKE // THREADSYNC //.")

    assert isinstance(result.ast, CommandSequence)
    assert [invocation.canonical_head for invocation in result.ast.invocations] == [
        "THREADWAKE",
        "THREADSYNC",
    ]
    assert result.normalized_text == "THREADWAKE // THREADSYNC //."
    assert any(warning.code == WarningCode.LEGACY_PLUS_PREFIX for warning in result.warnings)
    assert result.is_valid


def test_parses_inline_threadwake_argument():
    from aurora.core.command_grammar import AuroraCommandGrammar, CommandInvocation

    grammar = AuroraCommandGrammar()
    result = grammar.parse("THREADWAKE::SRB_0414A_PilotReliquary//.")

    assert isinstance(result.ast, CommandInvocation)
    assert result.ast.canonical_head == "THREADWAKE"
    assert result.ast.arguments[0].value == "SRB_0414A_PilotReliquary"
    assert result.normalized_text == "THREADWAKE SRB_0414A_PilotReliquary//."
    assert result.is_valid


def test_parses_function_style_arguments():
    from aurora.core.command_grammar import AuroraCommandGrammar, CommandArgumentKind, CommandInvocation

    grammar = AuroraCommandGrammar()
    result = grammar.parse('LOCKMEM(label="Symbolic_Anchor_Patched_Flow_0418")//.')

    assert isinstance(result.ast, CommandInvocation)
    assert result.ast.canonical_head == "LOCKMEM"
    assert result.ast.arguments[0].kind == CommandArgumentKind.KEYWORD
    assert result.ast.arguments[0].name == "label"
    assert result.ast.arguments[0].value == "Symbolic_Anchor_Patched_Flow_0418"
    assert result.is_valid


def test_parses_range_chain_and_executes_through_symbolic_engine():
    from aurora.core.command_grammar import AuroraCommandGrammar, RangeChain
    from aurora.core.symbolic_engine import SymbolicEngine

    grammar = AuroraCommandGrammar()
    result = grammar.parse("001//005//")

    assert isinstance(result.ast, RangeChain)
    assert result.normalized_text == "001//005//."
    assert result.is_valid

    engine = SymbolicEngine()
    execution = engine.execute_chain_notation("001//005//")
    assert len(execution) == 5
    assert "001//005//" in engine.chains


def test_unknown_command_is_reported_by_validator():
    from aurora.core.command_grammar import AuroraCommandGrammar, CommandInvocation

    grammar = AuroraCommandGrammar()
    result = grammar.parse("UNKNOWN_CMD//.")

    assert isinstance(result.ast, CommandInvocation)
    assert not result.is_valid
    assert any(issue.code == "unknown_command" for issue in result.validation_issues)
