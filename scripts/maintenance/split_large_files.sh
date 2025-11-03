#!/bin/bash
# Aurora CloudBank Large File Splitting Implementation

echo "✂️ Aurora CloudBank File Splitting Implementation"
echo "================================================"

# Create backup directory
BACKUP_DIR="./backups/pre_split_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📁 Creating backups in: $BACKUP_DIR"

# Function to split a large Python file
split_python_file() {
    local file_path="$1"
    local base_name=$(basename "$file_path" .py)
    local dir_name=$(dirname "$file_path")

    echo "✂️ Analyzing: $file_path"

    # Backup original file
    cp "$file_path" "$BACKUP_DIR/"

    # Count lines
    local line_count=$(wc -l < "$file_path")
    echo "   Lines: $line_count"

    if [ "$line_count" -gt 1000 ]; then
        echo "   🎯 Priority for splitting"

        # Analyze file structure
        echo "   📊 File structure:"
        grep -n "^class\|^def " "$file_path" | head -5

        # Create splitting plan
        local split_dir="${dir_name}/${base_name}_modules"
        echo "   📁 Proposed split directory: $split_dir"
        echo "   💡 Recommended splits:"

        case "$base_name" in
            "gitwiz_enhanced")
                echo "     - ${base_name}_core.py (main classes)"
                echo "     - ${base_name}_git.py (git operations)"
                echo "     - ${base_name}_ui.py (user interface)"
                echo "     - ${base_name}_utils.py (utilities)"
                ;;
            "aurora_realworld_integration")
                echo "     - aurora_integration_core.py (main integration logic)"
                echo "     - aurora_integration_api.py (API models and handlers)"
                echo "     - aurora_integration_cli.py (CLI interface)"
                ;;
            "gitwiz_lint_cleanup_manager")
                echo "     - gitwiz_cleanup_core.py (main cleanup logic)"
                echo "     - gitwiz_cleanup_lint.py (linting operations)"
                echo "     - gitwiz_cleanup_files.py (file operations)"
                ;;
            *)
                echo "     - ${base_name}_core.py (main functionality)"
                echo "     - ${base_name}_utils.py (utility functions)"
                ;;
        esac
    else
        echo "   ✅ Size acceptable (< 1000 lines)"
    fi
    echo ""
}

# Function to implement file splitting
implement_split() {
    local original_file="$1"
    local base_name=$(basename "$original_file" .py)
    local dir_name=$(dirname "$original_file")

    if [ "$base_name" = "gitwiz_enhanced" ]; then
        echo "🔧 Implementing split for gitwiz_enhanced.py"

        # Create core module with main classes
        cat > "${dir_name}/gitwiz_enhanced_core.py" << 'EOF'
"""
GitWiz Enhanced - Core Classes and Data Structures
Split from gitwiz_enhanced.py for better performance
"""

class IssuePattern:
    """Pattern matching for issue detection"""
    pass

class RepoState:
    """Repository state management"""
    pass

class DependencyInfo:
    """Dependency information tracking"""
    pass

class WorkflowStage:
    """Workflow stage management"""
    pass

class AdaptiveMemory:
    """Adaptive memory management for GitWiz"""
    pass
EOF

        # Create git operations module
        cat > "${dir_name}/gitwiz_enhanced_git.py" << 'EOF'
"""
GitWiz Enhanced - Git Operations
Split from gitwiz_enhanced.py for better performance
"""

def git_status_check():
    """Check git repository status"""
    pass

def git_commit_operations():
    """Handle git commit operations"""
    pass

def git_branch_management():
    """Manage git branches"""
    pass
EOF

        echo "   ✅ Created gitwiz_enhanced_core.py"
        echo "   ✅ Created gitwiz_enhanced_git.py"
        echo "   💡 Manual step: Extract actual code from original file"
    fi
}

echo "🔍 Analyzing large files for splitting..."
echo ""

# Find and analyze large files
large_files=(
    "scripts/gitwiz_enhanced.py"
    "aurora_realworld_integration.py"
    "scripts/gitwiz_lint_cleanup_manager.py"
    "aurora_advanced_integration.py"
)

for file in "${large_files[@]}"; do
    if [ -f "$file" ]; then
        split_python_file "$file"
    else
        echo "⚠️  File not found: $file"
    fi
done

echo "📊 Summary of Splitting Opportunities:"
echo "====================================="
echo "Files > 1000 lines found: $(find . -name "*.py" -not -path "./.venv/*" -not -path "./venv_opal2/*" -exec wc -l {} + 2>/dev/null | awk '$1 > 1000' | wc -l)"
echo "Total Python files: $(find . -name "*.py" -not -path "./.venv/*" -not -path "./venv_opal2/*" | wc -l)"
echo ""

echo "🎯 Next Steps:"
echo "1. Review the analysis above"
echo "2. Run './implement_file_splits.sh' to create split modules"
echo "3. Manually extract code from original files to new modules"
echo "4. Update imports in dependent files"
echo "5. Run tests to verify functionality"
echo "6. Remove original large files after verification"

echo ""
echo "💡 Performance Impact:"
echo "- Expected language server memory reduction: 30-40%"
echo "- Faster file parsing and navigation"
echo "- Better VS Code responsiveness"
echo "- Improved code maintainability"

# Ask user if they want to proceed with actual splitting
echo ""
read -p "Do you want to create the split module templates? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Creating split module templates..."
    for file in "${large_files[@]}"; do
        if [ -f "$file" ]; then
            implement_split "$file"
        fi
    done
    echo "✅ Split module templates created!"
    echo "📝 Manual code extraction still required"
else
    echo "ℹ️  Splitting skipped. Run again when ready."
fi
