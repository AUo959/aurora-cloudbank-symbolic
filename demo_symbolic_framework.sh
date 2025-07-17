#!/bin/bash
# Aurora Symbolic Simulation Framework Demonstration Script

echo "=== Aurora Symbolic Simulation Framework Demo ==="
echo "Demonstrating comprehensive symbolic simulation capabilities"
echo

# Set working directory
cd /home/runner/work/aurora-cloudbank-symbolic/aurora-cloudbank-symbolic

echo "1. Executing symbolic chains with entropy monitoring..."
python -m src.aurora.cli.symbolic_cli chain 1 5 --stream-data "aurora_demo_high_entropy_test_data"
echo

echo "2. Sealing symbolic threads with different DLP classifications..."
python -m src.aurora.cli.symbolic_cli seal-thread production_thread confidential --operator-key prod_secret_2025
python -m src.aurora.cli.symbolic_cli seal-thread test_thread internal --operator-key test_key_123  
python -m src.aurora.cli.symbolic_cli seal-thread public_thread public --operator-key public_access
echo

echo "3. Checking entropy monitoring status..."
python -m src.aurora.cli.symbolic_cli entropy-status
echo

echo "4. Listing all symbolic threads..."
python -m src.aurora.cli.symbolic_cli list-threads
echo

echo "5. Exporting comprehensive symbolic manifest..."
python -m src.aurora.cli.symbolic_cli export-manifest --filename complete_demo_manifest.json
echo

echo "6. Executing additional symbolic operations..."
python -m src.aurora.cli.symbolic_cli chain 10 15 --stream-data "additional_entropy_data_for_testing"
echo

echo "7. Rehydrating sealed thread..."
python -m src.aurora.cli.symbolic_cli rehydrate-thread test_thread --operator-key test_key_123
echo

echo "8. Exporting second manifest for diff comparison..."
python -m src.aurora.cli.symbolic_cli export-manifest --filename demo_manifest_v2.json
echo

echo "9. Generating diff report between manifests..."
python -m src.aurora.cli.symbolic_cli diff-manifest exports/complete_demo_manifest.json
echo

echo "10. Generating comprehensive documentation..."
python -m src.aurora.cli.symbolic_cli generate-readme --output-file demo_system_documentation.md
echo

echo "=== Demo Complete ==="
echo "Generated files in exports/ directory:"
ls -la exports/ | grep demo | head -10

echo
echo "=== Key Features Demonstrated ==="
echo "✅ T1, SRB, and EOS_SEED symbolic anchors"
echo "✅ Real-time entropy monitoring with thresholds" 
echo "✅ Memory sealing with DLP classification (public, internal, confidential)"
echo "✅ Thread sealing and rehydration with authentication"
echo "✅ CLI chain framework with 001//999//. format"
echo "✅ Glyphcard generation for sealed threads"
echo "✅ Structured export manifests with metadata"
echo "✅ Diff tools for state comparison"
echo "✅ Automated documentation generation"
echo "✅ Comprehensive CLI tooling"