#!/bin/bash
# Aurora Archive Optimization Runner
# Automates the archive optimization process and generates environment bundles

set -e

REPO_ROOT="${1:-$(pwd)}"
SCRIPT_DIR="$REPO_ROOT/scripts"
VERBOSE="${VERBOSE:-false}"

echo "🎯 Aurora Archive Optimization Runner"
echo "📂 Repository: $REPO_ROOT"
echo ""

# Function to run with error handling
run_with_logging() {
    local cmd="$1"
    local description="$2"
    
    echo "▶️  $description..."
    
    if [ "$VERBOSE" = "true" ]; then
        eval "$cmd --verbose" || {
            echo "❌ Failed: $description"
            return 1
        }
    else
        eval "$cmd" || {
            echo "❌ Failed: $description"
            return 1
        }
    fi
    
    echo "✅ Completed: $description"
    echo ""
}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Check if scripts exist
if [ ! -f "$SCRIPT_DIR/archive_optimizer.py" ]; then
    echo "❌ Archive optimizer script not found: $SCRIPT_DIR/archive_optimizer.py"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/bundle_generator.py" ]; then
    echo "❌ Bundle generator script not found: $SCRIPT_DIR/bundle_generator.py"
    exit 1
fi

# Make scripts executable
chmod +x "$SCRIPT_DIR/archive_optimizer.py"
chmod +x "$SCRIPT_DIR/bundle_generator.py"

echo "🔍 Phase 1: Archive Analysis and Optimization"
echo "=============================================="

# Run archive optimization
run_with_logging "python3 $SCRIPT_DIR/archive_optimizer.py --repo-root $REPO_ROOT" \
                 "Analyzing and optimizing archive content"

echo "📦 Phase 2: Environment Bundle Generation"
echo "========================================="

# Generate all predefined bundles
run_with_logging "python3 $SCRIPT_DIR/bundle_generator.py --repo-root $REPO_ROOT --generate-all" \
                 "Generating environment-specific bundles"

echo "📊 Phase 3: Analysis and Indexing"
echo "=================================="

# Create bundle index
run_with_logging "python3 $SCRIPT_DIR/bundle_generator.py --repo-root $REPO_ROOT --create-index" \
                 "Creating bundle index"

# Analyze bundles
run_with_logging "python3 $SCRIPT_DIR/bundle_generator.py --repo-root $REPO_ROOT --analyze" \
                 "Analyzing generated bundles"

echo "📋 Phase 4: Summary Report"
echo "=========================="

# Check if manifest was created
MANIFEST_FILE="$REPO_ROOT/archive_optimization_manifest.json"
if [ -f "$MANIFEST_FILE" ]; then
    echo "✅ Archive optimization manifest created: $(basename $MANIFEST_FILE)"
    
    # Extract key statistics
    if command -v jq &> /dev/null; then
        echo "📊 Statistics:"
        echo "   Archives processed: $(jq -r '.total_archives' $MANIFEST_FILE)"
        echo "   Total content size: $(jq -r '.total_content_size' $MANIFEST_FILE) bytes"
        echo "   Canonical content: $(jq -r '.canonical_content | length' $MANIFEST_FILE) items"
        echo "   Environment bundles: $(jq -r '.environment_bundles | length' $MANIFEST_FILE) types"
        
        optimization_ratio=$(jq -r '.optimization_stats.space_optimization_ratio' $MANIFEST_FILE)
        echo "   Space optimization: $(echo "$optimization_ratio * 100" | bc -l 2>/dev/null || echo "N/A")%"
    else
        echo "   (Install 'jq' for detailed statistics)"
    fi
else
    echo "⚠️  Archive optimization manifest not found"
fi

# Check bundle directory
BUNDLE_DIR="$REPO_ROOT/environment_bundles"
if [ -d "$BUNDLE_DIR" ]; then
    bundle_count=$(find "$BUNDLE_DIR" -name "*.zip" | wc -l)
    echo "✅ Environment bundles directory: $(basename $BUNDLE_DIR)"
    echo "   Generated bundles: $bundle_count"
    
    if [ $bundle_count -gt 0 ]; then
        echo "   Bundle files:"
        find "$BUNDLE_DIR" -name "*.zip" -exec basename {} \; | sort | sed 's/^/     - /'
    fi
else
    echo "⚠️  Environment bundles directory not found"
fi

# Check extracted content directory
EXTRACTED_DIR="$REPO_ROOT/optimized_archives"
if [ -d "$EXTRACTED_DIR" ]; then
    extracted_count=$(find "$EXTRACTED_DIR" -type f | wc -l)
    echo "✅ Optimized archives directory: $(basename $EXTRACTED_DIR)"
    echo "   Extracted files: $extracted_count"
else
    echo "⚠️  Optimized archives directory not found"
fi

echo ""
echo "🎉 Archive optimization completed successfully!"
echo ""
echo "📁 Generated files:"
echo "   📄 $MANIFEST_FILE"
echo "   📁 $BUNDLE_DIR/"
echo "   📁 $EXTRACTED_DIR/"
echo ""
echo "💡 Next steps:"
echo "   1. Review the optimization manifest for detailed analysis"
echo "   2. Use environment bundles for deployment/development"
echo "   3. Add optimized_archives/ and environment_bundles/ to .gitignore if desired"
echo "   4. Consider integrating bundle generation into your CI/CD pipeline"
echo ""