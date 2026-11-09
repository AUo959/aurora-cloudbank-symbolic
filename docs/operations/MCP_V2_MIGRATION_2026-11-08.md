# Connector migration to Python SDK v2

Scope: `cloudbank-mcp-v2-migration`, from CloudBank main
`28db5950e404ca2ec9fc007a1b5c6c114c3641dd`. This upgrades the Python SDK major
version, while retaining the connector's five read-only tool interfaces.

## Implementation

The v1 decorators and private request-handler table are replaced with v2 typed
constructor callbacks and explicit result envelopes. SDK Python model fields
use snake_case (`input_schema`, `is_error`); the JSON wire aliases retain their
existing spelling. A snapshot captured with SDK 1.30.0 verifies all five tool
schemas through real current/legacy client sessions. Tool failures retain
sanitized error text and validation failures never dispatch to the backend.

JSON Schema validation is mandatory in supported installations, consistent
with the SDK's required dependency. An incomplete install fails at import
rather than offering an unchecked dispatch path. Tests exercise the actual
server, replacing earlier tests that merely repeated schema validation logic.

The SSE route now receives an ASGI callable instead of a function that
Starlette would wrap as a one-argument request handler. The transport owns the
stream lifecycle. `/sse` remains public and the message endpoint advertises its
canonical trailing slash. Stdio remains the CLI default, with protocol output
separate from logging. Authentication to the Aurora API, identifying headers,
Pilot-seal implementation and backend endpoint bindings are unchanged.

The standalone wheel previously contained only distribution metadata. Explicit
package selection and a source-prefix mapping now include the connector,
authentication, bridge and five tool modules. Installed console entry points
and protocol discovery are checked from outside the source checkout.

## Dependencies

Supported SDK range: `mcp>=2.3.0,<3.0.0`; test environments pin 2.3.0.
The SDK adds matching `mcp-types` and OpenTelemetry API dependencies. Resolving
the current universal graph also includes the existing HTTPX2 stack's
Emscripten-specific JS transport; unused `httpx-sse`, `distro` and `tqdm`
entries fall out of that graph. Every previously present package retaining a
pin keeps its version except MCP. The plain Linux lock is synchronized with
the generated hash profile, including previously missing HTTPX2 entries.
The core runtime hash file and unrelated application/framework pins are retained.

The Aurora bridge continues to use HTTPX 0.x, explicitly bounded below 1 in
the standalone package. The SDK uses its own HTTPX2 dependency. Standalone
metadata and optional/test requirements agree, and the regenerated CI lock
requires verified hashes and binary distributions.

## Verification evidence

- Unmodified connector under SDK 2.3: seven failures / three passes in the
  server dispatch/error subset, including the removed `Server.list_tools` API.
- Real in-memory SDK sessions cover current discovery and legacy initialization,
  all five frozen wire schemas, dispatch, sanitized failures and input bounds.
- Real stdio and SSE sessions use a controlled loopback API. They verify bearer
  and identifying headers, discovery, a successful backend request, and rejected
  calls that never reach that backend. No live Aurora service or model provider
  credentials are required.
- The CLI fails before protocol startup without backend credentials or its
  required validator. Protocol fixtures close their subprocesses, sockets and
  servers on exit.
- A separate SDK 1.30 client checks compatibility with the SDK 2.3 stdio server.
- The rebuilt wheel is installed into a separate environment and imported with
  isolated Python from outside the checkout; discovery and error results work.
- A fresh environment installs the full regenerated CI lock with required
  hashes and binary-only packages; dependency checks and lock coverage pass.

Full-suite and GitHub check outcomes are recorded on the associated PR and in
the root completion receipt. Legacy live-backend tests retain their configured
service requirement; the new protocol and validation checks run without it.
The connector skip hook is now scoped to its own directory.

## Upstream references

- [Official SDK migration guide](https://py.sdk.modelcontextprotocol.io/migration/)
- [Low-level server API](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/)
- [Testing guidance](https://py.sdk.modelcontextprotocol.io/get-started/testing/)
- [Legacy client support](https://py.sdk.modelcontextprotocol.io/run/legacy-clients/)

## Rollback

Revert this change's connector, requirements and test updates together to
restore the v1 contract and locked environment. Reinstall that lock into a
separate environment; do not leave v2 callbacks paired with v1 dependencies.
Any root pin rollback must follow the explicit registry/owner-attestation
workflow and re-verify that the simulation owner source is unchanged.
