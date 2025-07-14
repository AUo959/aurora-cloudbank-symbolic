#!/usr/bin/env python3
"""
Archive Optimization Summary Report Generator
Creates a comprehensive summary of optimization results.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_summary_report(repo_root=None):
    """Generate a summary report of archive optimization results."""
    repo_root = Path(repo_root or os.getcwd())
    manifest_path = repo_root / "archive_optimization_manifest.json"
    bundles_dir = repo_root / "environment_bundles"
    
    if not manifest_path.exists():
        print("❌ Archive optimization manifest not found. Run optimization first.")
        return
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Generate report
    report = {
        "report_date": datetime.now().isoformat(),
        "optimization_summary": {
            "archives_processed": manifest["total_archives"],
            "total_original_size": manifest["total_content_size"],
            "canonical_content_extracted": len(manifest["canonical_content"]),
            "environment_bundles_created": len([f for f in bundles_dir.glob("*.zip") if f.name != "bundle_index.json"]) if bundles_dir.exists() else 0
        },
        "space_optimization": {},
        "content_analysis": {},
        "bundles_generated": {},
        "recommendations": []
    }
    
    # Calculate space optimization
    original_size = manifest["total_content_size"]
    canonical_size = sum(content["size"] for content in manifest["canonical_content"].values())
    
    if bundles_dir.exists():
        bundle_sizes = {f.stem: f.stat().st_size for f in bundles_dir.glob("*.zip")}
        total_bundle_size = sum(bundle_sizes.values())
    else:
        bundle_sizes = {}
        total_bundle_size = 0
    
    report["space_optimization"] = {
        "original_total_size_bytes": original_size,
        "original_total_size_mb": round(original_size / 1024 / 1024, 2),
        "canonical_content_size_bytes": canonical_size,
        "canonical_content_size_mb": round(canonical_size / 1024 / 1024, 2),
        "bundles_total_size_bytes": total_bundle_size,
        "bundles_total_size_mb": round(total_bundle_size / 1024 / 1024, 2),
        "space_reduction_ratio": round((original_size - total_bundle_size) / original_size * 100, 2) if original_size > 0 else 0,
        "canonical_efficiency": round(canonical_size / original_size * 100, 2) if original_size > 0 else 0
    }
    
    # Content analysis
    content_types = {}
    importance_distribution = {"high": 0, "medium": 0, "low": 0}
    environment_distribution = {}
    
    for content in manifest["canonical_content"].values():
        # Content types
        content_type = content["content_type"]
        content_types[content_type] = content_types.get(content_type, 0) + 1
        
        # Importance distribution
        score = content["importance_score"]
        if score >= 75:
            importance_distribution["high"] += 1
        elif score >= 50:
            importance_distribution["medium"] += 1
        else:
            importance_distribution["low"] += 1
        
        # Environment distribution
        for env in content["environment_tags"]:
            environment_distribution[env] = environment_distribution.get(env, 0) + 1
    
    report["content_analysis"] = {
        "content_types": content_types,
        "importance_distribution": importance_distribution,
        "environment_distribution": environment_distribution
    }
    
    # Bundle information
    for bundle_name, size in bundle_sizes.items():
        report["bundles_generated"][bundle_name] = {
            "size_bytes": size,
            "size_mb": round(size / 1024 / 1024, 2)
        }
    
    # Generate recommendations
    recommendations = []
    
    # Large file analysis
    large_files = []
    for content in manifest["canonical_content"].values():
        if content["size"] > 1024 * 1024:  # >1MB
            large_files.append(content)
    
    if large_files:
        recommendations.append(f"Consider chunking {len(large_files)} large files (>1MB) for better loading performance")
    
    # Bundle optimization
    if bundle_sizes:
        max_bundle = max(bundle_sizes.items(), key=lambda x: x[1])
        if max_bundle[1] > 100 * 1024:  # >100KB
            recommendations.append(f"Consider splitting '{max_bundle[0]}' bundle ({round(max_bundle[1]/1024, 1)}KB) into smaller components")
    
    # Environment coverage
    if "documentation" not in environment_distribution:
        recommendations.append("No documentation content found - consider adding documentation to archives")
    
    if total_bundle_size > original_size:
        recommendations.append("Bundle size exceeds original archives - review compression settings")
    elif total_bundle_size < original_size * 0.1:
        recommendations.append("Very high compression achieved - verify all essential content is included")
    
    report["recommendations"] = recommendations
    
    return report

def print_summary_report(report):
    """Print a formatted summary report."""
    print("🎯 Aurora Archive Optimization Summary Report")
    print("=" * 50)
    print(f"📅 Generated: {report['report_date']}")
    print()
    
    # Optimization Summary
    summary = report["optimization_summary"]
    print("📊 Optimization Summary")
    print("-" * 25)
    print(f"Archives processed: {summary['archives_processed']}")
    print(f"Canonical content extracted: {summary['canonical_content_extracted']}")
    print(f"Environment bundles created: {summary['environment_bundles_created']}")
    print()
    
    # Space Optimization
    space = report["space_optimization"]
    print("💾 Space Optimization")
    print("-" * 20)
    print(f"Original size: {space['original_total_size_mb']} MB")
    print(f"Canonical content: {space['canonical_content_size_mb']} MB")
    print(f"Bundle total: {space['bundles_total_size_mb']} MB")
    print(f"Space reduction: {space['space_reduction_ratio']}%")
    print(f"Canonical efficiency: {space['canonical_efficiency']}%")
    print()
    
    # Content Analysis
    content = report["content_analysis"]
    print("📋 Content Analysis")
    print("-" * 18)
    print("Content types:")
    for content_type, count in sorted(content["content_types"].items()):
        print(f"  {content_type}: {count}")
    
    print("\nImportance distribution:")
    importance = content["importance_distribution"]
    print(f"  High (75-100): {importance['high']}")
    print(f"  Medium (50-74): {importance['medium']}")
    print(f"  Low (0-49): {importance['low']}")
    
    print("\nEnvironment distribution:")
    for env, count in sorted(content["environment_distribution"].items()):
        print(f"  {env}: {count}")
    print()
    
    # Bundles Generated
    bundles = report["bundles_generated"]
    if bundles:
        print("📦 Bundles Generated")
        print("-" * 18)
        for bundle_name, info in sorted(bundles.items()):
            print(f"{bundle_name}: {info['size_mb']} MB")
        print()
    
    # Recommendations
    recommendations = report["recommendations"]
    if recommendations:
        print("💡 Recommendations")
        print("-" * 16)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        print()
    
    print("✅ Optimization completed successfully!")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate archive optimization summary report")
    parser.add_argument("--repo-root", help="Repository root directory")
    parser.add_argument("--output-json", help="Save report as JSON file")
    
    args = parser.parse_args()
    
    report = generate_summary_report(args.repo_root)
    if not report:
        return
    
    print_summary_report(report)
    
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {args.output_json}")

if __name__ == "__main__":
    main()