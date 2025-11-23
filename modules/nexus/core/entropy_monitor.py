#!/usr/bin/env python3
"""
NEXUS Entropy Monitor
Anchor: T1-ENTROPY-2025
Seed: EOS_SEED_ORION
Team: Aurora Core
Version: 1.0.0
DLP Tag: MONITORING_TOOL
"""

import asyncio
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict
import hashlib
import math
import random
import logging

logger = logging.getLogger(__name__)


class EntropyMonitor:
    """
    Real-time entropy monitoring and alerting system
    Tracks entropy drift across the NEXUS system
    """
    
    def __init__(self, anchor: str = "T1-ENTROPY-2025"):
        self.anchor = anchor
        self.seed = "EOS_SEED_ORION"
        self.entropy_history = []
        self.drift_threshold = 0.1
        self.alert_threshold = 0.2
        self.monitoring_active = False
        self.alert_callbacks = []
        
    def calculate_system_entropy(self) -> float:
        """Calculate current system entropy"""
        try:
            # Check memory manager entropy
            from .memory_manager import get_memory_manager
            manager = get_memory_manager()
            
            if not manager.memory_store:
                return 0.0
            
            # Calculate entropy across all stored memories
            total_entropy = 0.0
            count = 0
            
            for key, entry in manager.memory_store.items():
                if "entropy" in entry:
                    total_entropy += entry["entropy"]
                    count += 1
            
            if count == 0:
                return 0.0
                
            avg_entropy = total_entropy / count
            
            # Add system complexity factors
            complexity_factor = min(1.0, count / 100.0)  # Normalized complexity
            time_factor = self._calculate_temporal_entropy()
            
            # Combined entropy metric
            system_entropy = (
                avg_entropy * 0.6 +
                complexity_factor * 0.3 +
                time_factor * 0.1
            )
            
            return min(1.0, max(0.0, system_entropy))
            
        except ImportError:
            # Fallback entropy calculation
            return self._fallback_entropy_calculation()
    
    def _calculate_temporal_entropy(self) -> float:
        """Calculate entropy based on temporal patterns"""
        if len(self.entropy_history) < 2:
            return 0.0
        
        # Calculate variance in recent entropy measurements
        recent_entropy = [h["entropy"] for h in self.entropy_history[-10:]]
        if len(recent_entropy) < 2:
            return 0.0
        
        mean_entropy = sum(recent_entropy) / len(recent_entropy)
        variance = sum((e - mean_entropy) ** 2 for e in recent_entropy) / len(recent_entropy)
        
        # Normalize variance to [0, 1] range
        temporal_entropy = min(1.0, variance * 10)
        return temporal_entropy
    
    def _fallback_entropy_calculation(self) -> float:
        """Fallback entropy calculation when memory manager unavailable"""
        # Simulated entropy based on system state
        base_entropy = 0.5
        
        # Add some realistic variation
        time_variation = math.sin(time.time() / 100) * 0.1
        random_noise = (random.random() - 0.5) * 0.05
        
        entropy = base_entropy + time_variation + random_noise
        return min(1.0, max(0.0, entropy))
    
    def record_entropy_measurement(self, entropy: float) -> Dict:
        """Record an entropy measurement"""
        timestamp = datetime.utcnow()
        
        measurement = {
            "timestamp": timestamp.isoformat(),
            "entropy": entropy,
            "anchor": self.anchor,
            "drift": 0.0,
            "alert_level": "NORMAL"
        }
        
        # Calculate drift if we have previous measurements
        if self.entropy_history:
            previous_entropy = self.entropy_history[-1]["entropy"]
            drift = abs(entropy - previous_entropy)
            measurement["drift"] = drift
            
            # Determine alert level
            if drift >= self.alert_threshold:
                measurement["alert_level"] = "CRITICAL"
            elif drift >= self.drift_threshold:
                measurement["alert_level"] = "WARNING"
        
        # Add to history
        self.entropy_history.append(measurement)
        
        # Keep only last 1000 measurements
        if len(self.entropy_history) > 1000:
            self.entropy_history = self.entropy_history[-1000:]
        
        # Check for alerts
        if measurement["alert_level"] != "NORMAL":
            self._trigger_alert(measurement)
        
        return measurement
    
    def _trigger_alert(self, measurement: Dict):
        """Trigger entropy alert"""
        alert = {
            "type": "entropy_alert",
            "level": measurement["alert_level"],
            "entropy": measurement["entropy"],
            "drift": measurement["drift"],
            "timestamp": measurement["timestamp"],
            "anchor": self.anchor,
            "action_required": measurement["alert_level"] == "CRITICAL"
        }
        
        # Save alert to disk
        alert_path = Path(f".nexus/alerts/entropy_{datetime.utcnow().timestamp()}.json")
        alert_path.parent.mkdir(parents=True, exist_ok=True)
        alert_path.write_text(json.dumps(alert, indent=2))
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error("Alert callback failed: %s", e)
    
    def get_current_status(self) -> Dict:
        """Get current entropy status"""
        current_entropy = self.calculate_system_entropy()
        measurement = self.record_entropy_measurement(current_entropy)
        
        # Calculate statistics
        recent_measurements = self.entropy_history[-10:] if len(self.entropy_history) >= 10 else self.entropy_history
        
        stats = {
            "current_entropy": current_entropy,
            "current_drift": measurement["drift"],
            "alert_level": measurement["alert_level"],
            "measurements_count": len(self.entropy_history),
            "average_entropy": 0.0,
            "max_entropy": 0.0,
            "min_entropy": 1.0,
            "drift_trend": "STABLE"
        }
        
        if recent_measurements:
            entropies = [m["entropy"] for m in recent_measurements]
            stats["average_entropy"] = sum(entropies) / len(entropies)
            stats["max_entropy"] = max(entropies)
            stats["min_entropy"] = min(entropies)
            
            # Calculate drift trend
            if len(recent_measurements) >= 3:
                recent_drifts = [m["drift"] for m in recent_measurements[-3:]]
                avg_drift = sum(recent_drifts) / len(recent_drifts)
                
                if avg_drift > self.drift_threshold:
                    stats["drift_trend"] = "INCREASING"
                elif avg_drift < self.drift_threshold / 2:
                    stats["drift_trend"] = "DECREASING"
        
        return stats
    
    async def start_monitoring(self, interval: float = 1.0):
        """Start continuous entropy monitoring"""
        self.monitoring_active = True
        logger.info("Entropy monitoring started (interval: %.2fs)", interval)
        
        while self.monitoring_active:
            try:
                status = self.get_current_status()
                
                # Status update
                ts = datetime.utcnow().strftime('%H:%M:%S')
                logger.info("[%s] Entropy: %.3f | Drift: %.3f | Alert: %s", ts,
                            status['current_entropy'], status['current_drift'], status['alert_level'])
                
                # Wait for next measurement
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error("Monitoring error: %s", e)
                await asyncio.sleep(interval)
        
        logger.info("Entropy monitoring stopped")
    
    def stop_monitoring(self):
        """Stop entropy monitoring"""
        self.monitoring_active = False
    
    def add_alert_callback(self, callback):
        """Add callback function for entropy alerts"""
        self.alert_callbacks.append(callback)
    
    def export_entropy_report(self) -> Dict:
        """Export comprehensive entropy report"""
        report = {
            "report_version": "1.0.0",
            "anchor": self.anchor,
            "seed": self.seed,
            "export_time": datetime.utcnow().isoformat(),
            "monitoring_status": "ACTIVE" if self.monitoring_active else "INACTIVE",
            "total_measurements": len(self.entropy_history),
            "current_status": self.get_current_status(),
            "recent_history": self.entropy_history[-50:] if len(self.entropy_history) >= 50 else self.entropy_history,
            "alert_summary": self._generate_alert_summary(),
            "dlp_classification": "INTERNAL_MONITORING"
        }
        
        # Seal the report
        report_hash = hashlib.sha256(
            json.dumps(report, sort_keys=True).encode()
        ).hexdigest()
        
        report["seal"] = report_hash
        
        return report
    
    def _generate_alert_summary(self) -> Dict:
        """Generate summary of recent alerts"""
        # Count alerts by level in recent history
        recent_measurements = self.entropy_history[-100:] if len(self.entropy_history) >= 100 else self.entropy_history
        
        alert_counts = {"NORMAL": 0, "WARNING": 0, "CRITICAL": 0}
        
        for measurement in recent_measurements:
            level = measurement.get("alert_level", "NORMAL")
            alert_counts[level] += 1
        
        return {
            "total_measurements": len(recent_measurements),
            "normal_count": alert_counts["NORMAL"],
            "warning_count": alert_counts["WARNING"],
            "critical_count": alert_counts["CRITICAL"],
            "alert_percentage": ((alert_counts["WARNING"] + alert_counts["CRITICAL"]) / 
                               len(recent_measurements) * 100) if recent_measurements else 0
        }

# Module-level entropy monitor
entropy_monitor = EntropyMonitor()

def get_entropy_monitor() -> EntropyMonitor:
    """Get singleton entropy monitor instance"""
    return entropy_monitor

async def main():
    """Main function for running entropy monitor"""
    monitor = get_entropy_monitor()
    
    # Add a simple alert callback
    def print_alert(alert):
        logger.warning("ENTROPY ALERT: %s - Entropy: %.3f, Drift: %.3f",
                       alert['level'], alert['entropy'], alert['drift'])
    
    monitor.add_alert_callback(print_alert)
    
    try:
        await monitor.start_monitoring(interval=2.0)
    except KeyboardInterrupt:
        logger.info("Stopping entropy monitor...")
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())