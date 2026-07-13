# Recovered Protocol Wiring Verification

**Required by:** `docs/security/pentest_scope_v2.md` Section 2.2  
**Operator decision:** Issue #1126, 2026-06-22  
**Classification:** Internal / Pre-engagement gate  
**Status:** ⏳ PENDING — must be completed before pentest engagement begins

---

## Purpose

This document records the result of the mandatory pre-engagement code verification confirming that no recovered protocol (Sherlock, Watson, Moriarty, Tribunal, SHADOWFAX) is wired into any runtime enforcement surface. This is a hard gate. The pentest engagement defined in `pentest_scope_v2.md` must not begin until this document is complete and signed.

---

## Verification procedure

Run the following from the repo root against the exact commit that will be used as the engagement baseline:

```bash
# Step 1 — record the baseline commit
git rev-parse HEAD

# Step 2 — search ethics enforcement surfaces
grep -rni "sherlock\|watson\|moriarty\|tribunal\|shadowfax" \
  src/monitoring/ \
  src/subroutines/ \
  modules/ethics_field/ \
  modules/cask/ \
  api/ \
  --include="*.py"

# Step 3 — broader sweep (catch imports, config references, string literals)
grep -rni "sherlock\|watson\|moriarty\|tribunal\|shadowfax" \
  src/ modules/ api/ config/ \
  --include="*.py" --include="*.json" --include="*.yaml" --include="*.toml"

# Step 4 — exclude known-safe documentation references
# (the above will match docs/ — only src/, modules/, api/, config/ matter for wiring)
```

**Expected clean result:** Zero matches in `src/`, `modules/`, `api/`, `config/`.  
Matches in `docs/` are expected and safe — do not count those.  
Any match outside `docs/` is a finding — severity HIGH per `pentest_scope_v2.md` Section 3.5.

---

## Result

**Verification date:** _________________  
**Verified by:** _________________  
**Baseline commit SHA:** _________________  

### Step 2 output (ethics surfaces — src/monitoring/, src/subroutines/, modules/)

```
[ paste grep output here — or write "No matches" ]
```

### Step 3 output (full sweep — src/, modules/, api/, config/)

```
[ paste grep output here — or write "No matches" ]
```

### Verdict

- [ ] ✅ CLEAN — zero matches outside `docs/`. Pentest Section 2.2 pre-condition met.
- [ ] ❌ FINDING — one or more matches outside `docs/`. Do not begin engagement. Open GitHub issue tagged `security` `pentest-blocker` and resolve before re-verification.

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| Verifier | — | |
| Engineering Lead | — | |

---

*Once signed CLEAN, this document becomes part of the engagement package delivered to the external tester alongside `pentest_scope_v2.md`.*
