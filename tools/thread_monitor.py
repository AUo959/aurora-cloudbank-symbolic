#!/usr/bin/env python3
"""
Aurora/GUMAS Thread Monitor
Real-time state tracking and analysis
Operator: AUo959
"""

import json
import time
import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
import signal

@dataclass
class ThreadState:
    thread_id: str
    state: str
    last_activity: datetime
    operator_id: str
    classification: str
    lineage: List[str]
    dependencies: List[str]
    metadata: Dict[str, Any]

@dataclass
class MonitoringStats:
    total_threads: int
    active_threads: int
    sealed_threads: int
    pending_closure: int
    violations: int
    last_update: datetime

class ThreadMonitor:
    def __init__(self, reliquary_id: str = "main"):
        self.operator_id = "AUo959"
        self.reliquary_id = reliquary_id
        self.monitoring = False
        self.threads: Dict[str, ThreadState] = {}
        self.stats = MonitoringStats(0, 0, 0, 0, 0, datetime.utcnow())
        
    def start_monitoring(self, interval: int = 60, continuous: bool = True):
        """Start thread monitoring with specified interval."""
        print(f"[INFO] Starting Aurora/GUMAS Thread Monitor")
        print(f"[INFO] Operator: {self.operator_id}")
        print(f"[INFO] Reliquary: {self.reliquary_id}")
        print(f"[INFO] Interval: {interval} seconds")
        
        self.monitoring = True
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.monitoring:
                self._monitor_cycle()
                
                if not continuous:
                    break
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\\n[INFO] Monitoring interrupted by user")
        finally:
            self._cleanup()
    
    def _monitor_cycle(self):
        """Execute a single monitoring cycle."""
        cycle_start = datetime.utcnow()
        print(f"[INFO] Monitoring cycle started: {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Discover threads
        threads = self._discover_threads()
        
        # Analyze thread states
        self._analyze_threads(threads)
        
        # Check for violations
        violations = self._check_violations()
        
        # Update statistics
        self._update_statistics(threads, violations)
        
        # Generate alerts if needed
        self._process_alerts(violations)
        
        cycle_end = datetime.utcnow()
        duration = (cycle_end - cycle_start).total_seconds()
        
        print(f"[INFO] Monitoring cycle completed in {duration:.2f}s")
        self._print_status_summary()
    
    def _discover_threads(self) -> List[ThreadState]:
        """Discover active and archived threads."""
        threads = []
        
        # In a real implementation, this would query the actual system
        # For demonstration, we'll create mock thread data
        
        mock_threads = [
            {
                "thread_id": "thread_001_active",
                "state": "active",
                "last_activity": datetime.utcnow() - timedelta(minutes=5),
                "classification": "internal",
                "lineage": ["genesis_001", "parent_001"],
                "dependencies": ["thread_002_ref"],
                "metadata": {"purpose": "aurora_enhancement", "priority": "high"}
            },
            {
                "thread_id": "thread_002_idle", 
                "state": "idle",
                "last_activity": datetime.utcnow() - timedelta(hours=2),
                "classification": "restricted",
                "lineage": ["genesis_002"],
                "dependencies": [],
                "metadata": {"purpose": "symbolic_simulation", "priority": "medium"}
            },
            {
                "thread_id": "thread_003_sealed",
                "state": "sealed", 
                "last_activity": datetime.utcnow() - timedelta(days=1),
                "classification": "confidential",
                "lineage": ["genesis_003", "parent_003", "evolved_003"],
                "dependencies": ["thread_001_active"],
                "metadata": {"purpose": "security_testing", "priority": "critical"}
            }
        ]
        
        for thread_data in mock_threads:
            thread = ThreadState(
                thread_id=thread_data["thread_id"],
                state=thread_data["state"],
                last_activity=thread_data["last_activity"],
                operator_id=self.operator_id,
                classification=thread_data["classification"],
                lineage=thread_data["lineage"],
                dependencies=thread_data["dependencies"],
                metadata=thread_data["metadata"]
            )
            threads.append(thread)
            
        return threads
    
    def _analyze_threads(self, threads: List[ThreadState]):
        """Analyze thread states and update internal tracking."""
        self.threads.clear()
        
        for thread in threads:
            self.threads[thread.thread_id] = thread
            
            # Analyze thread health
            idle_time = datetime.utcnow() - thread.last_activity
            
            if thread.state == "active" and idle_time > timedelta(hours=1):
                print(f"[WARN] Thread {thread.thread_id} has been idle for {idle_time}")
                
            if thread.state == "sealed" and not thread.dependencies:
                print(f"[INFO] Sealed thread {thread.thread_id} has no dependencies")
    
    def _check_violations(self) -> List[Dict[str, Any]]:
        """Check for policy violations and compliance issues."""
        violations = []
        
        for thread_id, thread in self.threads.items():
            # Check for stale threads
            idle_time = datetime.utcnow() - thread.last_activity
            if thread.state == "active" and idle_time > timedelta(hours=24):
                violations.append({
                    "type": "stale_thread",
                    "severity": "medium",
                    "thread_id": thread_id,
                    "description": f"Thread idle for {idle_time}",
                    "recommended_action": "consider_sealing"
                })
            
            # Check for broken lineage
            if len(thread.lineage) == 0:
                violations.append({
                    "type": "broken_lineage",
                    "severity": "high", 
                    "thread_id": thread_id,
                    "description": "Thread has no lineage information",
                    "recommended_action": "investigate_ancestry"
                })
            
            # Check for missing classification
            if not thread.classification or thread.classification == "unknown":
                violations.append({
                    "type": "missing_classification",
                    "severity": "medium",
                    "thread_id": thread_id,
                    "description": "Thread lacks proper DLP classification",
                    "recommended_action": "apply_classification"
                })
            
            # Check operator traceability
            if thread.operator_id != self.operator_id:
                violations.append({
                    "type": "operator_mismatch",
                    "severity": "critical",
                    "thread_id": thread_id,
                    "description": f"Thread not traceable to {self.operator_id}",
                    "recommended_action": "investigate_ownership"
                })
        
        return violations
    
    def _update_statistics(self, threads: List[ThreadState], violations: List[Dict[str, Any]]):
        """Update monitoring statistics."""
        active_count = sum(1 for t in threads if t.state == "active")
        sealed_count = sum(1 for t in threads if t.state == "sealed")
        idle_count = sum(1 for t in threads if t.state == "idle")
        
        # Threads pending closure (idle > 30 minutes)
        pending_closure = sum(
            1 for t in threads 
            if t.state == "idle" and (datetime.utcnow() - t.last_activity) > timedelta(minutes=30)
        )
        
        self.stats = MonitoringStats(
            total_threads=len(threads),
            active_threads=active_count,
            sealed_threads=sealed_count,
            pending_closure=pending_closure,
            violations=len(violations),
            last_update=datetime.utcnow()
        )
    
    def _process_alerts(self, violations: List[Dict[str, Any]]):
        """Process and alert on violations."""
        critical_violations = [v for v in violations if v["severity"] == "critical"]
        high_violations = [v for v in violations if v["severity"] == "high"]
        
        if critical_violations:
            print(f"[ALERT] {len(critical_violations)} CRITICAL violations detected!")
            for violation in critical_violations:
                print(f"  - {violation['thread_id']}: {violation['description']}")
        
        if high_violations:
            print(f"[WARN] {len(high_violations)} HIGH severity violations detected")
            for violation in high_violations:
                print(f"  - {violation['thread_id']}: {violation['description']}")
    
    def _print_status_summary(self):
        """Print current monitoring status."""
        print(f"\\n=== Thread Monitor Status ===")
        print(f"Operator: {self.operator_id}")
        print(f"Reliquary: {self.reliquary_id}")
        print(f"Last Update: {self.stats.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Threads: {self.stats.total_threads}")
        print(f"Active: {self.stats.active_threads}")
        print(f"Sealed: {self.stats.sealed_threads}")
        print(f"Pending Closure: {self.stats.pending_closure}")
        print(f"Violations: {self.stats.violations}")
        print("=" * 30)
    
    def get_thread_status(self, thread_id: str) -> Optional[ThreadState]:
        """Get status of specific thread."""
        return self.threads.get(thread_id)
    
    def export_status_report(self, output_file: str):
        """Export detailed status report."""
        report = {
            "monitor_info": {
                "operator_id": self.operator_id,
                "reliquary_id": self.reliquary_id,
                "generated_at": datetime.utcnow().isoformat() + "Z"
            },
            "statistics": asdict(self.stats),
            "threads": {tid: asdict(thread) for tid, thread in self.threads.items()},
            "compliance": {
                "aurora_standards": "2024.1",
                "gumas_compliant": self.stats.violations == 0,
                "operator_traceability": True
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"[INFO] Status report exported: {output_file}")
    
    def verify_continuity(self) -> bool:
        """Verify symbolic continuity across all threads."""
        print(f"[INFO] Verifying symbolic continuity...")
        
        continuity_issues = []
        
        for thread_id, thread in self.threads.items():
            # Check lineage integrity
            if not thread.lineage:
                continuity_issues.append(f"Thread {thread_id}: Missing lineage")
                continue
            
            # Check dependency resolution
            for dep_id in thread.dependencies:
                if dep_id not in self.threads:
                    continuity_issues.append(f"Thread {thread_id}: Unresolved dependency {dep_id}")
        
        if continuity_issues:
            print(f"[ERROR] Continuity verification failed:")
            for issue in continuity_issues:
                print(f"  - {issue}")
            return False
        else:
            print(f"[INFO] Symbolic continuity verified successfully")
            return True
    
    def rebuild_lineage(self) -> bool:
        """Attempt to rebuild broken lineage chains."""
        print(f"[INFO] Rebuilding lineage chains...")
        
        # In a real implementation, this would query the reliquary system
        # and reconstruct lineage from available data
        
        rebuilt_count = 0
        for thread_id, thread in self.threads.items():
            if not thread.lineage:
                # Attempt reconstruction
                reconstructed_lineage = self._reconstruct_lineage(thread_id)
                if reconstructed_lineage:
                    thread.lineage = reconstructed_lineage
                    rebuilt_count += 1
                    print(f"[INFO] Rebuilt lineage for {thread_id}")
        
        print(f"[INFO] Rebuilt lineage for {rebuilt_count} threads")
        return rebuilt_count > 0
    
    def _reconstruct_lineage(self, thread_id: str) -> List[str]:
        """Attempt to reconstruct lineage for a thread."""
        # Mock reconstruction logic
        if "001" in thread_id:
            return ["genesis_001", thread_id]
        elif "002" in thread_id:
            return ["genesis_002", "parent_002", thread_id]
        else:
            return ["genesis_unknown", thread_id]
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\\n[INFO] Received signal {signum}, shutting down...")
        self.monitoring = False
    
    def _cleanup(self):
        """Cleanup resources and save final state."""
        print(f"[INFO] Thread monitor shutting down")
        print(f"[INFO] Final statistics: {self.stats.total_threads} threads monitored")
        
        # Save final state
        final_report = f"thread_monitor_final_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self.export_status_report(final_report)

def main():
    parser = argparse.ArgumentParser(description="Aurora/GUMAS Thread Monitor")
    parser.add_argument("--reliquary", default="main", help="Reliquary ID to monitor")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run once instead of continuously")
    parser.add_argument("--status", action="store_true", help="Show current status only")
    parser.add_argument("--verify-continuity", action="store_true", help="Verify symbolic continuity")
    parser.add_argument("--rebuild-lineage", action="store_true", help="Rebuild broken lineage chains")
    parser.add_argument("--export", help="Export status report to file")
    parser.add_argument("--thread-id", help="Show status for specific thread")
    
    args = parser.parse_args()
    
    monitor = ThreadMonitor(args.reliquary)
    
    try:
        if args.thread_id:
            # Show specific thread status
            monitor._monitor_cycle()  # Refresh data
            thread = monitor.get_thread_status(args.thread_id)
            if thread:
                print(f"Thread Status: {args.thread_id}")
                print(f"State: {thread.state}")
                print(f"Last Activity: {thread.last_activity}")
                print(f"Classification: {thread.classification}")
                print(f"Lineage: {' → '.join(thread.lineage)}")
                print(f"Dependencies: {', '.join(thread.dependencies) if thread.dependencies else 'None'}")
            else:
                print(f"Thread not found: {args.thread_id}")
                
        elif args.status:
            # Show status summary
            monitor._monitor_cycle()
            monitor._print_status_summary()
            
        elif args.verify_continuity:
            # Verify continuity
            monitor._monitor_cycle()
            is_valid = monitor.verify_continuity()
            sys.exit(0 if is_valid else 1)
            
        elif args.rebuild_lineage:
            # Rebuild lineage
            monitor._monitor_cycle()
            success = monitor.rebuild_lineage()
            sys.exit(0 if success else 1)
            
        elif args.export:
            # Export report
            monitor._monitor_cycle()
            monitor.export_status_report(args.export)
            
        else:
            # Start monitoring
            continuous = not args.once
            monitor.start_monitoring(args.interval, continuous)
            
    except Exception as e:
        print(f"[ERROR] Monitor failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()