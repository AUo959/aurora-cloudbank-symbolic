# MCP connector SSE DNS-rebinding guard

Scope: `connector-sse-dns-rebinding-guard`, from CloudBank main
`fe99f3e5a300ecdc21c9fdf86563834d9e782568`. It acts on finding f1 of the
independent review `pr-20261108-mcp-v2-migration` (root repository), which
showed that the loopback SSE listener accepted any `Host` and `Origin`
(`curl -H 'Host: evil.example.com' -H 'Origin: http://evil.example.com' .../sse`
returned 200).

## Change

- `build_transport_security()` builds the SDK's `TransportSecuritySettings`
  (DNS-rebinding protection on). `build_sse_app()` passes it to
  `SseServerTransport`, whose `connect_sse` (the `/sse` stream) and
  `handle_post_message` (`/messages/`) both call the validator.
- Loopback default: Host `127.0.0.1|localhost|[::1]` on the exact listen port;
  Origin absent, or a loopback web origin on any port. Refused Host: 421.
  Refused Origin: 403.
- Remote binding stays explicit: wildcard binds add nothing, `--allowed-host` /
  `--allowed-origin` add exact entries, and `*`-style wildcards are rejected at
  startup. The allowlist flags are refused for stdio.
- `SseEndpoint` now absorbs the `ValueError` that the SDK's `connect_sse`
  raises after it has already sent the 421/403, so refused requests do not
  surface as ASGI tracebacks.
- Unchanged: stdio, the tool contracts, error envelopes, the backend bearer
  boundary, and every dependency pin.

## Limits

- Header validation only; it does not authenticate clients.
- Any web app served from a loopback origin is accepted (SDK localhost profile).
- Host matching is the SDK's exact, case-sensitive comparison plus `:*`.
- A client that omits `Host` (HTTP/1.0) is refused.

## Rollback

Revert this change; behaviour returns to the unguarded SSE listener.
