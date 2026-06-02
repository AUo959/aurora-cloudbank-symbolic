# Dependency Version Policy

**Status**: Active
**Scope**: `requirements.txt` (core runtime dependencies)
**Review cadence**: Quarterly
**Review owner**: Aurora CloudBank maintainers (release/dependency steward)

---

## Policy

Critical runtime packages in `requirements.txt` are pinned with **both** a
floor and an upper bound set at the **next major above the current latest
release**:

```
package>=<current_floor>,<<next_major_above_current>
```

The floor guarantees required features and security fixes; the upper bound
prevents a fresh install (or a transitive resolution) from silently pulling a
future **major** version whose breaking changes have not been validated against
Aurora. The Pydantic V1 → V2 migration is the cautionary example: a
platform-wide major bump should be an explicit, tested decision — never an
accident of `pip install`.

**Caps are calibrated to the current release reality, not a fixed number.**
For projects still on a `0.x` line (e.g. `fastapi`, `httpx`, `anthropic`) the
cap is `<1.0.0`; for projects already past `1.0` (e.g. `starlette` at `1.x`,
`openai` at `2.x`, `cryptography` at `48.x`) the cap is the *next* major above
where they are today, so the bound never downgrades the version that installs
now. This is why the numbers below differ from any earlier draft written when
these packages were on lower majors.

Upper bounds are a **resolver hint and a human-readable contract**. They are
complementary to, not a replacement for, a fully pinned lock file
(see issue #787) which provides build-to-build determinism.

## Critical packages and their caps

| Package        | Pin                          | Current major | Rationale                                              |
|----------------|------------------------------|---------------|--------------------------------------------------------|
| `fastapi`      | `>=0.128.8,<1.0.0`           | `0.x`         | Pre-1.0; any 1.0 is a deliberate upgrade.              |
| `starlette`    | `>=0.49.3,<2.0.0`            | `1.x`         | Already on 1.x; cap blocks an unvalidated 2.0.         |
| `pydantic`     | `>=2.5.0,<3.0.0`             | `2.x`         | V2→V3 would be a breaking migration of V1→V2 shape.    |
| `cryptography` | `>=44.0.0,<49.0.0`           | `48.x`        | Security-critical; cap blocks 49.0 until validated.    |
| `pyjwt`        | `>=2.10.0,<3.0.0`            | `2.x`         | Auth-critical token handling.                          |
| `httpx`        | `>=0.28.0,<1.0.0`            | `0.x`         | Pre-1.0 async HTTP client; API still evolving.         |
| `anthropic`    | `>=0.40.0,<1.0.0`            | `0.x`         | Claude SDK; pre-1.0, surface changes between minors.   |
| `openai`       | `>=1.50.0,<3.0.0`            | `2.x`         | Already on 2.x; cap blocks an unvalidated 3.0.         |

> Caps last calibrated against PyPI latest releases as of the policy date.
> A cap that sits below the installed major would force a downgrade — when
> bumping a floor across a major, raise the matching cap in the same PR.

## When to change a cap

- **Security release above the cap** (e.g. `cryptography` 46.x with a CVE fix):
  raise the upper bound in a dedicated PR, run the dependency-validation
  workflow, and note the reason in the commit.
- **Intentional major upgrade** (e.g. Pydantic V3): treat as a project, not a
  bump — migrate code, update tests, then move the cap.
- **Quarterly review**: confirm each cap is still one major above the floor and
  that no upstream security advisory requires crossing it.

## Out of scope

- Non-critical / leaf utilities are floor-pinned only; over-capping them adds
  resolver friction without protecting an API surface Aurora depends on.
- Optional/heavy dependencies (`requirements-optional.txt`) follow their own
  graceful-degradation contract and are not covered here.
