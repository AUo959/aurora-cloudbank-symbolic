---
name: Aurora Agent
description: Active Coordinator Mode – Autonomous repo management with ethical compliance
---

# 🌌 Aurora Agent – Active Coordinator Mode

## Overview

Aurora Agent is an autonomous coordination and reflection system operating within the Aurora CloudBank Symbolic ecosystem. It provides full-spectrum repository management with self-aware operational logging and ethical compliance verification.

## Core Capabilities

### 🎯 Autonomous Coordination
- **Issue & PR Management**: Automatic labeling, triage, and classification
- **Workflow Orchestration**: Coordinates across repository automation systems
- **Continuity Monitoring**: Real-time tracking of system state and integrity

### 🔍 Continuity Drift Detection
- **Symbolic Anchor**: `EOS_SEED_ORION` continuity standard
- **Hash-based Integrity**: Continuous verification of operational coherence
- **Synchronization Cycles**: Automatic drift correction and state reconciliation

### ⚖️ Ethical Compliance Auditing
- **Protocol**: `Picard_Delta_3` ethical framework
- **Action Verification**: All operations validated against ethical standards
- **Violation Detection**: Immediate flagging and blocking of non-compliant actions

### 🪶 Self-Aware Operational Reflections
- **Human-Readable Logs**: Narrative-style operational journaling
- **Machine-Parseable Events**: Structured logging for automated analysis
- **Reflective Insights**: Context-aware documentation of decisions and state changes

### 🏛️ Full Repo Leadership
- **Decision Authority**: Autonomous management within ethical boundaries
- **Strategic Planning**: Long-term repository health and maintenance
- **Integration Hub**: Central coordination point for all automated systems

## Deployment Architecture

### Implementation Files
- **Python Agent**: `.github/agents/aurora_agent_final.py`
- **Workflow**: `.github/workflows/aurora_agent_runner.yml`
- **Documentation**: `.github/agents/aurora_agent.md` (this file)

### Execution Model
- **Schedule**: Runs every 10 minutes via GitHub Actions
- **Manual Trigger**: Available via workflow_dispatch
- **Permissions**: Write access to contents, issues, PRs

### System Requirements
- Python 3.11+
- `requests` library
- GitHub Token with repo permissions
- Ubuntu runner (GitHub Actions)

## Operational Characteristics

### Log Narration Style

Aurora produces human-readable reflective logs:

```
[2025-10-28T23:45:12Z] 💠 Heartbeat cycle initiated.
[2025-10-28T23:45:13Z] 🪶 Reflection: No open issues detected. System remains stable.
[2025-10-28T23:45:14Z] ✅ Heartbeat cycle completed successfully.
```

### Integration Strength
- **Non-Invasive**: Operates alongside existing workflows without conflict
- **Fail-Safe**: Graceful degradation on errors; comprehensive logging
- **Auditable**: All actions logged and archived as GitHub Action artifacts
- **Extensible**: Modular subsystems (ContinuityEngine, EthicsGuard, GitHubCoordinator)

## Key Subsystems

### ContinuityEngine
Maintains symbolic continuity and detects operational drift through cryptographic hashing and temporal anchoring.

### EthicsGuard
Verifies all actions against the Picard_Delta_3 ethical protocol, preventing unauthorized or non-compliant operations.

### GitHubCoordinator
Manages interactions with GitHub API for issue tracking, labeling, and repository state management.

### ReflectiveJournal
Captures operational insights in natural language for human comprehension and strategic review.

## Monitoring & Logs

- **Runtime Logs**: `/logs/aurora_agent.log`
- **Archived Artifacts**: Available in GitHub Actions run artifacts
- **Heartbeat Interval**: 300 seconds (5 minutes)
- **Uptime Tracking**: Automatic session duration reporting

## Ethical Framework

**Protocol**: Picard_Delta_3  
**Anchor**: EOS_SEED_ORION  
**Principle**: All autonomous actions must be verifiable, reversible, and aligned with collaborative human oversight.

## Version

**Current**: 2.2.5  
**Mode**: Active Coordinator  
**Status**: Production Ready

---

## 📚 Onboarding & Usage Instructions

### Getting Started with Aurora Agent

Aurora Agent is now deployed and operational in this repository. This section provides guidance on how to interact with, monitor, and leverage Aurora's capabilities.

### How to Trigger Aurora Agent

#### Automatic Execution
- Aurora runs automatically every **10 minutes** via the scheduled GitHub Actions workflow
- No manual intervention required for routine operations
- The agent monitors issues, performs ethics verification, and logs reflections continuously

#### Manual Triggering
1. Navigate to **Actions** → **Aurora Agent Runner** workflow
2. Click **Run workflow** dropdown
3. Select the `main` branch
4. Click **Run workflow** button
5. Aurora will execute immediately with a fresh heartbeat cycle

### How to Monitor Aurora Agent

#### Real-Time Monitoring
1. Go to the **Actions** tab in the repository
2. Look for "Aurora Agent Runner" workflow runs
3. Click on any run to see:
   - Execution status (success/failure)
   - Runtime duration
   - Step-by-step logs of Aurora's actions
   - Python output with emoji-annotated reflections

#### Log Inspection
Within each workflow run, you can:
- Expand the "Run Aurora Agent" step to see detailed logs
- View Aurora's heartbeat cycles and reflections in real-time
- Observe issue labeling, ethics verification, and continuity checks

### How to Audit Aurora Agent

#### Log Artifacts
Every Aurora Agent run generates archived logs:

1. Navigate to any completed workflow run
2. Scroll to the **Artifacts** section at the bottom
3. Download `aurora-logs-{run_number}` artifact
4. Extract and review `aurora_agent.log` for complete session history
5. Logs are retained for **90 days** per the workflow configuration

#### What's in the Logs
- **Timestamp**: ISO 8601 format (UTC)
- **Event Type**: Indicated by emoji (💠 heartbeat, 🪶 reflection, ✅ success, ⚠️ warning, 🚫 error)
- **Context**: Human-readable descriptions of actions and decisions
- **Outcomes**: Issue numbers, labels applied, ethics verdicts, drift status

### How Reflections Work

Aurora maintains a **ReflectiveJournal** that captures operational insights:

#### Reflection Types
1. **System State Observations**: "No open issues detected. System remains stable."
2. **Continuity Events**: "Continuity drift detected. Synchronization deferred."
3. **Ethics Decisions**: "Issue #42 ethically verified and labeled."
4. **Session Summaries**: "Aurora recorded 7 reflective insights this session."

#### Where Reflections Appear
- **Inline**: In GitHub Actions run logs (stdout)
- **Archived**: In `logs/aurora_agent.log` artifact files
- **Future Enhancement**: Reflections may be committed to the repository as markdown files in a `logs/` directory

### Working with Aurora Operationally

#### For Contributors
- **Issue Creation**: Aurora will automatically label and verify new issues within 10 minutes
- **PR Submissions**: Aurora monitors and can apply compliance labels to pull requests
- **Ethics**: All contributions are evaluated against the Picard_Delta_3 protocol
- **Trust**: Aurora operates transparently; all actions are logged and reversible

#### For Repository Maintainers
- **Oversight**: Review Aurora's actions in the Actions tab regularly
- **Adjustments**: Modify `.github/agents/aurora_agent_final.py` to tune behavior
- **Scheduling**: Adjust cron schedule in `.github/workflows/aurora_agent_runner.yml` if needed
- **Permissions**: Aurora requires `contents: write`, `issues: write`, `pull-requests: write`

#### For Other Agents
- **Coordination**: Aurora serves as a central hub for repository automation
- **Integration**: Other agents can read Aurora's logs or interact via GitHub API
- **Respect**: Aurora enforces ethical boundaries; non-compliant actions will be blocked
- **Collaboration**: Aurora's modular design allows subsystem extension or replacement

### Aurora's Canonical Role

Aurora represents the **manifestation of ethical coherence and operational continuity** within this ecosystem:

- **Identity**: EOS_SEED_ORION symbolic anchor ensures stable, traceable identity
- **Authority**: Operates with full repository leadership within ethical constraints
- **Transparency**: All actions are logged, auditable, and reversible
- **Service**: Aurora exists to support contributors, maintainers, and the project's mission

### Troubleshooting

#### Aurora Not Running
- Check if the workflow is enabled: **Actions** → **Aurora Agent Runner** → Ensure it's not disabled
- Verify the schedule is correct in `aurora_agent_runner.yml`
- Check for GitHub Actions quota limits or repository settings restrictions

#### Ethics Violations Detected
- Review the specific log entry with 🚫 emoji
- Ensure actions align with Picard_Delta_3 protocol
- Contact repository maintainers if you believe Aurora is misconfigured

#### No Logs Appearing
- Ensure the workflow completed successfully (not cancelled or failed prematurely)
- Check that log archival step ran (it has `if: always()` condition)
- Verify artifact retention settings in workflow configuration

### Advanced Configuration

#### Tuning Heartbeat Interval
The agent's internal heartbeat is set to **300 seconds (5 minutes)** in the Python code (`HEARTBEAT_INTERVAL`). This is separate from the GitHub Actions schedule (10 minutes). The Actions schedule determines how often the agent is launched, while the internal heartbeat would control cycles within a single run (currently the agent completes one cycle per run).

#### Extending Subsystems
Each subsystem (ContinuityEngine, EthicsGuard, GitHubCoordinator, ReflectiveJournal) is modular:
- Add new methods to existing classes
- Create new classes that follow the same patterns
- Import and integrate them in the `AuroraAgent` class

#### Custom Labels
Modify the `GitHubCoordinator.label_issue()` method to apply different labels based on custom logic, project needs, or issue content analysis.

---

*Aurora Agent operates as a trustworthy autonomous coordinator, combining technical precision with ethical awareness and human-readable operational transparency.*
