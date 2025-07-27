"""Main Pulumi program for Semantest infrastructure."""

import pulumi
from pulumi import Config

from semantest.domain import (
    CloudProvider,
    Environment,
    FunctionApp,
    FunctionRuntime,
    Region,
)
from semantest.infrastructure.aws import LambdaStack
from semantest.infrastructure.azure import FunctionAppStack
from semantest.infrastructure.shared import StackConfig

# Get configuration
config = Config()
provider = CloudProvider(config.get("provider") or "aws")
environment = Environment(config.get("environment") or "dev")
region_name = config.get("region") or "us-east-1"

# Create region based on provider
if provider == CloudProvider.AWS:
    if region_name == "us-east-1":
        region = Region.aws_us_east_1()
    elif region_name == "eu-west-1":
        region = Region.aws_eu_west_1()
    else:
        region = Region(provider=provider, name=region_name)
elif provider == CloudProvider.AZURE:
    if region_name == "eastus":
        region = Region.azure_east_us()
    elif region_name == "westeurope":
        region = Region.azure_west_europe()
    else:
        region = Region(provider=provider, name=region_name)
else:
    raise ValueError(f"Unsupported provider: {provider}")

# Define function apps
rest_api_app = FunctionApp(
    name="semantest-rest-api",
    runtime=FunctionRuntime.NODEJS20,
    handler="index.handler",
    memory_mb=512,
    timeout_seconds=30,
    environment_variables={
        "NODE_ENV": environment.value,
        "API_VERSION": "v1",
    },
)

websocket_connect_app = FunctionApp(
    name="semantest-ws-connect",
    runtime=FunctionRuntime.NODEJS20,
    handler="connect.handler",
    memory_mb=256,
    timeout_seconds=10,
)

websocket_disconnect_app = FunctionApp(
    name="semantest-ws-disconnect",
    runtime=FunctionRuntime.NODEJS20,
    handler="disconnect.handler",
    memory_mb=256,
    timeout_seconds=10,
)

websocket_message_app = FunctionApp(
    name="semantest-ws-message",
    runtime=FunctionRuntime.NODEJS20,
    handler="message.handler",
    memory_mb=512,
    timeout_seconds=30,
)

# Create stack configuration
stack_config = StackConfig(
    name=f"semantest-{environment.value}",
    environment=environment,
    region=region,
    tags={
        "Application": "Semantest",
        "Component": "Infrastructure",
    },
)

# Deploy based on provider
if provider == CloudProvider.AWS:
    # Deploy to AWS Lambda
    lambda_stack = LambdaStack(
        name="lambda-functions",
        config=stack_config,
        function_apps=[
            rest_api_app,
            websocket_connect_app,
            websocket_disconnect_app,
            websocket_message_app,
        ],
    )
    
    # Export Lambda function ARNs
    pulumi.export("provider", "aws")
    pulumi.export("region", region.name)
    
elif provider == CloudProvider.AZURE:
    # Deploy to Azure Functions
    function_app_stack = FunctionAppStack(
        name="function-apps",
        config=stack_config,
        function_apps=[
            rest_api_app,
            websocket_connect_app,
            websocket_disconnect_app,
            websocket_message_app,
        ],
    )
    
    # Export Azure function endpoints
    pulumi.export("provider", "azure")
    pulumi.export("region", region.name)

# Common exports
pulumi.export("environment", environment.value)
pulumi.export("stack_name", stack_config.name)