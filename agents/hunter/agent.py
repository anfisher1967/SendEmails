"""HUNTER Agent - Automated threat hunting and query generation."""

from typing import Any, Dict

import structlog

from agents.base_agent import BaseAgent


class HunterAgent(BaseAgent):
    """HUNTER Agent for automated threat hunting and KQL query generation.
    
    This agent:
    1. Receives threat hypotheses and investigation requests
    2. Generates optimized KQL queries for threat hunting
    3. Maps threats to MITRE ATT&CK framework
    4. Executes hunts against Sentinel data lake
    5. Provides structured findings and recommendations
    """

    def __init__(
        self,
        name: str = "HUNTER",
        mode: str = "advisory",
        log_level: str = "INFO",
    ):
        """Initialize HUNTER agent.
        
        Args:
            name: Agent identifier
            mode: Operating mode (advisory, automated, hybrid)
            log_level: Logging level
        """
        super().__init__(
            name=name,
            description="Threat hunting and query generation agent for Sentinel",
            mode=mode,
            log_level=log_level,
        )
        self.logger = structlog.get_logger(self.name)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HUNTER threat hunting logic.
        
        Args:
            input_data: Contains threat hypothesis and hunt parameters
            
        Returns:
            Dictionary with hunt results and findings
        """
        if not await self.validate_input(input_data):
            return {
                "status": "failed",
                "error": "Invalid input data",
            }

        self.log_event("Starting threat hunt")

        # Get hunt parameters
        threat_type = input_data.get("threat_type", "")
        mitre_tactics = input_data.get("mitre_tactics", [])
        
        # Map to MITRE ATT&CK
        from agents.hunter.threat_mappings import MITREMapping
        mitre_engine = MITREMapping()
        threat_mappings = mitre_engine.map_threat(threat_type, mitre_tactics)

        # Generate KQL query
        from agents.hunter.query_generator import KQLQueryGenerator
        query_engine = KQLQueryGenerator()
        kql_query = await query_engine.generate_query(
            threat_type=threat_type,
            mitre_techniques=threat_mappings.get("techniques", []),
        )

        # Execute hunt (placeholder - would call Sentinel)
        hunt_result = {
            "status": "generated",
            "query": kql_query,
            "threat_mappings": threat_mappings,
            "agent": self.name,
            "mode": self.mode,
        }

        self.log_event(
            "Hunt generation completed",
            threat_type=threat_type,
            query_length=len(kql_query),
        )

        return hunt_result

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input contains required hunt parameters.
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(input_data, dict):
            self.log_event("Invalid input: not a dictionary", level="warning")
            return False

        if "threat_type" not in input_data:
            self.log_event("Invalid input: missing 'threat_type'", level="warning")
            return False

        return True
