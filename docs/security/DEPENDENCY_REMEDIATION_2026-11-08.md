# Dependency security remediation

Verified November 8 UTC (November 7 in New York). Scope: the dependency findings
identified during queue recovery; no independent repository-wide audit claim.

## Classification and patch boundary

The old locks contained affected package versions. Application exploitability
varies by advisory: the inspected JWT verification path fixes HS256 and does
not share an unverified-decode options dictionary; the connector uses SDK v1
stdio/SSE server APIs rather than the affected client/Streamable HTTP paths.
Dependency upgrades remove affected versions without changing those contracts.

| Package | Before | Replacement |
| --- | --- | --- |
| certifi | 2026.7.22 | 2026.10.23 |
| MCP SDK | 1.29.1 | 1.30.0 |
| PyJWT | 2.13.0 | 2.15.1 |
| urllib3 | 2.7.0 | 2.8.0 |
| DOMPurify npm override | 3.4.12 | 3.4.17 |

The connector's standalone package and SSE extra also require MCP 1.30.0;
its v1 ceiling remains. Requirements sources, the plain lock, and both hashed
locks agree. Package-manager-generated replacement blocks preserve unrelated
Python package versions and markers. Hash-verified installation uses the CI
lock. Certifi's replacement includes the corrected trust-store changes after
the overly broad October 18 removal.

The previous audit did not list a patched PyJWT release for PYSEC-2026-4146.
Current PyPI metadata and the fresh audit identify 2.15.1 as clear. The regression
test proves an unverified decode cannot poison a later verified decode through
a shared options dictionary; expired tokens are rejected and valid tokens work.

## Actual editor sanitizer boundary

Updating the npm override alone would miss two copies: Monaco vendors an older
DOMPurify, and the React wrapper defaults to a CDN-hosted editor. The editor now
loads the locked local ESM module and local workers. A Vite alias redirects
Monaco's relative sanitizer import to the direct, exact DOMPurify dependency.
The production module-graph test requires the patched module and rejects the
vendored implementation. Monaco is excluded from development prebundling because the optimizer can
otherwise retain its vendored copy. A forced-optimizer regression plus direct
ESM transform check verifies that the patched binding is used in development.

The reported critical advisory requires non-default shadow-root/template
handling, which was not observed in the application's Monaco configuration.
The dependency regression nevertheless reproduces that upstream boundary:
DOM-node input with a shadow root, a split template expression, and
IN_PLACE + SAFE_FOR_TEMPLATES. It fails against 3.4.12 and passes against 3.4.17
for template-literal, Mustache, and ERB forms. Ordinary formatted HTML and
shadow-root text remain usable. No payload is evaluated by the test.

Compatible security updates refresh frontend lock entries. Vitest stays on
major 4. A version-qualified minimatch override replaces affected majors 7–10
with 11.0.1 without touching unaffected older copies; its named exports used by
current tooling remain compatible, with lint/build/test controls passing.
No forced downgrade of ESLint or major upgrade of the application framework
was used.

## Verification evidence

- Before: runtime audit matched four packages / 23 unique advisory IDs; frontend
  audit reported 39 affected packages, including one critical and 21 high.
- After: plain runtime and full frontend lock audits report zero findings.
  Advisory services are point-in-time package/version evidence, not proof of
  absence of all vulnerabilities or application exploitability.
- `uv pip sync --require-hashes --only-binary=:all: requirements-ci-hashed.txt`
  installs into an isolated Python environment; no application keys are used.
- Focused JWT/auth/connector/lock tests: 99 passed / 79 skipped. Live-backend
  connector tests retain their existing environment guards. An actual SDK
  stdio initialization/list-tools smoke independently verifies all five tool
  schemas with a temporary in-memory connector token and no remote backend.
- Frontend type-check, strict lint, production build, and six security checks
  pass. Chromium verifies local editor loading, typing, and worker requests
  with no Monaco CDN requests or page errors. Development browser checks also
verify that the sanitizer request targets the patched package, not the vendor
copy. The source-anchor scanner excludes gitignored dist directories so a
post-build backend test run does not scan large generated/minified bundles;
a regression preserves scanning of authored source. An unrelated external font
  stylesheet is stubbed for the deterministic browser check.
- Full test/CI landing evidence: PENDING_FINAL_CHECKS.

The independent pre-patch investigator confirmed the separate vendored/CDN
boundary. The candidate reviewer could not run because of its usage limit;
the parent performed the separate bypass/regression pass, found and fixed the
standalone MCP manifest copy, and checked both accepted and rejected JWT paths
plus ordinary editor controls. No relevant missing check is represented as a
pass. Shared skill artifact-storage reference resources were unavailable;
intermediate material stayed under work/, and this repository-owned receipt
contains bounded, nonsensitive validation evidence.

## Reproduction

```sh
python scripts/check_hashed_lock_drift.py
python -m pytest tests/test_dependency_security_regressions.py tests/test_oauth2_auth.py -q
python -m pip_audit -r requirements-lock.txt --no-deps --disable-pip --format json
cd frontend
npm ci --ignore-scripts
npm run type-check
npm run lint
npm run test:security
npm audit --package-lock-only --json
```

Sources: [DOMPurify critical advisory](https://github.com/advisories/GHSA-cg2g-xh64-v4q7),
current PyPI version/advisory metadata, npm advisory output, and repository
callers. No production deployment, external provider call, canon mutation, or
live simulation advancement was performed.
