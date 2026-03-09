"""Alert triage logic for AnalystBot01."""

from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class AlertTriage:
    """Triages security alerts to determine priority and recommended actions."""

    # Severity thresholds
    CRITICAL_INDICATORS = [
        "ransomware",
        "credential dumping",
        "lateral movement",
        "data exfiltration",
    ]

    HIGH_INDICATORS = [
        "brute force",
        "privilege escalation",
        "persistence",
        "command injection",
    ]

    async def triage(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Triage an alert to determine severity and recommendation.
        
        Args:
            alert: Alert object to triage
            
        Returns:
            Triage result with severity, score, and recommendation
        """
        logger.info("Triaging alert", alert_name=alert.get("AlertName"))

        severity_score = self._calculate_severity_score(alert)
        risk_indicators = self._identify_risk_indicators(alert)
        recommended_action = self._determine_recommendation(severity_score, risk_indicators)

        return {
            "alert_id": alert.get("AlertId"),
            "alert_name": alert.get("AlertName"),
            "severity_score": severity_score,
            "risk_indicators": risk_indicators,
            "recommendation": recommended_action,
            "confidence": self._calculate_confidence(severity_score, alert),
        }

    def _calculate_severity_score(self, alert: Dict[str, Any]) -> float:
        """Calculate composite severity score.
        
        Args:
            alert: Alert to score
            
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0

        # Base score from alert severity
        severity = alert.get("AlertSeverity", "").lower()
        severity_map = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
            "informational": 0.05,
        }
        score += severity_map.get(severity, 0.3)

        # Boost for indicators
        alert_text = str(alert.get("Description", "")).lower()
        for indicator in self.CRITICAL_INDICATORS:
            if indicator in alert_text:
                score = min(1.0, score + 0.3)

        for indicator in self.HIGH_INDICATORS:
            if indicator in alert_text:
                score = min(1.0, score + 0.15)

        return round(score, 2)

    def _identify_risk_indicators(self, alert: Dict[str, Any]) -> list[str]:
        """Identify risk indicators in alert.
        
        Args:
            alert: Alert to analyze
            
        Returns:
            List of identified risk indicators
        """
        indicators = []

        alert_text = str(alert.get("Description", "")).lower()
        tactics = alert.get("Tactics", [])
        techniques = alert.get("Techniques", [])

        # Check for behavioral indicators
        for indicator in self.CRITICAL_INDICATORS + self.HIGH_INDICATORS:
            if indicator in alert_text:
                indicators.append(indicator)

        # Include MITRE ATT&CK info
        indicators.extend([t.lower() for t in tactics])
        indicators.extend([t.lower() for t in techniques])

        return list(set(indicators))  # Remove duplicates

    def _determine_recommendation(
        self,
        severity_score: float,
        risk_indicators: list[str],
    ) -> str:
        """Determine recommended action based on triage.
        
        Args:
            severity_score: Calculated severity score
            risk_indicators: List of identified indicators
            
        Returns:
            Recommended action
        """
        if severity_score >= 0.8 or any(
            ind in risk_indicators for ind in ["exfiltration", "ransomware"]
        ):
            return "escalate_immediately"
        elif severity_score >= 0.6:
            return "escalate"
        elif severity_score >= 0.4:
            return "investigate"
        elif severity_score >= 0.2:
            return "review"
        else:
            return "dismiss_or_monitor"

    def _calculate_confidence(self, severity_score: float, alert: Dict[str, Any]) -> float:
        """Calculate triage confidence score.
        
        Args:
            severity_score: Calculated severity score
            alert: Alert being triaged
            
        Returns:
            Confidence from 0.0 to 1.0
        """
        confidence = 0.5  # Base confidence

        # Higher confidence for clearer indicators
        if severity_score in [0.0, 1.0]:
            confidence += 0.3

        # High confidence if multiple fields populated
        fields_populated = sum(
            1 for key in ["Description", "Tactics", "Techniques"]
            if alert.get(key)
        )
        confidence += fields_populated * 0.1

        return min(1.0, confidence)
