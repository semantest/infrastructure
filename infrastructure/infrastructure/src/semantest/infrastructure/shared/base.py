"""Base infrastructure stack abstraction."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import pulumi
import structlog
from pydantic import BaseModel

from semantest.domain import CloudProvider, Environment, Region

logger = structlog.get_logger(__name__)


class StackConfig(BaseModel):
    """Configuration for infrastructure stacks."""
    
    name: str
    environment: Environment
    region: Region
    tags: Dict[str, str] = {}
    
    class Config:
        frozen = True


class InfrastructureStack(pulumi.Stack, ABC):
    """Base class for all infrastructure stacks."""
    
    def __init__(
        self,
        name: str,
        config: StackConfig,
        opts: Optional[pulumi.StackOptions] = None,
    ) -> None:
        """Initialize infrastructure stack."""
        super().__init__(name, opts)
        self.config = config
        self.logger = logger.bind(
            stack_name=name,
            environment=config.environment.value,
            region=config.region.name,
        )
        
        # Apply common tags
        self.common_tags = {
            "Environment": config.environment.value,
            "ManagedBy": "Pulumi",
            "Project": "Semantest",
            **config.tags,
        }
        
        # Initialize provider-specific resources
        self._initialize_provider()
        
        # Create stack resources
        self.logger.info("Creating infrastructure stack")
        self._create_resources()
    
    @abstractmethod
    def _initialize_provider(self) -> None:
        """Initialize cloud provider configuration."""
        pass
    
    @abstractmethod
    def _create_resources(self) -> None:
        """Create stack resources."""
        pass
    
    def export_outputs(self, outputs: Dict[str, Any]) -> None:
        """Export stack outputs."""
        for key, value in outputs.items():
            pulumi.export(key, value)
            self.logger.info(f"Exported output: {key}")