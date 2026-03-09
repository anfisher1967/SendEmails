"""KQL query generator for HUNTER agent."""

from typing import Any, Dict, List

import structlog

logger = structlog.get_logger(__name__)


class KQLQueryGenerator:
    """Generates optimized KQL queries for threat hunting."""

    # Query templates for common threat patterns
    QUERY_TEMPLATES = {
        "brute_force": """
SigninLogs
| where TimeGenerated > ago(24h)
| where ResultDescription contains "Invalid username or password"
| summarize FailureCount = count() by UserPrincipalName, IPAddress
| where FailureCount > 10
| order by FailureCount desc
        """,
        "lateral_movement": """
SecurityEvent
| where EventID in (4625, 4624)
| where TimeGenerated > ago(24h)
| summarize LoginAttempts = count() by Account, ComputerName
| where LoginAttempts > 5
| order by LoginAttempts desc
        """,
        "data_exfiltration": """
FileModifyEvents
| union DownloadEvents
| where TimeGenerated > ago(24h)
| summarize FileCount = count(), TotalSize = sum(FileSize) by UserName, DeviceName
| where FileCount > 20 or TotalSize > 1000000000
| order by TotalSize desc
        """,
        "persistence": """
SecurityEvent
| where EventID in (4688, 4697, 4698)
| where TimeGenerated > ago(24h)
| where CommandLine contains "Run" or CommandLine contains "Startup"
| project TimeGenerated, Computer, Account, CommandLine
| order by TimeGenerated desc
        """,
    }

    async def generate_query(
        self,
        threat_type: str,
        mitre_techniques: List[str],
        timespan: str = "24h",
    ) -> str:
        """Generate KQL query for threat hunting.
        
        Args:
            threat_type: Type of threat to hunt for
            mitre_techniques: MITRE ATT&CK techniques to hunt
            timespan: Time period to search (e.g., '24h', '7d')
            
        Returns:
            Generated KQL query string
        """
        logger.info(
            "Generating KQL query",
            threat_type=threat_type,
            techniques_count=len(mitre_techniques),
        )

        # Use template if available
        threat_key = threat_type.lower().replace(" ", "_")
        if threat_key in self.QUERY_TEMPLATES:
            query = self.QUERY_TEMPLATES[threat_key]
            # Replace timespan placeholder
            query = query.replace("ago(24h)", f"ago({timespan})")
            return query

        # Generate custom query
        query = await self._build_custom_query(threat_type, mitre_techniques, timespan)
        return query

    async def _build_custom_query(
        self,
        threat_type: str,
        techniques: List[str],
        timespan: str,
    ) -> str:
        """Build custom KQL query for specific threat.
        
        Args:
            threat_type: Threat type
            techniques: MITRE techniques
            timespan: Time period
            
        Returns:
            Custom KQL query
        """
        # Start with a base query
        base_table = self._select_table_for_threat(threat_type)
        
        query = f"""
{base_table}
| where TimeGenerated > ago({timespan})
        """

        # Add technique-specific filters
        for technique in techniques:
            if "reconnaissance" in technique.lower():
                query += "\n| where DeviceAction in ['Reconnaissance', 'Scan']"
            elif "exploitation" in technique.lower():
                query += "\n| where EventSeverity in ['High', 'Critical']"
            elif "command" in technique.lower():
                query += "\n| where CommandLine != ''"

        query += "\n| order by TimeGenerated desc\n| take 100"

        return query

    def _select_table_for_threat(self, threat_type: str) -> str:
        """Select appropriate table for threat type.
        
        Args:
            threat_type: Type of threat
            
        Returns:
            Table name for query
        """
        threat_lower = threat_type.lower()

        # Map threat types to tables
        if "sign-in" in threat_lower or "login" in threat_lower:
            return "SigninLogs"
        elif "process" in threat_lower or "execution" in threat_lower:
            return "SecurityEvent"
        elif "file" in threat_lower or "data" in threat_lower:
            return "FileModifyEvents"
        elif "network" in threat_lower or "communication" in threat_lower:
            return "NetworkEvents"
        elif "audit" in threat_lower or "activity" in threat_lower:
            return "AuditLogs"
        else:
            return "SecurityAlert"

    def validate_query(self, query: str) -> bool:
        """Validate generated KQL query.
        
        Args:
            query: Query to validate
            
        Returns:
            True if query appears valid
        """
        # Basic validation
        if not query or len(query.strip()) == 0:
            return False

        # Check for table name
        if "|" not in query and not any(
            query.startswith(table)
            for table in [
                "SigninLogs",
                "SecurityEvent",
                "FileModifyEvents",
                "SecurityAlert",
            ]
        ):
            return False

        return True
