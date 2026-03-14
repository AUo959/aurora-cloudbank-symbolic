# Security Best Practices Report

Date: 2026-03-08

Scope: Repo-wide scan of `/Users/travisstreets/Library/Mobile Documents/com~apple~CloudDocs/Aurora_ORIONCORE_Directory_Main`, with the actionable security surface concentrated in `Aurora_Sim_Architecture/aurora-cloudbank-symbolic-main`.

## Executive Summary

This workspace contains substantial security-themed documentation and helper code, but the enforceable security posture is mixed. There are real controls in place, including CodeQL, Dependabot, `.env` ignore rules, non-root container execution, a bearer-token gate on one WebSocket hub, and a file upload size limit. However, the live application surfaces still expose multiple high-risk paths: unauthenticated Socket.IO handlers can execute shell commands and read arbitrary files, one bridge API effectively bypasses its own activation-phrase gate, and several services use wildcard CORS with credentials.

The most important conclusion is that the repository currently has more security artifacts than reliable runtime enforcement. Some controls are implemented only as standalone files, some are not wired into active entrypoints, and one security workflow file is stored outside `.github/workflows/`, so it will not execute as a GitHub Actions workflow.

## Observed Security Infrastructure

- Policy and documentation:
  - [`SECURITY.md`](./SECURITY.md) defines a reporting path and expected practices ([`SECURITY.md:1`](./SECURITY.md)).
  - `.security/*.json` contains policy/config declarations for MFA, DNS, incident response, network, storage, and CSPM. These are also referenced by local validation tooling ([`aurora_security_validation.py:22`](./aurora_security_validation.py), [`aurora_enhanced_security.py:23`](./aurora_enhanced_security.py)).
- CI and dependency hygiene:
  - CodeQL is configured with least-privilege workflow permissions ([`.github/workflows/codeql-enhanced.yml:13`](./.github/workflows/codeql-enhanced.yml)).
  - Dependabot is configured for weekly `pip` and `npm` updates ([`.github/dependabot.yml:1`](./.github/dependabot.yml)).
  - `package.json` includes an `npm audit` script ([`package.json:18`](./package.json)).
- Local developer hygiene:
  - Pre-commit validates YAML/JSON, merge conflicts, and Python linting ([`.pre-commit-config.yaml:4`](./.pre-commit-config.yaml)).
  - `.gitignore` excludes `.env`, `.env.*`, `.venv/`, and `node_modules/` ([`.gitignore:54`](./.gitignore), [`.gitignore:72`](./.gitignore), [`.gitignore:103`](./.gitignore)).
- Runtime hardening already present:
  - The container drops to a non-root `aurora` user ([`Dockerfile:19`](./Dockerfile)).
  - The AIF hub requires a bearer token header, although the default is unsafe ([`services/aif_hub.py:42`](./services/aif_hub.py)).
  - The GUI FastAPI app enforces a 10 MiB upload limit and stores uploads under UUID filenames ([`aurora_gui_cloudhub_fastapi.py:132`](./aurora_gui_cloudhub_fastapi.py), [`aurora_gui_cloudhub_fastapi.py:141`](./aurora_gui_cloudhub_fastapi.py)).

## Critical Findings

### SBP-001: Unauthenticated Socket.IO command execution is vulnerable to shell injection

- Severity: Critical
- Location:
  - [`aurora_collaboration_chamber_launcher.js:291`](./aurora_collaboration_chamber_launcher.js)
  - [`aurora_collaboration_chamber_launcher.js:549`](./aurora_collaboration_chamber_launcher.js)
- Evidence:
  - The launcher executes raw commands with `exec(command, ...)` ([`aurora_collaboration_chamber_launcher.js:291`](./aurora_collaboration_chamber_launcher.js)).
  - The `execute_system_command` socket handler accepts a client-supplied `command` and only checks `command.startsWith(allowed)` before passing it to `exec` ([`aurora_collaboration_chamber_launcher.js:553`](./aurora_collaboration_chamber_launcher.js), [`aurora_collaboration_chamber_launcher.js:564`](./aurora_collaboration_chamber_launcher.js), [`aurora_collaboration_chamber_launcher.js:574`](./aurora_collaboration_chamber_launcher.js)).
  - The Socket.IO server is created with permissive cross-origin access and no visible authentication gate ([`aurora_collaboration_chamber_launcher.js:17`](./aurora_collaboration_chamber_launcher.js), [`aurora_collaboration_chamber_launcher.js:378`](./aurora_collaboration_chamber_launcher.js)).
- Impact: A remote client can append shell metacharacters to an allowed prefix such as `git status; ...` and execute arbitrary commands on the host process.
- Fix:
  - Remove `exec` for user-influenced input.
  - Replace prefix matching with an exact server-side command map.
  - Require authentication and authorization before any command-capable socket event is accepted.
- Mitigation:
  - Disable the `execute_system_command` event until a fixed command dispatcher exists.
  - If the launcher must remain available, bind it to localhost or a trusted reverse proxy.
- False positive notes:
  - This finding does not depend on arbitrary command generation elsewhere; the `startsWith` check plus `exec()` is sufficient on its own.

### SBP-002: Unauthenticated Socket.IO file transfer endpoint can read arbitrary server files

- Severity: Critical
- Location:
  - [`aurora_collaboration_chamber_launcher.js:316`](./aurora_collaboration_chamber_launcher.js)
  - [`aurora_collaboration_chamber_launcher.js:602`](./aurora_collaboration_chamber_launcher.js)
- Evidence:
  - `readFileForContext(filePath)` reads any provided path with `fs.readFile(filePath, 'utf8')` ([`aurora_collaboration_chamber_launcher.js:318`](./aurora_collaboration_chamber_launcher.js)).
  - `prepare_context_transfer` accepts a client-provided `files` array and feeds each path into that reader without normalization or allowlisting ([`aurora_collaboration_chamber_launcher.js:604`](./aurora_collaboration_chamber_launcher.js), [`aurora_collaboration_chamber_launcher.js:617`](./aurora_collaboration_chamber_launcher.js)).
- Impact: Any connected client can exfiltrate application source, local configs, secrets, or other readable files from the server filesystem.
- Fix:
  - Restrict file access to an explicit allowlist of workspace-relative paths.
  - Reject absolute paths and any path containing `..`.
  - Require authentication and authorization before file export operations.
- Mitigation:
  - Disable `prepare_context_transfer` or return only metadata until path validation exists.
- False positive notes:
  - The risk holds even if the client is intended to be trusted; there is no server-side boundary enforcing that trust.

## High Findings

### SBP-003: Mesh bridge activation phrase can be bypassed and is also disclosed by another endpoint

- Severity: High
- Location:
  - [`src/servers/l2_integration_server.py:231`](./src/servers/l2_integration_server.py)
  - [`src/servers/l2_integration_server.py:328`](./src/servers/l2_integration_server.py)
- Evidence:
  - The bridge connect handler only rejects the activation phrase when one is supplied and wrong: `if phrase and phrase != expected_phrase:` ([`src/servers/l2_integration_server.py:233`](./src/servers/l2_integration_server.py)).
  - The `/api/orion-core` route returns activation phrases for every agent ([`src/servers/l2_integration_server.py:332`](./src/servers/l2_integration_server.py)).
- Impact: A caller can omit the phrase entirely and still connect; if phrase enforcement is later tightened, another public endpoint already reveals every valid phrase.
- Fix:
  - Make the activation phrase mandatory or replace it with proper authenticated identities.
  - Remove activation phrases from API responses.
  - Store secrets in environment variables or a secret manager, not computed public values.
- Mitigation:
  - Keep this runtime internal-only until real authn/authz exists.
- False positive notes:
  - This assumes these routes are reachable by untrusted callers. No access-control evidence is visible in app code.

### SBP-004: The AIF WebSocket hub falls back to a predictable default token on a network-exposed listener

- Severity: High
- Location:
  - [`services/aif_hub.py:12`](./services/aif_hub.py)
  - [`services/aif_hub.py:66`](./services/aif_hub.py)
- Evidence:
  - `AIF_TOKEN = os.environ.get("AIF_TOKEN", "change-me")` uses a fixed default token ([`services/aif_hub.py:12`](./services/aif_hub.py)).
  - The service listens on `0.0.0.0:8090` when run directly ([`services/aif_hub.py:68`](./services/aif_hub.py)).
- Impact: If the environment variable is missing in any deployment or operator session, the service becomes reachable with a guessable bearer token.
- Fix:
  - Refuse to start when `AIF_TOKEN` is unset or equal to the placeholder.
  - Bind to localhost by default unless an explicit external host is configured.
- Mitigation:
  - Enforce network-level access controls around port `8090`.
- False positive notes:
  - If `AIF_TOKEN` is always injected by deployment tooling, risk is reduced but the code still encodes an unsafe fallback.

## Medium Findings

### SBP-005: Multiple live services use wildcard CORS, including configurations that allow credentials

- Severity: Medium
- Location:
  - [`aurora_api_server.py:43`](./aurora_api_server.py)
  - [`aurora_gui_cloudhub_fastapi.py:44`](./aurora_gui_cloudhub_fastapi.py)
  - [`src/servers/l2_integration_server.py:77`](./src/servers/l2_integration_server.py)
  - [`aurora_collaboration_chamber_launcher.js:17`](./aurora_collaboration_chamber_launcher.js)
  - [`src/orchestrators/holographic_interface_orchestrator.js:23`](./src/orchestrators/holographic_interface_orchestrator.js)
  - [`src/orchestrators/holographic_interface_orchestrator.js:53`](./src/orchestrators/holographic_interface_orchestrator.js)
- Evidence:
  - FastAPI apps use `allow_origins=["*"]` together with `allow_credentials=True` ([`aurora_api_server.py:45`](./aurora_api_server.py), [`aurora_gui_cloudhub_fastapi.py:46`](./aurora_gui_cloudhub_fastapi.py), [`src/servers/l2_integration_server.py:79`](./src/servers/l2_integration_server.py)).
  - Socket/Express surfaces also expose `origin: '*'` or `Access-Control-Allow-Origin: '*'` ([`aurora_collaboration_chamber_launcher.js:19`](./aurora_collaboration_chamber_launcher.js), [`src/orchestrators/holographic_interface_orchestrator.js:25`](./src/orchestrators/holographic_interface_orchestrator.js), [`src/orchestrators/holographic_interface_orchestrator.js:54`](./src/orchestrators/holographic_interface_orchestrator.js)).
- Impact: Browser-origin restrictions are effectively disabled, which widens the attack surface for any endpoint that later gains cookies, tokens, or sensitive state.
- Fix:
  - Replace `*` with explicit origin allowlists.
  - Do not enable credentials on wildcard origins.
  - Apply auth before exposing cross-origin mutating endpoints.
- Mitigation:
  - Constrain these services to internal development networks until origin policy is narrowed.
- False positive notes:
  - If these are strictly local-only dev services, the operational risk is lower, but the defaults are not production-safe.

### SBP-006: Parts of the security automation layer are inert or misleading

- Severity: Medium
- Location:
  - [`.github/security-config.yml:1`](./.github/security-config.yml)
  - [`security_verification.py:66`](./security_verification.py)
  - [`security_verification.py:82`](./security_verification.py)
  - [`middleware/aurora-security-middleware.js:6`](./middleware/aurora-security-middleware.js)
  - [`package.json:33`](./package.json)
- Evidence:
  - The Bandit/Safety/Semgrep workflow file lives in `.github/security-config.yml`, not `.github/workflows/`, so it is not an active GitHub Actions workflow ([`.github/security-config.yml:1`](./.github/security-config.yml)).
  - `security_verification.py` checks for `.security/secure_helpers.py` but later prints blanket success claims such as `OWASP Top 10: Compliant` and `Dependency Scanning: Automated` regardless of the actual runtime state ([`security_verification.py:66`](./security_verification.py), [`security_verification.py:94`](./security_verification.py), [`security_verification.py:98`](./security_verification.py)).
  - The Express security middleware requires `helmet` and `express-rate-limit`, but those packages are not declared in `package.json` ([`middleware/aurora-security-middleware.js:6`](./middleware/aurora-security-middleware.js), [`package.json:40`](./package.json)).
- Impact: The repository can appear security-hardened while some advertised controls never execute, which increases the chance of missed regressions and unsafe deployment assumptions.
- Fix:
  - Move the security scanning workflow into `.github/workflows/`.
  - Make verification reports reflect actual checks and fail when expected controls are absent.
  - Either wire the Express security modules into active entrypoints and declare their dependencies, or remove them as dead code.
- Mitigation:
  - Treat the current security scripts as advisory only until the pipeline is validated end-to-end.
- False positive notes:
  - This finding is about operational reliability of controls, not direct code execution.

## Lower-Priority Observations

- `package.json` does not declare `helmet`, `express-rate-limit`, `express-validator`, `bcryptjs`, or `jsonwebtoken`, even though local security helper modules depend on them ([`package.json:33`](./package.json), [`config/aurora-security-config.js:6`](./config/aurora-security-config.js)).
- The repo includes many `.security/*.json` files and validation scripts, but most of those controls are declarative and not tied to visible infrastructure provisioning in this codebase ([`aurora_enhanced_security.py:39`](./aurora_enhanced_security.py), [`aurora_security_validation.py:42`](./aurora_security_validation.py)).

## Recommended Next Actions

1. Disable or harden `aurora_collaboration_chamber_launcher.js` first. It currently presents the highest host-compromise risk.
2. Fix `src/servers/l2_integration_server.py` so authentication is mandatory and activation phrases are never disclosed.
3. Remove the `change-me` fallback in `services/aif_hub.py`.
4. Narrow CORS policies across all FastAPI and Express entrypoints.
5. Move the security scanning workflow into `.github/workflows/` and make local verification scripts fail closed instead of reporting blanket success.

