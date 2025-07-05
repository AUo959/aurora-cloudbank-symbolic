# Documentation Directory

Architecture diagrams, system maps, and user/developer guides for the Aurora Reflective Autonomy System.

## [2025-06-25] VSA-Based Symbolic Data & API Schema Update

- Symbolic data structures are now VSA-based (see `modules/symbolic_core/vsa.py`).
- All symbolic REST/WebSocket endpoints should use the `SymbolicVector` JSON schema for validation and documentation.
- See `docs/symbolicvector_api_schema.md` for schema details and usage examples.
- Extension points for quantum/geometric plugins are planned for future stages.

## [2025-06-30] Opal2 Graphics Card Module

- Introduces `modules/opal2` with the first Opal2 component.
- `GlyphGenerator` combines geometric algebra with quantum symbolic vectors.
- Designed to function as a lightweight graphics card for hybrid symbolic processing.
- Configuration lives in `config/opal2_graphics.yaml`.
- `GlyphCache` allows persistent storage of generated glyphs.

---

For architecture diagrams, see `architecture.md`.
