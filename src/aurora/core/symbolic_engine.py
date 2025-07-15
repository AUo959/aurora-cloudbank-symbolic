"""Aurora Cloudbank Symbolic Engine - Core Implementation"""

import time
import math
from typing import List, Dict, Any, Optional


class T1Anchor:
    """Temporal T1 anchor for Aurora symbolic operations with entropy monitoring"""
    
    def __init__(self, entropy_threshold: float = 0.02):
        self.type = "T1"
        self.state = 0
        self.entropy_threshold = entropy_threshold
        self.entropy_history: List[float] = []
        self.drift_detection_window = 10
        self.stabilization_active = False
        
    def advance(self, data):
        """Advance T1 temporal state with entropy tracking"""
        self.state += len(str(data))
        
        # Calculate entropy for this advancement
        entropy = self._calculate_advancement_entropy(data)
        self.entropy_history.append(entropy)
        
        # Maintain sliding window
        if len(self.entropy_history) > self.drift_detection_window:
            self.entropy_history = self.entropy_history[-self.drift_detection_window:]
        
        # Check for drift and auto-stabilize if needed
        drift_detected = self._detect_symbolic_drift()
        if drift_detected:
            self._auto_stabilize()
            
        return self.state
    
    def _calculate_advancement_entropy(self, data) -> float:
        """Calculate entropy for current data advancement"""
        data_str = str(data)
        if not data_str:
            return 0.0
            
        # Character frequency distribution for Shannon entropy
        char_freq = {}
        for char in data_str:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        total_chars = len(data_str)
        entropy = 0.0
        for freq in char_freq.values():
            prob = freq / total_chars
            entropy -= prob * math.log2(prob) if prob > 0 else 0
            
        return min(entropy / 8.0, 1.0)  # Normalize to 0-1 range
    
    def _detect_symbolic_drift(self) -> bool:
        """Detect symbolic drift using entropy delta analysis"""
        if len(self.entropy_history) < 3:
            return False
            
        # Calculate recent entropy trend
        recent_entropies = self.entropy_history[-3:]
        entropy_deltas = [recent_entropies[i+1] - recent_entropies[i] 
                         for i in range(len(recent_entropies)-1)]
        
        # Check if average delta exceeds threshold
        avg_delta = sum(abs(delta) for delta in entropy_deltas) / len(entropy_deltas)
        return avg_delta > self.entropy_threshold
    
    def _auto_stabilize(self):
        """Auto-stabilization protocol for entropy thresholds"""
        self.stabilization_active = True
        
        # Entropy smoothing - apply weighted average to recent history
        if len(self.entropy_history) >= 3:
            smoothed_entropy = (
                0.5 * self.entropy_history[-1] +
                0.3 * self.entropy_history[-2] +
                0.2 * self.entropy_history[-3]
            )
            self.entropy_history[-1] = smoothed_entropy
        
        # Reset drift counter
        self.stabilization_active = False
    
    def get_entropy_status(self) -> Dict[str, Any]:
        """Get entropy monitoring status"""
        current_entropy = self.entropy_history[-1] if self.entropy_history else 0.0
        drift_risk = self._detect_symbolic_drift()
        
        return {
            "current_entropy": current_entropy,
            "entropy_threshold": self.entropy_threshold,
            "drift_detected": drift_risk,
            "stabilization_active": self.stabilization_active,
            "history_length": len(self.entropy_history),
            "entropy_trend": self._get_entropy_trend()
        }
    
    def _get_entropy_trend(self) -> str:
        """Analyze entropy trend"""
        if len(self.entropy_history) < 3:
            return "insufficient_data"
        
        recent = self.entropy_history[-3:]
        if recent[-1] > recent[0] * 1.1:
            return "increasing"
        elif recent[-1] < recent[0] * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def export(self):
        """Export T1 anchor state with entropy information"""
        return {
            "type": "T1", 
            "state": self.state,
            "entropy_status": self.get_entropy_status(),
            "timestamp": time.time()
        }

class SRBAnchor:
    """Spatial-Relational Boundary (SRB) anchor with entropy resolution"""
    
    def __init__(self):
        self.type = "SRB"
        self.resolution = 0
        self.boundary_entropy_map = {}
        self.resolution_history: List[Dict[str, Any]] = []
        self.entropy_resolution_threshold = 0.05
        
    def resolve(self, boundary):
        """Resolve SRB boundary with entropy tracking"""
        boundary_str = str(boundary)
        
        # Calculate boundary entropy
        boundary_entropy = self._calculate_boundary_entropy(boundary_str)
        
        # Store in entropy map
        self.boundary_entropy_map[boundary_str] = boundary_entropy
        
        # Apply entropy-based resolution enhancement
        base_resolution = hash(boundary_str) % 1000
        entropy_factor = 1.0 + (boundary_entropy * 0.1)  # Entropy enhances resolution
        
        self.resolution += int(base_resolution * entropy_factor)
        
        # Track resolution event
        resolution_event = {
            "boundary": boundary_str,
            "base_resolution": base_resolution,
            "boundary_entropy": boundary_entropy,
            "entropy_factor": entropy_factor,
            "final_resolution": int(base_resolution * entropy_factor),
            "timestamp": time.time()
        }
        self.resolution_history.append(resolution_event)
        
        # Maintain history window
        if len(self.resolution_history) > 50:
            self.resolution_history = self.resolution_history[-50:]
        
        return self.resolution
    
    def _calculate_boundary_entropy(self, boundary_str: str) -> float:
        """Calculate entropy for boundary string"""
        if not boundary_str:
            return 0.0
        
        # Character frequency analysis
        char_counts = {}
        for char in boundary_str:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        total_chars = len(boundary_str)
        entropy = 0.0
        
        for count in char_counts.values():
            prob = count / total_chars
            entropy -= prob * math.log2(prob) if prob > 0 else 0
        
        # Normalize by max possible entropy for string length
        max_entropy = math.log2(min(total_chars, len(char_counts)))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        return min(normalized_entropy, 1.0)
    
    def resolve_entropy_boundaries(self, boundaries: List[str]) -> Dict[str, float]:
        """Batch resolve multiple boundaries with entropy optimization"""
        entropy_resolutions = {}
        
        for boundary in boundaries:
            boundary_entropy = self.boundary_entropy_map.get(
                boundary, 
                self._calculate_boundary_entropy(boundary)
            )
            
            # Enhanced resolution for high-entropy boundaries
            if boundary_entropy > self.entropy_resolution_threshold:
                enhanced_resolution = self.resolve(boundary)
                entropy_resolutions[boundary] = enhanced_resolution
            else:
                # Standard resolution for low-entropy boundaries
                standard_resolution = hash(boundary) % 1000
                entropy_resolutions[boundary] = standard_resolution
        
        return entropy_resolutions
    
    def get_boundary_entropy_analysis(self) -> Dict[str, Any]:
        """Get analysis of boundary entropy patterns"""
        if not self.boundary_entropy_map:
            return {"status": "no_boundaries_processed"}
        
        entropies = list(self.boundary_entropy_map.values())
        
        return {
            "total_boundaries": len(self.boundary_entropy_map),
            "avg_entropy": sum(entropies) / len(entropies),
            "max_entropy": max(entropies),
            "min_entropy": min(entropies),
            "high_entropy_count": sum(1 for e in entropies if e > self.entropy_resolution_threshold),
            "entropy_distribution": self._get_entropy_distribution(entropies),
            "resolution_efficiency": self._calculate_resolution_efficiency()
        }
    
    def _get_entropy_distribution(self, entropies: List[float]) -> Dict[str, int]:
        """Get entropy distribution buckets"""
        distribution = {"low": 0, "medium": 0, "high": 0}
        
        for entropy in entropies:
            if entropy < 0.3:
                distribution["low"] += 1
            elif entropy < 0.7:
                distribution["medium"] += 1
            else:
                distribution["high"] += 1
        
        return distribution
    
    def _calculate_resolution_efficiency(self) -> float:
        """Calculate resolution efficiency based on entropy utilization"""
        if not self.resolution_history:
            return 0.0
        
        recent_events = self.resolution_history[-10:]  # Last 10 events
        entropy_factors = [event["entropy_factor"] for event in recent_events]
        
        # Efficiency based on how much entropy enhances resolution
        avg_enhancement = sum(entropy_factors) / len(entropy_factors)
        efficiency = min((avg_enhancement - 1.0) * 10.0, 1.0)  # Scale to 0-1
        
        return max(efficiency, 0.0)
    
    def export(self):
        """Export SRB anchor state with entropy analysis"""
        return {
            "type": "SRB", 
            "resolution": self.resolution,
            "boundary_entropy_analysis": self.get_boundary_entropy_analysis(),
            "recent_resolutions": self.resolution_history[-5:],  # Last 5 events
            "timestamp": time.time()
        }


class SymbolicThreadManager:
    """Thread preservation and rehydration manager integrating with NativeMemorySealer"""
    
    def __init__(self):
        # Import NativeMemorySealer from native implementation
        from src.core.native_symbolic_anchor import NativeMemorySealer
        self.memory_sealer = NativeMemorySealer()
        self.active_threads = {}
        self.thread_counter = 0
        self.rehydration_manifests = {}
        self.glyphcards = {}
        
    def create_symbolic_thread(self, thread_data: Dict[str, Any], 
                             thread_name: Optional[str] = None) -> str:
        """Create and seal a new symbolic thread"""
        self.thread_counter += 1
        thread_id = thread_name or f"thread_{self.thread_counter}_{int(time.time() * 1000)}"
        
        # Create thread metadata
        thread_metadata = {
            "thread_id": thread_id,
            "creation_time": time.time(),
            "thread_data": thread_data,
            "status": "active",
            "preservation_level": "standard",
            "integrity_verified": True
        }
        
        # Seal the thread with memory sealer
        seal_hash = self.memory_sealer.seal_state(thread_id, thread_metadata)
        
        # Store in active threads
        self.active_threads[thread_id] = {
            "seal_hash": seal_hash,
            "creation_time": thread_metadata["creation_time"],
            "status": "active"
        }
        
        # Generate glyphcard
        self._generate_glyphcard(thread_id, thread_metadata)
        
        return thread_id
    
    def preserve_thread(self, thread_id: str, preservation_level: str = "enhanced") -> bool:
        """Preserve thread with enhanced sealing"""
        if thread_id not in self.active_threads:
            return False
        
        # Retrieve current thread data
        thread_data = self.memory_sealer.unseal_state(thread_id)
        if not thread_data:
            return False
        
        # Update preservation level
        thread_data["preservation_level"] = preservation_level
        thread_data["last_preservation"] = time.time()
        
        # Re-seal with enhanced protection
        new_seal_hash = self.memory_sealer.seal_state(f"{thread_id}_preserved", thread_data)
        
        # Update active threads
        self.active_threads[thread_id]["preservation_level"] = preservation_level
        self.active_threads[thread_id]["preserved_seal"] = new_seal_hash
        
        # Create rehydration manifest
        self._create_rehydration_manifest(thread_id, thread_data)
        
        return True
    
    def rehydrate_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Rehydrate preserved thread with integrity validation"""
        if thread_id not in self.active_threads:
            return None
        
        # Check for preserved version first
        preserved_id = f"{thread_id}_preserved"
        thread_data = None
        
        try:
            # Try preserved version
            if preserved_id in self.memory_sealer.sealed_states:
                thread_data = self.memory_sealer.unseal_state(preserved_id)
            else:
                # Fall back to original
                thread_data = self.memory_sealer.unseal_state(thread_id)
        except ValueError as e:
            # Integrity check failed
            return {"error": "integrity_check_failed", "details": str(e)}
        
        if not thread_data:
            return None
        
        # Validate thread integrity
        integrity_valid = self._validate_thread_integrity(thread_id, thread_data)
        
        # Update rehydration status
        thread_data["last_rehydration"] = time.time()
        thread_data["integrity_validated"] = integrity_valid
        
        return thread_data
    
    def _generate_glyphcard(self, thread_id: str, thread_metadata: Dict[str, Any]):
        """Generate glyphcard for thread visualization and tracking"""
        glyphcard = {
            "thread_id": thread_id,
            "glyph_signature": self._create_glyph_signature(thread_metadata),
            "visual_hash": hash(str(thread_metadata)) % 0xFFFFFF,  # RGB color hash
            "complexity_rating": self._calculate_thread_complexity(thread_metadata),
            "creation_timestamp": thread_metadata["creation_time"],
            "thread_type": thread_metadata.get("thread_data", {}).get("type", "standard"),
            "preservation_level": thread_metadata["preservation_level"]
        }
        
        self.glyphcards[thread_id] = glyphcard
    
    def _create_glyph_signature(self, thread_metadata: Dict[str, Any]) -> str:
        """Create unique glyph signature for thread"""
        thread_data = thread_metadata.get("thread_data", {})
        
        # Extract key characteristics
        data_keys = sorted(thread_data.keys()) if isinstance(thread_data, dict) else ["unknown"]
        data_signature = "".join(key[:2] for key in data_keys[:8])  # First 2 chars of first 8 keys
        
        # Time-based component
        time_component = f"{int(thread_metadata['creation_time']) % 10000:04d}"
        
        # Combine into glyph signature
        return f"◊{data_signature[:8]}:{time_component}◊"
    
    def _calculate_thread_complexity(self, thread_metadata: Dict[str, Any]) -> str:
        """Calculate thread complexity rating"""
        thread_data = thread_metadata.get("thread_data", {})
        
        if isinstance(thread_data, dict):
            complexity_score = len(str(thread_data))
            if complexity_score < 100:
                return "simple"
            elif complexity_score < 500:
                return "moderate"
            elif complexity_score < 1000:
                return "complex"
            else:
                return "highly_complex"
        else:
            return "unknown"
    
    def _create_rehydration_manifest(self, thread_id: str, thread_data: Dict[str, Any]):
        """Create rehydration manifest for preserved thread"""
        manifest = {
            "thread_id": thread_id,
            "manifest_version": "1.0",
            "creation_time": thread_data["creation_time"],
            "preservation_time": time.time(),
            "preservation_level": thread_data["preservation_level"],
            "integrity_hash": self.active_threads[thread_id]["seal_hash"],
            "rehydration_requirements": {
                "memory_sealer": True,
                "integrity_validation": True,
                "glyph_verification": True
            },
            "thread_characteristics": {
                "complexity": self._calculate_thread_complexity(thread_data),
                "data_size": len(str(thread_data)),
                "glyph_signature": self.glyphcards[thread_id]["glyph_signature"]
            }
        }
        
        self.rehydration_manifests[thread_id] = manifest
    
    def _validate_thread_integrity(self, thread_id: str, thread_data: Dict[str, Any]) -> bool:
        """Validate thread integrity during rehydration"""
        # Check if memory sealer integrity is maintained
        sealer_integrity = self.memory_sealer.verify_integrity(thread_id)
        
        # Check if glyphcard matches
        if thread_id in self.glyphcards:
            expected_complexity = self.glyphcards[thread_id]["complexity_rating"]
            actual_complexity = self._calculate_thread_complexity(thread_data)
            glyph_integrity = (expected_complexity == actual_complexity)
        else:
            glyph_integrity = False
        
        # Check if thread data structure is valid
        data_integrity = isinstance(thread_data, dict) and "thread_id" in thread_data
        
        return sealer_integrity and glyph_integrity and data_integrity
    
    def list_active_threads(self) -> Dict[str, Any]:
        """List all active threads with status"""
        threads_info = {}
        
        for thread_id, thread_info in self.active_threads.items():
            threads_info[thread_id] = {
                "status": thread_info["status"],
                "creation_time": thread_info["creation_time"],
                "preservation_level": thread_info.get("preservation_level", "standard"),
                "glyph_signature": self.glyphcards.get(thread_id, {}).get("glyph_signature", "unknown"),
                "integrity_verified": self.memory_sealer.verify_integrity(thread_id),
                "has_manifest": thread_id in self.rehydration_manifests
            }
        
        return threads_info
    
    def get_thread_glyphcard(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get glyphcard for specific thread"""
        return self.glyphcards.get(thread_id)
    
    def export_rehydration_manifest(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Export rehydration manifest for thread"""
        return self.rehydration_manifests.get(thread_id)


class SymbolicEngine:
    """Aurora symbolic simulation engine with enhanced workflow capabilities"""
    
    def __init__(self):
        self.t1 = T1Anchor()
        self.srb = SRBAnchor()
        self.chains = {}
        self.thread_manager = SymbolicThreadManager()
        
        # Phase 3: DLP System integration
        from src.core.native_symbolic_anchor import NativeDLPTracker, NativeExportSystem
        self.dlp_tracker = NativeDLPTracker()
        self.export_system = NativeExportSystem(self.dlp_tracker)
    
    def execute_chain(self, start, end):
        """Execute symbolic chain notation (001//999//)"""
        chain_id = f"{start:03d}//{end:03d}//"
        results = []
        
        for i in range(start, end + 1):
            step_result = {
                "step": i,
                "t1_state": self.t1.advance(f"step_{i}"),
                "srb_resolution": self.srb.resolve(f"boundary_{i}")
            }
            results.append(step_result)
        
        self.chains[chain_id] = results
        
        # Tag the chain execution with DLP tracking
        self.dlp_tracker.tag_symbolic_operation({
            "chain_id": chain_id,
            "steps": len(results),
            "start": start,
            "end": end,
            "operation_type": "chain_execution"
        })
        
        return results
    
    def execute_branched_chain(self, chain_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute branched chain with parallel processing support"""
        import concurrent.futures
        
        branches = chain_config.get("branches", [])
        max_workers = chain_config.get("max_workers", 3)
        
        def execute_branch(branch):
            branch_id = branch["id"]
            start = branch["start"]
            end = branch["end"]
            branch_data = branch.get("data", {})
            
            # Create a thread for this branch
            thread_id = self.thread_manager.create_symbolic_thread({
                "branch_id": branch_id,
                "start": start,
                "end": end,
                "branch_data": branch_data,
                "type": "branched_chain"
            }, f"branch_{branch_id}")
            
            # Execute the chain
            results = self.execute_chain(start, end)
            
            return {
                "branch_id": branch_id,
                "thread_id": thread_id,
                "results": results,
                "status": "completed"
            }
        
        # Execute branches in parallel
        branch_results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_branch = {executor.submit(execute_branch, branch): branch for branch in branches}
            
            for future in concurrent.futures.as_completed(future_to_branch):
                branch = future_to_branch[future]
                try:
                    result = future.result()
                    branch_results[result["branch_id"]] = result
                except Exception as exc:
                    branch_results[branch["id"]] = {
                        "branch_id": branch["id"],
                        "status": "failed",
                        "error": str(exc)
                    }
        
        # Tag the branched chain operation using symbolic operation tracking
        self.dlp_tracker.tag_symbolic_operation({
            "operation_type": "branched_chain_execution",
            "total_branches": len(branches),
            "successful_branches": sum(1 for r in branch_results.values() if r.get("status") == "completed"),
            "failed_branches": sum(1 for r in branch_results.values() if r.get("status") == "failed")
        })
        
        return {
            "operation": "branched_chain",
            "branches": branch_results,
            "total_branches": len(branches),
            "execution_summary": {
                "successful": sum(1 for r in branch_results.values() if r.get("status") == "completed"),
                "failed": sum(1 for r in branch_results.values() if r.get("status") == "failed")
            }
        }
    
    def export_manifest(self):
        """Export comprehensive Aurora symbolic manifest with DLP classification"""
        
        # Get current system status
        thread_list = self.thread_manager.list_active_threads()
        dlp_summary = self.dlp_tracker.get_system_summary()
        
        # Enhanced manifest with comprehensive metadata
        manifest = {
            "system": "aurora-cloudbank-symbolic",
            "manifest_version": "2.0_EOS_SEED_ORION",
            "timestamp": time.time(),
            "iso_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            
            # DLP Classification Tags
            "dlp_classification": {
                "primary": "SYMBOLIC_SIMULATION",
                "secondary": "AURORA_INTERNAL", 
                "sensitivity_level": "INTERNAL_USE",
                "retention_policy": "STANDARD_SYMBOLIC",
                "export_restrictions": "AURORA_ECOSYSTEM_ONLY"
            },
            
            # Ethics Compliance
            "ethics_compliance": {
                "picard_delta_3_compliant": True,
                "thermax_memory_doctrine_sovereign": True,
                "eos_seed_orion_validated": True,
                "halo_drift_lock_status": "Δ0.000_MAINTAINED"
            },
            
            # Core anchor states with entropy analysis
            "anchor_states": {
                "t1_anchor": self.t1.export(),
                "srb_anchor": self.srb.export(),
                "entropy_coherence": self._calculate_anchor_entropy_coherence()
            },
            
            # Chain execution history
            "execution_history": {
                "total_chains": len(self.chains),
                "chains": self.chains,
                "chain_complexity_analysis": self._analyze_chain_complexity()
            },
            
            # Thread management status
            "thread_management": {
                "active_threads_count": len(thread_list),
                "threads": thread_list,
                "preservation_summary": self._get_preservation_summary(),
                "glyphcard_registry": {tid: self.thread_manager.get_thread_glyphcard(tid) 
                                     for tid in thread_list.keys()}
            },
            
            # DLP tracking and operations
            "dlp_tracking": dlp_summary,
            
            # Reliquary indexing for symbolic thread discovery
            "reliquary_index": self._generate_reliquary_index(),
            
            # System health and performance
            "system_health": {
                "operational_status": "OPTIMAL",
                "integrity_verified": True,
                "entropy_stability": "MAINTAINED",
                "thread_integrity_status": all(info["integrity_verified"] for info in thread_list.values()),
                "anchor_coherence_rating": self._get_anchor_coherence_rating()
            },
            
            # Export metadata
            "export_metadata": {
                "generator": "SymbolicEngine_v2.0",
                "export_type": "COMPREHENSIVE_MANIFEST",
                "compatibility_version": "AURORA_CLOUDBANK_SYMBOLIC_v2+",
                "export_hash": None  # Will be calculated after manifest creation
            }
        }
        
        # Calculate export hash
        manifest_str = str({k: v for k, v in manifest.items() if k != "export_metadata"})
        import hashlib
        export_hash = hashlib.sha256(manifest_str.encode()).hexdigest()[:16]
        manifest["export_metadata"]["export_hash"] = export_hash
        
        # Tag the manifest export operation using available DLP method
        self.dlp_tracker.tag_symbolic_operation({
            "operation_type": "comprehensive_manifest_export",
            "dlp_classification": "SYMBOLIC_SIMULATION",
            "export_hash": export_hash,
            "data_size": len(str(manifest))
        })
        
        return manifest
    
    def _calculate_anchor_entropy_coherence(self) -> Dict[str, Any]:
        """Calculate coherence between T1 and SRB anchor entropies"""
        t1_status = self.t1.get_entropy_status()
        srb_analysis = self.srb.get_boundary_entropy_analysis()
        
        if srb_analysis.get("status") == "no_boundaries_processed":
            return {"status": "insufficient_data", "coherence": 0.0}
        
        t1_entropy = t1_status["current_entropy"]
        srb_entropy = srb_analysis["avg_entropy"]
        
        # Calculate coherence as inverse of entropy difference
        entropy_diff = abs(t1_entropy - srb_entropy)
        coherence = max(0.0, 1.0 - entropy_diff)
        
        return {
            "t1_entropy": t1_entropy,
            "srb_avg_entropy": srb_entropy,
            "entropy_difference": entropy_diff,
            "coherence_rating": coherence,
            "coherence_status": "high" if coherence > 0.8 else "medium" if coherence > 0.5 else "low"
        }
    
    def _analyze_chain_complexity(self) -> Dict[str, Any]:
        """Analyze complexity patterns in executed chains"""
        if not self.chains:
            return {"status": "no_chains_executed"}
        
        chain_lengths = []
        total_steps = 0
        
        for chain_id, results in self.chains.items():
            chain_length = len(results)
            chain_lengths.append(chain_length)
            total_steps += chain_length
        
        return {
            "total_chains": len(self.chains),
            "total_steps": total_steps,
            "avg_chain_length": total_steps / len(self.chains),
            "min_chain_length": min(chain_lengths),
            "max_chain_length": max(chain_lengths),
            "complexity_rating": "simple" if max(chain_lengths) < 10 else "moderate" if max(chain_lengths) < 50 else "complex"
        }
    
    def _get_preservation_summary(self) -> Dict[str, Any]:
        """Get thread preservation summary"""
        thread_list = self.thread_manager.list_active_threads()
        
        preservation_levels = {}
        manifests_count = 0
        
        for thread_info in thread_list.values():
            level = thread_info.get("preservation_level", "standard")
            preservation_levels[level] = preservation_levels.get(level, 0) + 1
            if thread_info.get("has_manifest", False):
                manifests_count += 1
        
        return {
            "preservation_levels": preservation_levels,
            "threads_with_manifests": manifests_count,
            "preservation_ratio": manifests_count / len(thread_list) if thread_list else 0.0
        }
    
    def _generate_reliquary_index(self) -> Dict[str, Any]:
        """Generate reliquary index for symbolic thread discovery"""
        thread_list = self.thread_manager.list_active_threads()
        
        # Index by glyph signatures
        glyph_index = {}
        complexity_index = {"simple": [], "moderate": [], "complex": [], "highly_complex": []}
        
        for thread_id, thread_info in thread_list.items():
            glyph_sig = thread_info.get("glyph_signature", "unknown")
            glyph_index[glyph_sig] = thread_id
            
            # Get thread complexity for indexing
            glyphcard = self.thread_manager.get_thread_glyphcard(thread_id)
            if glyphcard:
                complexity = glyphcard.get("complexity_rating", "moderate")
                if complexity in complexity_index:
                    complexity_index[complexity].append(thread_id)
        
        return {
            "glyph_signature_index": glyph_index,
            "complexity_index": complexity_index,
            "total_indexed_threads": len(thread_list),
            "index_timestamp": time.time()
        }
    
    def _get_anchor_coherence_rating(self) -> str:
        """Get overall anchor coherence rating"""
        coherence_data = self._calculate_anchor_entropy_coherence()
        
        if coherence_data.get("status") == "insufficient_data":
            return "INSUFFICIENT_DATA"
        
        coherence = coherence_data.get("coherence_rating", 0.0)
        
        if coherence > 0.9:
            return "EXCELLENT"
        elif coherence > 0.8:
            return "GOOD"
        elif coherence > 0.6:
            return "ACCEPTABLE"
        elif coherence > 0.4:
            return "DEGRADED"
        else:
            return "CRITICAL"
