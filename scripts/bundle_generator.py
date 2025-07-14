#!/usr/bin/env python3
"""
Archive Bundle Generator
Creates optimized, environment-specific archive bundles from canonical content.
"""

import json
import os
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

@dataclass
class BundleConfig:
    """Configuration for generating an environment-specific bundle."""
    name: str
    description: str
    environment_tags: List[str]
    max_size_mb: int
    compression_level: int
    include_patterns: List[str]
    exclude_patterns: List[str]

class BundleGenerator:
    """Generates optimized archive bundles for specific environments."""
    
    def __init__(self, repo_root: str = None):
        self.repo_root = Path(repo_root or os.getcwd())
        self.manifest_path = self.repo_root / "archive_optimization_manifest.json"
        self.extracted_content_dir = self.repo_root / "optimized_archives"
        self.bundles_output_dir = self.repo_root / "environment_bundles"
        self.bundles_output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Predefined bundle configurations
        self.bundle_configs = {
            'minimal_runtime': BundleConfig(
                name="Aurora Minimal Runtime",
                description="Essential files for runtime operation",
                environment_tags=['runtime', 'configuration'],
                max_size_mb=5,
                compression_level=9,
                include_patterns=['*manifest*', '*config*', '*key*'],
                exclude_patterns=['*test*', '*debug*', '*.md']
            ),
            'development_kit': BundleConfig(
                name="Aurora Development Kit",
                description="Complete development environment setup",
                environment_tags=['development', 'runtime', 'configuration'],
                max_size_mb=50,
                compression_level=6,
                include_patterns=['*'],
                exclude_patterns=['*.png', '*.jpg']
            ),
            'production_deployment': BundleConfig(
                name="Aurora Production Deployment",
                description="Production-ready deployment package",
                environment_tags=['production', 'runtime'],
                max_size_mb=20,
                compression_level=9,
                include_patterns=['*manifest*', '*config*', '*prod*'],
                exclude_patterns=['*dev*', '*test*', '*debug*', '*.md']
            ),
            'documentation_bundle': BundleConfig(
                name="Aurora Documentation Bundle",
                description="Complete documentation and guides",
                environment_tags=['documentation'],
                max_size_mb=100,
                compression_level=6,
                include_patterns=['*.md', '*doc*', '*guide*'],
                exclude_patterns=['*temp*', '*cache*']
            ),
            'research_assets': BundleConfig(
                name="Aurora Research Assets",
                description="Research data and analysis tools",
                environment_tags=['universal'],
                max_size_mb=200,
                compression_level=6,
                include_patterns=['*.csv', '*.py', '*research*', '*analysis*'],
                exclude_patterns=['*temp*']
            )
        }
    
    def load_manifest(self) -> Dict[str, Any]:
        """Load the archive optimization manifest."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.manifest_path}")
            
        with open(self.manifest_path, 'r') as f:
            return json.load(f)
    
    def filter_content_for_bundle(self, manifest: Dict[str, Any], 
                                 config: BundleConfig) -> List[str]:
        """Filter canonical content for a specific bundle configuration."""
        matching_content = []
        canonical_content = manifest["canonical_content"]
        
        for content_key, content_data in canonical_content.items():
            # Check environment tags
            content_tags = content_data.get("environment_tags", [])
            if not any(tag in config.environment_tags for tag in content_tags):
                continue
                
            # Check include patterns
            filename = content_data["filename"]
            if not self._matches_patterns(filename, config.include_patterns):
                continue
                
            # Check exclude patterns
            if self._matches_patterns(filename, config.exclude_patterns):
                continue
                
            matching_content.append(content_key)
            
        return matching_content
    
    def _matches_patterns(self, filename: str, patterns: List[str]) -> bool:
        """Check if filename matches any of the given patterns."""
        import fnmatch
        filename_lower = filename.lower()
        
        for pattern in patterns:
            if fnmatch.fnmatch(filename_lower, pattern.lower()):
                return True
        return False
    
    def create_bundle(self, bundle_name: str, config: BundleConfig, 
                     content_keys: List[str], manifest: Dict[str, Any]) -> Path:
        """Create an optimized archive bundle."""
        bundle_path = self.bundles_output_dir / f"{bundle_name}.zip"
        canonical_content = manifest["canonical_content"]
        
        total_size = 0
        max_size_bytes = config.max_size_mb * 1024 * 1024
        
        with zipfile.ZipFile(bundle_path, 'w', 
                           compression=zipfile.ZIP_DEFLATED,
                           compresslevel=config.compression_level) as zf:
            
            # Add bundle metadata
            bundle_info = {
                "bundle_name": config.name,
                "description": config.description,
                "created_by": "Aurora Archive Optimizer",
                "environment_tags": config.environment_tags,
                "content_count": len(content_keys),
                "optimization_level": config.compression_level
            }
            
            zf.writestr("bundle_info.json", json.dumps(bundle_info, indent=2))
            
            # Add content files
            added_files = []
            skipped_files = []
            
            for content_key in content_keys:
                content_data = canonical_content[content_key]
                content_size = content_data["size"]
                
                # Check size limits
                if total_size + content_size > max_size_bytes:
                    skipped_files.append(content_key)
                    continue
                
                # Find the extracted file
                source_filename = content_data["filename"]
                safe_filename = source_filename.replace('/', '_').replace('\\', '_')
                source_path = self.extracted_content_dir / safe_filename
                
                if source_path.exists():
                    # Add to bundle with original path structure
                    zf.write(source_path, source_filename)
                    added_files.append(content_key)
                    total_size += content_size
                    
                    self.logger.debug(f"Added {source_filename} to {bundle_name}")
                else:
                    self.logger.warning(f"Source file not found: {source_path}")
                    skipped_files.append(content_key)
            
            # Add bundle summary
            bundle_summary = {
                "added_files": len(added_files),
                "skipped_files": len(skipped_files),
                "total_size_bytes": total_size,
                "compression_ratio": bundle_path.stat().st_size / total_size if total_size > 0 else 0,
                "added_content_keys": added_files,
                "skipped_content_keys": skipped_files
            }
            
            zf.writestr("bundle_summary.json", json.dumps(bundle_summary, indent=2))
        
        self.logger.info(f"Created bundle: {bundle_path} ({bundle_path.stat().st_size} bytes)")
        return bundle_path
    
    def generate_all_bundles(self) -> Dict[str, Path]:
        """Generate all predefined environment bundles."""
        manifest = self.load_manifest()
        generated_bundles = {}
        
        for bundle_id, config in self.bundle_configs.items():
            try:
                content_keys = self.filter_content_for_bundle(manifest, config)
                
                if content_keys:
                    bundle_path = self.create_bundle(bundle_id, config, content_keys, manifest)
                    generated_bundles[bundle_id] = bundle_path
                else:
                    self.logger.warning(f"No content found for bundle: {bundle_id}")
                    
            except Exception as e:
                self.logger.error(f"Failed to create bundle {bundle_id}: {e}")
        
        return generated_bundles
    
    def create_custom_bundle(self, name: str, environment_tags: List[str], 
                           max_size_mb: int = 50, compression_level: int = 6) -> Path:
        """Create a custom bundle with specified parameters."""
        config = BundleConfig(
            name=f"Custom Bundle: {name}",
            description=f"Custom bundle for {', '.join(environment_tags)}",
            environment_tags=environment_tags,
            max_size_mb=max_size_mb,
            compression_level=compression_level,
            include_patterns=['*'],
            exclude_patterns=[]
        )
        
        manifest = self.load_manifest()
        content_keys = self.filter_content_for_bundle(manifest, config)
        
        return self.create_bundle(name, config, content_keys, manifest)
    
    def analyze_bundles(self) -> Dict[str, Any]:
        """Analyze existing bundles and provide optimization suggestions."""
        analysis = {
            "bundle_count": 0,
            "total_bundle_size": 0,
            "bundles": {},
            "optimization_suggestions": []
        }
        
        for bundle_file in self.bundles_output_dir.glob("*.zip"):
            try:
                bundle_size = bundle_file.stat().st_size
                analysis["bundle_count"] += 1
                analysis["total_bundle_size"] += bundle_size
                
                # Analyze bundle content
                with zipfile.ZipFile(bundle_file, 'r') as zf:
                    file_count = len(zf.namelist())
                    
                    # Load bundle info if available
                    bundle_info = {}
                    try:
                        with zf.open("bundle_info.json") as f:
                            bundle_info = json.load(f)
                    except:
                        pass
                    
                    analysis["bundles"][bundle_file.name] = {
                        "size_bytes": bundle_size,
                        "file_count": file_count,
                        "info": bundle_info
                    }
                    
            except Exception as e:
                self.logger.error(f"Failed to analyze bundle {bundle_file}: {e}")
        
        # Generate optimization suggestions
        if analysis["bundle_count"] > 0:
            avg_size = analysis["total_bundle_size"] / analysis["bundle_count"]
            
            for bundle_name, bundle_data in analysis["bundles"].items():
                if bundle_data["size_bytes"] > avg_size * 2:
                    analysis["optimization_suggestions"].append(
                        f"{bundle_name}: Consider splitting into smaller bundles (current: {bundle_data['size_bytes']} bytes)"
                    )
                elif bundle_data["file_count"] < 5:
                    analysis["optimization_suggestions"].append(
                        f"{bundle_name}: Consider merging with similar bundles (only {bundle_data['file_count']} files)"
                    )
        
        return analysis
    
    def create_bundle_index(self) -> Path:
        """Create an index of all available bundles."""
        index_path = self.bundles_output_dir / "bundle_index.json"
        
        index = {
            "created_at": "2025-01-15T00:00:00Z",
            "available_bundles": {},
            "bundle_configs": {}
        }
        
        # Index existing bundles
        for bundle_file in self.bundles_output_dir.glob("*.zip"):
            if bundle_file.name == "bundle_index.json":
                continue
                
            try:
                with zipfile.ZipFile(bundle_file, 'r') as zf:
                    bundle_info = {}
                    try:
                        with zf.open("bundle_info.json") as f:
                            bundle_info = json.load(f)
                    except:
                        pass
                    
                    index["available_bundles"][bundle_file.name] = {
                        "size_bytes": bundle_file.stat().st_size,
                        "file_count": len(zf.namelist()),
                        "info": bundle_info
                    }
                    
            except Exception as e:
                self.logger.error(f"Failed to index bundle {bundle_file}: {e}")
        
        # Add bundle configurations
        for config_id, config in self.bundle_configs.items():
            index["bundle_configs"][config_id] = {
                "name": config.name,
                "description": config.description,
                "environment_tags": config.environment_tags,
                "max_size_mb": config.max_size_mb
            }
        
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)
        
        self.logger.info(f"Bundle index created: {index_path}")
        return index_path

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora Bundle Generator")
    parser.add_argument("--repo-root", help="Repository root directory")
    parser.add_argument("--generate-all", action="store_true", help="Generate all predefined bundles")
    parser.add_argument("--custom-bundle", help="Create custom bundle with specified name")
    parser.add_argument("--environment-tags", nargs="+", default=["universal"], 
                       help="Environment tags for custom bundle")
    parser.add_argument("--max-size-mb", type=int, default=50, help="Maximum bundle size in MB")
    parser.add_argument("--analyze", action="store_true", help="Analyze existing bundles")
    parser.add_argument("--create-index", action="store_true", help="Create bundle index")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    generator = BundleGenerator(args.repo_root)
    
    if args.generate_all:
        bundles = generator.generate_all_bundles()
        print(f"Generated {len(bundles)} bundles:")
        for bundle_id, path in bundles.items():
            print(f"  {bundle_id}: {path}")
    
    elif args.custom_bundle:
        bundle_path = generator.create_custom_bundle(
            args.custom_bundle, 
            args.environment_tags,
            args.max_size_mb
        )
        print(f"Created custom bundle: {bundle_path}")
    
    elif args.analyze:
        analysis = generator.analyze_bundles()
        print("Bundle Analysis:")
        print(f"  Total bundles: {analysis['bundle_count']}")
        print(f"  Total size: {analysis['total_bundle_size']} bytes")
        if analysis['optimization_suggestions']:
            print("  Optimization suggestions:")
            for suggestion in analysis['optimization_suggestions']:
                print(f"    - {suggestion}")
    
    elif args.create_index:
        index_path = generator.create_bundle_index()
        print(f"Bundle index created: {index_path}")
    
    else:
        print("Use --generate-all, --custom-bundle, --analyze, or --create-index")

if __name__ == "__main__":
    main()