# OPAL2 Tool Foundry Architecture

**Status:** Phase 2.1 landing baseline

**Runtime topology:** standalone service

**Reference implementation:** `modules/opal2/`

**Reference tools:** `opal2.glyph.render`, `opal2.regex.workshop`

## Definition

OPAL2 is a portable tool foundry: a workshop and runtime for describing,
registering, validating, executing, and eventually packaging modular tools.
Aurora is the first platform integration profile, not a dependency of the
portable foundry contract.

The symbolic glyph stack and deterministic regex workshop are the first two
reference tools produced by the foundry. Together they prove that OPAL2's
contract is not specific to rendering.

## Current implementation boundary

Phase 1 establishes a small executable spine:

- a neutral `ToolManifest` with input/output schemas and portability metadata;
- an asynchronous `Opal2Tool` interface;
- an explicit trusted-tool registry;
- a standard execution envelope with run ID, duration, and manifest digest;
- the existing glyph renderer adapted as `opal2.glyph.render`;
- standalone discovery and execution endpoints;
- compatibility routing from the existing `/render` endpoint through the
  foundry registry.

Phase 2 proves generality and begins the portability boundary:

- `opal2.regex.workshop` generates bounded curated patterns and checks sample
  expectations without executing arbitrary user-provided regex;
- `.opaltool` specification 0.1 exports deterministic archives containing the
  tool manifest, schemas, implementation artifact, fixtures, and digests;
- package verification is inspect-only and never extracts, imports, or executes
  package code.

This baseline does **not** claim that signatures, package activation, remote
installation, multi-tenant isolation, or third-party loading are complete.

Phase 2.1 makes that baseline operable as a deliberately standalone service:

- a dedicated non-root container image and opt-in Compose profile;
- an explicit microservice dependency manifest and hash lock independent of
  the monolith;
- loopback-only host publication on port 8001;
- fail-closed module syntax and focused Foundry test gates in CI;
- a usable package-root API for the supported contracts and packaging tools.

## Runtime topology

OPAL2 remains a standalone FastAPI service. It is not mounted inside the main
Aurora API. This preserves its independent WebSocket lifecycle and security
middleware boundary.

```text
tool author or client
        |
        v
OPAL2 standalone API
        |
        +-- tool manifest + validation
        +-- explicit trusted registry
        +-- execution + provenance
        |
        v
reference tools (glyph renderer + regex workshop)
        |
        +-- neutral consumer
        `-- Aurora adapter / policy profile
```

Aurora-specific anchors, DLP classifications, Picard_Delta_3, and continuity
fields must enter through a policy profile or adapter. They must not be added
as required fields in `ToolManifest` or `ToolExecutionContext`.

## Tool contract

Every tool declares:

- stable ID, name, version, and description;
- capabilities;
- JSON-shaped input and output schemas;
- runtime type and determinism claim;
- declared side effects;
- supported policy profiles;
- intended export targets.

Every run returns:

- a unique run ID;
- tool ID and version;
- JSON-serializable output;
- measured execution duration;
- a SHA-256 digest of the exact manifest used;
- runtime and selected policy-profile provenance.

The Phase 1 validator implements the required top-level JSON-Schema subset:
required fields, primitive types, enums, and `additionalProperties`. Full
JSON-Schema conformance belongs to the packaging/conformance phase.

## Trust boundary

The foundry registry accepts explicit in-process tool instances only. It does
not scan arbitrary directories or import user-supplied code. The older OPAL2
plugin loader remains a visualization compatibility surface and is not the
portable foundry installation mechanism.

`.opaltool` 0.1 now provides the versioned package manifest and digest checks.
Remote or third-party packages must not be enabled until OPAL2 additionally
has:

1. asymmetric publisher-signature verification;
2. dependency and SBOM validation;
3. an isolated subprocess, container, or WASM execution boundary;
4. capability and resource-limit enforcement;
5. clean-room conformance tests and revocation provenance.

## Standalone API

Existing compatibility routes remain available:

- `POST /generate`
- `POST /render`
- `GET /plugins`
- `GET /cache/stats`
- `DELETE /cache/clear`
- `WebSocket /ws`

Foundry routes introduced in Phase 1:

- `GET /tools` — list portable manifests;
- `GET /tools/{tool_id}` — retrieve one manifest;
- `POST /tools/{tool_id}/run` — validate and execute a registered tool.

Mutating routes retain the standalone service's CSRF bearer-token contract.

## Start and validate

The service requires real secrets and refuses insecure defaults:

```bash
export CSRF_SECRET_KEY='<strong deployment secret>'
export WS_AUTH_SECRET='<strong deployment secret>'
uvicorn modules.opal2.api.opal2_api:app --host 127.0.0.1 --port 8001
```

The supported container path is an opt-in Compose profile and publishes only
to the local host by default:

```bash
export CSRF_SECRET_KEY="$(openssl rand -hex 32)"
export WS_AUTH_SECRET="$(openssl rand -hex 32)"
docker compose --profile opal2 up --build opal2
curl --fail http://127.0.0.1:8001/health
curl --fail http://127.0.0.1:8001/tools
```

This deployment does not activate `.opaltool` packages and does not join the
main Aurora API process.

Regenerate the Python 3.11 multi-platform hash lock after an intentional
dependency change:

```bash
make opal2-lock
```

Focused validation:

```bash
python -m compileall -q modules/opal2
python -m pytest \
  tests/test_opal2_foundry.py \
  tests/test_opal2_api_routes.py \
  tests/test_opal2_regex_workshop.py \
  tests/test_opal2_tool_package.py \
  tests/test_opal2_staging_dashboard.py \
  tests/test_opal2_deployment.py -q
```

## Planned convergence

### Phase 2: prove generality

- **Implemented:** narrowly specified regex generation and sample conformance as
  the first non-renderer tool.
- **Implemented:** deterministic inspect-only `.opaltool` 0.1 export with a
  packaged regex fixture.
- **Deferred:** authoring scaffold and full schema-conformance harness.
- **Deferred:** Aurora adapter rather than direct runtime imports.

### Phase 3: prove portability

- Promote `.opaltool` to a signed format with dependency lock, SBOM, publisher
  identity, and revocation provenance.
- Export and import the same tool in a clean neutral environment and a clean
  Aurora environment.
- Require matching fixture output and provenance digests.

### Phase 4: workshop and scale

- Add scaffold, build, test, run, export, and publish workflows.
- Move execution into isolated workers.
- Add an external artifact registry and queue-backed worker pools.
- Extract the neutral core to an independent package or repository only after
  the clean-room conformance suite is green.

## Public proof flow

The target public demonstration is now split into implemented and deferred
proofs:

1. **Implemented:** run the regex tool through the neutral registry and HTTP
   API;
2. **Implemented:** export and integrity-verify a deterministic inspect-only
   package carrying its fixture;
3. **Deferred:** scaffold the same tool from an authoring SDK;
4. **Deferred:** sign and execute the package in isolated neutral OPAL2 and
   through the Aurora adapter;
5. **Deferred:** visualize its run and provenance through
   `opal2.glyph.render`.

That flow proves that OPAL2 is a tool foundry rather than a renderer with a new
name.
