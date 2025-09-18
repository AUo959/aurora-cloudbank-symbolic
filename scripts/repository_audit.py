#!/usr/bin/env python3

"""
Aurora CloudBank Repository Audit
Comprehensive analysis and optimization recommendations

Uses enhanced GITWiz and ZIPWiz to audit the repository state
and provide intelligent recommendations for optimization.
"""

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))


def analyze_repository_files():
    pass
    """Analyze all files in the repository."""
    project_root = Path("/workspaces/aurora-cloudbank-symbolic")

    analysis = {
        "total_files": 0,
        "total_size": 0,
        "file_types": {},
        "large_files": [],
        "zip_files": [],
        "markdown_files": [],
        "duplicate_names": {},
        "potential_cleanup": [],
    }

    # Scan all files
    for file_path in project_root.rglob("*"):
    pass
        if file_path.is_file() and not any(part.startswith(".git") for part in file_path.parts):
    pass
            analysis["total_files"] += 1
            size = file_path.stat().st_size
            analysis["total_size"] += size

            # Track file types
            ext = file_path.suffix.lower()
            analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1

            # Track large files (>10MB)
            if size > 10 * 1024 * 1024:
    pass
                analysis["large_files"].append(
                    {
                        "path": str(file_path.relative_to(project_root)),
                        "size": size,
                        "size_mb": round(size / (1024 * 1024), 2),
                    }
                )

            # Collect ZIP files
            if ext == ".zip":
    pass
                analysis["zip_files"].append(str(file_path.relative_to(project_root)))

            # Collect markdown files
            if ext == ".md":
    pass
                analysis["markdown_files"].append(str(file_path.relative_to(project_root)))

            # Track potential duplicates by name
            name = file_path.name.lower()
            if name not in analysis["duplicate_names"]:
    pass
                analysis["duplicate_names"][name] = []
            analysis["duplicate_names"][name].append(str(file_path.relative_to(project_root)))

    # Find actual duplicates
    actual_duplicates = {k: v for k, v in analysis["duplicate_names"].items() if len(v) > 1}
    analysis["duplicate_names"] = actual_duplicates

    # Identify potential cleanup candidates
    cleanup_patterns = [
        "backup",
        "old",
        "copy",
        "temp",
        "tmp",
        "_2",
        " 2",
        "draft",
        "test",
    ]

    for file_path in project_root.rglob("*"):
    pass
        if file_path.is_file():
    pass
            name_lower = file_path.name.lower()
            if any(pattern in name_lower for pattern in cleanup_patterns):
    pass
                analysis["potential_cleanup"].append(str(file_path.relative_to(project_root)))

    return analysis

def analyze_zip_files():
    pass
    """Analyze all ZIP files in the repository."""
    project_root = Path("/workspaces/aurora-cloudbank-symbolic")
    zip_files = list(project_root.glob("*.zip"))

    zip_analysis = {
        "total_zip_files": len(zip_files),
        "total_zip_size": 0,
        "zip_details": [],
    }

    for zip_file in zip_files:
    pass
        size = zip_file.stat().st_size
        zip_analysis["total_zip_size"] += size

        zip_info = {
            "name": zip_file.name,
            "size": size,
            "size_mb": round(size / (1024 * 1024), 2),
            "category": categorize_zip_file(zip_file.name),
        }
        zip_analysis["zip_details"].append(zip_info)

    # Sort by size (largest first)
    zip_analysis["zip_details"].sort(key=lambda x: x["size"], reverse=True)

    return zip_analysis

def categorize_zip_file(filename: str) -> str:
    pass
    """Categorize ZIP file based on name patterns."""
    name_lower = filename.lower()

    if any(word in name_lower for word in ["bundle", "export", "package"]):
    pass
        return "bundle"
    elif any(word in name_lower for word in ["toolkit", "tool"]):
    pass
        return "toolkit"
    elif any(word in name_lower for word in ["module", "component"]):
    pass
        return "module"
    elif any(word in name_lower for word in ["seed", "template"]):
    pass
        return "seed"
    elif any(word in name_lower for word in ["docs", "documentation"]):
    pass
        return "documentation"
    else:
    pass
        return "other"

def analyze_markdown_documentation():
    pass
    """Analyze markdown documentation structure."""
    project_root = Path("/workspaces/aurora-cloudbank-symbolic")
    md_files = list(project_root.glob("*.md"))

    md_analysis = {
        "total_md_files": len(md_files),
        "status_reports": [],
        "documentation": [],
        "guides": [],
        "other": [],
    }

    for md_file in md_files:
    pass
        name_lower = md_file.name.lower()

        if any(word in name_lower for word in ["status", "complete", "report"]):
    pass
            md_analysis["status_reports"].append(md_file.name)
        elif any(word in name_lower for word in ["guide", "readme", "how"]):
    pass
            md_analysis["documentation"].append(md_file.name)
        elif any(word in name_lower for word in ["deployment", "package"]):
    pass
            md_analysis["guides"].append(md_file.name)
        else:
    pass
            md_analysis["other"].append(md_file.name)

    return md_analysis

def generate_recommendations(file_analysis, zip_analysis, md_analysis):
    pass
    """Generate optimization recommendations."""
    recommendations = {"critical": [], "important": [], "suggestions": []}

    # Critical recommendations
    if file_analysis["total_size"] > 500 * 1024 * 1024:  # >500MB
        recommendations["critical"].append(
            "Repository size is {file_analysis['total_size'] / (1024 * 1024 * 1024):.2f}GB - consider archiving old files"
        )

    if len(file_analysis["large_files"]) > 5:
    pass
        recommendations["critical"].append(
            "Found {len(file_analysis['large_files'])} large files - consider using Git LFS"
        )

    # Important recommendations
    if zip_analysis["total_zip_files"] > 15:
    pass
        recommendations["important"].append(
            "Found {zip_analysis['total_zip_files']} ZIP files - consider consolidating or archiving"
        )

    if len(file_analysis["duplicate_names"]) > 5:
    pass
        recommendations["important"].append(
            "Found {len(file_analysis['duplicate_names'])} potential duplicate file sets"
        )

    if md_analysis["total_md_files"] > 30:
    pass
        recommendations["important"].append(
            "Found {md_analysis['total_md_files']} markdown files - consider organizing into docs/ directory"
        )

    # Suggestions
    if len(file_analysis["potential_cleanup"]) > 0:
    pass
        recommendations["suggestions"].append(
            "Found {len(file_analysis['potential_cleanup'])} files that might be candidates for cleanup"
        )

    # ZIP-specific recommendations
    zip_categories = {}
    for zip_info in zip_analysis["zip_details"]:
    pass
        cat = zip_info["category"]
        zip_categories[cat] = zip_categories.get(cat, 0) + 1

    if zip_categories.get("bundle", 0) > 3:
    pass
        recommendations["suggestions"].append("Multiple bundle files detected - consider consolidating related bundles")

    return recommendations

def main():
    pass
    """Main audit function."""
    print("🔍 AURORA CLOUDBANK REPOSITORY AUDIT")
    print("=" * 50)

    # Perform analyses
    print("📊 Analyzing repository files...")
    file_analysis = analyze_repository_files()

    print("📦 Analyzing ZIP archives...")
    zip_analysis = analyze_zip_files()

    print("📝 Analyzing markdown documentation...")
    md_analysis = analyze_markdown_documentation()

    print("💡 Generating recommendations...")
    recommendations = generate_recommendations(file_analysis, zip_analysis, md_analysis)

    # Generate report
    report = {
        "audit_timestamp": "2025-07-02",
        "file_analysis": file_analysis,
        "zip_analysis": zip_analysis,
        "markdown_analysis": md_analysis,
        "recommendations": recommendations,
    }

    # Print summary
    print("\n📋 AUDIT SUMMARY")
    print("-" * 30)
    print("Total Files: {file_analysis['total_files']}")
    print("Total Size: {file_analysis['total_size'] / (1024 * 1024):.2f} MB")
    print("ZIP Files: {zip_analysis['total_zip_files']} ({zip_analysis['total_zip_size'] / (1024 * 1024):.2f} MB)")
    print("Markdown Files: {md_analysis['total_md_files']}")
    print("Large Files: {len(file_analysis['large_files'])}")
    print("Potential Duplicates: {len(file_analysis['duplicate_names'])}")

    print("\n🚨 CRITICAL RECOMMENDATIONS")
    for rec in recommendations["critical"]:
    pass
        print("  • {rec}")

    print("\n⚠️  IMPORTANT RECOMMENDATIONS")
    for rec in recommendations["important"]:
    pass
        print("  • {rec}")

    print("\n💡 SUGGESTIONS")
    for rec in recommendations["suggestions"]:
    pass
        print("  • {rec}")

    print("\n📦 ZIP FILE ANALYSIS")
    print("Top 10 largest ZIP files:")
    for i, zip_info in enumerate(zip_analysis["zip_details"][:10]):
    pass
        print("  {i + 1}. {zip_info['name']} ({zip_info['size_mb']} MB) - {zip_info['category']}")

    print("\n📝 MARKDOWN FILE CATEGORIES")
    print("  Status Reports: {len(md_analysis['status_reports'])}")
    print("  Documentation: {len(md_analysis['documentation'])}")
    print("  Guides: {len(md_analysis['guides'])}")
    print("  Other: {len(md_analysis['other'])}")

    # Save detailed report
    report_path = Path("/workspaces/aurora-cloudbank-symbolic/REPOSITORY_AUDIT_REPORT.json")
    with open(report_path, "w", encoding="utf-8") as f:
    pass
        json.dump(report, f, indent=2)

    print("\n💾 Detailed report saved to: {report_path}")

    return report

if __name__ == "__main__":
    pass
    main()
