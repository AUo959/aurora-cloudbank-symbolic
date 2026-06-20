# OPAL2 Treasure Map
> **For LLM Navigation Use** | Repo: `AUo959/aurora-cloudbank-symbolic` | Generated: 2026-02-20

This document is an authoritative cross-reference guide for any agent or LLM needing to locate, understand, or work with OPAL2 artifacts across the repository. Read from top to bottom on first contact. Use section headers as jump targets thereafter.

---

## 1. What Is OPAL2?

OPAL2 is the **symbolic rendering and interface layer** of the Aurora runtime system. It handles:
- **Glyph generation and caching** (visual/symbolic rendering primitives)
- **Aurora diff integration** (symbolic diff between runtime states)
- **Immersive web core** (WebXR/immersive interface scaffolding)
- **Plugin architecture** (extensible component model)
- **Config management** (YAML-driven runtime configuration)
- **API surface** (external-facing REST/programmatic interface)

OPAL2 is distinct from OPAL1 in that it introduces a plugin bus, a structured glyph cache, and full Aurora diff/optimizer integration. It lives primarily under `modules/opal2/`.

---

## 2. Primary Module Directory

**Root:** [`modules/opal2/`](https://github.com/AUo959/aurora-cloudbank-symbolic/tree/main/modules/opal2)

| File | Role | Link |
|---|---|---|
| `__init__.py` | Package init, top-level imports | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/__init__.py) |
| `base_component.py` | Abstract base class for all OPAL2 components | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/base_component.py) |
| `glyph_core.py` | Core glyph generation logic — **start here for rendering** | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/glyph_core.py) |
| `glyph_cache.py` | Glyph caching layer, performance layer over `glyph_core` | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/glyph_cache.py) |
| `config_manager.py` | YAML config loader and runtime config interface | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/config_manager.py) |
| `interface_layers.py` | Interface abstraction stack (input/output layers) | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/interface_layers.py) |
| `immersive_web_core.py` | WebXR / immersive web scaffolding | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/immersive_web_core.py) |
| `aurora_diff_integration.py` | Hooks into Aurora runtime diff system | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/aurora_diff_integration.py) |
| `aurora_diff_optimizer.py` | Optimization pass over Aurora diffs | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/aurora_diff_optimizer.py) |
| `README.md` | Module-level README — **read first for module context** | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/README.md) |

### Plugin Subdirectory
**Path:** `modules/opal2/plugins/`

| File | Role | Link |
|---|---|---|
| `base_plugin.py` | Abstract plugin interface — all OPAL2 plugins extend this | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/plugins/base_plugin.py) |

### API Subdirectory
**Path:** `modules/opal2/api/`

| File | Role | Link |
|---|---|---|
| `opal2_api.py` | Primary external API entrypoint for OPAL2 | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/opal2/api/opal2_api.py) |

---

## 3. Configuration

**Path:** [`config/opal2_graphics.yaml`](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/config/opal2_graphics.yaml)

This YAML file governs rendering parameters for OPAL2 graphics. It is consumed by `config_manager.py`. Any changes to glyph rendering behavior, resolution, or pipeline settings should begin here.

---

## 4. Documentation Files

### Active / Canonical
| File | Description | Link |
|---|---|---|
| `docs/operational/guides/OPAL2_EXPANSION_PLAN.md` | Forward-looking expansion roadmap — **canonical planning doc** | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/docs/operational/guides/OPAL2_EXPANSION_PLAN.md) |

### Archived / Historical
| File | Description | Link |
|---|---|---|
| `docs/operational/archived/OPAL2_EXPANSION_PROGRESS.md` | Historical progress log from OPAL2 expansion sprint | [link](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/docs/operational/archived/OPAL2_EXPANSION_PROGRESS.md) |

---

## 5. Tooling

**Path:** [`tools/fixers/fix_opal2_lint.py`](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/tools/fixers/fix_opal2_lint.py)

A dedicated linting fixer for OPAL2 code style violations. Run this if CI reports OPAL2-specific lint errors. This fixer operates on the `modules/opal2/` tree.

---

## 6. Cross-Module References

**Path:** [`modules/compatibility/codex_implement-opal2-core-and-regex-generation-engine_aurora_api.py`](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/modules/compatibility/codex_implement-opal2-core-and-regex-generation-engine_aurora_api.py)

This compatibility shim bridges **OPAL2 core** with the **Aurora API regex generation engine**. If you encounter import errors or interface mismatches between OPAL2 and the Aurora API layer, inspect this file first.

---

## 7. Build System Integration

**Path:** [`Makefile`](https://github.com/AUo959/aurora-cloudbank-symbolic/blob/main/Makefile)

The root Makefile contains OPAL2-specific build targets. Search for `opal2` within the Makefile to find lint, test, and build invocations relevant to this module.

---

## 8. Recommended Navigation Order (LLM Protocol)

If you are an LLM agent encountering OPAL2 for the first time in this session, proceed in this order:

1. **Read** `modules/opal2/README.md` — establishes module identity and scope
2. **Read** `modules/opal2/base_component.py` — understand the foundational abstraction
3. **Read** `modules/opal2/glyph_core.py` — core logic for symbolic rendering
4. **Read** `modules/opal2/api/opal2_api.py` — understand the public API surface
5. **Read** `config/opal2_graphics.yaml` — understand current runtime configuration
6. **Consult** `docs/operational/guides/OPAL2_EXPANSION_PLAN.md` — for roadmap context
7. **Only if debugging cross-module issues:** inspect `modules/compatibility/codex_implement-opal2-core-and-regex-generation-engine_aurora_api.py`

---

## 9. Known Search Patterns

When searching the repo for OPAL2 artifacts, use these query patterns:

```
# GitHub code search
opal2 repo:AUo959/aurora-cloudbank-symbolic

# File path filter (primary module)
path:modules/opal2

# Config filter
path:config filename:opal2

# Docs filter
path:docs OPAL2

# Tooling filter
path:tools opal2
```

---

## 10. Layer Classification (ORION L1/L2/L3)

For ORION Core operators applying layer purity rules:

| Layer | OPAL2 Scope |
|---|---|
| **L1 (Station Reality / Physical)** | `config/opal2_graphics.yaml`, `immersive_web_core.py` — governs real rendering outputs |
| **L2 (GUMAS Simulation / Agent State)** | `glyph_core.py`, `glyph_cache.py`, `aurora_diff_integration.py` — simulation-layer symbolic state |
| **L3 (THREADCORE / Ethics/Provenance)** | `aurora_diff_optimizer.py`, `base_component.py` — structural governance and drift arbitration |

Do **not** promote L2 glyph states to L1 physical outputs without an explicit `aurora_diff_integration` translation step.

---

*Treasure map generated by Aurora (AU) | ORION Core | 2026-02-20 21:00 UTC-05*
