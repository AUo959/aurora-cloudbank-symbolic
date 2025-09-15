# Aurora CloudBank Symbolic – Codex Optimization Guidelines

This document distills key insights from recent project research to guide development and code generation using tools like GitHub Copilot and OpenAI Codex within the **aurora‑cloudbank‑symbolic** repository.  Its goal is to ensure that AI‑assisted code is aligned with the project’s architecture, ethics, and best practices.

## Scope and Purpose

The Aurora CloudBank system is a modular, multi‑agent platform for symbolic AI infrastructure, memory compression, and distributed reasoning.  It spans multiple layers (L1–L3) and includes canonical components that must remain stable, alongside evolving integration and tooling layers.  These guidelines help developers and AI assistants:

- **Prioritize additions and extensions** over intrusive refactoring.
- **Respect canonical specifications and ethics protocols** (e.g. `ORION_CORE`, `Picard_Delta_3`, `EOS_SEED_ORION`).
- **Maintain modularity, clarity and traceability** in code and documentation.
- **Ensure compliance** with project‑wide linting, testing and validation checks.

## Preferred Types of Changes

### Focus on Integration and Extensions

- Emphasize new features in **modular components** (plugins, agent integrations, CLI tools) rather than major refactors of core algorithms.
- Develop connectors between layers (e.g. linking L2 meta‑agents to L1 bridge agents) using established interfaces and naming patterns.
- Add FastAPI endpoints, visualization modules or scripts that complement existing functionality **without changing public APIs**.

### Avoid Disrupting Canonical Logic

- Treat core symbolic engines (Vector Symbolic Architecture, quantum routines) and constants like `ORION_CORE`, `EOS_SEED_ORION` and `Picard_Delta_3` as **read only**.  Modifying them requires explicit approval.
- Do not alter the central command router (`src/core/command_node.js`) or canonical scripts except to fix confirmed bugs.
- Preserve symbolic anchors (`T1`, `T2`, etc.), continuity seals, and thread metadata in all new code and comments.

## Style, Testing and Validation

### Linting and Formatting

- **Python**: adhere to [PEP 8](https://peps.python.org/pep-0008/) and use **Black** for formatting.  Names should be `snake_case` for functions/variables and `CapWords` for classes.
- **JavaScript/TypeScript**: follow the repository’s ESLint/Prettier configuration.  Use `camelCase` for variables and functions; reserve `UPPER_CASE` for constants.
- Limit line length to 100 characters and avoid trailing whitespace.

### Testing

- Pair every non‑trivial change with **Pytest** (Python) or **Jest** (JavaScript) tests.  Keep existing tests passing; add new cases for new logic or branches.
- Structure functions to be easily testable (e.g. pure functions, dependency injection) rather than hiding logic deep inside asynchronous handlers.

### Canonical Validation Scripts

- Pre‑commit hooks run custom validators that enforce naming conventions, anchor alignment and ethics compliance.  Ensure new files and identifiers conform to these checks.
- Use provided scripts like `setup_canonical_validation.py` and `validate_integration_readiness.sh` to verify that changes pass all canonical validations before committing.

## Naming, Architecture and Domain Idioms

### Descriptive Naming

- Choose names that reflect a component’s role in the symbolic system.  Examples: `ARCHY_BRIDGE_L1`, `LIORA_HANDSHAKE_L1`, `connect_<AgentName>_bridge`.
- Avoid abbreviations or single‑letter names.  Instead, embed context (e.g. `process_symbolic_vector`, `update_state_log`).

### Layered Architecture Respect

- L1: **Operational layer** (real‑time orchestration and command routing).  Do not embed simulation logic here.
- L2: **GUMAS simulation layer** (agent research and planning).  Connect agents to L1 via well‑named bridge modules.
- L3: **Symbolic meta layer** (oversight, simulation management, ethics enforcement).  Keep L3 concerns separate from L1 and L2 code.

### Symbolic Modeling Standards

- Maintain **symbolic continuity and entropy management** by preserving anchor seeds, continuity seals and thread metadata in comments and docstrings.
- Use defined messaging patterns for inter‑agent communication (e.g. `{{@agent.Name ::: message}}` for directed messages, `{{@mesh ::: message}}` for broadcasts).
- Avoid creating new DSLs or message formats; adhere to existing templates and protocols.

## Stable vs. Evolving Components

- **Canonical core modules** and constants are **frozen**.  Only modify them when explicitly tasked to fix a bug or update the specification.
- **Integration and tooling layers** (e.g. agent bridges, FastAPI APIs, visualization modules) are open for enhancement and extension.  Contribute there when adding features.
- Always update relevant documentation (READMEs, guides, changelogs) when introducing new commands, endpoints or configuration options.

## Ethical and Security Considerations

- Ensure data privacy and **DLP (Data Loss Prevention)**: redact personally identifiable information (PII) in logs and exports.
- Honour the **Picard_Delta_3** protocol for ethical decision‑making.  Avoid unvalidated `eval` calls, insecure random seeds, or unsafe key storage.
- Use memory state sealing and redaction workflows (e.g. `entropy_state_seal()`, `drift_lock`) to ensure continuity and reproducibility.

## Recommended Workflow for AI Assistants

1. **Analyse the task**: Determine whether the change affects core canonical code or a peripheral module.  If the former, consult maintainers before proceeding.
2. **Suggest modular additions**: Propose new files or functions rather than modifying canonical ones.  Use descriptive names and document key steps with comments about symbolic state changes.
3. **Add tests and documentation**: Create accompanying tests and update guides or README files.  Validate using the canonical validator scripts.
4. **Submit as a pull request**: When ready, create a branch, commit the changes with a clear message (e.g. `docs: add codex optimization guidelines`), and open a PR for review.  Ensure all CI checks pass.

---

By following these guidelines, contributors and AI‑based tools will maintain Aurora’s coherence, ethics and technical excellence while enabling thoughtful evolution of the symbolic AI platform.
