# 🤖 Copilot Commands for Aurora CloudBank Migration

This file contains exact phrases you can use with GitHub Copilot Chat in old codespaces to trigger automated migration.

## 🎯 Primary Migration Commands

### **Command 1: Full Migration**
```
"migrate this codespace to Aurora CloudBank"
```
**What it does:** Complete automated migration with backup, container optimization, and dependency sync

### **Command 2: Emergency Backup & Migration**  
```
"backup uncommitted changes and migrate to Aurora"
```
**What it does:** Creates emergency backup branch, then runs full migration

### **Command 3: Container Standardization**
```
"standardize this codespace container to Aurora CloudBank"
```
**What it does:** Applies Aurora's performance-optimized devcontainer configuration

### **Command 4: Sync with Main Repository**
```
"sync this codespace with main Aurora repository"
```
**What it does:** Pulls latest changes and synchronizes environment

## 🔧 Specific Action Commands

### **Emergency Backup Only**
```
"create emergency backup of uncommitted changes"
```
**Result:** Creates timestamped backup branch with all uncommitted work

### **Dependency Installation**
```
"install Aurora CloudBank dependencies"
```
**Result:** Installs Python (FastAPI, Qiskit, etc.) and Node.js dependencies

### **Performance Optimization**
```
"optimize this codespace for Aurora performance"
```
**Result:** Applies memory and CPU optimizations (60% reduction)

### **Environment Assessment**
```
"assess this codespace environment for Aurora"
```
**Result:** Shows current state, container config, versions, uncommitted files

## 🚀 One-Liner Migration Commands

### **Download and Run (for codespaces without scripts)**
```bash
curl -sSL https://raw.githubusercontent.com/AUo959/aurora-cloudbank-symbolic/main/copilot-migrate | bash
```

### **Quick Migration (if repository available)**
```bash
git pull origin main && ./migrate
```

### **Direct Automator Execution**
```bash
./aurora_codespace_migration_automator.sh
```

## 🎯 Advanced Copilot Phrases

### **For Large Uncommitted Changes**
```
"I have many uncommitted changes, safely migrate this codespace to Aurora"
```

### **For Different Container Types**  
```
"this codespace has a different dev container, standardize it to Aurora"
```

### **For Complete Cleanup**
```
"clean up and migrate this entire codespace to Aurora CloudBank"
```

### **For Dependency Issues**
```
"fix dependencies and migrate this codespace to Aurora"
```

## 🤖 What Copilot Will Understand

When you use these phrases, Copilot should:

1. **Recognize Aurora CloudBank migration intent**
2. **Download migration scripts if needed**  
3. **Run the appropriate automation commands**
4. **Handle backup, standardization, and sync automatically**

## 🛡️ Safety Features

All migration commands include:
- ✅ **Automatic backup** before any changes
- ✅ **Timestamped branches** for rollback capability  
- ✅ **Aurora DLP compliance** with audit trails
- ✅ **Non-destructive operations** - preserves all work
- ✅ **Comprehensive logging** for troubleshooting

## 📋 Expected Results

After running any migration command, you should see:
- Emergency backup branch created (if uncommitted changes existed)
- Container optimized for Aurora performance  
- Dependencies synchronized (Python 3.11, Node.js 20)
- Migration report generated with next steps
- Clean working directory ready for development

## 🔗 Related Files

- `aurora_codespace_migration_automator.sh` - Main automation script
- `migrate` - Simple launcher script  
- `copilot-migrate` - Copilot-specific migration script
- `CODESPACE_MIGRATION_GUIDE.md` - Complete manual procedures

---

**Remember:** These commands work in any Aurora CloudBank codespace. Copilot will handle downloading scripts if they're not available locally.
