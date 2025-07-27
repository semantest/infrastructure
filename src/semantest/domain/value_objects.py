"""Value objects for infrastructure domain."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    """Supported cloud providers."""
    
    AWS = "aws"
    AZURE = "azure"


class Environment(str, Enum):
    """Deployment environments."""
    
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class FunctionRuntime(str, Enum):
    """Supported function runtimes."""
    
    NODEJS18 = "nodejs18.x"
    NODEJS20 = "nodejs20.x"
    PYTHON311 = "python3.11"
    PYTHON312 = "python3.12"


class Region(BaseModel):
    """Cloud region configuration."""
    
    provider: CloudProvider
    name: str
    display_name: Optional[str] = None
    
    class Config:
        frozen = True
    
    @classmethod
    def aws_us_east_1(cls) -> "Region":
        """AWS US East 1 (N. Virginia)."""
        return cls(
            provider=CloudProvider.AWS,
            name="us-east-1",
            display_name="US East (N. Virginia)"
        )
    
    @classmethod
    def aws_eu_west_1(cls) -> "Region":
        """AWS EU West 1 (Ireland)."""
        return cls(
            provider=CloudProvider.AWS,
            name="eu-west-1",
            display_name="EU West (Ireland)"
        )
    
    @classmethod
    def azure_east_us(cls) -> "Region":
        """Azure East US."""
        return cls(
            provider=CloudProvider.AZURE,
            name="eastus",
            display_name="East US"
        )
    
    @classmethod
    def azure_west_europe(cls) -> "Region":
        """Azure West Europe."""
        return cls(
            provider=CloudProvider.AZURE,
            name="westeurope",
            display_name="West Europe"
        )