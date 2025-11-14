#!/bin/bash
# Fix ESLint Issues - Targeted Approach
# Fixes the most common ESLint issues automatically

echo "🔧 Fixing ESLint Issues - Aurora CloudBank"
echo "=" * 50

# Count initial issues
initial_count=$(npx eslint . --format=compact 2>/dev/null | wc -l)
echo "📊 Initial ESLint issues: $initial_count"

echo ""
echo "🚀 Step 1: Fix auto-fixable issues..."
npx eslint . --fix --quiet

# Check progress
step1_count=$(npx eslint . --format=compact 2>/dev/null | wc -l)
step1_fixed=$((initial_count - step1_count))
echo "✅ Fixed $step1_fixed auto-fixable issues"
echo "📊 Remaining: $step1_count"

echo ""
echo "🔍 Step 2: Analyze remaining issue types..."
echo "Top remaining issues:"
npx eslint . --format=compact 2>/dev/null | grep -o 'Warning - .*' | sort | uniq -c | sort -nr | head -10

echo ""
echo "📈 Progress Summary:"
echo "• Started with: $initial_count issues"
echo "• Fixed automatically: $step1_fixed issues"  
echo "• Remaining: $step1_count issues"
echo "• Improvement: $(( (step1_fixed * 100) / initial_count ))%"

if [ $step1_count -lt 100 ]; then
    echo ""
    echo "🎯 Excellent! Under 100 issues remaining - manual review recommended"
elif [ $step1_count -lt 200 ]; then
    echo ""
    echo "🚀 Good progress! Under 200 issues - ready for targeted fixes"
else
    echo ""
    echo "⚡ Significant improvement! Continue with targeted fixes"
fi

echo ""
echo "✨ ESLint fix script completed!"
