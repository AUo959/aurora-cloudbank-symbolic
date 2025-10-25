# Command Chain Parser

**Anchor:** CMD-CHAIN-DOC-001  
**Team:** AUo959-team  
**Ethics:** Picard_Delta_3  
**DLP:** CONFIDENTIAL  
**Version:** 1.0.0

## Overview

The Command Chain Parser provides a safe, structured syntax for executing powerful commands in the Aurora CloudBank system. Commands require explicit termination with `//.` to execute, preventing accidental command execution.

## Command Syntax

### Valid Command

```
#command//.
```

**Pattern:** Hash prefix `#` + command name + terminator `//.`

**Examples:**
- `#seal//.` ✅
- `#verify//.` ✅
- `#deploy//.` ✅

### Invalid Command (Naked)

```
#command
```

**Pattern:** Hash prefix `#` + command name + **MISSING terminator**

**Examples:**
- `#seal` ❌ (incomplete - will NOT execute)
- `#verify` ❌ (incomplete - will NOT execute)
- `#deploy` ❌ (incomplete - will NOT execute)

## Safety Features

### 1. Terminator Required

Commands **MUST** have the `//.` terminator to execute. This prevents:
- Accidental command execution
- Typos triggering commands
- Unintentional operations

### 2. Helpful Error Messages

When a naked command is detected, the system provides:
- Clear explanation of the error
- Correct syntax examples
- Quick fix suggestions
- Educational context about why the terminator matters

### 3. Command Validation

The parser validates:
- Command syntax (proper terminator)
- Command name (supported commands only)
- Command position (tracking in text)

## Supported Commands

Current supported commands:

| Command | Description |
|---------|-------------|
| `#anchor//.` | Establish or update anchor point |
| `#build//.` | Build artifacts or components |
| `#clean//.` | Clean temporary files or caches |
| `#commit//.` | Commit changes with DLP tracking |
| `#deploy//.` | Deploy to production or staging |
| `#export//.` | Export data with DLP tags |
| `#import//.` | Import data with validation |
| `#restore//.` | Restore from snapshot |
| `#seal//.` | Seal symbolic state |
| `#snapshot//.` | Create snapshot |
| `#status//.` | Show system status |
| `#sync//.` | Synchronize with remote |
| `#test//.` | Run test suite |
| `#validate//.` | Validate integrity |
| `#verify//.` | Verify checksums or seals |

## Command Chaining

Execute multiple commands in sequence:

```
#seal//. #verify//. #deploy//.
```

**Benefits:**
- Sequential execution
- Combined operations
- DLP tracking across chain
- Single command hash for audit trail

## Usage

### Python API

```python
from tools.command_chain import CommandChainParser

parser = CommandChainParser()

# Parse input text
result = parser.parse("Please run #seal//. and #verify//.")

# Check for valid commands
if result.commands:
    for cmd in result.commands:
        print(f"Command: {cmd.name}")

# Check for errors (naked commands)
if result.naked_commands:
    for cmd in result.naked_commands:
        print(cmd.error_message)

# Extract only valid commands
valid_cmds = parser.extract_valid_commands(input_text)

# Generate DLP tracking hash
cmd_hash = parser.generate_command_hash(valid_cmds)
```

### Command Line Interface

```bash
# Parse command chain
python tools/command_chain/cli.py parse "Execute #seal//. #verify//."

# Detect naked commands
python tools/command_chain/cli.py parse "Run #deploy"

# Validate syntax
python tools/command_chain/cli.py validate "#seal//. #verify//.?"

# List supported commands
python tools/command_chain/cli.py list

# Format command chain
python tools/command_chain/cli.py format seal verify deploy

# Run demonstration
python tools/command_chain/cli.py demo
```

## Examples

### Example 1: Valid Command Chain

**Input:**
```
Please run #seal//. and then #verify//.
```

**Result:**
```
✅ Valid Commands: 2
   • #seal//. → seal
   • #verify//. → verify
```

### Example 2: Naked Command Detection

**Input:**
```
Can you #seal this for me?
```

**Result:**
```
╔══════════════════════════════════════════════════════════════════╗
║ ⚠️  COMMAND SYNTAX ERROR: Missing Terminator                     ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  You entered: #seal                                              ║
║                                                                  ║
║  ❌ This command is INCOMPLETE and will NOT be executed.         ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  📖 CORRECT SYNTAX                                               ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Commands MUST end with the //. terminator for safety.          ║
║                                                                  ║
║  ✅ Correct:   #seal//.                                          ║
║  ❌ Incorrect: #seal                                             ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  💡 WHY THIS MATTERS                                             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  The //. terminator prevents accidental command execution.      ║
║  Powerful commands require explicit, intentional syntax.         ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  🎯 QUICK FIX                                                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Did you mean to execute this command?                          ║
║  Add the //. terminator:                                        ║
║                                                                  ║
║    #seal//.                                                      ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Example 3: Mixed Valid and Invalid

**Input:**
```
#seal//. #verify #deploy//.
```

**Result:**
```
✅ Valid Commands: 2
   • #seal//. → seal
   • #deploy//. → deploy

⚠️  Naked Command: verify
   [Error message explaining how to fix]
```

## DLP Integration

All command chains generate SHA-256 hashes for audit trails:

```python
commands = ["seal", "verify", "deploy"]
cmd_hash = parser.generate_command_hash(commands)
# Returns: "a7f4e3d2..." (64-character SHA-256 hash)
```

**DLP Tags:** All command execution includes:
- Command chain hash
- Timestamp
- Anchor reference (EOS_SEED_ORION)
- Ethics protocol (Picard_Delta_3)

## Adding Custom Commands

```python
parser = CommandChainParser()

# Add new command
parser.add_command("my_custom_cmd")

# Now supported
result = parser.parse("#my_custom_cmd//.")
# Returns valid command
```

## Testing

Run comprehensive test suite:

```bash
# All tests
pytest tools/command_chain/tests/test_parser.py -v

# Specific test category
pytest tools/command_chain/tests/test_parser.py::TestCommandChainParser -v

# Integration tests
pytest tools/command_chain/tests/test_parser.py::TestCommandChainIntegration -v
```

**Test Coverage:** 28 tests, 100% passing
- Valid command parsing
- Naked command detection
- Error message generation
- Command chaining
- DLP hash generation
- Command validation
- Position tracking

## Architecture

### Core Components

```
tools/command_chain/
├── __init__.py          # Package exports
├── parser.py            # Core parsing logic
├── cli.py               # Command-line interface
├── tests/
│   ├── __init__.py
│   └── test_parser.py   # Comprehensive test suite
└── README.md            # This file
```

### Design Principles

1. **Safety First:** Never execute incomplete commands
2. **Helpful Errors:** Guide users to correct syntax
3. **Explicit Intent:** Require intentional terminator
4. **DLP Tracking:** Hash all command chains
5. **Extensible:** Easy to add new commands

## Why This Matters

### Security

The `//.` terminator requirement provides:
- Protection against typos
- Prevention of accidental execution
- Clear intent verification
- Audit trail generation

### User Experience

When users forget the terminator:
- Immediate, clear feedback
- Explanation of the issue
- Correct syntax examples
- Quick fix suggestions

### Integration

Command chains integrate with:
- DLP tracking system
- Anchor protocols
- Ethics validation (Picard_Delta_3)
- Symbolic state management

## Common Patterns

### Sequential Operations

```
#snapshot//. #seal//. #verify//.
```

Create snapshot, seal state, verify integrity.

### Deployment Pipeline

```
#build//. #test//. #verify//. #deploy//.
```

Full deployment with validation.

### Maintenance Workflow

```
#clean//. #sync//. #status//.
```

Clean, synchronize, check status.

## Error Handling

The parser handles:
- **Missing terminators:** Helpful error with fix
- **Unknown commands:** List of supported commands
- **Invalid syntax:** Clear explanation
- **Mixed valid/invalid:** Separate processing

## Performance

- **Parsing:** < 1ms for typical command chains
- **Validation:** < 1ms per command
- **Hash generation:** < 1ms (SHA-256)
- **Test suite:** 0.15s for 28 tests

## Future Enhancements

Planned features:
- Command parameters: `#deploy(prod)//.`
- Conditional execution: `#if(test_passed)//.`
- Command aliases: `#d//. → #deploy//.`
- Async command chains
- Command history with undo

## Support

For issues or questions:
- Check test suite for examples
- Run demo: `python tools/command_chain/cli.py demo`
- Review error messages (they're designed to be helpful!)

## License

Part of Aurora CloudBank Symbolic System  
Anchor: EOS_SEED_ORION  
Ethics: Picard_Delta_3  
Team: AUo959-team

---

**Remember:** Powerful commands require powerful syntax. The `//.` terminator ensures you mean what you execute. 🔐
