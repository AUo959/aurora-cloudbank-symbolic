"""
T1-EDG-INTEGRATION - Data Guardian Integration Layer
Integrates PII detection/redaction with Aurora's DLP tracking and export systems.

Chain: #005//004/EDG
Anchor: T1-EDG-004
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib

# Add src to path for DLP imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from core.native_dlp_export import NativeDLPTracker, NativeDLPTag
except ImportError:
    # Fallback if src path not available
    NativeDLPTracker = None
    NativeDLPTag = None

from modules.data_guardian.detection_rules import PIIDetector
from modules.data_guardian.redaction import RedactionEngine, RedactionStrategy


class DataGuardianDLPIntegration:
    """
    Integrates Data Guardian with Aurora's native DLP tracking system.
    Provides PII detection/redaction with full data lineage tracking.
    """

    def __init__(self, region: str = "US", context_tag: str = "data-guardian"):
        """
        Initialize integration layer.

        Args:
            region: Region for PII detection rules
            context_tag: DLP context tag for tracking
        """
        self.detector = PIIDetector(region=region)
        self.redactor = RedactionEngine()
        self.context_tag = context_tag
        self.region = region

        # Initialize DLP tracker if available
        if NativeDLPTracker:
            self.dlp_tracker = NativeDLPTracker()
        else:
            self.dlp_tracker = None

    def scan_with_tracking(
        self,
        data: Any,
        min_confidence: float = 0.7,
        operation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Scan data for PII with DLP tracking.

        Args:
            data: Data to scan (str or dict)
            min_confidence: Minimum confidence threshold
            operation_id: Optional operation identifier

        Returns:
            Dict with detections and DLP tag information
        """
        # Generate operation ID
        if not operation_id:
            timestamp = datetime.now().isoformat()
            operation_id = f"pii-scan-{hashlib.sha256(timestamp.encode()).hexdigest()[:8]}"

        # Detect PII
        if isinstance(data, dict):
            detections = self.detector.scan_dict(data)
            data_str = str(data)
        else:
            detections = self.detector.detect(data, min_confidence)
            data_str = data

        # Calculate data hash
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()

        # Track with DLP if available
        dlp_tag_id = None
        if self.dlp_tracker and NativeDLPTag:
            # Create DLP tag
            dlp_tag = NativeDLPTag(
                tag_id=f"{self.context_tag}-{operation_id}",
                operation="pii_detection",
                data_hash=data_hash,
            )

            # Add T1-EDG anchor
            dlp_tag.add_t1_srb_anchor("T1-EDG-004")

            # Add detection metadata
            if isinstance(detections, list):
                detection_count = len(detections)
                pii_types = list(set(d['type'] for d in detections))
            else:
                # Dict structure from scan_dict
                detection_count = self._count_nested_detections(detections)
                pii_types = self._extract_pii_types(detections)

            dlp_tag.metadata.update({
                "detection_count": detection_count,
                "pii_types": pii_types,
                "confidence_threshold": min_confidence,
                "region": self.region,
                "data_size": len(data_str),
            })

            # Register with tracker
            tag_id = self.dlp_tracker.create_tag(
                operation="pii_detection",
                data=data_str,
                tag_id=f"{self.context_tag}-{operation_id}"
            )

            # Add metadata to tag
            tag = self.dlp_tracker.tags.get(tag_id)
            if tag:
                tag.add_t1_srb_anchor("T1-EDG-004")
                tag.metadata.update({
                    "detection_count": detection_count,
                    "pii_types": pii_types,
                    "confidence_threshold": min_confidence,
                    "region": self.region,
                    "data_size": len(data_str),
                })

            dlp_tag_id = tag_id

        return {
            "operation_id": operation_id,
            "detections": detections,
            "data_hash": data_hash,
            "dlp_tag_id": dlp_tag_id,
            "timestamp": datetime.now().isoformat(),
            "region": self.region,
        }

    def redact_with_tracking(
        self,
        data: Any,
        strategy: RedactionStrategy = RedactionStrategy.MASK,
        min_confidence: float = 0.7,
        operation_id: Optional[str] = None,
        scan_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Redact PII from data with DLP tracking.

        Args:
            data: Data to redact (str or dict)
            strategy: Redaction strategy to use
            min_confidence: Minimum confidence threshold
            operation_id: Optional operation identifier
            scan_result: Optional previous scan result (reuses detections)

        Returns:
            Dict with redacted data and DLP tag information
        """
        # Generate operation ID
        if not operation_id:
            timestamp = datetime.now().isoformat()
            operation_id = f"pii-redact-{hashlib.sha256(timestamp.encode()).hexdigest()[:8]}"

        # Get detections (reuse or scan)
        if scan_result and 'detections' in scan_result:
            detections = scan_result['detections']
            original_hash = scan_result.get('data_hash')
        else:
            if isinstance(data, dict):
                detections = self.detector.scan_dict(data)
            else:
                detections = self.detector.detect(data, min_confidence)
            original_hash = hashlib.sha256(str(data).encode()).hexdigest()

        # Redact
        if isinstance(data, dict):
            redacted_data = self.redactor.redact_dict(data, detections, strategy)
        else:
            redacted_data = self.redactor.redact_text(data, detections, strategy)

        # Calculate redacted data hash
        redacted_hash = hashlib.sha256(str(redacted_data).encode()).hexdigest()

        # Get audit trail
        audit = self.redactor.get_audit_trail()

        # Track with DLP if available
        dlp_tag_id = None
        if self.dlp_tracker and NativeDLPTag:
            # Create DLP tag
            dlp_tag = NativeDLPTag(
                tag_id=f"{self.context_tag}-{operation_id}",
                operation="pii_redaction",
                data_hash=redacted_hash,
            )

            # Add T1-EDG anchor
            dlp_tag.add_t1_srb_anchor("T1-EDG-004")

            # Add dependency on original data
            if scan_result and scan_result.get('dlp_tag_id'):
                dlp_tag.add_dependency(scan_result['dlp_tag_id'])

            # Add redaction metadata
            dlp_tag.metadata.update({
                "original_hash": original_hash,
                "redacted_hash": redacted_hash,
                "strategy": strategy.value,
                "redaction_count": len(audit),
                "confidence_threshold": min_confidence,
                "region": self.region,
            })

            # Register with tracker
            tag_id = self.dlp_tracker.create_tag(
                operation="pii_redaction",
                data=str(redacted_data),
                tag_id=f"{self.context_tag}-{operation_id}"
            )

            # Add metadata and dependency
            tag = self.dlp_tracker.tags.get(tag_id)
            if tag:
                tag.add_t1_srb_anchor("T1-EDG-004")

                # Add dependency on original data
                if scan_result and scan_result.get('dlp_tag_id'):
                    self.dlp_tracker.add_dependency(tag_id, scan_result['dlp_tag_id'])

                tag.metadata.update({
                    "original_hash": original_hash,
                    "redacted_hash": redacted_hash,
                    "strategy": strategy.value,
                    "redaction_count": len(audit),
                    "confidence_threshold": min_confidence,
                    "region": self.region,
                })

            dlp_tag_id = tag_id

        return {
            "operation_id": operation_id,
            "redacted_data": redacted_data,
            "original_hash": original_hash,
            "redacted_hash": redacted_hash,
            "redaction_count": len(audit),
            "audit_trail": audit,
            "strategy": strategy.value,
            "dlp_tag_id": dlp_tag_id,
            "timestamp": datetime.now().isoformat(),
        }

    def create_export_manifest(self, output_path: str = "data_guardian_export.json") -> Dict[str, Any]:
        """
        Create export manifest with all tracked operations.

        Args:
            output_path: Path to write manifest

        Returns:
            Export manifest dict
        """
        if not self.dlp_tracker:
            return {
                "error": "DLP tracker not available",
                "context_tag": self.context_tag,
            }

        # Create manifest
        manifest_name = Path(output_path).stem
        manifest = self.dlp_tracker.create_export_manifest(manifest_name=manifest_name)

        # Add Data Guardian specific metadata
        manifest.update({
            "export_path": output_path,
            "data_guardian_version": "0.1.0",
            "anchor": "T1-EDG-004",
            "region": self.region,
            "pii_types_supported": [
                "email", "phone", "ssn", "credit_card", "ip_address",
                "date_of_birth", "passport", "driver_license", "bank_account",
                "full_name", "address", "custom"
            ],
            "redaction_strategies": [
                "mask", "hash", "remove", "partial", "token", "synthetic"
            ],
        })

        # Write to file
        Path(output_path).write_text(json.dumps(manifest, indent=2))

        return manifest

    def _count_nested_detections(self, detections: Dict) -> int:
        """Count total detections in nested dict structure."""
        count = 0
        for value in detections.values():
            if isinstance(value, list):
                if value and isinstance(value[0], dict) and 'matches' in value[0]:
                    # Array element with matches
                    for item in value:
                        count += len(item.get('matches', []))
                else:
                    # Direct list of detections
                    count += len(value)
            elif isinstance(value, dict):
                count += self._count_nested_detections(value)
        return count

    def _extract_pii_types(self, detections: Dict) -> List[str]:
        """Extract unique PII types from nested dict structure."""
        types = set()

        def extract_recursive(data):
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        if 'type' in item:
                            types.add(item['type'])
                        if 'matches' in item:
                            for match in item['matches']:
                                if 'type' in match:
                                    types.add(match['type'])
                        extract_recursive(item)
            elif isinstance(data, dict):
                for value in data.values():
                    extract_recursive(value)

        extract_recursive(detections)
        return list(types)


def demo_integration():
    """Demonstration of Data Guardian with DLP integration."""
    print("🛡️ Data Guardian DLP Integration Demo")
    print("=" * 60)

    # Initialize integration
    integration = DataGuardianDLPIntegration(context_tag="demo-guardian")

    # Sample data with PII
    sample_data = """
    Customer Record:
    Name: Jane Smith
    Email: jane.smith@example.com
    Phone: (555) 123-4567
    SSN: 123-45-6789
    Account: 9876543210
    IP Address: 192.168.1.100
    """

    print("\n📊 Step 1: Scan for PII with DLP tracking")
    scan_result = integration.scan_with_tracking(sample_data, min_confidence=0.7)
    print(f"  ✓ Operation ID: {scan_result['operation_id']}")
    print(f"  ✓ Detections: {len(scan_result['detections'])}")
    print(f"  ✓ Data Hash: {scan_result['data_hash'][:16]}...")
    if scan_result['dlp_tag_id']:
        print(f"  ✓ DLP Tag: {scan_result['dlp_tag_id']}")

    print("\n🔒 Step 2: Redact PII with DLP tracking")
    redact_result = integration.redact_with_tracking(
        sample_data,
        strategy=RedactionStrategy.MASK,
        scan_result=scan_result,
    )
    print(f"  ✓ Operation ID: {redact_result['operation_id']}")
    print(f"  ✓ Redactions: {redact_result['redaction_count']}")
    print(f"  ✓ Strategy: {redact_result['strategy']}")
    print(f"  ✓ Redacted Hash: {redact_result['redacted_hash'][:16]}...")
    if redact_result['dlp_tag_id']:
        print(f"  ✓ DLP Tag: {redact_result['dlp_tag_id']}")

    print("\n📋 Redacted Data Preview:")
    print("-" * 60)
    print(redact_result['redacted_data'][:200] + "...")

    print("\n📦 Step 3: Create export manifest")
    manifest = integration.create_export_manifest("demo_guardian_export.json")
    if "error" not in manifest:
        print(f"  ✓ Manifest created: {manifest.get('export_path', 'N/A')}")
        print(f"  ✓ Anchor: {manifest.get('anchor')}")
        print(f"  ✓ Operations tracked: {manifest.get('total_operations', 0)}")

    print("\n✅ Integration demo complete!")
    print("   Anchor: T1-EDG-004")
    print(f"   DLP Context: {integration.context_tag}")


if __name__ == "__main__":
    demo_integration()
