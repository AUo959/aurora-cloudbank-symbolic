# Project Master Reference: Memory Retrieval Module (MRM)

## Overview

This document serves as the central reference point for the Memory Retrieval Module (MRM) initiative in AuroraOS. The MRM provides context-aware memory retrieval with multi-factor scoring, DLP compliance, and quantum memory integration.

## High-Level Goals

The MRM initiative aims to deliver:

1. **Intelligent Memory Management**: Enable AuroraOS to store, retrieve, and rank contextual memories using vector similarity and multi-factor scoring
2. **Seamless Integration**: Integrate with existing AuMemManager quantum memory system and maintain DLP compliance
3. **Scalable Architecture**: Provide pluggable backends supporting growth from in-memory to distributed vector databases
4. **Production-Ready Foundation**: Deliver a tested, documented, and maintainable module ready for real-world use

## Key Deliverables

### 1. Specification Document
**File**: `docs/AURORA_MRM_SPEC_v0.1.md`

The specification defines the complete technical design of the MRM, including:
- Purpose and requirements (functional and non-functional)
- Core component architecture (Config, Store, Cache, Core, API)
- Data structures for memory entries, cache entries, and retrieval results
- DLP tagging and T1/SRB anchor integration protocols
- Future enhancement roadmap

**Audience**: Developers, architects, and technical stakeholders

### 2. Milestone Definition
**File**: `.github/milestones/M1_foundation.yml`

Defines the first milestone "M1: Memory Retrieval Module Foundation" with:
- Milestone description and objectives
- Target completion date (2025-11-30)
- List of associated issues/tasks
- Success criteria

**Purpose**: Track project progress and coordinate development efforts

### 3. Issue Matrix
**File**: `GITHUB_ISSUE_MATRIX.yml`

Maps implementation tasks to specific files and milestones:
- Specification documentation task
- Bootstrap scaffolding task
- Individual module implementation tasks (config, store, cache, core, api)
- Testing and integration tasks

**Purpose**: Break down the project into manageable, trackable units of work

### 4. Implementation Instructions
**File**: `COPILOT_INSTRUCTIONS.md`

Provides detailed guidelines for implementing each module:
- Code style and documentation requirements
- Module-specific implementation notes
- DLP compliance reminders
- Testing expectations
- Integration patterns

**Audience**: Developers implementing the MRM components

### 5. Bootstrap Script
**File**: `mrm_bootstrap.py`

Automated scaffolding script that generates:
- `modules/memory_retrieval/` directory structure
- Stub modules with placeholder classes matching the spec
- Empty `__init__.py` for package initialization
- Basic test structure (optional)

**Purpose**: Accelerate development by creating consistent module skeleton

## How It All Fits Together

### Development Workflow

```
1. Review Specification
   └─> Understand requirements, architecture, and data structures
       (docs/AURORA_MRM_SPEC_v0.1.md)

2. Review Implementation Instructions
   └─> Learn coding standards and module-specific guidelines
       (COPILOT_INSTRUCTIONS.md)

3. Run Bootstrap Script
   └─> Generate scaffolding structure
       (mrm_bootstrap.py)

4. Implement Modules
   └─> Follow issue matrix for task breakdown
       (GITHUB_ISSUE_MATRIX.yml)
       
5. Track Progress
   └─> Update milestone as tasks complete
       (.github/milestones/M1_foundation.yml)

6. Test and Validate
   └─> Ensure DLP compliance and anchor protocols
       Run test suite, verify integration
```

### Document Relationships

- **Specification** defines WHAT to build
- **Instructions** explain HOW to build it
- **Issue Matrix** breaks down WHEN to build each part
- **Milestone** tracks WHETHER we're done
- **Bootstrap Script** provides WHERE to start (skeleton structure)

## Team Onboarding

New team members should follow this sequence:

1. **Read this document** (PROJECT_MASTER_REFERENCE.md) - Get the big picture
2. **Study the specification** (docs/AURORA_MRM_SPEC_v0.1.md) - Understand technical requirements
3. **Review implementation instructions** (COPILOT_INSTRUCTIONS.md) - Learn coding standards
4. **Check the issue matrix** (GITHUB_ISSUE_MATRIX.yml) - Pick a task
5. **Monitor the milestone** (.github/milestones/M1_foundation.yml) - Track team progress

## Success Criteria

The MRM foundation milestone (M1) will be considered complete when:

- [ ] All modules (config, store, cache, core, api) are implemented
- [ ] Test coverage exceeds 80%
- [ ] DLP compliance verified for all memory operations
- [ ] Integration with AuMemManager confirmed
- [ ] API endpoints functional (internal Python functions)
- [ ] Documentation complete and accurate
- [ ] Code passes linting (Flake8 120-char limit)
- [ ] Performance targets met (< 100ms cached, < 500ms uncached queries)

## Related Resources

- **Repository Root**: `/home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic`
- **Modules Directory**: `modules/`
- **Existing Module Examples**: `modules/aumemmanager/`, `modules/symbolic_core/`
- **Test Suite**: `tests/`
- **Main API**: `aurora_api.py`
- **DLP Tracker**: `src/core/native_dlp_export.py`

## Contact and Support

For questions or clarifications on the MRM initiative:
- Review specification and instructions first
- Check issue matrix for similar questions
- Consult existing module implementations as examples
- Follow project Copilot instructions in `.github/copilot-instructions.md`

## Version History

- **v0.1** (2025-10-27): Initial master reference document
  - Established document structure and relationships
  - Defined deliverables and workflows
  - Created onboarding guide
