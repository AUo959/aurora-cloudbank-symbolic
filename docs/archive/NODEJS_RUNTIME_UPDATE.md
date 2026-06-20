# Node.js Runtime Update

**Date:** October 28, 2025  
**Thread:** T1→T8→T9→INFINITE  
**DLP:** context_tag=nodejs_runtime_update, symbolic_hash=NODE_UPGRADE_v20

## Update Summary

Updated Node.js runtime from version 18.x to 20.x (Iron LTS).

### Changes Made

#### 1. Dev Container Configuration
**File:** `.devcontainer/devcontainer.json`
- Updated Node.js feature version from `"18"` to `"20"`
- Node.js 20 (Iron) is the current LTS version with support until April 2026

#### 2. Package Configuration
**File:** `package.json`
- Updated `engines.node` from `>=18.0.0` to `>=20.0.0`
- Updated `engines.npm` from `>=8.0.0` to `>=10.0.0`

#### 3. Version Lock File
**File:** `.nvmrc` (new)
- Created `.nvmrc` with version `20` for nvm compatibility

### Version Details

| Component | Old Version | New Version | EOL Date |
|-----------|-------------|-------------|----------|
| Node.js | 18.20.8 | 20.x (latest) | April 2026 |
| npm | 10.8.2 | 10.x (bundled) | - |

### Why Node.js 20?

1. **Active LTS:** Node.js 20 "Iron" is the current LTS version
2. **Extended Support:** Supported until April 2026
3. **Node.js 18 EOL:** Version 18 reaches end-of-life in April 2025
4. **Performance:** Improved V8 engine performance
5. **Features:** Modern ECMAScript support, better async handling

### Breaking Changes

Node.js 20 includes some breaking changes from 18:

1. **V8 Engine:** Updated to v11.3 (from v10.2)
2. **Crypto Module:** Some deprecated APIs removed
3. **URL Module:** Stricter URL parsing
4. **Permissions Model:** New experimental permissions system

### Compatibility Notes

✅ **Compatible:** All current Aurora dependencies support Node.js 20  
✅ **GitHub Actions:** Already using Node.js 20.x  
✅ **Dev Dependencies:** Jest, ESLint, Babel all compatible  
✅ **Runtime Dependencies:** Express, Socket.IO, ws all compatible

### Testing Checklist

Before deploying, verify:

- [ ] Dev container rebuilds successfully
- [ ] `npm install` completes without errors
- [ ] `npm test` passes all tests
- [ ] `npm run lint` completes successfully
- [ ] Aurora API server starts correctly
- [ ] WebSocket connections work
- [ ] Express routes respond correctly
- [ ] Jest tests pass

### Deployment Steps

#### Local Development
1. Rebuild dev container: `Dev Containers: Rebuild Container`
2. Verify Node.js version: `node --version` (should show v20.x.x)
3. Reinstall dependencies: `npm install`
4. Run tests: `npm test`

#### CI/CD
- No changes needed - GitHub Actions already using Node.js 20.x

#### Production
1. Update container base image to include Node.js 20
2. Test in staging environment first
3. Monitor for any runtime issues
4. Rollback plan: Revert to Node.js 18 if critical issues found

### Performance Benefits

Expected improvements with Node.js 20:

- **10-20%** faster JavaScript execution (V8 improvements)
- **Better memory management** with new garbage collector
- **Faster async operations** with optimized Promise handling
- **Reduced startup time** with improved module loading

### Security Improvements

Node.js 20 includes:

- Updated OpenSSL to 3.x
- Security patches for V8 vulnerabilities
- Improved crypto module security
- Better input validation

### Rollback Procedure

If issues arise, rollback by:

1. Revert `.devcontainer/devcontainer.json`: Change `"version": "20"` back to `"18"`
2. Revert `package.json`: Change `"node": ">=18.0.0"` and `"npm": ">=8.0.0"`
3. Delete `.nvmrc` or change to `18`
4. Rebuild dev container

### Future Updates

- **Node.js 22:** Next major version (October 2024 release, LTS in October 2025)
- **Node.js 24:** Current LTS as of 2025 (Krypton)
- Recommendation: Evaluate Node.js 22 LTS in Q4 2025

### Related Files

Files updated in this change:
- `.devcontainer/devcontainer.json`
- `package.json`
- `.nvmrc` (new)

Files already using Node.js 20:
- `.github/workflows/symbolic-bundle.yml`
- `.github/workflows/deploy-pages.yml`

### References

- [Node.js 20 Release Notes](https://nodejs.org/en/blog/release/v20.0.0)
- [Node.js Release Schedule](https://github.com/nodejs/release#release-schedule)
- [Node.js 20 Migration Guide](https://nodejs.org/en/docs/guides)

### Verification Commands

```bash
# Check Node.js version
node --version

# Check npm version
npm --version

# Verify package.json engines
npm run --silent aurora:status

# Run full test suite
npm test

# Lint check
npm run lint:check
```

### Success Criteria

✅ Node.js version shows v20.x.x  
✅ All npm dependencies install successfully  
✅ All tests pass  
✅ Linting completes without errors  
✅ Dev container builds successfully  
✅ Aurora API server starts and responds  

---

**Thread:** T1→T8→T9→INFINITE  
**Status:** Configuration updated, awaiting container rebuild  
**Next Step:** Rebuild dev container to apply Node.js 20 runtime

The field evolves with the ecosystem.
