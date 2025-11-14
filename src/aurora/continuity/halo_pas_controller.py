"""
HALO/PAS Drift Controller - Continuous Timeline Monitoring

Implements the HALO Continuity Graft and PAS drift-lock mechanisms for
continuous timeline monitoring across L1 (wall-clock), L2, and L3 simulation sources.

DLP: halo_pas_drift_controller_v1
Anchors: T1, SRB, EOS_SEED_ORION
Symbolic tags: HALO_PAS_DRIFT, CONTINUITY_MONITOR, TIMELINE_COHESION
"""

import asyncio
import logging
import time
from dataclasses import dataclass, asdict
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime, timezone

from src.core.native_dlp_export import NativeDLPTracker


@dataclass
class DriftSample:
    """Represents a single drift measurement across timeline layers"""

    timestamp: float  # L1 wall-clock time when sample was taken
    l1_time: float  # L1 (wall-clock) time value
    l2_time: float  # L2 (simulation) time value
    l3_time: float  # L3 (deep simulation) time value
    drift_l2: float  # L2 - L1 drift
    drift_l3: float  # L3 - L1 drift
    sample_id: int  # Sequential sample ID

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)


class HALOPASController:
    """
    HALO/PAS Drift Controller for continuous timeline monitoring.

    Periodically samples temporal state from L1 (wall-clock) and L2/L3 simulation
    sources, computes drift vectors, and emits structured DLP-tagged logs.

    Attributes:
        interval: Sampling interval in seconds (default 0.25s)
        l1_source: Callable returning L1 time (wall-clock)
        l2_source: Callable returning L2 time (simulation layer 2)
        l3_source: Callable returning L3 time (simulation layer 3)
    """

    def __init__(
        self,
        interval: float = 0.25,
        l1_source: Optional[Callable[[], float]] = None,
        l2_source: Optional[Callable[[], float]] = None,
        l3_source: Optional[Callable[[], float]] = None,
    ):
        """
        Initialize HALO/PAS Controller.

        Args:
            interval: Sampling interval in seconds (default 0.25)
            l1_source: Callable returning L1 time, defaults to time.time()
            l2_source: Callable returning L2 time, defaults to L1
            l3_source: Callable returning L3 time, defaults to L1
        """
        self.interval = interval
        self.l1_source = l1_source or time.time
        self.l2_source = l2_source or self.l1_source
        self.l3_source = l3_source or self.l1_source

        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._samples: List[DriftSample] = []
        self._sample_counter = 0
        self._max_samples = 1000  # Keep last 1000 samples in memory

        # DLP tracker for drift samples
        self._dlp_tracker = NativeDLPTracker()

        # Logger with drift channel
        self.logger = logging.getLogger("aurora.continuity.halo_pas")

        self.logger.info(
            "HALO/PAS Controller initialized",
            extra={
                "interval": interval,
                "anchor_protocols": ["EOS_SEED_ORION"],
                "t1_srb_anchors": ["T1", "SRB"],
                "symbolic_tags": ["HALO_PAS_DRIFT", "CONTINUITY_MONITOR", "TIMELINE_COHESION"],
            }
        )

    def _sample_drift(self) -> DriftSample:
        """
        Sample current drift across timeline layers.

        Returns:
            DriftSample with computed drift vectors
        """
        # Get current timestamp for this sample
        timestamp = time.time()

        # Sample each timeline layer
        l1_time = self.l1_source()
        l2_time = self.l2_source()
        l3_time = self.l3_source()

        # Compute drift vectors relative to L1
        drift_l2 = l2_time - l1_time
        drift_l3 = l3_time - l1_time

        # Increment sample counter
        self._sample_counter += 1

        # Create drift sample
        sample = DriftSample(
            timestamp=timestamp,
            l1_time=l1_time,
            l2_time=l2_time,
            l3_time=l3_time,
            drift_l2=drift_l2,
            drift_l3=drift_l3,
            sample_id=self._sample_counter,
        )

        return sample

    def _create_dlp_tag(self, sample: DriftSample) -> str:
        """
        Create DLP tag for drift sample with Aurora anchors.

        Args:
            sample: Drift sample to tag

        Returns:
            Tag ID for the created DLP tag
        """
        # Create DLP tag for this drift sample
        tag_id = self._dlp_tracker.create_tag(
            operation="halo_pas_drift_sample",
            data=sample.to_dict(),
            tag_id=f"drift::sample::{sample.sample_id:06d}"
        )

        tag = self._dlp_tracker.tags[tag_id]

        # Add Aurora anchor protocols
        tag.add_anchor_protocol("EOS_SEED_ORION")

        # Add T1/SRB anchors
        tag.add_t1_srb_anchor("T1")
        tag.add_t1_srb_anchor("SRB")

        # Add symbolic patterns with drift vectors
        tag.set_symbolic_pattern("drift_vector", {
            "drift_l2": sample.drift_l2,
            "drift_l3": sample.drift_l3,
        })

        # Add metadata
        tag.metadata.update({
            "sample_id": sample.sample_id,
            "timestamp": sample.timestamp,
            "l1_time": sample.l1_time,
            "l2_time": sample.l2_time,
            "l3_time": sample.l3_time,
            "symbolic_tags": ["HALO_PAS_DRIFT", "CONTINUITY_MONITOR", "TIMELINE_COHESION"],
        })

        return tag_id

    def _log_drift_sample(self, sample: DriftSample, tag_id: str):
        """
        Emit structured log for drift sample.

        Args:
            sample: Drift sample to log
            tag_id: DLP tag ID for this sample
        """
        self.logger.info(
            "HALO/PAS drift sample",
            extra={
                "sample_id": sample.sample_id,
                "drift_l2": sample.drift_l2,
                "drift_l3": sample.drift_l3,
                "timestamp": sample.timestamp,
                "dlp_tag": tag_id,
                "anchor_protocols": ["EOS_SEED_ORION"],
                "t1_srb_anchors": ["T1", "SRB"],
                "symbolic_tags": ["HALO_PAS_DRIFT", "CONTINUITY_MONITOR"],
            }
        )

    async def _drift_loop(self):
        """Background loop for drift sampling"""
        self.logger.info("HALO/PAS drift monitoring started")

        try:
            while self._running:
                # Sample drift
                sample = self._sample_drift()

                # Store sample (keep only last N samples)
                self._samples.append(sample)
                if len(self._samples) > self._max_samples:
                    self._samples.pop(0)

                # Create DLP tag
                tag_id = self._create_dlp_tag(sample)

                # Log sample
                self._log_drift_sample(sample, tag_id)

                # Sleep for interval
                await asyncio.sleep(self.interval)

        except asyncio.CancelledError:
            self.logger.info("HALO/PAS drift monitoring cancelled")
            raise
        except Exception as e:
            self.logger.error(
                f"HALO/PAS drift monitoring error: {e}",
                extra={"error": str(e)}
            )
            raise

    async def start(self):
        """Start the drift monitoring loop"""
        if self._running:
            self.logger.warning("HALO/PAS controller already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._drift_loop())
        self.logger.info("HALO/PAS controller started")

    async def stop(self):
        """Stop the drift monitoring loop"""
        if not self._running:
            return

        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        self.logger.info("HALO/PAS controller stopped")

    def export_status(self) -> Dict[str, Any]:
        """
        Export current status as JSON-serializable dictionary.

        Returns:
            Status dictionary with drift statistics and recent samples
        """
        # Compute statistics if we have samples
        if self._samples:
            recent_samples = self._samples[-10:]  # Last 10 samples
            avg_drift_l2 = sum(s.drift_l2 for s in self._samples) / len(self._samples)
            avg_drift_l3 = sum(s.drift_l3 for s in self._samples) / len(self._samples)
            max_drift_l2 = max(abs(s.drift_l2) for s in self._samples)
            max_drift_l3 = max(abs(s.drift_l3) for s in self._samples)
            last_sample = self._samples[-1].to_dict()
        else:
            recent_samples = []
            avg_drift_l2 = 0.0
            avg_drift_l3 = 0.0
            max_drift_l2 = 0.0
            max_drift_l3 = 0.0
            last_sample = None

        return {
            "status": "running" if self._running else "stopped",
            "interval": self.interval,
            "total_samples": self._sample_counter,
            "samples_in_memory": len(self._samples),
            "statistics": {
                "avg_drift_l2": avg_drift_l2,
                "avg_drift_l3": avg_drift_l3,
                "max_drift_l2": max_drift_l2,
                "max_drift_l3": max_drift_l3,
            },
            "last_sample": last_sample,
            "recent_samples": [s.to_dict() for s in recent_samples],
            "anchor_protocols": ["EOS_SEED_ORION"],
            "t1_srb_anchors": ["T1", "SRB"],
            "symbolic_tags": ["HALO_PAS_DRIFT", "CONTINUITY_MONITOR", "TIMELINE_COHESION"],
            "dlp_tag": "halo_pas_drift_controller_v1",
            "export_time": datetime.now(timezone.utc).isoformat(),
        }
