"""Hunt result data model."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field


class HuntStatus(str, Enum):
    """Status of a hunt execution."""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"


class HuntResult(BaseModel):
    """Result of a threat hunting query.
    
    Represents the output of KQL queries executed by HUNTER agent,
    including query details, results, and metadata.
    """

    hunt_id: str = Field(..., description="Unique hunt identifier")
    hunt_name: str = Field(..., description="Human-readable hunt name")
    status: HuntStatus = Field(default=HuntStatus.COMPLETED)
    
    # Query information
    query: str = Field(..., description="KQL query executed")
    query_description: Optional[str] = None
    timespan: Optional[str] = Field(default="PT24H")
    
    # Results
    total_records: int = Field(default=0)
    result_records: List[Dict[str, Any]] = Field(default_factory=list)
    
    # MITRE ATT&CK mapping
    tactics: List[str] = Field(default_factory=list)
    techniques: List[str] = Field(default_factory=list)
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = None
    data_processed_bytes: Optional[int] = None
    
    # Findings and recommendations
    findings: List[str] = Field(default_factory=list)
    anomalies_detected: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    risk_score: Optional[float] = Field(default=0.0)
    
    # Investigation tracking
    investigation_id: Optional[str] = None
    follow_up_hunts: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "hunt_id": "hunt-20260218-001",
                "hunt_name": "Anomalous Sign-in Detection",
                "status": "Completed",
                "query": 'SigninLogs | where RiskLevel == "high"',
                "total_records": 42,
                "tactics": ["Initial Access"],
                "techniques": ["Valid Accounts"],
            }
        }

    def is_successful(self) -> bool:
        """Check if hunt executed successfully."""
        return self.status == HuntStatus.COMPLETED

    def has_findings(self) -> bool:
        """Check if hunt detected any findings."""
        return bool(self.result_records) or bool(self.anomalies_detected)

    def add_finding(self, finding: str) -> None:
        """Add a finding.
        
        Args:
            finding: Description of finding
        """
        if finding not in self.findings:
            self.findings.append(finding)

    def add_anomaly(self, anomaly: str) -> None:
        """Add detected anomaly.
        
        Args:
            anomaly: Description of anomaly
        """
        if anomaly not in self.anomalies_detected:
            self.anomalies_detected.append(anomaly)

    def add_recommendation(self, recommendation: str) -> None:
        """Add investigation recommendation.
        
        Args:
            recommendation: Recommended action
        """
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)

    def add_follow_up_hunt(self, hunt_id: str) -> None:
        """Add follow-up hunt reference.
        
        Args:
            hunt_id: ID of follow-up hunt
        """
        if hunt_id not in self.follow_up_hunts:
            self.follow_up_hunts.append(hunt_id)

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of hunt results.
        
        Returns:
            Dictionary with key metrics
        """
        return {
            "hunt_id": self.hunt_id,
            "hunt_name": self.hunt_name,
            "status": self.status,
            "total_records": self.total_records,
            "findings_count": len(self.findings),
            "anomalies_count": len(self.anomalies_detected),
            "risk_score": self.risk_score,
            "execution_time_ms": self.execution_time_ms,
        }
