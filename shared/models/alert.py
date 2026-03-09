"""Security Alert data model."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFORMATIONAL = "Informational"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlertStatus(str, Enum):
    """Alert processing status."""

    NEW = "New"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    DISMISSED = "Dismissed"
    ESCALATED = "Escalated"


class SecurityAlert(BaseModel):
    """Sentinel security alert model.
    
    Represents a security alert from Microsoft Sentinel with
    enriched context and metadata.
    """

    alert_id: str = Field(..., alias="AlertId")
    alert_name: str = Field(..., alias="AlertName")
    severity: AlertSeverity = Field(..., alias="AlertSeverity")
    time_generated: datetime = Field(..., alias="TimeGenerated")
    description: Optional[str] = Field(None, alias="Description")
    status: AlertStatus = Field(default=AlertStatus.NEW, alias="Status")
    
    # Entities involved in the alert
    entities: List[Dict[str, Any]] = Field(default_factory=list, alias="Entities")
    
    # Custom fields
    product_name: Optional[str] = Field(None, alias="ProductName")
    vendor_name: Optional[str] = Field(None, alias="VendorName")
    tactics: List[str] = Field(default_factory=list, alias="Tactics")
    techniques: List[str] = Field(default_factory=list, alias="Techniques")
    
    # Sentinel-specific fields
    resource_id: Optional[str] = Field(None, alias="ResourceId")
    alert_type: Optional[str] = Field(None, alias="AlertType")
    confidence_level: Optional[str] = Field(None, alias="ConfidenceLevel")
    confidence_score: Optional[int] = Field(None, alias="ConfidenceScore")
    
    # Metadata
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "AlertId": "12345678-1234-1234-1234-123456789012",
                "AlertName": "Suspicious Sign-in Activity",
                "AlertSeverity": "High",
                "TimeGenerated": "2026-02-18T10:30:00Z",
                "Description": "Sign-in anomaly detected from impossible travel",
                "Status": "New",
                "Entities": [],
                "ProductName": "Azure AD",
                "VendorName": "Microsoft",
                "Tactics": ["Initial Access"],
                "Techniques": ["Valid Accounts"],
            }
        }

    def is_critical(self) -> bool:
        """Check if alert is critical severity."""
        return self.severity == AlertSeverity.CRITICAL

    def is_high_priority(self) -> bool:
        """Check if alert is high priority (critical or high)."""
        return self.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]

    def get_affected_users(self) -> List[str]:
        """Extract affected user identities from entities."""
        users = []
        for entity in self.entities:
            if entity.get("type") == "account":
                if "name" in entity:
                    users.append(entity["name"])
        return users

    def get_affected_ips(self) -> List[str]:
        """Extract affected IP addresses from entities."""
        ips = []
        for entity in self.entities:
            if entity.get("type") == "ip":
                if "address" in entity:
                    ips.append(entity["address"])
        return ips
