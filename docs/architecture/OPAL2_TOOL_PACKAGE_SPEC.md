# OPAL2 Tool Package Specification

**Format:** `.opaltool`

**Specification version:** `0.1`

**Activation status:** inspect-only

## Purpose

An `.opaltool` file is the portable transport artifact produced by the OPAL2
foundry. Version 0.1 proves deterministic export, schema carriage, bounded
inspection, and content-integrity verification. It does not grant execution
trust and it is not a remote plugin installer.

## Archive layout

The artifact is a reproducible ZIP archive with sorted members, fixed metadata,
and canonical JSON:

```text
opaltool.json
schemas/input.schema.json
schemas/output.schema.json
src/<implementation files>
fixtures/<optional conformance fixtures>
```

`opaltool.json` declares:

- format and specification version;
- the complete portable `ToolManifest`;
- the descriptive `module:object` entrypoint;
- the required OPAL2 core API;
- activation state;
- SHA-256 and byte length for every payload member.

The archive SHA-256 returned by the verifier is a transport receipt. File
digests detect corruption or mutation, but they do not prove publisher
identity: an attacker capable of replacing a package can replace unsigned
digests too.

## Safety boundary

The version 0.1 verifier:

- never extracts package members;
- never imports or executes implementation code;
- rejects absolute paths, traversal, backslashes, duplicate members, and
  symlinks;
- enforces file-count and uncompressed-size limits;
- rejects undeclared members and missing payloads;
- verifies every declared SHA-256 and schema copy;
- requires `activation: inspect-only`.

Package activation remains deferred until OPAL2 has publisher signatures,
dependency and SBOM policy, isolated workers, capability limits, and clean-room
conformance. The legacy dynamic plugin loader is not an activation mechanism
for `.opaltool` files.

## Reference export

The first package-enabled tool is `opal2.regex.workshop`:

```python
from modules.opal2.tool_package import export_builtin_tool

receipt = export_builtin_tool(
    "opal2.regex.workshop",
    "/tmp/opal2-regex-workshop.opaltool",
)
print(receipt.to_dict())
```

The same artifact can be verified without loading its source:

```python
from modules.opal2.tool_package import verify_opaltool_package

receipt = verify_opaltool_package("/tmp/opal2-regex-workshop.opaltool")
assert receipt.package_manifest["activation"] == "inspect-only"
```

## Deferred version 1.0 requirements

Before the format can be called installable or generally trustworthy, version
1.0 must add:

1. publisher identity and an asymmetric signature envelope;
2. dependency lock and SBOM members;
3. fixture digests and a conformance result contract;
4. a neutral OPAL2 core distribution;
5. isolated activation with CPU, memory, time, network, and filesystem limits;
6. revocation and registry provenance.
