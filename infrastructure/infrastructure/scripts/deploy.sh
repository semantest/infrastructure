#!/bin/bash
set -e

# Deploy script for Semantest infrastructure

PROVIDER=${1:-aws}
ENVIRONMENT=${2:-dev}
REGION=${3:-us-east-1}

echo "Deploying Semantest infrastructure..."
echo "Provider: $PROVIDER"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"

# Set Pulumi config
pulumi config set provider "$PROVIDER"
pulumi config set environment "$ENVIRONMENT"
pulumi config set region "$REGION"

# Select or create stack
STACK_NAME="${PROVIDER}-${ENVIRONMENT}"
pulumi stack select "$STACK_NAME" 2>/dev/null || pulumi stack init "$STACK_NAME"

# Run deployment
pulumi up

echo "Deployment complete!"