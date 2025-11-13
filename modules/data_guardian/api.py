"""
Data Guardian API Endpoints

FastAPI routes for PII detection and redaction services.

Anchor: T1-EDG-002-API
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from .detection_rules import PIIDetector, PIIType
from .redaction import RedactionEngine, RedactionStrategy

# Pydantic models for API requests/responses

class ScanRequest(BaseModel):
    """Request body for scanning data."""
    data: Dict[str, Any] = Field(..., description="Data to scan for PII")
    min_confidence: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for PII detection"
    )
    region: str = Field("US", description="Region for detection rules (US, EU, etc.)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": {
                    "user_email": "john.doe@example.com",
                    "phone": "555-123-4567",
                    "notes": "Contact SSN: 123-45-6789"
                },
                "min_confidence": 0.7,
                "region": "US"
            }
        }
    }


class RedactRequest(BaseModel):
    """Request body for redacting PII."""
    data: Dict[str, Any] = Field(..., description="Data to redact")
    strategy: RedactionStrategy = Field(
        RedactionStrategy.MASK,
        description="Redaction strategy to apply"
    )
    min_confidence: float = Field(
        0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for PII detection"
    )
    region: str = Field("US", description="Region for detection rules")

    model_config = {
        "json_schema_extra": {
            "example": {
                "data": {
                    "user_email": "john.doe@example.com",
                    "phone": "555-123-4567"
                },
                "strategy": "mask",
                "min_confidence": 0.7,
                "region": "US"
            }
        }
    }


class PIIDetection(BaseModel):
    """Single PII detection result."""
    field_path: str = Field(..., description="Path to the field containing PII")
    pii_type: str = Field(..., description="Type of PII detected")
    confidence: float = Field(..., description="Detection confidence (0.0-1.0)")
    location: Optional[Dict[str, int]] = Field(
        None,
        description="Location in text (start, end positions)"
    )


class ScanResponse(BaseModel):
    """Response from scanning operation."""
    pii_detected: bool = Field(..., description="Whether any PII was detected")
    total_detections: int = Field(..., description="Total number of PII instances found")
    detections: List[PIIDetection] = Field(..., description="Detailed detection results")
    detector_stats: Dict[str, Any] = Field(..., description="Detector statistics")

    model_config = {
        "json_schema_extra": {
            "example": {
                "pii_detected": True,
                "total_detections": 3,
                "detections": [
                    {
                        "field_path": "user_email",
                        "pii_type": "email",
                        "confidence": 0.95,
                        "location": {"start": 0, "end": 20}
                    },
                    {
                        "field_path": "phone",
                        "pii_type": "phone",
                        "confidence": 0.85,
                        "location": {"start": 0, "end": 12}
                    }
                ],
                "detector_stats": {
                    "total_rules": 7,
                    "region": "US",
                    "avg_confidence": 0.82
                }
            }
        }
    }


class RedactResponse(BaseModel):
    """Response from redaction operation."""
    redacted: bool = Field(..., description="Whether redaction was performed")
    redacted_data: Dict[str, Any] = Field(..., description="Data with PII redacted")
    redaction_count: int = Field(..., description="Number of fields redacted")
    audit_trail: Dict[str, Any] = Field(..., description="Audit information")

    model_config = {
        "json_schema_extra": {
            "example": {
                "redacted": True,
                "redacted_data": {
                    "user_email": "****@*******.***",
                    "phone": "***-***-4567"
                },
                "redaction_count": 2,
                "audit_trail": {
                    "total_redactions": 2,
                    "strategy": "mask"
                }
            }
        }
    }


# Create router
router = APIRouter(prefix="/data", tags=["Data Guardian"])


@router.post(
    "/scan",
    response_model=ScanResponse,
    summary="Scan data for PII",
    description="Scan provided data structure for personally identifiable information (PII)"
)
async def scan_data(request: ScanRequest = Body(...)):
    """
    Scan data for PII using configurable detection rules.

    Returns detailed information about detected PII including:
    - Type of PII (email, SSN, phone, etc.)
    - Confidence score
    - Location in the data
    - Field path

    **Example:**
    ```json
    {
        "data": {
            "email": "user@example.com",
            "phone": "555-1234"
        },
        "min_confidence": 0.7,
        "region": "US"
    }
    ```
    """
    try:
        # Initialize detector with specified region
        detector = PIIDetector(region=request.region)

        # Scan the data
        scan_results = detector.scan_dict(request.data, request.min_confidence)

        # Convert to API response format
        detections = []
        total_count = 0

        def extract_detections(obj, path=""):
            nonlocal total_count
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, dict) and 'type' in item:
                        location = None
                        if 'start' in item and 'end' in item:
                            location = {'start': item['start'], 'end': item['end']}
                        detections.append(PIIDetection(
                            field_path=path,
                            pii_type=item['type'],
                            confidence=item['confidence'],
                            location=location
                        ))
                        total_count += 1
                    else:
                        extract_detections(item, path)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    extract_detections(value, new_path)

        extract_detections(scan_results)

        return ScanResponse(
            pii_detected=len(detections) > 0,
            total_detections=total_count,
            detections=detections,
            detector_stats=detector.get_stats()
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scanning data: {str(e)}"
        )


@router.post(
    "/redact",
    response_model=RedactResponse,
    summary="Redact PII from data",
    description="Detect and redact PII from provided data using specified strategy"
)
async def redact_data(request: RedactRequest = Body(...)):
    """
    Detect and redact PII from data.

    **Redaction Strategies:**
    - `mask`: Replace with asterisks (preserves structure)
    - `hash`: Replace with deterministic hash
    - `remove`: Remove completely
    - `partial`: Show first/last characters only
    - `token`: Replace with numbered tokens [EMAIL_1]
    - `synthetic`: Replace with fake but realistic data

    **Example:**
    ```json
    {
        "data": {
            "email": "john@example.com",
            "ssn": "123-45-6789"
        },
        "strategy": "mask",
        "min_confidence": 0.7
    }
    ```
    """
    try:
        # Initialize detector and redaction engine
        detector = PIIDetector(region=request.region)
        redactor = RedactionEngine(default_strategy=request.strategy)

        # Scan for PII
        scan_results = detector.scan_dict(request.data, request.min_confidence)

        if not scan_results:
            # No PII detected
            return RedactResponse(
                redacted=False,
                redacted_data=request.data,
                redaction_count=0,
                audit_trail={"total_redactions": 0, "strategy": request.strategy.value}
            )

        # Redact the data
        redacted_data = redactor.redact_dict(
            request.data,
            scan_results,
            request.strategy
        )

        # Get audit trail
        audit = redactor.get_audit_trail()
        audit['strategy'] = request.strategy.value

        return RedactResponse(
            redacted=True,
            redacted_data=redacted_data,
            redaction_count=audit['total_redactions'],
            audit_trail=audit
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error redacting data: {str(e)}"
        )


@router.get(
    "/strategies",
    response_model=List[str],
    summary="List available redaction strategies",
    description="Get list of available PII redaction strategies"
)
async def list_strategies():
    """
    List all available redaction strategies.

    Returns a list of strategy names that can be used in /redact endpoint.
    """
    return [strategy.value for strategy in RedactionStrategy]


@router.get(
    "/pii-types",
    response_model=List[str],
    summary="List detectable PII types",
    description="Get list of PII types that can be detected"
)
async def list_pii_types():
    """
    List all detectable PII types.

    Returns a list of PII categories the detector can identify.
    """
    return [pii_type.value for pii_type in PIIType]


@router.get(
    "/regions",
    response_model=List[str],
    summary="List supported regions",
    description="Get list of supported regions for PII detection rules"
)
async def list_regions():
    """
    List supported regions for detection rules.

    Different regions may have different PII detection rules
    (e.g., SSN formats, phone number patterns).
    """
    return ["US", "EU", "UK", "CA", "AU"]


@router.get(
    "/health",
    summary="Health check for Data Guardian service",
    description="Check if Data Guardian service is operational"
)
async def health_check():
    """
    Health check endpoint for Data Guardian.

    Returns service status and basic configuration.
    """
    detector = PIIDetector()
    return {
        "status": "healthy",
        "service": "data_guardian",
        "version": "0.1.0",
        "anchor": "T1-EDG-002",
        "detector_stats": detector.get_stats()
    }
