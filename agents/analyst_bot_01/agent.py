"""AnalystBot01 Agent - Alert triage and enrichment."""

from typing import Any, Dict

import structlog

from agents.base_agent import BaseAgent


class AnalystBot01Agent(BaseAgent):
    """AnalystBot01 Agent for automated security alert triage and enrichment.
    
    This agent:
    1. Receives security alerts from Microsoft Sentinel
    2. Triages alerts based on risk, context, and historical patterns
    3. Enriches alerts with identity, device, and threat intelligence
    4. Recommends actions: dismiss, escalate, or investigate
    5. Provides actionable intelligence for SOC analysts
    """

    def __init__(
        self,
        name: str = "AnalystBot01",
        mode: str = "advisory",
        log_level: str = "INFO",
    ):
        """Initialize AnalystBot01 agent.
        
        Args:
            name: Agent identifier
            mode: Operating mode (advisory, automated, hybrid)
            log_level: Logging level
        """
        super().__init__(
            name=name,
            description="Alert triage and enrichment agent for Sentinel alerts",
            mode=mode,
            log_level=log_level,
        )
        self.logger = structlog.get_logger(self.name)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AnalystBot01 triage logic.
        
        Args:
            input_data: Contains alert data to triage
            
        Returns:
            Dictionary with triage results and recommendations
        """
        if not await self.validate_input(input_data):
            return {
                "status": "failed",
                "error": "Invalid input data",
            }

        self.log_event("Starting alert triage")

        # Extract alert data
        alert = input_data.get("alert")
        
        # Triage the alert
        from agents.analyst_bot_01.triage import AlertTriage
        triage_engine = AlertTriage()
        triage_result = await triage_engine.triage(alert)

        # Enrich with context
        from agents.analyst_bot_01.enrichment import EntityEnrichment
        enrichment_engine = EntityEnrichment()
        enriched_context = await enrichment_engine.enrich(alert)

        self.log_event(
            "Alert triage completed",
            severity=triage_result.get("severity"),
            recommendation=triage_result.get("recommendation"),
        )

        return {
            "status": "success",
            "triage_result": triage_result,
            "enriched_context": enriched_context,
            "agent": self.name,
            "mode": self.mode,
        }

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input contains required alert data.
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(input_data, dict):
            self.log_event("Invalid input: not a dictionary", level="warning")
            return False

        if "alert" not in input_data:
            self.log_event("Invalid input: missing 'alert' field", level="warning")
            return False

        return True
