# 🚀 #321//. Enhancement Proposal: LLM-Agnostic Context Persistence

**Version:** 1.0.0  
**Date:** 2025-11-15  
**Status:** PROPOSED  
**Priority:** HIGH  
**Anchor:** CMD-CHAIN-321-ENHANCEMENT-001

---

## Executive Summary

Current Issue: #321//. (Comprehensive Sync & Validate) generates artifacts during post-commit hooks that interfere with subsequent git operations, causing rebase failures. Additionally, command context is not persisted across LLM model switches, requiring agents to rediscover command functionality.

**Core Problem:**
1. **Artifact Generation**: `.aurora/audit_trail.json`, `.security/scan_log.json`, `.rebuild_prevention_status.json` modified by post-commit hooks → blocks `git pull --rebase`
2. **Context Fragility**: Command semantics, execution history, and state are volatile across LLM model changes
3. **Manual Recovery**: Requires human intervention to stage/commit generated files before sync can complete

**Proposed Solution:**
Implement a **persistent command context layer** with pre/post-execution hooks, artifact management, and LLM-agnostic state tracking.

---

## 🎯 Design Principles

### 1. Model-Agnostic Context Persistence

**Current State:**
- Command documentation in markdown (`COMPREHENSIVE_SYNC_321.md`)
- Execution logic in Python (`executor.py`)
- No persistent state across model switches
- Relies on copilot-instructions.md being read by new model

**Enhanced State:**
```python
# .aurora/command_context/321_state.json
{
  "command": "321",
  "semantic_name": "comprehensive_sync_validate",
  "last_execution": {
    "timestamp": "2025-11-15T22:15:00Z",
    "model": "claude-sonnet-4",
    "success": true,
    "phases_completed": ["check", "stage_commit", "sync", "validate"],
    "artifacts_generated": [
      ".aurora/audit_trail.json",
      ".security/scan_log.json"
    ],
    "execution_time_ms": 3421
  },
  "execution_count": 147,
  "average_duration_ms": 3200,
  "success_rate": 0.98,
  "known_artifacts": [
    {
      "path": ".aurora/audit_trail.json",
      "generator": "post_commit_security_monitor",
      "action": "stash",
      "restore_on_failure": true
    },
    {
      "path": ".security/scan_log.json",
      "generator": "post_commit_security_scan",
      "action": "stash",
      "restore_on_failure": true
    },
    {
      "path": ".rebuild_prevention_status.json",
      "generator": "gitwiz_post_commit",
      "action": "ignore",
      "restore_on_failure": false
    }
  ],
  "phase_metadata": {
    "1_check": {
      "description": "Detect pending changes via git status",
      "expected_duration_ms": 200,
      "failure_recovery": "safe_to_retry"
    },
    "2_3_stage_commit": {
      "description": "Intelligent staging and semantic commit",
      "expected_duration_ms": 1000,
      "failure_recovery": "review_staged_files"
    },
    "4_sync": {
      "description": "Pull --rebase and push to origin",
      "expected_duration_ms": 1500,
      "failure_recovery": "stash_artifacts_and_retry",
      "artifact_interference_risk": "high"
    },
    "5_validate": {
      "description": "Quick lint and test validation",
      "expected_duration_ms": 500,
      "failure_recovery": "non_blocking_warning"
    }
  },
  "recovery_strategies": {
    "sync_failure_exit_128": {
      "cause": "Unstaged changes block git pull --rebase",
      "detection": "exit_code == 128 && stderr contains 'unstaged changes'",
      "remedy": "stash_artifacts → retry_pull_rebase → apply_stash",
      "auto_remediate": true
    },
    "post_commit_artifact_conflict": {
      "cause": "Post-commit hooks generate files after commit",
      "detection": "git status --porcelain shows modifications after commit",
      "remedy": "pre_sync_stash → sync → post_sync_restore",
      "auto_remediate": true
    }
  },
  "context_for_new_models": {
    "quick_description": "Universal clean working tree command - handles status, commit, sync, validate",
    "when_to_use": "Anytime you want pending changes sorted quickly with high quality",
    "invocation_patterns": [
      "#321//.",
      "comprehensive sync",
      "clean working tree",
      "sort pending changes"
    ],
    "critical_notes": [
      "Generates artifacts during commit - automatically handles via stash/restore",
      "Phase 4 sync uses rebase - cleaner history than merge",
      "Phase 5 validation is fast unit tests only - not full suite",
      "Always safe to retry on partial failure"
    ]
  }
}
```

### 2. Pre/Post Execution Hook System

**Hook Architecture:**

```python
class CommandExecutionHooks:
    """Hooks for #321 artifact management and state persistence"""
    
    def pre_execution(self, command: str, context: Dict) -> Dict:
        """Before command execution"""
        return {
            "workspace_snapshot": self._snapshot_workspace(),
            "git_state": self._capture_git_state(),
            "known_artifacts": self._list_known_artifacts(),
            "stash_ref": None  # Will be set if artifacts exist
        }
    
    def pre_phase(self, phase: str, context: Dict) -> Dict:
        """Before each phase"""
        if phase == "4_sync":
            # CRITICAL: Stash any artifacts generated by previous commit
            return self._stash_post_commit_artifacts(context)
        return context
    
    def post_phase(self, phase: str, result: Dict, context: Dict) -> Dict:
        """After each phase"""
        if phase == "2_3_stage_commit":
            # Post-commit hooks may have generated artifacts
            context["artifacts_check_required"] = True
        
        if phase == "4_sync" and context.get("stash_ref"):
            # Restore stashed artifacts after successful sync
            self._restore_stashed_artifacts(context["stash_ref"])
        
        return context
    
    def post_execution(self, result: Dict, context: Dict) -> None:
        """After command execution - persist state"""
        self._persist_execution_state(
            command="321",
            result=result,
            context=context,
            model=self._detect_current_model()
        )
        self._update_command_statistics(result)
    
    def on_failure(self, phase: str, error: Exception, context: Dict) -> Dict:
        """Failure recovery"""
        if "stash_ref" in context and context["stash_ref"]:
            # Restore workspace on failure
            self._restore_stashed_artifacts(context["stash_ref"])
        
        return {
            "recovery_strategy": self._lookup_recovery(phase, error),
            "auto_remediate": self._can_auto_remediate(phase, error),
            "context_preserved": True
        }
```

### 3. Artifact Management Strategy

**Current Problem:**
```bash
# After commit succeeds:
git commit -m "feat: add feature"  # ✓ Success
# Post-commit hooks run:
# - post_commit_security_monitor → modifies .aurora/audit_trail.json
# - post_commit_security_scan → modifies .security/scan_log.json
# - gitwiz_post_commit → modifies .rebuild_prevention_status.json

git status --porcelain
# M .aurora/audit_trail.json
# M .security/scan_log.json
# M .rebuild_prevention_status.json

git pull --rebase origin main
# error: cannot rebase with unstaged changes  # ❌ FAIL (exit 128)
```

**Enhanced Solution:**

```python
def _handle_sync_with_artifact_management(self) -> Dict[str, Any]:
    """Phase 4: Sync with automatic artifact handling"""
    
    # 1. Detect post-commit artifact generation
    artifacts = self._detect_generated_artifacts([
        ".aurora/audit_trail.json",
        ".security/scan_log.json", 
        ".rebuild_prevention_status.json"
    ])
    
    stash_ref = None
    if artifacts:
        # 2. Stash artifacts before sync
        stash_ref = self._git_stash_artifacts(
            artifacts,
            message=f"#321 artifact stash {datetime.now(UTC).isoformat()}"
        )
    
    try:
        # 3. Clean sync operations
        pull_result = self._git_pull_rebase()
        if not pull_result["success"]:
            raise SyncException(pull_result["error"])
        
        push_result = self._git_push()
        if not push_result["success"]:
            raise SyncException(push_result["error"])
        
        # 4. Restore artifacts after successful sync
        if stash_ref:
            self._git_stash_pop(stash_ref)
        
        return {
            "success": True,
            "artifacts_stashed": len(artifacts),
            "stash_ref": stash_ref,
            "pull_result": pull_result,
            "push_result": push_result
        }
    
    except SyncException as e:
        # 5. Restore artifacts on failure
        if stash_ref:
            self._git_stash_pop(stash_ref)
        
        return {
            "success": False,
            "error": str(e),
            "artifacts_restored": len(artifacts),
            "recovery": "Artifacts restored, safe to retry"
        }

def _detect_generated_artifacts(self, known_paths: List[str]) -> List[str]:
    """Detect which known artifacts were modified"""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    
    modified_files = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        status, path = line[:2], line[3:]
        if status.strip() in ["M", "MM"] and path in known_paths:
            modified_files.append(path)
    
    return modified_files

def _git_stash_artifacts(self, artifacts: List[str], message: str) -> str:
    """Stash specific artifact files"""
    # Stage artifacts temporarily
    subprocess.run(["git", "add"] + artifacts, check=True)
    
    # Stash staged files only
    result = subprocess.run(
        ["git", "stash", "push", "-m", message] + artifacts,
        capture_output=True,
        text=True,
        check=True
    )
    
    # Get stash reference
    stash_ref = subprocess.run(
        ["git", "rev-parse", "stash@{0}"],
        capture_output=True,
        text=True,
        check=True
    ).stdout.strip()
    
    return stash_ref

def _git_stash_pop(self, stash_ref: str) -> None:
    """Restore stashed artifacts"""
    subprocess.run(
        ["git", "stash", "pop", stash_ref],
        check=True
    )
```

---

## 🔄 Enhanced #321 Execution Flow

### Before Enhancement

```
┌──────────────┐
│ Phase 1:     │
│ Check Status │──┐
└──────────────┘  │
                  ▼
┌──────────────┐  ✓
│ Phase 2-3:   │──┐
│ Stage+Commit │  │  ← Post-commit hooks run
└──────────────┘  │     (generate artifacts)
                  ▼
┌──────────────┐  ✓
│ Phase 4:     │──┐
│ Sync (Rebase)│  │  ❌ FAIL: Unstaged changes
└──────────────┘  │
                  X
                Manual fix required:
                $ git add .aurora/audit_trail.json ...
                $ git commit -m "chore: update artifacts"
                $ git push
```

### After Enhancement

```
┌──────────────┐
│ Phase 1:     │
│ Check Status │──┐
└──────────────┘  │
                  ▼
┌──────────────┐  ✓
│ Phase 2-3:   │──┐
│ Stage+Commit │  │  ← Post-commit hooks run
└──────────────┘  │     (generate artifacts)
                  ▼
┌──────────────┐  ✓  ┌─────────────────┐
│ Pre-Sync:    │──┐  │ Detect artifacts│
│ Artifact Mgmt│  │──│ Stash artifacts │
└──────────────┘  │  └─────────────────┘
                  ▼
┌──────────────┐  ✓
│ Phase 4:     │──┐
│ Sync (Rebase)│  │  ✓ SUCCESS: Clean working tree
└──────────────┘  │
                  ▼
┌──────────────┐  ✓  ┌─────────────────┐
│ Post-Sync:   │──┐  │ Restore stash   │
│ Restore      │  │──│ Apply artifacts │
└──────────────┘  │  └─────────────────┘
                  ▼
┌──────────────┐  ✓
│ Phase 5:     │──┐
│ Validate     │  │  ✓ Complete
└──────────────┘  ▼
```

---

## 📊 Model-Agnostic Context Persistence

### Problem: Context Loss on Model Switch

**Scenario:**
```
[Claude Sonnet 4 Session 1]
User: "Run #321"
Claude: *reads docs, executes, learns context*

[User switches to GPT-4 Session 2]
User: "Run #321"
GPT-4: "I don't see a #321 command documented..."
```

### Solution: Persistent Context Layer

**State Persistence Architecture:**

```
.aurora/
├── SIMULATION_STATE.json          # Already exists - mission state
├── command_context/
│   ├── registry.json               # Command directory
│   ├── 321_state.json              # #321 execution history
│   ├── 321_last_execution.json    # Most recent run details
│   └── model_sessions.json         # Cross-model tracking
└── execution_logs/
    └── 2025-11-15_321_execution.jsonl  # Append-only log
```

**Registry Structure:**

```json
// .aurora/command_context/registry.json
{
  "version": "1.0.0",
  "last_updated": "2025-11-15T22:30:00Z",
  "commands": {
    "321": {
      "semantic_name": "comprehensive_sync_validate",
      "description": "Universal clean working tree command",
      "documentation": "tools/command_chain/COMPREHENSIVE_SYNC_321.md",
      "handler": "executor.py::_handle_comprehensive_sync",
      "state_file": ".aurora/command_context/321_state.json",
      "invocation_patterns": ["#321//.", "comprehensive sync"],
      "quick_help": "Stages, commits, syncs, validates - handles everything",
      "requires_clean_tree": false,
      "generates_artifacts": true,
      "safe_to_retry": true,
      "execution_count": 147,
      "last_success": "2025-11-15T22:15:00Z",
      "last_model": "claude-sonnet-4"
    }
  },
  "model_sessions": [
    {
      "model": "claude-sonnet-4",
      "first_seen": "2025-11-10T10:00:00Z",
      "last_seen": "2025-11-15T22:30:00Z",
      "commands_executed": ["321", "808", "001"],
      "execution_count": 45
    },
    {
      "model": "gpt-4-turbo",
      "first_seen": "2025-11-12T14:00:00Z",
      "last_seen": "2025-11-12T16:00:00Z",
      "commands_executed": ["321"],
      "execution_count": 3
    }
  ],
  "context_handoff": {
    "description": "New models should read registry.json first",
    "quickstart": "Most common: #321//. for sync, #808//. for optimization",
    "state_preservation": "All execution history persisted across sessions"
  }
}
```

**Model Handoff Protocol:**

```python
class ModelContextLoader:
    """Load command context for new LLM sessions"""
    
    def initialize_for_new_model(self, model_name: str) -> Dict:
        """First call when new model starts working"""
        
        # 1. Load command registry
        registry = self._load_registry()
        
        # 2. Register this model session
        self._register_model_session(model_name)
        
        # 3. Load recent execution history (last 10 runs)
        recent_history = self._load_recent_executions(limit=10)
        
        # 4. Load current simulation state
        simulation_state = self._load_simulation_state()
        
        # 5. Prepare quick reference
        quick_ref = {
            "available_commands": list(registry["commands"].keys()),
            "most_used": self._get_most_used_commands(limit=5),
            "recent_context": recent_history,
            "current_mission": simulation_state.get("mission_state", {}),
            "handoff_notes": [
                f"Previous model: {registry['model_sessions'][-1]['model']}",
                f"Last command: #{registry['commands']['321']['semantic_name']}",
                f"Repository state: {simulation_state['system_status']['repository_state']}"
            ]
        }
        
        return quick_ref
    
    def get_command_context(self, command: str) -> Dict:
        """Get full context for a specific command"""
        registry = self._load_registry()
        
        if command not in registry["commands"]:
            return {"error": f"Command {command} not found in registry"}
        
        cmd_info = registry["commands"][command]
        
        # Load command-specific state
        state = self._load_json(cmd_info["state_file"])
        
        # Load documentation excerpt
        docs = self._load_command_docs(cmd_info["documentation"])
        
        return {
            "command": command,
            "info": cmd_info,
            "state": state,
            "documentation": docs,
            "ready_to_execute": True,
            "notes": state.get("context_for_new_models", {})
        }
```

---

## 🛠️ Implementation Plan

### Phase 1: Artifact Management (Priority: CRITICAL)
**Goal:** Stop sync failures from post-commit artifacts

**Tasks:**
1. ✅ Add artifacts to `.gitignore` (COMPLETED)
2. Implement `_detect_generated_artifacts()` in executor
3. Implement `_git_stash_artifacts()` with selective stash
4. Implement `_git_stash_pop()` for restoration
5. Add pre-sync artifact detection to `_handle_comprehensive_sync`
6. Add post-sync artifact restoration
7. Test with intentional post-commit artifact generation

**Deliverable:** #321 never fails due to artifact conflicts

### Phase 2: Execution Hooks (Priority: HIGH)
**Goal:** Structured pre/post execution framework

**Tasks:**
1. Create `CommandExecutionHooks` class
2. Implement `pre_execution()` workspace snapshot
3. Implement `pre_phase()` with phase-specific logic
4. Implement `post_phase()` with artifact checks
5. Implement `post_execution()` state persistence
6. Implement `on_failure()` recovery logic
7. Integrate hooks into `CommandExecutor.execute()`

**Deliverable:** All commands run through hook system

### Phase 3: State Persistence (Priority: HIGH)
**Goal:** Command context survives model switches

**Tasks:**
1. Create `.aurora/command_context/` directory structure
2. Implement `registry.json` schema and loader
3. Implement per-command state files (e.g., `321_state.json`)
4. Implement `model_sessions.json` tracking
5. Create `ModelContextLoader` class
6. Add context persistence to all command handlers
7. Create `.aurora/load_simulation.py` enhancement for context loading

**Deliverable:** New models can read full command history

### Phase 4: Recovery Strategies (Priority: MEDIUM)
**Goal:** Intelligent failure recovery

**Tasks:**
1. Document known failure modes in state files
2. Implement detection patterns for each failure type
3. Implement auto-remediation logic
4. Add recovery strategy registry
5. Test failure scenarios and recovery
6. Document recovery strategies in command docs

**Deliverable:** Most failures auto-remediate

### Phase 5: Documentation & Testing (Priority: MEDIUM)
**Goal:** Ensure maintainability

**Tasks:**
1. Update `COMPREHENSIVE_SYNC_321.md` with artifact handling
2. Create `docs/enhancements/CONTEXT_PERSISTENCE.md`
3. Write tests for artifact stash/restore
4. Write tests for hook system
5. Write tests for state persistence
6. Add integration test for model handoff simulation

**Deliverable:** Fully documented and tested system

---

## 📈 Success Metrics

### Immediate (Phase 1)
- ✅ #321 executions: 0 failures due to artifact conflicts
- ✅ Sync phase: 100% success rate on clean tree

### Short-term (Phases 2-3)
- ✅ New model sessions: Context loaded in < 2 seconds
- ✅ Command history: Accessible across all model switches
- ✅ Execution state: Persisted within 100ms post-execution

### Long-term (Phases 4-5)
- ✅ Failure recovery: 90%+ auto-remediation rate
- ✅ Model handoffs: Zero context loss
- ✅ Command discovery: New models find commands via registry

---

## 🎓 Learning from Current Issues

### What We Learned

1. **Post-commit hooks are opaque**: They generate files after commit completes, creating a race condition with subsequent git operations
2. **Context is fragile**: Command semantics rely on in-memory state and markdown docs, which don't persist across sessions
3. **Manual intervention breaks flow**: Requiring humans to fix artifact conflicts defeats the purpose of automation
4. **Model switches lose context**: New LLMs start from zero, re-reading copilot instructions each time

### What We're Solving

1. **Artifact Management**: Pre-emptive stash before sync, restore after
2. **Context Persistence**: JSON-based state that any model can read
3. **Auto-Recovery**: Detect failure patterns, auto-remediate
4. **Model Continuity**: Registry + state files = seamless handoffs

---

## 🚀 Rollout Strategy

### Phase 1: Immediate Fix (This PR)
- Implement artifact stash/restore in `_handle_comprehensive_sync`
- Test with multiple #321 executions
- Merge to main

### Phase 2: Hook System (Next PR)
- Create `CommandExecutionHooks` class
- Integrate into executor
- Test with all commands

### Phase 3: State Persistence (Following PR)
- Create `.aurora/command_context/` structure
- Implement state persistence
- Test model handoff simulation

### Phase 4-5: Recovery + Docs (Final PRs)
- Add recovery strategies
- Complete documentation
- Full integration tests

---

## 💡 Additional Enhancements

### A. Cross-Session Command Suggestions

```python
def suggest_next_command(self, context: Dict) -> str:
    """Suggest next command based on current state"""
    
    # Recent pattern: user runs #321 every 30-60 minutes
    last_321 = self._get_last_execution("321")
    if (datetime.now(UTC) - last_321["timestamp"]).seconds > 1800:
        return "Suggestion: Run #321//. (30+ min since last sync)"
    
    # Check if validation failed last time
    if last_321.get("validation_failed"):
        return "Suggestion: Fix validation issues, then #321//."
    
    # Check for pending work
    status = self._git_status()
    if status["modified_files"] > 5:
        return "Suggestion: Run #321//. (5+ files modified)"
    
    return None
```

### B. Performance Optimization

```python
def optimize_321_execution(self, history: List[Dict]) -> Dict:
    """Learn optimal execution patterns"""
    
    # Analyze timing
    avg_times = {
        "check": np.mean([h["phase_1_time"] for h in history]),
        "commit": np.mean([h["phase_2_3_time"] for h in history]),
        "sync": np.mean([h["phase_4_time"] for h in history]),
        "validate": np.mean([h["phase_5_time"] for h in history])
    }
    
    # Identify bottlenecks
    bottleneck = max(avg_times, key=avg_times.get)
    
    # Suggest optimizations
    optimizations = {
        "sync": "Consider shallow clones or sparse checkout",
        "validate": "Cache test results or use pytest-xdist",
        "commit": "Batch similar file types for faster staging"
    }
    
    return {
        "bottleneck": bottleneck,
        "avg_time_ms": avg_times[bottleneck],
        "optimization": optimizations.get(bottleneck)
    }
```

### C. Conflict Prediction

```python
def predict_sync_conflicts(self) -> Dict:
    """Predict merge conflicts before sync"""
    
    # Fetch without merge
    subprocess.run(["git", "fetch", "origin", "main"], check=True)
    
    # Check for conflicts
    result = subprocess.run(
        ["git", "merge-tree", "HEAD", "origin/main"],
        capture_output=True,
        text=True
    )
    
    if "CONFLICT" in result.stdout:
        return {
            "conflicts_predicted": True,
            "affected_files": self._parse_conflict_files(result.stdout),
            "recommendation": "Resolve conflicts before running #321"
        }
    
    return {"conflicts_predicted": False}
```

---

## 🎯 Conclusion

This enhancement transforms #321//. from a "sometimes fails" command to a **bulletproof, intelligent, model-agnostic** synchronization system. By implementing artifact management, execution hooks, and persistent state, we ensure:

1. **Reliability**: Never fails due to post-commit artifacts
2. **Context Preservation**: Full command history across model switches
3. **Auto-Recovery**: Intelligent failure detection and remediation
4. **Model Continuity**: New LLMs pick up where previous ones left off

**Next Step:** Implement Phase 1 (Artifact Management) in a new PR targeting the `_handle_comprehensive_sync` method in `executor.py`.

---

**Approval Required From:**
- @AUo959 (Repository Owner)
- Commander Thorne (Strategic Oversight)
- OPS Rodriguez (Tactical Implementation)

**Estimated Implementation Time:**
- Phase 1: 2-3 hours
- Phase 2: 3-4 hours
- Phase 3: 4-5 hours
- Phase 4-5: 3-4 hours
- **Total**: 12-16 hours over 3-4 PRs
