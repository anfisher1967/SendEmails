"""Entity data models for identities, devices, and IPs."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Supported entity types."""

    ACCOUNT = "Account"
    DEVICE = "Device"
    IP = "IP"
    URL = "URL"
    HASH = "Hash"
    FILE = "File"
    PROCESS = "Process"
    REGISTRY = "Registry"


class RiskLevel(str, Enum):
    """Risk assessment levels."""

    UNKNOWN = "Unknown"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Entity(BaseModel):
    """Base entity model for all investigation entities.
    
    Represents security entities like users, devices, IPs, etc.
    that are involved in security alerts and investigations.
    """

    entity_id: str = Field(..., description="Unique entity identifier")
    entity_type: EntityType = Field(..., description="Type of entity")
    name: str = Field(..., description="Entity name or identifier")
    display_name: Optional[str] = Field(None, description="User-friendly display name")
    
    # Risk and status
    risk_level: RiskLevel = Field(default=RiskLevel.UNKNOWN)
    is_compromised: bool = Field(default=False)
    
    # Context and metadata
    context: Dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    
    # Timestamps
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Investigation tracking
    investigation_id: Optional[str] = None
    related_alerts: list[str] = Field(default_factory=list)
    notes: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        use_enum_values = True

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(type={self.entity_type}, name={self.name})"

    def mark_compromised(self, reason: Optional[str] = None) -> None:
        """Mark entity as compromised.
        
        Args:
            reason: Reason for compromise designation
        """
        self.is_compromised = True
        self.risk_level = RiskLevel.CRITICAL
        if reason:
            self.notes = f"Marked as compromised: {reason}"

    def add_tag(self, tag: str) -> None:
        """Add tag to entity.
        
        Args:
            tag: Tag to add
        """
        if tag not in self.tags:
            self.tags.append(tag)

    def add_related_alert(self, alert_id: str) -> None:
        """Add related alert reference.
        
        Args:
            alert_id: Alert ID to associate
        """
        if alert_id not in self.related_alerts:
            self.related_alerts.append(alert_id)


class UserEntity(Entity):
    """User/Account entity."""

    user_principal_name: Optional[str] = None
    email: Optional[str] = None
    object_id: Optional[str] = None
    directory_role: Optional[str] = None
    mfa_enabled: bool = False
    password_last_changed: Optional[datetime] = None

    def __init__(self, **data):
        """Initialize user entity."""
        super().__init__(entity_type=EntityType.ACCOUNT, **data)


class DeviceEntity(Entity):
    """Device entity."""

    device_id: Optional[str] = None
    os_platform: Optional[str] = None
    os_version: Optional[str] = None
    device_owner: Optional[str] = None
    antivirus_status: Optional[str] = None
    last_logon: Optional[datetime] = None

    def __init__(self, **data):
        """Initialize device entity."""
        super().__init__(entity_type=EntityType.DEVICE, **data)


class IPEntity(Entity):
    """IP Address entity."""

    ip_address: str = Field(..., alias="address")
    ip_type: Optional[str] = None  # Internal, External, Routable, etc.
    country: Optional[str] = None
    organization: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False

    def __init__(self, **data):
        """Initialize IP entity."""
        if "address" in data:
            data["ip_address"] = data.pop("address")
        super().__init__(entity_type=EntityType.IP, **data)

    def is_suspicious(self) -> bool:
        """Check if IP is suspicious."""
        return self.is_vpn or self.is_proxy or self.is_tor or self.risk_level in [
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ]
