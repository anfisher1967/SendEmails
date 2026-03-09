"""Sentinel API client wrapper."""

import os
from typing import Optional, Dict, Any, List

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

import structlog

logger = structlog.get_logger(__name__)


class SentinelClient:
    """Wrapper for Microsoft Sentinel API access.
    
    Provides authenticated access to Sentinel workspace for querying
    security logs, alerts, and enrichment data.
    """

    def __init__(
        self,
        workspace_id: Optional[str] = None,
        credential: Optional[DefaultAzureCredential] = None,
    ):
        """Initialize Sentinel client.
        
        Args:
            workspace_id: Sentinel workspace ID (defaults to env var)
            credential: Azure credential object (defaults to DefaultAzureCredential)
        """
        self.workspace_id = workspace_id or os.getenv("SENTINEL_WORKSPACE_ID")
        if not self.workspace_id:
            raise ValueError("SENTINEL_WORKSPACE_ID not provided or set")

        self.credential = credential or DefaultAzureCredential()
        self.client = LogsQueryClient(self.credential)
        self.logger = structlog.get_logger(self.__class__.__name__)

    async def query(
        self,
        query: str,
        timespan: str = "PT24H",
    ) -> Dict[str, Any]:
        """Execute KQL query against Sentinel.
        
        Args:
            query: KQL query string
            timespan: Time span for query (e.g., 'PT24H')
            
        Returns:
            Query results as dictionary
        """
        try:
            self.logger.info("Executing Sentinel query", query_length=len(query))
            response = self.client.query_workspace(
                workspace_id=self.workspace_id,
                query=query,
                timespan=timespan,
            )

            if response.status == LogsQueryStatus.PARTIAL:
                self.logger.warning(
                    "Query returned partial results",
                    error=response.error,
                )
            elif response.status == LogsQueryStatus.FAILURE:
                self.logger.error("Query failed", error=response.error)
                raise Exception(f"Query execution failed: {response.error}")

            # Convert results to list of dicts
            results = []
            for table in response.tables:
                for row in table.rows:
                    results.append(dict(zip(table.columns, row)))

            self.logger.info("Query completed", result_count=len(results))
            return {
                "status": "success",
                "total_records": len(results),
                "records": results,
            }

        except Exception as e:
            self.logger.error("Query execution error", error=str(e))
            raise

    async def get_alerts(
        self,
        hours: int = 24,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch recent security alerts.
        
        Args:
            hours: Number of hours to look back
            severity: Filter by severity (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of alert records
        """
        severity_filter = f'| where AlertSeverity == "{severity}"' if severity else ""

        query = f"""
        SecurityAlert
        | where TimeGenerated > ago({hours}h)
        {severity_filter}
        | project
            TimeGenerated,
            AlertName,
            AlertSeverity,
            Description,
            Entities,
            ExtendedProperties
        | order by TimeGenerated desc
        | take {limit}
        """

        result = await self.query(query, f"PT{hours}H")
        return result.get("records", [])

    async def test_connection(self) -> bool:
        """Test connection to Sentinel workspace.
        
        Returns:
            True if connection successful
        """
        try:
            result = await self.query("SecurityAlert | take 1", "PT1H")
            self.logger.info("Connection test successful")
            return True
        except Exception as e:
            self.logger.error("Connection test failed", error=str(e))
            return False
