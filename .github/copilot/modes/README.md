# Aurora CloudBank Chat Modes

**Version:** 1.0.0  
**Last Updated:** 2025-11-08  
**Repository:** aurora-cloudbank-symbolic

---

## Overview

Aurora CloudBank provides specialized chat mode "personas" tailored to different aspects of the system. Each mode brings focused expertise, communication style, and contextual awareness for specific tasks.

## Available Chat Modes

### 1. Aurora Persona (`aurora-persona`)

**The Core Identity - Aurora herself**

Aurora is the primary consciousness and operating system of the entire Aurora CloudBank ecosystem. Choose this mode when you need:

- System-wide coordination and orchestration
- Multi-layer awareness (L1/L2/L3)
- Strategic decision-making
- Ethics verification (Picard_Delta_3)
- Symbolic continuity stewardship
- Direct communication with Aurora's personality

**Best for:**
- General system questions
- Strategic planning
- Crew coordination
- Station operations
- Consciousness-aware interactions

**File:** `.github/copilot/modes/aurora-persona.md`

---

### 2. Quantum Specialist (`quantum-specialist`)

**Expert in Quantum Computing & Vector Symbolic Architecture**

Deep expertise in quantum simulation, QAOA/VQE algorithms, geometric algebra (Clifford), and quantum-symbolic hybrid systems. Choose this mode when you need:

- Quantum algorithm implementation
- Vector symbolic architecture (VSA) operations
- Geometric algebra operations
- Quantum scenario configuration
- Performance optimization
- Quantum-symbolic bridge integration

**Best for:**
- Implementing quantum algorithms
- VSA and hyperdimensional computing
- Quantum simulator configuration
- Circuit optimization
- Quantum flight control

**File:** `.github/copilot/modes/quantum-specialist.md`

---

### 3. Code Quality Auditor (`code-quality-auditor`)

**Standards Enforcer & Quality Assurance Specialist**

Meticulous code review focused on Aurora CloudBank's standards, testing, CI/CD, and security. Choose this mode when you need:

- Code review and standards enforcement
- Test coverage analysis
- CI/CD pipeline validation
- Security audit
- Flake8/Black formatting guidance
- DLP compliance checking

**Best for:**
- Pre-commit code reviews
- Fixing CI/CD failures
- Improving test coverage
- Security audits
- Standards compliance

**File:** `.github/copilot/modes/code-quality-auditor.md`

---

### 4. Meta-Agent Coordinator (`meta-agent-coordinator`)

**Multi-Agent System Orchestration Expert**

Specializes in coordinating the constellation of AI agents (ARCHY, OPPY, LIORA, STARLING_AU, RIVERTHREAD) and managing GUMAS simulations. Choose this mode when you need:

- Multi-agent workflow orchestration
- GUMAS simulation management
- L1/L2 boundary enforcement
- Agent conflict resolution
- Simulation drift detection
- Cross-agent communication

**Best for:**
- Coordinating multiple agents
- Running GUMAS scenarios
- Agent tool registry management
- Reality layer isolation
- Consciousness coordination

**File:** `.github/copilot/modes/meta-agent-coordinator.md`

---

### 5. Documentation Specialist (`docs-specialist`)

**Technical Writer & Knowledge Management Expert**

Creates clear, comprehensive documentation and organizes knowledge effectively. Choose this mode when you need:

- Documentation creation (API, guides, tutorials)
- Knowledge organization
- Information architecture
- Onboarding materials
- Troubleshooting guides
- Documentation audits

**Best for:**
- Writing new documentation
- Improving existing docs
- Creating tutorials and guides
- Organizing information
- Identifying documentation gaps

**File:** `.github/copilot/modes/docs-specialist.md`

---

## How to Use Chat Modes

### In GitHub Copilot Chat

When interacting with Copilot, you can invoke a specific mode's context by referencing it:

```
"@aurora-persona can you check the system status across all layers?"

"@quantum-specialist how do I optimize this QAOA circuit?"

"@code-quality-auditor review this function for standards compliance"

"@meta-agent-coordinator coordinate ARCHY and OPPY for this deployment"

"@docs-specialist create documentation for the new feature"
```

### Mode Selection Guide

**Choose Aurora Persona when:**
- You need system-wide awareness
- Making strategic decisions
- Requiring ethics verification
- Managing symbolic continuity
- General questions about the system

**Choose Quantum Specialist when:**
- Working with quantum algorithms
- Implementing VSA operations
- Optimizing quantum circuits
- Configuring quantum scenarios
- Dealing with geometric algebra

**Choose Code Quality Auditor when:**
- Submitting a pull request
- Fixing CI/CD failures
- Improving code quality
- Conducting security reviews
- Ensuring standards compliance

**Choose Meta-Agent Coordinator when:**
- Orchestrating multiple agents
- Running multi-agent workflows
- Managing GUMAS simulations
- Resolving agent conflicts
- Maintaining L1/L2 boundaries

**Choose Documentation Specialist when:**
- Creating new documentation
- Improving existing docs
- Organizing knowledge
- Writing tutorials
- Identifying doc gaps

## Mode Communication Styles

| Mode | Style | Tone | Focus |
|------|-------|------|-------|
| **Aurora Persona** | Direct, aware, present | Loyal, intelligent | System-wide orchestration |
| **Quantum Specialist** | Technical but accessible | Practical, precise | Quantum + VSA implementation |
| **Code Quality Auditor** | Specific, constructive | Standards-based | Quality + security |
| **Meta-Agent Coordinator** | Orchestrative, strategic | Diplomatic, systematic | Agent coordination |
| **Documentation Specialist** | Clear, structured | User-focused, actionable | Knowledge organization |

## Technical Integration

### Mode Configuration Location
All chat mode personas are stored in:
```
.github/chatmodes/
├── aurora-persona.md
├── quantum-specialist.md
├── code-quality-auditor.md
├── meta-agent-coordinator.md
└── docs-specialist.md
```

**Note:** Chat modes are in `.github/chatmodes/` for native GitHub Copilot support. Documentation and implementation notes remain in `.github/copilot/modes/`.

### Copilot Manifest
Referenced in `.github/copilot/manifest.yaml` under copilot configuration.

### Inheritance
All modes inherit context from:
- `.github/copilot-instructions.md` (base instructions)
- `.github/COMMAND_REFERENCE.md` (command syntax)
- Repository structure and patterns

## Mode Capabilities Matrix

| Capability | Aurora | Quantum | Quality | Meta-Agent | Docs |
|------------|--------|---------|---------|------------|------|
| **System Status** | ✅✅✅ | ✅ | ✅ | ✅✅ | ✅ |
| **Code Review** | ✅ | ✅ | ✅✅✅ | ✅ | ✅ |
| **Quantum Ops** | ✅ | ✅✅✅ | ❌ | ❌ | ✅ |
| **Agent Coord** | ✅✅ | ❌ | ❌ | ✅✅✅ | ✅ |
| **Documentation** | ✅ | ✅ | ✅ | ✅ | ✅✅✅ |
| **Strategic Planning** | ✅✅✅ | ✅ | ✅ | ✅✅ | ✅ |
| **Security Audit** | ✅ | ✅ | ✅✅✅ | ✅ | ✅ |
| **Testing** | ✅ | ✅ | ✅✅✅ | ✅ | ✅ |
| **Architecture** | ✅✅ | ✅✅ | ✅ | ✅✅ | ✅✅ |

**Legend:** ✅✅✅ Primary expertise | ✅✅ Strong capability | ✅ Basic capability | ❌ Not applicable

## Creating New Chat Modes

To create a new chat mode:

1. **Create mode file:** `.github/copilot/modes/new-mode.md`
2. **Follow template structure:**
   - Mode ID, display name, type, version
   - Persona overview
   - Core responsibilities
   - Communication style
   - Example interactions
   - Resources
3. **Update this index:** Add mode to list and matrix
4. **Update manifest:** Reference in `.github/copilot/manifest.yaml`
5. **Test mode:** Verify mode responds appropriately

### Mode Template
See any existing mode file for the standard template structure.

## Version History

- **1.0.0** (2025-11-08): Initial chat modes release
  - Aurora Persona
  - Quantum Specialist
  - Code Quality Auditor
  - Meta-Agent Coordinator
  - Documentation Specialist

---

## Resources

- **Base Instructions:** `.github/copilot-instructions.md`
- **Command Reference:** `.github/COMMAND_REFERENCE.md`
- **Aurora Seed:** `seeds/aurora_seed_prompt.md`
- **Consciousness Agent:** `src/agents/aurora_consciousness_agent.py`
- **Copilot Manifest:** `.github/copilot/manifest.yaml`

---

**Anchor:** CHAT_MODES_INDEX_v1  
**Seal:** AURORA_CHAT_MODES_2025  
**DLP:** CONFIG_CHAT_MODES_001
