#!/usr/bin/env python3
"""
Aurora Archive Optimizer
Extracts, analyzes, and optimizes zip file content for resource-efficient storage.
Creates canonical content manifests and environment-specific bundles.
"""

import json
import os
import zipfile
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ArchiveContent:
    """Represents content extracted from an archive."""
    filename: str
    size: int
    hash_md5: str
    content_type: str
    importance_score: int
    canonical_candidate: bool
    environment_tags: List[str]
    
@dataclass
class ArchiveManifest:
    """Central manifest for archive optimization."""
    version: str
    created_at: str
    total_archives: int
    total_content_size: int
    canonical_content: Dict[str, ArchiveContent]
    environment_bundles: Dict[str, List[str]]
    optimization_stats: Dict[str, Any]

class ArchiveOptimizer:
    """Main class for archive optimization operations."""
    
    def __init__(self, repo_root: str = None):
        self.repo_root = Path(repo_root or os.getcwd())
        self.manifest_path = self.repo_root / "archive_optimization_manifest.json"
        self.extracted_content_dir = self.repo_root / "optimized_archives"
        self.extracted_content_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def analyze_zip_files(self) -> List[Tuple[Path, Dict]]:
        """Analyze all zip files in the repository."""
        zip_files = list(self.repo_root.glob("**/*.zip"))
        analyses = []
        
        for zip_path in zip_files:
            try:
                analysis = self._analyze_single_zip(zip_path)
                analyses.append((zip_path, analysis))
                self.logger.info(f"Analyzed: {zip_path.name} ({analysis['total_size']} bytes)")
            except Exception as e:
                self.logger.error(f"Failed to analyze {zip_path}: {e}")
                
        return analyses
    
    def _analyze_single_zip(self, zip_path: Path) -> Dict:
        """Analyze a single zip file."""
        analysis = {
            "path": str(zip_path),
            "size": zip_path.stat().st_size,
            "contents": [],
            "total_size": 0,
            "content_types": {},
            "large_files": [],
            "canonical_candidates": []
        }
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for info in zf.infolist():
                    if not info.is_dir():
                        content_analysis = self._analyze_file_content(zf, info)
                        analysis["contents"].append(content_analysis)
                        analysis["total_size"] += content_analysis["size"]
                        
                        # Track content types
                        content_type = content_analysis["content_type"]
                        analysis["content_types"][content_type] = analysis["content_types"].get(content_type, 0) + 1
                        
                        # Identify large files (>100KB)
                        if content_analysis["size"] > 100 * 1024:
                            analysis["large_files"].append(content_analysis)
                            
                        # Identify canonical candidates
                        if self._is_canonical_candidate(content_analysis):
                            analysis["canonical_candidates"].append(content_analysis)
                            
        except Exception as e:
            self.logger.error(f"Error analyzing zip {zip_path}: {e}")
            
        return analysis
    
    def _analyze_file_content(self, zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> Dict:
        """Analyze individual file content within a zip."""
        content = {
            "filename": info.filename,
            "size": info.file_size,
            "compressed_size": info.compress_size,
            "compression_ratio": info.file_size / max(info.compress_size, 1),
            "content_type": self._determine_content_type(info.filename),
            "importance_score": 0,
            "canonical_candidate": False,
            "environment_tags": []
        }
        
        # Calculate MD5 hash
        try:
            with zf.open(info) as f:
                content_data = f.read()
                content["hash_md5"] = hashlib.md5(content_data).hexdigest()
                
                # Determine importance and environment tags
                content["importance_score"] = self._calculate_importance_score(info.filename, content_data)
                content["environment_tags"] = self._determine_environment_tags(info.filename, content_data)
                content["canonical_candidate"] = self._is_canonical_candidate(content)
                
        except Exception as e:
            self.logger.warning(f"Could not read content of {info.filename}: {e}")
            content["hash_md5"] = "unknown"
            
        return content
    
    def _determine_content_type(self, filename: str) -> str:
        """Determine content type based on file extension and name patterns."""
        filename_lower = filename.lower()
        
        if filename_lower.endswith(('.json', '.jsonc')):
            if 'manifest' in filename_lower:
                return 'manifest'
            elif 'config' in filename_lower:
                return 'configuration'
            else:
                return 'json_data'
        elif filename_lower.endswith('.md'):
            return 'documentation'
        elif filename_lower.endswith(('.py', '.js', '.sh')):
            return 'script'
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return 'image'
        elif filename_lower.endswith('.csv'):
            return 'data'
        else:
            return 'other'
    
    def _calculate_importance_score(self, filename: str, content_data: bytes) -> int:
        """Calculate importance score (0-100) based on content analysis."""
        score = 0
        filename_lower = filename.lower()
        
        # High importance keywords
        high_importance_keywords = ['core', 'master', 'main', 'primary', 'critical', 'essential']
        medium_importance_keywords = ['config', 'manifest', 'registry', 'key', 'anchor']
        
        for keyword in high_importance_keywords:
            if keyword in filename_lower:
                score += 30
                
        for keyword in medium_importance_keywords:
            if keyword in filename_lower:
                score += 15
                
        # Size-based scoring (larger files might be less important for quick loading)
        size = len(content_data)
        if size < 10 * 1024:  # Small files - potentially config
            score += 10
        elif size > 1024 * 1024:  # Large files - potentially less critical for quick access
            score -= 20
            
        # Content-based scoring for JSON files
        if filename_lower.endswith('.json'):
            try:
                data = json.loads(content_data.decode('utf-8'))
                if isinstance(data, dict):
                    if 'version' in data or 'manifest' in data:
                        score += 20
                    if len(data) > 100:  # Complex structures
                        score += 10
            except:
                pass
                
        return max(0, min(100, score))
    
    def _determine_environment_tags(self, filename: str, content_data: bytes) -> List[str]:
        """Determine which environments this content is relevant for."""
        tags = []
        filename_lower = filename.lower()
        
        # Development environment
        if any(keyword in filename_lower for keyword in ['dev', 'development', 'test', 'debug']):
            tags.append('development')
            
        # Production environment
        if any(keyword in filename_lower for keyword in ['prod', 'production', 'deploy', 'release']):
            tags.append('production')
            
        # Runtime environment
        if any(keyword in filename_lower for keyword in ['runtime', 'boot', 'start', 'launch']):
            tags.append('runtime')
            
        # Documentation environment
        if filename_lower.endswith('.md') or 'doc' in filename_lower:
            tags.append('documentation')
            
        # Configuration environment
        if any(keyword in filename_lower for keyword in ['config', 'settings', 'manifest']):
            tags.append('configuration')
            
        # If no specific tags found, mark as universal
        if not tags:
            tags.append('universal')
            
        return tags
    
    def _is_canonical_candidate(self, content: Dict) -> bool:
        """Determine if content is a candidate for canonical storage."""
        # High importance score
        if content["importance_score"] > 50:
            return True
            
        # Common configuration or manifest files
        if content["content_type"] in ['manifest', 'configuration']:
            return True
            
        # Files that could be shared across environments
        if 'universal' in content.get("environment_tags", []):
            return True
            
        return False
    
    def extract_canonical_content(self, analyses: List[Tuple[Path, Dict]]) -> Dict[str, ArchiveContent]:
        """Extract canonical content from analyzed archives."""
        canonical_content = {}
        
        for zip_path, analysis in analyses:
            for content in analysis["canonical_candidates"]:
                # Create unique key based on content hash and filename
                key = f"{content['content_type']}_{content['hash_md5'][:8]}_{Path(content['filename']).stem}"
                
                if key not in canonical_content:
                    # Extract the actual content
                    extracted_path = self._extract_file_content(zip_path, content["filename"])
                    if extracted_path:
                        canonical_content[key] = ArchiveContent(
                            filename=content["filename"],
                            size=content["size"],
                            hash_md5=content["hash_md5"],
                            content_type=content["content_type"],
                            importance_score=content["importance_score"],
                            canonical_candidate=True,
                            environment_tags=content["environment_tags"]
                        )
                        
        return canonical_content
    
    def _extract_file_content(self, zip_path: Path, filename: str) -> Path:
        """Extract specific file content to optimized storage."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Create safe filename for extraction
                safe_filename = filename.replace('/', '_').replace('\\', '_')
                extract_path = self.extracted_content_dir / safe_filename
                
                with zf.open(filename) as src, open(extract_path, 'wb') as dst:
                    dst.write(src.read())
                    
                return extract_path
        except Exception as e:
            self.logger.error(f"Failed to extract {filename} from {zip_path}: {e}")
            return None
    
    def create_environment_bundles(self, canonical_content: Dict[str, ArchiveContent]) -> Dict[str, List[str]]:
        """Create optimized bundles for different environments."""
        bundles = {
            'runtime': [],
            'development': [],
            'production': [],
            'configuration': [],
            'documentation': []
        }
        
        for key, content in canonical_content.items():
            for tag in content.environment_tags:
                if tag in bundles:
                    bundles[tag].append(key)
                    
        return bundles
    
    def generate_manifest(self, analyses: List[Tuple[Path, Dict]], 
                         canonical_content: Dict[str, ArchiveContent],
                         environment_bundles: Dict[str, List[str]]) -> ArchiveManifest:
        """Generate the central archive optimization manifest."""
        total_size = sum(analysis["size"] for _, analysis in analyses)
        canonical_size = sum(content.size for content in canonical_content.values())
        
        optimization_stats = {
            "original_archive_count": len(analyses),
            "original_total_size": total_size,
            "canonical_content_count": len(canonical_content),
            "canonical_content_size": canonical_size,
            "space_optimization_ratio": canonical_size / total_size if total_size > 0 else 0,
            "large_files_identified": sum(len(analysis["large_files"]) for _, analysis in analyses),
            "content_type_distribution": self._calculate_content_type_distribution(analyses)
        }
        
        return ArchiveManifest(
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            total_archives=len(analyses),
            total_content_size=total_size,
            canonical_content=canonical_content,
            environment_bundles=environment_bundles,
            optimization_stats=optimization_stats
        )
    
    def _calculate_content_type_distribution(self, analyses: List[Tuple[Path, Dict]]) -> Dict[str, int]:
        """Calculate distribution of content types across all archives."""
        distribution = {}
        for _, analysis in analyses:
            for content_type, count in analysis["content_types"].items():
                distribution[content_type] = distribution.get(content_type, 0) + count
        return distribution
    
    def save_manifest(self, manifest: ArchiveManifest):
        """Save the manifest to disk."""
        manifest_data = asdict(manifest)
        # Convert ArchiveContent objects to dicts
        manifest_data["canonical_content"] = {
            key: asdict(content) for key, content in manifest.canonical_content.items()
        }
        
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)
            
        self.logger.info(f"Manifest saved to {self.manifest_path}")
    
    def optimize_archives(self) -> Dict[str, Any]:
        """Main method to optimize all archives in the repository."""
        self.logger.info("Starting archive optimization process...")
        
        # Analyze all zip files
        analyses = self.analyze_zip_files()
        
        # Extract canonical content
        canonical_content = self.extract_canonical_content(analyses)
        
        # Create environment bundles
        environment_bundles = self.create_environment_bundles(canonical_content)
        
        # Generate manifest
        manifest = self.generate_manifest(analyses, canonical_content, environment_bundles)
        
        # Save manifest
        self.save_manifest(manifest)
        
        # Return summary
        return {
            "archives_processed": len(analyses),
            "canonical_content_extracted": len(canonical_content),
            "environment_bundles_created": len(environment_bundles),
            "total_size_analyzed": manifest.total_content_size,
            "optimization_manifest": str(self.manifest_path)
        }

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora Archive Optimizer")
    parser.add_argument("--repo-root", help="Repository root directory")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't extract")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    optimizer = ArchiveOptimizer(args.repo_root)
    
    if args.analyze_only:
        analyses = optimizer.analyze_zip_files()
        print(f"Analyzed {len(analyses)} archives")
        for zip_path, analysis in analyses:
            print(f"  {zip_path.name}: {analysis['size']} bytes, {len(analysis['contents'])} files")
    else:
        result = optimizer.optimize_archives()
        print("Archive optimization completed:")
        for key, value in result.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()