"""Domain entities for infrastructure components."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .value_objects import CloudProvider, Environment, FunctionRuntime, Region


class FunctionApp(BaseModel):
    """Serverless function application."""
    
    name: str
    runtime: FunctionRuntime
    handler: str
    memory_mb: int = Field(default=512, ge=128, le=10240)
    timeout_seconds: int = Field(default=30, ge=1, le=900)
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        frozen = True
    
    def get_provider_specific_config(self, provider: CloudProvider) -> Dict:
        """Get provider-specific configuration."""
        if provider == CloudProvider.AWS:
            return {
                "runtime": self.runtime.value,
                "handler": self.handler,
                "memory_size": self.memory_mb,
                "timeout": self.timeout_seconds,
                "environment": {"Variables": self.environment_variables},
            }
        elif provider == CloudProvider.AZURE:
            # Azure uses different naming conventions
            return {
                "runtime": self._map_runtime_to_azure(self.runtime),
                "handler": self.handler,
                "memory_mb": self.memory_mb,
                "timeout": f"PT{self.timeout_seconds}S",  # ISO 8601 duration
                "app_settings": self.environment_variables,
            }
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _map_runtime_to_azure(self, runtime: FunctionRuntime) -> str:
        """Map runtime to Azure naming convention."""
        mapping = {
            FunctionRuntime.NODEJS18: "node|18",
            FunctionRuntime.NODEJS20: "node|20",
            FunctionRuntime.PYTHON311: "python|3.11",
            FunctionRuntime.PYTHON312: "python|3.12",
        }
        return mapping.get(runtime, runtime.value)


class ApiEndpoint(BaseModel):
    """REST API endpoint configuration."""
    
    path: str
    method: str = Field(pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    function_app: FunctionApp
    auth_required: bool = True
    rate_limit: Optional[int] = Field(default=1000, ge=1)
    
    class Config:
        frozen = True


class WebSocketEndpoint(BaseModel):
    """WebSocket endpoint configuration."""
    
    route: str
    connect_function: FunctionApp
    disconnect_function: FunctionApp
    message_function: FunctionApp
    idle_timeout_seconds: int = Field(default=300, ge=60, le=86400)
    
    class Config:
        frozen = True