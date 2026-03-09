"""MITRE ATT&CK mapping for HUNTER agent."""

from typing import Any, Dict, List

import structlog

logger = structlog.get_logger(__name__)


class MITREMapping:
    """Maps threats to MITRE ATT&CK framework."""

    # Simplified MITRE ATT&CK mapping
    THREAT_MAPPINGS = {
        "credential_access": {
            "tactics": ["Credential Access"],
            "techniques": [
                "Brute Force",
                "Credential Dumping",
                "Input Capture",
                "Man-in-the-Middle",
                "Phishing",
            ],
        },
        "execution": {
            "tactics": ["Execution"],
            "techniques": [
                "Command and Scripting Interpreter",
                "Exploitation for Privilege Escalation",
                "Inter-Process Communication",
                "Scheduled Task/Job",
            ],
        },
        "lateral_movement": {
            "tactics": ["Lateral Movement"],
            "techniques": [
                "Exploitation of Remote Services",
                "Lateral Tool Transfer",
                "Pass the Ticket",
                "Windows Admin Shares",
            ],
        },
        "privilege_escalation": {
            "tactics": ["Privilege Escalation"],
            "techniques": [
                "Access Token Manipulation",
                "Abuse Elevation Control Mechanism",
                "Domain Escalation",
                "Exploitation for Privilege Escalation",
            ],
        },
        "persistence": {
            "tactics": ["Persistence"],
            "techniques": [
                "Account Manipulation",
                "Boot or Logon Autostart Execution",
                "Create Account",
                "Firmware",
            ],
        },
        "defense_evasion": {
            "tactics": ["Defense Evasion"],
            "techniques": [
                "Access Token Manipulation",
                "Abuse Elevation Control Mechanism",
                "Obfuscated Files or Information",
                "Masquerading",
            ],
        },
        "discovery": {
            "tactics": ["Discovery"],
            "techniques": [
                "Account Discovery",
                "Browser Information",
                "Domain Trust Discovery",
                "Network Share Discovery",
            ],
        },
        "collection": {
            "tactics": ["Collection"],
            "techniques": [
                "Clipboard Data",
                "Email Collection",
                "Screen Capture",
                "Data from Network Shared Drive",
            ],
        },
        "exfiltration": {
            "tactics": ["Exfiltration"],
            "techniques": [
                "Automated Exfiltration",
                "Data Compressed",
                "Data from Local System",
                "Exfiltration Over C2 Channel",
            ],
        },
    }

    def map_threat(
        self,
        threat_type: str,
        tactics: List[str] = None,
    ) -> Dict[str, Any]:
        """Map threat to MITRE ATT&CK framework.
        
        Args:
            threat_type: Type of threat (e.g., 'credential_access')
            tactics: Override tactics list
            
        Returns:
            Dictionary with MITRE mapping information
        """
        logger.info("Mapping threat to MITRE ATT&CK", threat_type=threat_type)

        threat_key = threat_type.lower().replace(" ", "_")

        # Get base mapping
        mapping = self.THREAT_MAPPINGS.get(threat_key, {})

        if not mapping:
            # Return generic mapping if not found
            mapping = {
                "tactics": tactics or ["Initial Access"],
                "techniques": ["Unknown"],
            }

        return {
            "threat_type": threat_type,
            "tactics": mapping.get("tactics", []),
            "techniques": mapping.get("techniques", []),
            "confidence": 0.85 if threat_key in self.THREAT_MAPPINGS else 0.5,
        }

    def get_tactics_for_technique(self, technique: str) -> List[str]:
        """Get tactics associated with a technique.
        
        Args:
            technique: MITRE technique name
            
        Returns:
            List of associated tactics
        """
        for threat_key, mapping in self.THREAT_MAPPINGS.items():
            if technique in mapping.get("techniques", []):
                return mapping.get("tactics", [])

        return []

    def suggest_hunts_for_threat(self, threat_type: str) -> List[Dict[str, str]]:
        """Suggest hunting queries for a threat.
        
        Args:
            threat_type: Type of threat
            
        Returns:
            List of suggested hunts with descriptions
        """
        threat_key = threat_type.lower().replace(" ", "_")
        mapping = self.THREAT_MAPPINGS.get(threat_key, {})

        hunts = []
        for technique in mapping.get("techniques", []):
            hunts.append(
                {
                    "technique": technique,
                    "tactic": mapping.get("tactics", ["Unknown"])[0],
                    "description": f"Hunt for {technique} activity",
                }
            )

        return hunts
