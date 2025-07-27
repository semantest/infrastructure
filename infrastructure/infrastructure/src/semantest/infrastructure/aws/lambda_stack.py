"""AWS Lambda infrastructure stack."""

from typing import Dict, List, Optional

import pulumi
import pulumi_aws as aws

from semantest.domain import FunctionApp
from semantest.infrastructure.shared import InfrastructureStack, StackConfig


class LambdaStack(InfrastructureStack):
    """AWS Lambda serverless functions stack."""
    
    def __init__(
        self,
        name: str,
        config: StackConfig,
        function_apps: List[FunctionApp],
        opts: Optional[pulumi.StackOptions] = None,
    ) -> None:
        """Initialize Lambda stack."""
        self.function_apps = function_apps
        self.lambda_functions: Dict[str, aws.lambda_.Function] = {}
        self.lambda_roles: Dict[str, aws.iam.Role] = {}
        super().__init__(name, config, opts)
    
    def _initialize_provider(self) -> None:
        """Initialize AWS provider."""
        self.aws_provider = aws.Provider(
            "aws",
            region=self.config.region.name,
            default_tags={"tags": self.common_tags},
        )
    
    def _create_resources(self) -> None:
        """Create Lambda functions and related resources."""
        # Create IAM roles for Lambda functions
        for app in self.function_apps:
            role = self._create_lambda_role(app.name)
            self.lambda_roles[app.name] = role
            
            # Create Lambda function
            function = self._create_lambda_function(app, role)
            self.lambda_functions[app.name] = function
        
        # Export function ARNs
        outputs = {
            f"{name}_arn": func.arn
            for name, func in self.lambda_functions.items()
        }
        self.export_outputs(outputs)
    
    def _create_lambda_role(self, name: str) -> aws.iam.Role:
        """Create IAM role for Lambda function."""
        return aws.iam.Role(
            f"{name}-role",
            assume_role_policy="""{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Effect": "Allow"
                    }
                ]
            }""",
            tags=self.common_tags,
            opts=pulumi.ResourceOptions(provider=self.aws_provider),
        )
    
    def _create_lambda_function(
        self, 
        app: FunctionApp, 
        role: aws.iam.Role
    ) -> aws.lambda_.Function:
        """Create Lambda function."""
        # Attach basic execution policy
        aws.iam.RolePolicyAttachment(
            f"{app.name}-basic-execution",
            role=role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            opts=pulumi.ResourceOptions(provider=self.aws_provider),
        )
        
        # Get provider-specific config
        config = app.get_provider_specific_config(self.config.region.provider)
        
        # For now, we'll use a placeholder for the code
        # In a real implementation, this would come from a build artifact
        return aws.lambda_.Function(
            app.name,
            role=role.arn,
            runtime=config["runtime"],
            handler=config["handler"],
            memory_size=config["memory_size"],
            timeout=config["timeout"],
            environment=config.get("environment"),
            code=pulumi.AssetArchive({
                "index.js": pulumi.StringAsset(
                    "exports.handler = async (event) => { return { statusCode: 200, body: 'Hello from Lambda!' }; };"
                ),
            }),
            tags=self.common_tags,
            opts=pulumi.ResourceOptions(provider=self.aws_provider),
        )