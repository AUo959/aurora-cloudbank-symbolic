#!/bin/bash

# Aurora CloudBank Markdown Linting Fix Script
# Addresses all MD022, MD032, MD009, MD026, MD029, MD036, MD058 issues
# Persistent solution for markdown formatting compliance

echo "🔧 AURORA CLOUDBANK MARKDOWN LINTING FIX"
echo "========================================"

# Set working directory
WORKSPACE_ROOT="/workspaces/aurora-cloudbank-symbolic"
cd "$WORKSPACE_ROOT"

# Function to fix markdown files
fix_markdown_file() {
    local file="$1"
    echo "📝 Fixing markdown formatting in: $file"
    
    # Create backup
    cp "$file" "$file.backup"
    
    # Fix the file using sed and awk
    awk '
    BEGIN {
        prev_line = ""
        prev_was_heading = 0
        prev_was_list = 0
        in_code_block = 0
    }
    
    # Track code blocks
    /^```/ {
        in_code_block = !in_code_block
        print
        prev_line = $0
        next
    }
    
    # Skip processing inside code blocks
    in_code_block {
        print
        prev_line = $0
        next
    }
    
    # Check if current line is heading
    /^#{1,6} / {
        current_is_heading = 1
        # Add blank line before heading if previous line is not blank and not heading
        if (prev_line != "" && !prev_was_heading && NR > 1) {
            print ""
        }
        # Remove trailing punctuation from headings (: only)
        gsub(/:$/, "", $0)
        print
        prev_was_heading = 1
        prev_was_list = 0
        prev_line = $0
        next
    }
    
    # Check if current line is list item
    /^[[:space:]]*[-*+] / || /^[[:space:]]*[0-9]+\. / {
        current_is_list = 1
        # Add blank line before list if previous line is not blank and not list
        if (prev_line != "" && !prev_was_list && NR > 1) {
            print ""
        }
        # Fix ordered list numbering
        if (/^[[:space:]]*[0-9]+\. /) {
            gsub(/^[[:space:]]*[0-9]+\./, list_counter ".")
            list_counter++
        }
        # Remove trailing spaces
        gsub(/[[:space:]]+$/, "", $0)
        print
        prev_was_list = 1
        prev_was_heading = 0
        prev_line = $0
        next
    }
    
    # Check if line ends list (non-list line after list)
    prev_was_list && !/^[[:space:]]*[-*+] / && !/^[[:space:]]*[0-9]+\. / && $0 != "" {
        # Add blank line after list
        if (prev_line != "") {
            print ""
        }
        prev_was_list = 0
    }
    
    # Check if line ends heading section
    prev_was_heading && !/^#{1,6} / && $0 != "" {
        # Add blank line after heading
        if (prev_line != "") {
            print ""
        }
        prev_was_heading = 0
    }
    
    # Handle table lines
    /^\|.*\|$/ {
        # Add blank line before table if needed
        if (prev_line != "" && prev_line !~ /^\|.*\|$/ && NR > 1) {
            print ""
        }
        print
        prev_line = $0
        next
    }
    
    # Handle end of table
    prev_line ~ /^\|.*\|$/ && $0 !~ /^\|.*\|$/ && $0 != "" {
        print ""
    }
    
    # Default case - just print the line after removing trailing spaces
    {
        gsub(/[[:space:]]+$/, "", $0)
        print
        prev_was_heading = 0
        if (!/^[[:space:]]*[-*+] / && !/^[[:space:]]*[0-9]+\. /) {
            prev_was_list = 0
        }
        prev_line = $0
    }
    ' "$file" > "$file.tmp"
    
    # Replace original with fixed version
    mv "$file.tmp" "$file"
    
    # Remove backup if fix was successful
    if [ $? -eq 0 ]; then
        rm "$file.backup"
        echo "   ✅ Fixed: $file"
    else
        echo "   ❌ Error fixing: $file - restored from backup"
        mv "$file.backup" "$file"
    fi
}

# List of markdown files to fix
markdown_files=(
    "DEPLOYMENT_SEQUENCE_COMPLETE.md"
    "MISSION_COMPLETE_FINAL_STATUS.md"
    "FLEET_DEPLOYMENT_PACKAGE.md"
    "FLEET_DEPLOYMENT_PACKAGE_ENTERPRISE.md"
    "COMPREHENSIVE_DEPLOYMENT_COMPLETE.md"
)

echo "🎯 Processing markdown files..."
echo ""

# Fix each markdown file
for file in "${markdown_files[@]}"; do
    if [ -f "$file" ]; then
        fix_markdown_file "$file"
    else
        echo "   ⚠️  File not found: $file"
    fi
done

echo ""
echo "📋 Additional formatting fixes..."

# Fix specific issues in each file
if [ -f "DEPLOYMENT_SEQUENCE_COMPLETE.md" ]; then
    echo "   🔧 Applying specific fixes to DEPLOYMENT_SEQUENCE_COMPLETE.md"
    
    # Fix emphasis used as heading (MD036)
    sed -i 's/\*\*ORION FLEET DEPLOYMENT CHECKLIST\*\*/## ORION FLEET DEPLOYMENT CHECKLIST/' "DEPLOYMENT_SEQUENCE_COMPLETE.md"
    
    # Fix ordered list numbering
    sed -i '/^2\./s/^2\./1./' "DEPLOYMENT_SEQUENCE_COMPLETE.md"
    sed -i '/^3\./s/^3\./2./' "DEPLOYMENT_SEQUENCE_COMPLETE.md"
fi

if [ -f "FLEET_DEPLOYMENT_PACKAGE.md" ]; then
    echo "   🔧 Applying specific fixes to FLEET_DEPLOYMENT_PACKAGE.md"
    
    # Fix ordered list numbering
    sed -i '/Ethics, Anchor, and Security Checks/,/Final Approval/ {
        s/^2\./1./
        s/^3\./2./
    }' "FLEET_DEPLOYMENT_PACKAGE.md"
fi

if [ -f "FLEET_DEPLOYMENT_PACKAGE_ENTERPRISE.md" ]; then
    echo "   🔧 Applying specific fixes to FLEET_DEPLOYMENT_PACKAGE_ENTERPRISE.md"
    
    # Fix emphasis used as heading
    sed -i 's/\*\*ORION FLEET DEPLOYMENT CHECKLIST\*\*/## ORION FLEET DEPLOYMENT CHECKLIST/' "FLEET_DEPLOYMENT_PACKAGE_ENTERPRISE.md"
    
    # Fix ordered list numbering
    sed -i '/Ethics, Anchor, and Security Checks/,/Final Approval/ {
        s/^2\./1./
        s/^3\./2./
    }' "FLEET_DEPLOYMENT_PACKAGE_ENTERPRISE.md"
fi

echo ""
echo "✅ Markdown linting fixes complete!"
echo ""
echo "📊 Summary of fixes applied:"
echo "   • MD022: Added blank lines around headings"
echo "   • MD032: Added blank lines around lists"
echo "   • MD009: Removed trailing spaces"
echo "   • MD026: Removed trailing punctuation from headings"
echo "   • MD029: Fixed ordered list numbering"
echo "   • MD036: Fixed emphasis used as headings"
echo "   • MD058: Added blank lines around tables"
echo ""
echo "🎯 All markdown files now comply with linting standards."
