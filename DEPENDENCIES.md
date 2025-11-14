# Aurora CloudBank Dependencies Documentation

## 📦 Dependency Files Overview

Aurora CloudBank uses a **two-tier dependency strategy** to support both full-featured local development and lightweight Vercel deployments.

### Dependency Files

| File | Purpose | Size | Used By |
|------|---------|------|---------|
| `requirements.txt` | **Vercel Production** - Lightweight dependencies | ~40MB | Vercel deployments |
| `requirements-full.txt` | **Local Development** - Complete dependencies | ~150MB | Local development, CI/CD |
| `requirements-lock.txt` | **Pinned versions** - Reproducible builds | ~150MB | `make setup` script |
| `requirements-dev.txt` | **Development tools** - Testing, linting, etc. | Variable | Local testing |
| `requirements-optional.txt` | **Optional features** - Advanced integrations | Variable | As needed |

## 🎯 Which File to Use?

### For Local Development (Full Features)
```bash
# Option 1: Use make (recommended)
make install

# Option 2: Direct pip install
pip install -r requirements-full.txt
```

### For Vercel-Compatible Testing
```bash
make install-vercel
# OR
pip install -r requirements.txt
```

### For Reproducible Setup
```bash
make setup  # Uses requirements-lock.txt with pinned versions
```

## 🔍 What's Different?

### requirements.txt (Lightweight - Vercel)
**Included:**
- ✅ FastAPI, uvicorn, starlette (web framework)
- ✅ httpx, websockets, aiofiles (networking)
- ✅ cryptography, JWT, security middleware
- ✅ anthropic, openai (AI integrations)
- ✅ numpy (basic math)
- ✅ All authentication and rate limiting

**Excluded (gracefully degrades):**
- ❌ qiskit, qiskit-aer (~100MB) - Quantum computing
- ❌ scipy (~50MB) - Advanced scientific computing
- ❌ pandas (~50MB) - Data analysis
- ❌ plotly (~30MB) - Visualizations
- ❌ redis (~20MB) - Caching

### requirements-full.txt (Complete - Local Dev)
**Includes everything** from `requirements.txt` PLUS:
- ✅ qiskit, qiskit-aer - Full quantum computing support
- ✅ scipy - Scientific computing
- ✅ pandas - Data analysis
- ✅ plotly - Interactive visualizations
- ✅ redis - Caching support

## 🔧 How It Works

### Graceful Degradation
All excluded dependencies have **graceful fallback implementations** in the codebase:

```python
# Example from the codebase
try:
    from qiskit import QuantumCircuit
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False
    # Uses mock implementation
```

This means:
- **Vercel deployment** works with core API features
- **Local development** has full quantum/scientific capabilities
- **No runtime errors** - features degrade gracefully

## 🚀 Common Tasks

### Fresh Install (Local Development)
```bash
# Clean install with full dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
make install
```

### Update Dependencies
```bash
# Update lock file (keeps versions consistent)
pip freeze > requirements-lock.txt

# Update full requirements
# (Edit requirements-full.txt manually, then reinstall)
make install
```

### Test Vercel Compatibility Locally
```bash
# Install lightweight deps
make install-vercel

# Test the app
cd api && python index.py
# Should show warnings about missing optional deps, but run successfully
```

## ⚠️ Important Notes

1. **DO NOT** delete `requirements-full.txt` - it's your backup for local development
2. **Vercel automatically** uses `requirements.txt` - no manual configuration needed
3. **CI/CD** should use `requirements-lock.txt` for reproducible builds
4. **Local dev** can use either `requirements-full.txt` or `requirements-lock.txt`

## 🔄 Migration from Old Setup

If you previously had the full `requirements.txt`:
```bash
# Your old requirements.txt is now saved as requirements-full.txt
# Your local environment is UNAFFECTED - packages stay installed
# To reinstall if needed:
make install  # Installs from requirements-full.txt
```

## 📊 Deployment Size Comparison

| Environment | Dependencies | Install Size | Build Time |
|------------|--------------|--------------|------------|
| Vercel (before) | requirements.txt (full) | ~150MB | ❌ FAILED |
| Vercel (after) | requirements.txt (light) | ~40MB | ✅ ~2-3 min |
| Local Dev | requirements-full.txt | ~150MB | ✅ ~5 min |

## 🎓 Best Practices

1. **Use `make install`** for local development (installs full deps)
2. **Use `make setup`** for fresh environments (uses pinned versions)
3. **Test locally** before pushing to Vercel
4. **Keep both files** - don't delete `requirements-full.txt`
5. **Update both** when adding new core dependencies

## 🆘 Troubleshooting

### "Module not found" error locally
```bash
# You need the full dependencies
make install
```

### Vercel deployment failing
```bash
# Check deployment size
# Should use requirements.txt (lightweight)
# Verify api/index.py exists
```

### Want full quantum features on Vercel?
Not possible due to Vercel's 50MB limit. Consider:
- Using AWS Lambda with larger limits
- Self-hosting with Docker
- Using Vercel for API only, compute elsewhere

---

**Last Updated:** November 14, 2025  
**Vercel Deployment Commit:** 26818bd4
