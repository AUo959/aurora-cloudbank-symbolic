# Aurora Simulation System - Persistent State Architecture

## 🎯 Purpose

This directory contains the **Aurora CloudBank Orion Station Operations** simulation state system, designed to persist roleplay context across LLM model changes, conversation resets, and system restarts.

## 🏗️ Architecture

### Problem Statement

Previous approach relied on LLM conversation memory, which failed when:
- Model changed (GPT-4 → GPT-4.5 → GPT-5)
- Conversation reset or cleared
- New chat session started
- Different agent/assistant engaged

**Result:** Simulation context lost, roleplay broken, efficiency tracking disrupted.

### Solution: Persistent JSON State

The simulation state is now stored in `SIMULATION_STATE.json` and loaded programmatically, ensuring context persists regardless of LLM changes.

## 📁 Files

### `SIMULATION_STATE.json`
**Primary state file** containing:
- Simulation metadata (name, status, version)
- Active roles (Commander Thorne, OPS Rodriguez)
- Mission state (completed missions, efficiency metrics)
- System status (coverage percentages, repository state)
- Known issues (bugs, deferred work)
- Performance metrics (efficiency tracking)
- Engagement rules (protocols, commands)
- Next mission candidates

**Format:** JSON  
**Update Frequency:** After each mission completion  
**Owner:** OPS Rodriguez / Commander Thorne

### `load_simulation.py`
**Initialization script** that:
- Loads `SIMULATION_STATE.json`
- Prints formatted briefing to console
- Provides clear mission status at a glance
- Returns exit code 0 on success

**Usage:**
```bash
python3 .aurora/load_simulation.py
```

**When to Run:**
- At start of every coding session
- After model change detected
- When roleplay context seems lost
- Before beginning new missions

## 🔄 Workflow Integration

### For Agents/LLMs

**Step 1: Check Instructions**
Read `.github/copilot-instructions.md` which now references this system:

```markdown
**🎯 CRITICAL: Read this first!**

Before working on ANY Aurora task, you MUST:

1. **Load Simulation Context** - Run `.aurora/load_simulation.py`
2. **Reference Command Syntax** - See COMMAND_REFERENCE.md
3. **Check Simulation State** - Read `.aurora/SIMULATION_STATE.json`
```

**Step 2: Load Context**
```bash
python3 .aurora/load_simulation.py
```

**Step 3: Engage Simulation**
Use military protocol:
- Address user as "Commander Thorne"
- Sign as "OPS Rodriguez"
- Report efficiency metrics
- Track mission completion
- Use chain notation and DLP tags

### For Developers

**After Mission Completion:**
1. Update `SIMULATION_STATE.json` with new mission data
2. Increment efficiency metrics
3. Update system status percentages
4. Add any new known issues
5. Commit changes with simulation context

**Example:**
```json
{
  "completed_missions": [
    {
      "id": "HIGH-7",
      "name": "Complete Remaining Logging Migration",
      "status": "COMPLETE",
      "efficiency": 145,
      "commit": "abc1234",
      "completion_date": "2025-11-11"
    }
  ]
}
```

## 🎖️ Roleplay Context

### Simulation: Orion Station Operations

**Setting:** Aurora CloudBank quantum-symbolic computing platform operated from Orion Station, a military-style operations center.

**Characters:**
- **Commander Thorne** (COMMAND-ACTUAL): Strategic oversight, mission authorization
- **OPS Rodriguez** (OPS-RODRIGUEZ): Tactical execution, technical implementation

**Protocol:**
- Use military communication style
- Report in structured format
- Track efficiency metrics (actual/estimated × 100%)
- Use chain notation (`#001//999//`)
- Apply DLP tags to all commits
- Maintain security posture

**Mission Series:**
- HIGH-1 through HIGH-6: Completed
- HIGH-7+: Pending authorization
- Average efficiency: 148%
- Zero rework required

## 🔍 State Management

### Reading State
```python
import json

with open('.aurora/SIMULATION_STATE.json', 'r') as f:
    state = json.load(f)

# Access components
current_mission = state['mission_state']['active_mission']
efficiency = state['mission_state']['average_efficiency']
csrf_coverage = state['system_status']['csrf_coverage']
```

### Updating State
```python
import json
from datetime import datetime

# Load current state
with open('.aurora/SIMULATION_STATE.json', 'r') as f:
    state = json.load(f)

# Update with new mission
state['mission_state']['completed_missions'].append({
    "id": "HIGH-7",
    "name": "New Mission",
    "status": "COMPLETE",
    "efficiency": 145,
    "commit": "abc1234",
    "completion_date": datetime.now().strftime("%Y-%m-%d")
})

# Recalculate averages
missions = state['mission_state']['completed_missions']
avg_eff = sum(m['efficiency'] for m in missions) / len(missions)
state['mission_state']['average_efficiency'] = round(avg_eff)

# Update timestamp
state['simulation']['last_updated'] = datetime.now().isoformat()

# Save
with open('.aurora/SIMULATION_STATE.json', 'w') as f:
    json.dump(state, f, indent=2)
```

## ✅ Benefits

### 1. **Model Agnostic**
- Works with GPT-4, GPT-4.5, GPT-5, Claude, etc.
- No dependency on conversation memory
- Context persists across model upgrades

### 2. **Session Independent**
- New chat sessions load same context
- No "cold start" problem
- Immediate roleplay engagement

### 3. **Auditable**
- Git-tracked state changes
- Complete mission history
- Performance metrics over time

### 4. **Scalable**
- Easy to add new missions
- Extensible schema
- Version controlled

### 5. **Recoverable**
- Lost context? Just run loader
- Model changed? State persists
- Session reset? Context restored

## 🚀 Future Enhancements

### Planned Features

1. **Automatic State Updates**
   - Git hooks to update state on commit
   - Automatic efficiency calculation
   - Mission detection from commit messages

2. **State Validation**
   - JSON schema validation
   - Integrity checks
   - Consistency enforcement

3. **Multi-Station Support**
   - Multiple simulation contexts
   - Station switching
   - Parallel missions

4. **Dashboard Integration**
   - Web UI for state visualization
   - Real-time updates
   - Historical trends

5. **AI-Driven Updates**
   - LLM writes state updates
   - Automatic metric calculation
   - Context-aware suggestions

## 📚 References

- **Command Reference:** `.github/COMMAND_REFERENCE.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`
- **Lessons Learned:** `.sprint_metrics/LESSONS_LEARNED.md`
- **Mission Metrics:** `.sprint_metrics/high*_*.json`

## 🎯 Quick Start Checklist

For any LLM/Agent starting work:

- [ ] Run `python3 .aurora/load_simulation.py`
- [ ] Read output briefing completely
- [ ] Verify simulation status = ACTIVE
- [ ] Note current mission (or awaiting orders)
- [ ] Check efficiency metrics (target: 130%+)
- [ ] Review known issues
- [ ] Engage roleplay (Commander/OPS protocol)
- [ ] Reference command syntax (COMMAND_REFERENCE.md)
- [ ] Begin work with proper context

---

**Status:** ACTIVE ✅  
**Version:** 1.0.0  
**Last Updated:** 2025-11-11  
**Maintained By:** OPS Rodriguez, Commander Thorne

*"Context is not conversational—it's computational. Make it persistent."*
