"""Shared utilities and models for Agentic SOC framework."""

__version__ = "0.1.0"

from shared.api_clients.sentinel_client import SentinelClient
from shared.api_clients.graph_client import GraphClient
from shared.models.alert import SecurityAlert
from shared.models.entity import Entity
from shared.utils.logging_config import setup_logging

__all__ = [
    "SentinelClient",
    "GraphClient",
    "SecurityAlert",
    "Entity",
    "setup_logging",
]
