# CodeQL Configuration Fix

The error "CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled" occurs because GitHub has both:

1. **Default CodeQL setup** enabled in repository settings
2. **Advanced CodeQL workflow** configured in `.github/workflows/codeql.yml`

## Solution Options:

### Option 1: Disable Default Setup (Recommended)
1. Go to your repository settings: https://github.com/AUo959/aurora-cloudbank-symbolic/settings/security_analysis
2. Under "Code scanning", disable "Default setup"
3. Keep the advanced configuration in `.github/workflows/codeql.yml`

### Option 2: Use Default Setup Only
1. Delete or rename `.github/workflows/codeql.yml`
2. Keep the default setup enabled in repository settings

### Option 3: Simplified Advanced Configuration
Replace the current advanced configuration with a simpler one that doesn't conflict.

## Current Status:
- ✅ Advanced CodeQL workflow exists: `.github/workflows/codeql.yml`
- ❌ Conflict with default setup causing analysis failure
- 🔧 Needs configuration adjustment

## Recommended Action:
**Use Option 1** - Disable the default setup and keep our advanced configuration which provides:
- Custom query suites (+security-and-quality)
- Multiple language support (JavaScript, Python)
- Scheduled weekly scans
- Better path filtering
- Enhanced error handling
