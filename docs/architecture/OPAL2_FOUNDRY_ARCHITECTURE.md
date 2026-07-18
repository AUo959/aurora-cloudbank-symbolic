# OPAL2 Tool Foundry Architecture

**Status:** Phase 1 implementation baseline

**Runtime topology:** standalone service

**Reference implementation:** `modules/opal2/`

**Primary reference tool:** `opal2.glyph.render`

## Definition

OPAL2 is a portable tool foundry: a workshop and runtime for describing,
registering, validating, executing, and eventually packaging modular tools.
Aurora is the first platform integration profile, not a dependency of the
portable foundry contract.

The symbolic glyph and rendering stack is the first reference tool produced by
the foundry. It is not the complete definition of OPAL2.

## Phase 1 boundary

Phase 1 establishes a small executable spine:

- a neutral `ToolManifest` with input/output schemas and portability metadata;
- an asynchronous `Opal2Tool` interface;
- an explicit trusted-tool registry;
- a standard execution envelope with run ID, duration, and manifest digest;
- the existing glyph renderer adapted as `opal2.glyph.render`;
- standalone discovery and execution endpoints;
- compatibility routing from the existing `/render` endpoint through the
  foundry registry.

Phase 1 does **not** claim that packaging, remote installation, multi-tenant
isolation, or general third-party loading is complete.

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
reference tools (glyph renderer today; regex and others later)
        |
        +-- neutral consumer
        `-- Aurora adapter / policy profile
```

Aurora-specific anchors, DLP classifications, Picard_Delta_3s, and continuity
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

Remote or third-party packages must not be enabled until OPAL2 has:

1. a versioned package manifest;
2. digest and signature verification;
3. dependency and SBOM validation;
4. an isolated subprocess, container, or WASM execution boundary;
5. capability and resource-limit enforcement;
6. clean-room conformance tests.

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

Focused validation:

```bash
python -m compileall -q -x 'modules/opal2/staging' modules/opal2
python -m pytest tests/test_opal2_foundry.py tests/test_opal2_api_routes.py -q
```

## Planned convergence

### Phase 2: prove generality

- Add an SDK/scaffold for authoring tools.
- Restore a narrowly specified regex-generation tool as the first non-renderer
  reference implementation.
- Add full input/output conformance fixtures.
- Introduce an Aurora adapter rather than direct runtime imports.

### Phase 3: prove portability

- Define a signed `.opaltool` archive containing the manifest, schemas,
  implementation artifact, fixtures, digest, and SBOM.
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

The target public demonstration is:

1. scaffold a regex tool;
2. run its conformance fixtures;
3. export one signed package;
4. execute the same package in neutral OPAL2 and through the Aurora adapter;
5. visualize its run and provenance through `opal2.glyph.render`.

That flow proves that OPAL2 is a tool foundry rather than a renderer with a new
name.
