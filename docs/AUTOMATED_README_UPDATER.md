# 🤖 Automated README Updater

**Location:** `scripts/update_readme.py`  
**Purpose:** Automatically update README.md with current version, stats, and AI capabilities

---

## ✨ Features

### Automatic Updates

- ✅ **Version Badge** - Reads from `VERSION` file
- ✅ **API Endpoint Count** - Scans source files for accurate count
- ✅ **AI Model Status** - Updates model availability from ai_core modules
- ✅ **Dynamic Content** - Keeps documentation synchronized with code

### Safety Features

- 🔒 **Automatic Backups** - Timestamped before each modification
- 🧪 **Dry-Run Mode** - Preview changes without modifying files
- 📋 **Change Reporting** - Detailed list of all modifications
- ✅ **Validation** - Checks file existence and format

---

## 🚀 Usage

### Basic Update

```bash
# Update README.md with current version from VERSION file
python3 scripts/update_readme.py
```

### Dry-Run (Preview Changes)

```bash
# See what would be changed without modifying files
python3 scripts/update_readme.py --dry-run
```

### Override Version

```bash
# Use specific version instead of VERSION file
python3 scripts/update_readme.py --version 1.2.0
```

### Custom Repository Location

```bash
# Specify repository root directory
python3 scripts/update_readme.py --repo-root /path/to/repo
```

---

## 📊 What It Updates

### 1. Version Badge

**Before:**

```markdown
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]
```

**After:**

```markdown
[![Version](https://img.shields.io/badge/version-1.1.0-blue)]
```

### 2. API Routes Count

**Scans these files:**

- `aurora_api.py`
- `aurora_api_server.py`
- `src/servers/l2_integration_server.py`
- `src/api/ai_management_routes.py`
- `modules/aumemmanager/api/aumemmanager_api.py`

**Counts patterns:**

- `@app.get`, `@app.post`, `@app.put`, `@app.delete`, `@app.patch`
- `@router.get`, `@router.post`, `@router.put`, `@router.delete`, `@router.patch`

**Example:** Found 42 endpoints (27 core + 11 AuMemManager + 4 AI management)

### 3. AI Integration Section

Adds comprehensive AI capabilities section including:

- Model comparison matrix
- Feature highlights
- Usage examples
- API endpoints
- Fallback chain documentation

---

## 🔄 Automation Integration

### Manual Workflow

```bash
# 1. Update VERSION file
echo "1.2.0" > VERSION

# 2. Run README updater
python3 scripts/update_readme.py

# 3. Review changes
git diff README.md

# 4. Commit
git add README.md VERSION
git commit -m "🔖 Release v1.2.0"
```

### CI/CD Integration

```yaml
# .github/workflows/release.yml
- name: Update README
  run: |
    python3 scripts/update_readme.py
    git add README.md
    git commit -m "docs: Update README for release" || true
```

### Git Hook (Pre-Commit)

```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 scripts/update_readme.py --dry-run
if [ $? -ne 0 ]; then
    echo "❌ README update would fail"
    exit 1
fi
```

---

## 📋 Output Example

```
======================================================================
🚀 Aurora CloudBank README.md Updater
======================================================================
🔄 Starting README.md update...
📌 Current version: 1.1.0
📖 Reading /workspaces/aurora-cloudbank-symbolic/README.md
✏️  Updated version badge to 1.1.0
🔍 Counted 42 API endpoints
✏️  Updated API routes badge to 42
✏️  Added AI integration section
💾 Creating backup at README.md.backup.20251021_004023
✍️  Writing updated README.md

✅ README.md updated successfully!

📋 Changes made:
  • Updated version badge: 1.1.0
  • Updated API routes count: 42
  • Added AI integration section

💾 Backup saved to: README.md.backup.20251021_004023

✨ Update complete!

📝 Next steps:
  1. Review the changes in README.md
  2. Commit the updated README.md
  3. Push to repository
```

---

## 🛠️ Customization

### Adding New Scans

Edit `scripts/update_readme.py`:

```python
def count_api_endpoints(self) -> int:
    """Count API endpoints by scanning source files"""
    api_files = [
        # Add your new API files here
        self.repo_root / "src" / "api" / "new_router.py",
    ]
    # ... rest of the function
```

### Adding New Sections

```python
def add_custom_section(self, content: str) -> str:
    """Add custom section to README"""
    custom_section = """
    ## Your Custom Section
    Content here...
    """
    
    insertion_point = "## Target Section"
    return content.replace(insertion_point, custom_section + insertion_point)
```

---

## 🎯 Benefits

### Consistency

- ✅ Version always matches VERSION file
- ✅ Endpoint counts always accurate
- ✅ No manual badge editing errors

### Automation

- ✅ One command updates everything
- ✅ Integrates with CI/CD pipelines
- ✅ Reduces maintenance burden

### Safety

- ✅ Automatic backups prevent data loss
- ✅ Dry-run mode for testing
- ✅ Detailed change reporting

### Accuracy

- ✅ Scans actual source code
- ✅ Real-time endpoint counting
- ✅ No stale documentation

---

## 📚 Related

- **VERSION** - Source of truth for version number
- **CHANGELOG.md** - Manual release notes (not automated)
- **docs/AI_INTEGRATION_UPGRADE_v1.1.0.md** - Comprehensive AI guide
- **.github/workflows/** - CI/CD integration opportunities

---

## 🔮 Future Enhancements

Potential future features:

- Health score badge updates from health reports
- Dependency version updates from requirements.txt
- Contributors section from git history
- Test coverage badge from pytest reports
- Performance metrics from benchmarks

---

**Status:** ✅ Production Ready  
**Tested:** ✅ v1.1.0 update successful  
**Maintained:** ✅ Active
