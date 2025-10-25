# Command Intelligence System
**Anchor:** CMD-CHAIN-INTELLIGENCE-001  
**DLP:** CONFIDENTIAL  
**Version:** 1.0.0

## Overview

The Command Intelligence System enables commands to work **both** behind the scenes AND as user-facing symbolic aliases. Commands optimize your workflow automatically while giving you the option to invoke them explicitly.

## Two-Mode Operation

### 1. Behind-the-Scenes Execution ⚡
Commands execute **transparently** when:
- Operation is read-only (analysis, status checks)
- High confidence the command is optimal (> 80%)
- Fast execution (< 30 seconds)
- Non-destructive operation

**Example:**
```
User: "What's our git status?"
System: ⚡ Running #STATUS//. behind the scenes: Show git status with tracking info
        → [Executes automatically, shows results]
```

### 2. User-Facing Suggestions 💡
Commands are **offered as options** when:
- Operation requires user approval (commit, deploy, merge)
- Multiple valid approaches exist
- Potentially destructive operation
- Long-running operation (> 30 seconds)

**Example:**
```
User: "Ready to deploy this"
System: 💡 Suggested: #SHIPIT//. - Full CI pipeline before deployment
           → Run complete CI: test + lint + security + build + validate (< 2min)
        
        You can:
        - Run it: '#SHIPIT//.'
        - Compose: '#TESTUNIT//. #AUDIT//. #DEPLOY//.'
```

## Intent Detection Patterns

The system analyzes your messages for common intents:

| User Intent | Detected Keywords | Suggested Command | Execution Mode |
|-------------|-------------------|-------------------|----------------|
| **Quick Testing** | "test", "quick", "fast" | `#TESTFAST//.` | ⚡ Auto |
| **Failed Tests** | "failed", "broken", "test" | `#TESTLAST//.` | ⚡ Auto |
| **Code Quality** | "format", "lint", "clean up" | `#QUICKFIX//.` | ⚡ Auto |
| **Git Status** | "status", "changes", "git" | `#STATUS//.` | ⚡ Auto |
| **Commit Ready** | "ready to commit", "save" | `#VALIDATE//. #COMMIT//.` | 💡 Suggest |
| **Deployment** | "deploy", "ship", "release" | `#SHIPIT//.` | 💡 Suggest |
| **Security Audit** | "security", "audit", "vulnerabilities" | `#AUDIT//.` | 💡 Suggest |
| **Documentation** | "document", "readme", "docs" | `#README//.` | 💡 Suggest |
| **File Search** | "find", "search file", "locate" | `#FIND//.` | ⚡ Auto |
| **Code Search** | "find", "search", "grep" | `#GREP//.` | ⚡ Auto |
| **Pre-Commit** | "before commit", "pre-commit" | `#QUICKFIX//.` | ⚡ Auto |

## Command Categories by Execution Mode

### Auto-Execute Commands (Behind the Scenes) ⚡
**Read-only, fast, non-destructive**

```python
# Analysis & Discovery
#CONTEXT//.     # Full context dump
#STATUS//.      # Git status with tracking
#ANALYZE//.     # Deep analysis
#CHECK//.       # Health check
#FIND//.        # Find files
#GREP//.        # Search code
#TREE//.        # Directory structure
#IMPORTS//.     # Import dependency graph
#DIFF//.        # Show changes
#TRACE//.       # Function tracing
#SEARCH//.      # Semantic search

# Fast Operations
#TESTFAST//.    # Quick unit tests (< 10s)
#TESTLAST//.    # Re-run failed tests
#FMT//.         # Auto-format code
#LINTFIX//.     # Fix linting errors
```

### Suggest to User (Offer as Options) 💡
**Requires approval, potentially destructive, or long-running**

```python
# Critical Operations
#COMMIT//.      # Commit changes
#PUSH//.        # Push to remote
#DEPLOY//.      # Deploy to environment
#MERGE//.       # Merge branches
#REBASE//.      # Rebase on main

# Destructive Operations
#CLEAN//.       # Clean build artifacts
#HOTFIX//.      # Create hotfix branch

# Major Workflows
#SHIPIT//.      # Full CI pipeline
#AUDIT//.       # Security audit
#POLISH//.      # Polish codebase
#VALIDATE//.    # Pre-commit validation
```

### Ask Permission (Risky Operations) 🤔
**Requires explicit confirmation**

```python
#REBASE//.      # Rebase (can cause conflicts)
#MERGE//.       # Merge (can cause conflicts)
#DEPLOY//.      # Deploy (affects production)
#HOTFIX//.      # Hotfix (fast-track to prod)
```

## How It Works for You (The User)

### Scenario 1: Quick Testing
```
You: "Let me run tests quickly"

System: ⚡ Running #TESTFAST//. behind the scenes: Run unit tests only (< 10s)
        [Executes pytest -m unit -x automatically]
        
        ✅ 34 tests passed in 8.2s
```

**What happened:** System detected "tests" + "quickly" → auto-executed `#TESTFAST//.`

### Scenario 2: Ready to Deploy
```
You: "This looks ready to ship"

System: 💡 Suggested: #SHIPIT//. - Full CI pipeline before deployment
           → Run complete CI: test + lint + security + build + validate (< 2min)
        
        You can:
        - Run it: 'Yes, run #SHIPIT//.'
        - Customize: '#TESTUNIT//. #AUDIT//. then deploy'
        - Skip: 'Just #DEPLOY//. directly'
```

**What happened:** System detected deployment intent → offered comprehensive pre-deployment check

### Scenario 3: Code Quality Fix
```
You: "Let's clean up the formatting before committing"

System: ⚡ Running #QUICKFIX//. behind the scenes: Format + lint + fast tests
        [Executes #FMT//. #LINTFIX//. #TESTFAST//. automatically]
        
        ✅ Formatted 12 files with black
        ✅ Fixed 8 linting issues
        ✅ 34 tests passed
        
        Ready to commit!
```

**What happened:** System detected code quality intent → auto-executed cleanup pipeline

## How It Works for Copilot (Behind the Scenes)

### When to Auto-Execute
Copilot automatically runs commands when:

1. **User asks for information**
   - "What's the git status?" → Auto-run `#STATUS//.`
   - "Find all test files" → Auto-run `#FIND//.`
   - "Check for circular imports" → Auto-run `#IMPORTS//.`

2. **Operation is clearly beneficial**
   - User edits code → Auto-run `#FMT//.` if formatting is off
   - Tests fail → Auto-suggest `#TESTLAST//.` to verify fixes
   - Before commit → Auto-run `#LINTCHECK//.`

3. **Zero risk of harm**
   - Read-only operations
   - Formatting (reversible with git)
   - Analysis and discovery

### When to Suggest with Symbolic Aliases
Copilot offers commands as options when:

1. **User approval needed**
   - "Ready to commit?" → Suggest: `#VALIDATE//. #COMMIT//.`
   - "Should we deploy?" → Suggest: `#SHIPIT//. #DEPLOY//.`

2. **Multiple valid approaches**
   - User: "Run tests" → Suggest: `#TESTFAST//.` or `#TESTUNIT//.` or `#TESTALL//.`
   - User: "Clean up" → Suggest: `#QUICKFIX//.` or `#CLEANUP//.` or `#POLISH//.`

3. **Operation takes time**
   - `#SHIPIT//.` (2 min) → Ask permission
   - `#AUDIT//.` (1 min) → Ask permission
   - `#BUILDTEST//.` (1 min) → Ask permission

### Offering Symbolic Aliases
When suggesting commands, Copilot provides:

✅ **Symbolic Alias:** Clear, memorable name (`#QUICKFIX//.`)  
✅ **Reason:** Why this command is suggested  
✅ **Expected Outcome:** What will happen  
✅ **Estimated Time:** How long it takes  
✅ **Alternative Options:** Other valid approaches

**Example Response:**
```
💡 I can help with that! Here are your options:

1. #QUICKFIX//. - Quick QA pipeline
   → Format + lint fix + fast tests (< 15s)
   
2. #VALIDATE//. - Full pre-commit validation
   → Syntax + tests + lint + type check + security (< 30s)
   
3. #SHIPIT//. - Complete CI pipeline
   → All checks + build + coverage (< 2min)

You can run any of these by saying:
- "Run #QUICKFIX//."
- "Let's do option 1"
- Or compose your own: "#FMT//. #TESTUNIT//. #COMMIT//."
```

## Smart Command Routing Logic

```python
# Copilot's decision tree
def should_auto_execute(command):
    if command.is_read_only():
        return True  # ⚡ Always auto-execute
    
    if command.confidence < 0.8:
        return False  # 💡 Suggest instead
    
    if command.is_destructive():
        return False  # 💡 or 🤔 Ask permission
    
    if command.estimated_time > 30:
        return False  # 💡 Suggest (user might not want to wait)
    
    if command in ['COMMIT', 'PUSH', 'DEPLOY', 'MERGE']:
        return False  # 🤔 Always ask permission
    
    return True  # ⚡ Auto-execute
```

## Composability with Symbolic Aliases

You can combine commands using symbolic aliases:

```bash
# Quick fix before commit
#QUICKFIX//. #COMMIT//.

# Full release workflow
#SHIPIT//. #AUDIT//. #POLISH//. #CHANGELOG//. #README//. #PUSH//.

# Development iteration
#TESTFAST//. #FMT//. #STATUS//.

# Emergency hotfix
#HOTFIX//. #TESTLAST//. #PUSH//. #DEPLOY//.

# Security hardening
#SECURITY//. #AUDIT//. #DEPS//. #VALIDATE//.
```

## Configuration

Commands are categorized by default behavior, but you can customize:

```python
# In context_aware_suggester.py
auto_execute_commands = {
    'CONTEXT', 'STATUS', 'ANALYZE', 'CHECK',
    'FIND', 'GREP', 'TREE', 'IMPORTS',
    'DIFF', 'TRACE', 'SEARCH',
}

suggest_only_commands = {
    'COMMIT', 'PUSH', 'DEPLOY', 'MERGE',
    'CLEAN', 'REBASE', 'HOTFIX',
    'SHIPIT', 'AUDIT', 'POLISH',
}

ask_permission_commands = {
    'REBASE', 'MERGE', 'DEPLOY', 'HOTFIX',
}
```

## Benefits

### For Users 👨‍💻
- **Faster workflow:** Commands execute when you need them
- **Clear options:** Symbolic aliases are memorable (`#QUICKFIX//.` not `fmt-lint-test-v2`)
- **Flexibility:** Auto-execute transparent operations, approve critical ones
- **Learning:** See what commands Copilot uses → learn the aliases
- **Composability:** Combine commands into custom workflows

### For Copilot 🤖
- **Proactive optimization:** Fix issues before user notices
- **Consistent quality:** Auto-format, auto-lint, auto-test
- **Clear communication:** Use symbolic aliases to explain actions
- **Context awareness:** Same intent, different commands based on repo state
- **Efficiency:** Batch operations, smart chaining

## Real-World Examples

### Example 1: User Edits Code
```
User: [Edits python file, introduces formatting inconsistency]

Copilot (behind the scenes):
  ⚡ Auto-running #FMT//. to fix formatting
  → Formatted file with black + isort
  ✅ Ready to test

User: "Run tests"

Copilot:
  ⚡ Running #TESTFAST//. behind the scenes
  → 34 unit tests passed in 7.8s
  ✅ All good!
```

### Example 2: User Ready to Commit
```
User: "I think this is ready to commit"

Copilot:
  💡 Before committing, I can run #VALIDATE//. to ensure everything passes:
     - Syntax check
     - Unit tests
     - Linting
     - Type checking
     - Security scan
     
     Should I run #VALIDATE//. first? (< 30s)

User: "Yes"

Copilot:
  ⚡ Running #VALIDATE//.
  ✅ All checks passed!
  
  Ready to #COMMIT//. Would you like me to generate a commit message?
```

### Example 3: User Deploying
```
User: "Let's deploy this to production"

Copilot:
  🤔 Before deploying to production, I recommend running #SHIPIT//.
     This ensures:
     ✅ All tests pass
     ✅ No linting errors
     ✅ Security scan clean
     ✅ Build succeeds
     ✅ Full validation
     
     Estimated time: < 2min
     
     Options:
     1. Run #SHIPIT//. then deploy (recommended)
     2. Run #AUDIT//. for security check only
     3. Deploy directly (skip checks)
     
     Which would you prefer?
```

## Integration with Copilot Chat

Copilot seamlessly integrates command intelligence:

```python
# When user says something
user_message = "Let's run tests quickly"

# Copilot analyzes intent
suggester = ContextAwareSuggester()
suggestions = suggester.analyze_user_intent(user_message)

# Auto-execute if appropriate
for sugg in suggestions:
    if suggester.should_auto_execute(sugg):
        result = executor.execute(sugg.commands)
        print(f"⚡ Ran {sugg.symbolic_alias}: {result.message}")
    else:
        print(f"💡 Suggested: {sugg.symbolic_alias}")
        print(f"   → {sugg.expected_outcome} ({sugg.estimated_time})")
```

## Future Enhancements

1. **Learning from history:** Track which suggestions user accepts → improve confidence scores
2. **Context persistence:** Remember repo state across sessions
3. **Custom aliases:** User-defined symbolic aliases for personal workflows
4. **Macro recording:** "Remember this as #MYWORKFLOW//."
5. **Conditional execution:** "If tests pass, auto-commit"
6. **Parallel execution:** Run multiple safe commands simultaneously
7. **Progress indicators:** Live progress for long-running commands
8. **Undo support:** Roll back commands if results aren't desired

## Philosophy

Commands are **accelerators for both user and Copilot**:

✅ **For User:** Clear symbolic aliases to invoke workflows  
✅ **For Copilot:** Transparent optimization behind the scenes  
✅ **Together:** Faster, smarter, more efficient development

The system knows when to act and when to ask. It respects user control while optimizing proactively. Commands work **for you**, not just **when you ask**.

---

**Next:** Implement real command logic with subprocess/git/pytest integration
