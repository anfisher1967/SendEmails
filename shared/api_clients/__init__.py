"""API client wrappers for Azure services."""

from shared.api_clients.sentinel_client import SentinelClient
from shared.api_clients.graph_client import GraphClient
from shared.api_clients.defender_client import DefenderClient

__all__ = ["SentinelClient", "GraphClient", "DefenderClient"]
