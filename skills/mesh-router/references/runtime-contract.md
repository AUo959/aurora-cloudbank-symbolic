# Runtime Contract

Canonical runtime endpoints:

- `GET /api/mesh/status`
- `GET /api/mesh/agents` — lists all registered mesh agents; implemented in `create_app()` (#764)
- `GET /api/mesh/agents/{id}` — returns agent detail; 404 on unknown agent (#764)
- `POST /api/mesh/agents/{id}/activate` — activates agent; requires `activationPhrase` in body (#764)
- `POST /api/mesh/messages`
- `GET /api/mesh/channels/{id}/history`
- `GET /api/mesh/events?after=<cursor>`
- `GET /ws/mesh` via native WebSocket

All three `/api/mesh/agents` routes are implemented in `src/servers/l2_integration_server.py#create_app()`
and covered by `tests/test_mesh_router_v1.py` as of PR #1011.

Canonical event envelope:

```json
{
  "event_id": 12,
  "event_type": "agent_reply",
  "message_id": "abc123",
  "channel_id": "private:captain:alex",
  "agent_id": "alex_thorne",
  "timestamp": "2026-03-06T12:00:00+00:00",
  "payload": {
    "content": "Reply text"
  }
}
```

Expected event flow for direct user messages:

1. `message_accepted`
2. `trace_update`
3. `agent_ack`
4. `agent_typing`
5. `trace_update`
6. `agent_reply` or `delivery_error`
