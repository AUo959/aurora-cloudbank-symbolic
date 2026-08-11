# OPAL2 Tool Foundry Architecture

**Status:** Phase 2.2 product-extraction baseline

**Runtime topology:** standalone service

**Reference implementation:** `modules/opal2/`

**Reference tools/products:** `opal2.glyph.render`, `opal2.regex.workshop`, SHERLOCK / WATSON protocol core

## Definition

OPAL2 is a portable tool foundry: a workshop and runtime for describing,
registering, validating, executing, and eventually packaging modular tools.
Aurora is the first platform integration profile, not a dependency of the
portable foundry contract.

The symbolic glyph stack and deterministic regex workshop proved that OPAL2's
contract is not specific to rendering. Phase 2.2 adds a second foundry role:
extracting independently useful capabilities discovered inside larger systems
into neutral product contracts.

See `OPAL2__DISCOVERY_TO_PRODUCT_LOOP__v1.0__2026-08-07.md` for the extraction
principle and `OPAL2__PRODUCT_SPEC__SHERLOCK_WATSON__v1.0__2026-08-07.md` for
the first reference product.

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

Phase 2.2 establishes the discovery-to-product loop and its first reference
extraction:

- SHERLOCK is defined as portable Evidence Intelligence rather than an Aurora
  character or simulation concept;
- WATSON is defined as portable Contextual Intelligence;
- `opal2.sherlock.casefile` seals provider-produced investigations into
  canonical SHA-256-addressed evidence records;
- `opal2.watson.brief` binds provider-produced synthesis to the exact SHERLOCK
  digest it analyzed;
- `opal2.sherlock-watson.verify` fails closed if either side of that handoff is
  mutated;
- the protocol core remains provider-neutral and has no Aurora runtime, web,
  connector, or model dependency;
- autonomous retrieval/synthesis providers and default standalone API
  registration remain explicit follow-up work rather than hidden assumptions.

## Runtime topology

OPAL2 remains a standalone FastAPI service. It is not mounted inside the main
Aurora API. This preserves its independent WebSocket lifecycle and security
middleware boundary.

```text
tool author, product adapter, or client
        |
        v
OPAL2 standalone runtime
        |
        +-- tool manifest + validation
        +-- explicit trusted registry
        +-- execution + provenance
        +-- product extraction contracts
        |
        v
portable tools/products
        |
        +-- neutral consumer
        `-- Aurora adapter / policy profile
```

Aurora-specific anchors, DLP classifications, Picard_Delta_3, and continuity
fields must enter through a policy profile or adapter. They must not be added
as required fields in `ToolManifest`, `ToolExecutionContext`, or portable
product artifacts.

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
JSON-Schema conformance belongs in the packaging/conformance phase. Tools may
perform stricter nested validation when their integrity properties require it,
as the SHERLOCK / WATSON core does.

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

SHERLOCK / WATSON adds another trust rule: a synthesis provider may not mutate
the evidence artifact it receives. The digest chain exists specifically so
that this boundary is testable rather than a prompt convention.

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

The SHERLOCK / WATSON classes are importable through `modules.opal2.tools` in
Phase 2.2. Registering them in the default standalone API registry is tracked as
a product-landing follow-up so this baseline does not overstate endpoint
availability.

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
  tests/test_opal2_sherlock_watson.py \
  tests/test_opal2_staging_dashboard.py \
  tests/test_opal2_deployment.py -q
```

## Planned convergence

### Phase 2: prove generality

- **Implemented:** narrowly specified regex generation and sample conformance as
  the first non-renderer tool.
- **Implemented:** deterministic inspect-only `.opaltool` 0.1 export with a
  packaged regex fixture.
- **Implemented:** provider-neutral SHERLOCK / WATSON integrity core as the
  first capability extracted from a larger Aurora workflow into a standalone
  product contract.
- **Deferred:** authoring scaffold and full schema-conformance harness.
- **Deferred:** Aurora adapter rather than direct runtime imports.

### Phase 3: prove portability

- Promote `.opaltool` to a signed format with dependency lock, SBOM, publisher
  identity, and revocation provenance.
- Export and import the same tool in a clean neutral environment and a clean
  Aurora environment.
- Require matching fixture output and provenance digests.
- Add neutral investigation/synthesis provider interfaces and a clean-room
  SHERLOCK -> WATSON execution proof.

### Phase 4: workshop and scale

- Add scaffold, build, test, run, export, and publish workflows.
- Move execution into isolated workers.
- Add an external artifact registry and queue-backed worker pools.
- Extract the neutral core to an independent package or repository only after
  the clean-room conformance suite is green.

## Public proof flow

The public proof is now two complementary demonstrations:

1. run the regex tool through the neutral registry and HTTP API;
2. export and integrity-verify a deterministic inspect-only regex package;
3. run SHERLOCK -> WATSON over a neutral evidence case and demonstrate that an
   evidence mutation invalidates the bound analysis;
4. rerun WATSON against the unchanged SHERLOCK digest to demonstrate competing
   interpretation without evidence rewriting;
5. execute the same product core in a clean environment outside Aurora;
6. later sign and execute `.opaltool` packages through isolated neutral OPAL2
   and an Aurora adapter.

That flow proves both halves of OPAL2's identity: it can host tools designed
from scratch, and it can extract useful capabilities discovered inside a larger
system into independently usable products.
