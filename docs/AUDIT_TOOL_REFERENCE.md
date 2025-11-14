# Comprehensive System Audit Tool - Quick Reference

## Overview

The Comprehensive System Audit Tool (`scripts/comprehensive_system_audit.py`) is an automated auditing solution for the Aurora CloudBank Symbolic system. It performs complete audits of:

1. **Dependency Management** - Python and Node.js packages
2. **MCP Server Components** - Bridge configuration, command routing, and security
3. **Security Scan Status** - Validation of security scanning system

## Usage

### Basic Usage

Run the complete audit:

```bash
python3 scripts/comprehensive_system_audit.py
```

The script will:
- Execute all three audit priorities automatically
- Generate a timestamped JSON report in `audit_reports/`
- Display a comprehensive summary in the console
- Exit with appropriate status codes (0=excellent/good, 1=needs attention, 2=critical)

### Output Files

1. **JSON Report:** `audit_reports/system_audit_YYYYMMDD_HHMMSS.json`
   - Complete audit data in structured format
   - Includes DLP metadata and symbolic hash validation
   - Machine-readable for integration with other tools

2. **Console Summary:** 
   - Real-time progress updates
   - Color-coded status indicators
   - Actionable recommendations

## Audit Coverage

### Priority 1: Security Scan Status
- Verifies `.security/scan_log.json` exists and is valid
- Reports total scans and latest scan status
- Identifies recent security issues
- Tracks scan history

### Priority 2: Dependency Audit

**Python Dependencies:**
- Counts installed packages
- Identifies missing critical packages
- Detects dependency conflicts (via `pip check`)
- Lists outdated packages
- Validates requirements files

**Node.js Dependencies:**
- Checks package.json presence
- Counts installed npm packages
- Reports vulnerabilities (if detected)

**Critical Python Packages Monitored:**
- fastapi
- uvicorn
- pydantic
- pandas
- numpy
- requests
- httpx
- pytest

### Priority 3: MCP Server Audit

**MCP Bridge Core Configuration:**
- Validates `modules/symbolic_core/mcp_bridge_core.json`
- Checks governance layer configuration
- Verifies core functions are defined
- Reviews security layers (drift_lock, guardian_ring, ethics_lock)

**MCP Command Router:**
- Tests `modules/symbolic_core/mcp_command_router.py`
- Verifies import capability
- Tests routing functionality
- Confirms governance layer integration

**MCP Security Module:**
- Checks `modules/symbolic_core/mcp_security.py`
- Validates import capability
- Reports dependency issues

**MCP Integration:**
- Scans for MCP integration in main application
- Verifies MCPCommandRouter usage in FastAPI app

## Status Codes

The audit categorizes findings with the following statuses:

- **healthy** ✅ - Component is fully operational
- **warning** ⚠️ - Component has minor issues or missing optional features
- **critical** 🔴 - Component has major issues requiring immediate attention
- **error** ❌ - Component failed to audit (unexpected error)
- **missing** ❓ - Component not found
- **not_applicable** ℹ️ - Component not relevant to current configuration

## Overall System Status

The tool computes an overall system status:

- **excellent** 🟢 - All components healthy
- **good** 🟢 - Mostly healthy with minor warnings
- **needs_attention** 🟡 - Some critical issues detected
- **critical** 🔴 - Multiple critical issues requiring immediate action

## DLP Tracking

Every audit includes Data Lineage Protocol (DLP) tracking:

- **context_tag:** Unique identifier for the audit session
- **export_timestamp:** ISO 8601 timestamp
- **symbolic_hash_validation:** SHA-256 hash (16 chars) for integrity verification

Example context tag format: `system_audit_20251031_030852`

## Exit Codes

The script returns different exit codes for automation:

- `0` - System status is excellent or good
- `1` - System needs attention (warnings present)
- `2` - System has critical issues

## Integration Examples

### CI/CD Pipeline

```bash
#!/bin/bash
# Run audit and fail build if critical issues detected
python3 scripts/comprehensive_system_audit.py
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
    echo "❌ Critical issues detected - failing build"
    exit 1
elif [ $EXIT_CODE -eq 1 ]; then
    echo "⚠️ Warnings detected - build continues with warnings"
    exit 0
else
    echo "✅ Audit passed - build continues"
    exit 0
fi
```

### Scheduled Audits

```bash
# Add to crontab for daily audits at 2 AM
0 2 * * * cd /path/to/aurora-cloudbank-symbolic && python3 scripts/comprehensive_system_audit.py >> logs/daily_audit.log 2>&1
```

### Pre-Deployment Checklist

```bash
# Run before deploying to production
python3 scripts/comprehensive_system_audit.py
if [ $? -ne 0 ]; then
    echo "Audit failed - review findings before deployment"
    exit 1
fi
echo "Audit passed - ready for deployment"
```

## Recommendations Processing

The audit automatically generates actionable recommendations based on findings:

1. **Missing Critical Dependencies** → Install commands provided
2. **Dependency Conflicts** → Suggests running `pip check` and resolution steps
3. **MCP Configuration Issues** → Recommends validation and testing
4. **Security Scan Issues** → Highlights files requiring attention
5. **Outdated Packages** → Suggests update strategy

## Customization

The audit tool can be extended by modifying:

- `_audit_python_deps()` - Add custom Python package checks
- `_audit_nodejs_deps()` - Add custom Node.js package checks
- `_check_mcp_*()` - Extend MCP auditing capabilities
- `_generate_recommendations()` - Add custom recommendation logic

## Best Practices

1. **Run regularly:** Execute audits at least weekly
2. **Review reports:** Check JSON reports for trends over time
3. **Act on recommendations:** Address critical issues promptly
4. **Track changes:** Compare audit reports to monitor system health trends
5. **Automate:** Integrate into CI/CD pipelines for continuous monitoring

## Troubleshooting

### Import Errors

If the script reports import errors:
1. Verify you're in the project root directory
2. Check if virtual environment is activated
3. Install missing dependencies as recommended

### Permission Errors

If unable to create audit reports:
```bash
mkdir -p audit_reports
chmod 755 audit_reports
```

### MCP Module Import Failures

This is expected when critical dependencies (like fastapi) are missing. Install missing packages first:
```bash
pip install fastapi uvicorn pydantic pandas numpy httpx pytest
```

## Version History

- **v1.0.0** (2025-10-31)
  - Initial release
  - Complete three-priority audit coverage
  - DLP tracking integration
  - Comprehensive reporting

## Related Files

- Main audit script: `scripts/comprehensive_system_audit.py`
- Latest execution summary: `AUDIT_EXECUTION_SUMMARY.md`
- Audit reports directory: `audit_reports/`
- MCP configuration: `modules/symbolic_core/mcp_bridge_core.json`
- Security scan log: `.security/scan_log.json`

## Support

For issues or questions about the audit tool:
1. Check the latest audit report in `audit_reports/`
2. Review `AUDIT_EXECUTION_SUMMARY.md` for detailed findings
3. Consult the main Aurora documentation

---

**Audit Tool Version:** 1.0.0  
**Last Updated:** 2025-10-31  
**Maintainer:** Aurora CloudBank Development Team
