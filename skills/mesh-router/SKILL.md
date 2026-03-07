---
name: mesh-router
description: Route local Aurora mesh messages through the FastAPI mesh runtime when users ask to send @mesh messages, address @agent.<name>, work in channels like #crew_lounge or private:captain:alex, or inspect status, history, activation, and live event tails.
---

# Mesh Router

Use the local mesh runtime instead of prompt-only simulation.

## Quick start

- `status`: run `python3 scripts/mesh_router.py status`
- `send`: run `python3 scripts/mesh_router.py send --to alex_thorne --channel private:captain:alex --message "..."`.
- `broadcast`: run `python3 scripts/mesh_router.py broadcast --channel "#crew_lounge" --message "..."`
- `history`: run `python3 scripts/mesh_router.py history private:captain:alex`
- `activate`: run `python3 scripts/mesh_router.py activate alex_thorne`
- `tail`: run `python3 scripts/mesh_router.py tail --follow`

## Rules

- Prefer the CLI/runtime contract over freeform roleplay.
- Resolve names to actual agent ids before sending.
- Use `private:captain:alex` for Alex Thorne's direct line unless the user explicitly names another channel.
- Use `#crew_lounge` for group broadcast.
- If the runtime is unavailable, report that directly and suggest starting `python3 src/servers/l2_integration_server.py`.

## References

- For command grammar examples, read `references/command-grammar.md`.
- For REST and WebSocket contracts, read `references/runtime-contract.md`.
