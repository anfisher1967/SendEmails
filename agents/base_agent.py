"""Base agent class for all SOC agents."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all SOC agents.
    
    This class defines the interface and common functionality for all
    AnalystBot01 and HUNTER agents in the Agentic SOC framework.
    """

    def __init__(
        self,
        name: str,
        description: str,
        mode: str = "advisory",
        log_level: str = "INFO",
    ):
        """Initialize base agent.
        
        Args:
            name: Agent name identifier
            description: Agent description and purpose
            mode: Operating mode (advisory, automated, or hybrid)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.description = description
        self.mode = mode
        self.log_level = log_level
        self.logger = structlog.get_logger(self.name)

    def __repr__(self) -> str:
        """Return string representation of agent."""
        return f"{self.__class__.__name__}(name={self.name}, mode={self.mode})"

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic on input data.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Dictionary containing agent execution results
        """
        pass

    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data before execution.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if input is valid, False otherwise
        """
        pass

    def log_event(
        self,
        event: str,
        level: str = "info",
        **kwargs: Any,
    ) -> None:
        """Log structured event.
        
        Args:
            event: Event name/description
            level: Log level (info, debug, warning, error)
            **kwargs: Additional context to log
        """
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(event, agent=self.name, **kwargs)
