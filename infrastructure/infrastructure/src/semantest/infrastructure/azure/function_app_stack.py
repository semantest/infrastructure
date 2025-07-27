"""Azure Functions infrastructure stack."""

from typing import Dict, List, Optional

import pulumi
import pulumi_azure_native as azure

from semantest.domain import FunctionApp
from semantest.infrastructure.shared import InfrastructureStack, StackConfig


class FunctionAppStack(InfrastructureStack):
    """Azure Functions serverless stack."""
    
    def __init__(
        self,
        name: str,
        config: StackConfig,
        function_apps: List[FunctionApp],
        opts: Optional[pulumi.StackOptions] = None,
    ) -> None:
        """Initialize Function App stack."""
        self.function_apps = function_apps
        self.resource_group: Optional[azure.resources.ResourceGroup] = None
        self.storage_account: Optional[azure.storage.StorageAccount] = None
        self.app_service_plan: Optional[azure.web.AppServicePlan] = None
        self.function_app_resources: Dict[str, azure.web.WebApp] = {}
        super().__init__(name, config, opts)
    
    def _initialize_provider(self) -> None:
        """Initialize Azure provider."""
        # Azure provider is automatically configured via Azure CLI
        pass
    
    def _create_resources(self) -> None:
        """Create Azure Functions and related resources."""
        # Create resource group
        self.resource_group = azure.resources.ResourceGroup(
            f"{self.config.name}-rg",
            location=self.config.region.name,
            tags=self.common_tags,
        )
        
        # Create storage account for function app
        self.storage_account = azure.storage.StorageAccount(
            f"{self.config.name}storage".replace("-", ""),
            resource_group_name=self.resource_group.name,
            location=self.resource_group.location,
            sku=azure.storage.SkuArgs(
                name=azure.storage.SkuName.STANDARD_LRS,
            ),
            kind=azure.storage.Kind.STORAGE_V2,
            tags=self.common_tags,
        )
        
        # Create consumption plan
        self.app_service_plan = azure.web.AppServicePlan(
            f"{self.config.name}-plan",
            resource_group_name=self.resource_group.name,
            location=self.resource_group.location,
            kind="functionapp",
            sku=azure.web.SkuDescriptionArgs(
                name="Y1",
                tier="Dynamic",
            ),
            tags=self.common_tags,
        )
        
        # Create function apps
        for app in self.function_apps:
            function_app = self._create_function_app(app)
            self.function_app_resources[app.name] = function_app
        
        # Export function app endpoints
        outputs = {
            f"{name}_endpoint": func.default_host_name.apply(
                lambda host: f"https://{host}"
            )
            for name, func in self.function_app_resources.items()
        }
        self.export_outputs(outputs)
    
    def _create_function_app(self, app: FunctionApp) -> azure.web.WebApp:
        """Create Azure Function App."""
        # Get storage connection string
        storage_connection_string = pulumi.Output.all(
            self.resource_group.name,
            self.storage_account.name
        ).apply(
            lambda args: azure.storage.list_storage_account_keys(
                resource_group_name=args[0],
                account_name=args[1]
            )
        ).apply(
            lambda keys: f"DefaultEndpointsProtocol=https;AccountName={self.storage_account.name};"
            f"AccountKey={keys.keys[0].value};EndpointSuffix=core.windows.net"
        )
        
        # Get provider-specific config
        config = app.get_provider_specific_config(self.config.region.provider)
        
        # Create function app
        return azure.web.WebApp(
            app.name,
            resource_group_name=self.resource_group.name,
            location=self.resource_group.location,
            server_farm_id=self.app_service_plan.id,
            kind="functionapp",
            site_config=azure.web.SiteConfigArgs(
                app_settings=[
                    azure.web.NameValuePairArgs(
                        name="AzureWebJobsStorage",
                        value=storage_connection_string,
                    ),
                    azure.web.NameValuePairArgs(
                        name="FUNCTIONS_WORKER_RUNTIME",
                        value=self._get_worker_runtime(config["runtime"]),
                    ),
                    azure.web.NameValuePairArgs(
                        name="FUNCTIONS_EXTENSION_VERSION",
                        value="~4",
                    ),
                    *[
                        azure.web.NameValuePairArgs(name=k, value=v)
                        for k, v in config.get("app_settings", {}).items()
                    ],
                ],
                linux_fx_version=config["runtime"],
            ),
            tags=self.common_tags,
        )
    
    def _get_worker_runtime(self, runtime: str) -> str:
        """Get Azure Functions worker runtime."""
        if "node" in runtime:
            return "node"
        elif "python" in runtime:
            return "python"
        else:
            raise ValueError(f"Unsupported runtime: {runtime}")