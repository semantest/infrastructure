#!/bin/bash
set -euo pipefail

# Deploy script for Semantest infrastructure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
PROVIDER=${1:-aws}
ENVIRONMENT=${2:-dev}
REGION=${3:-us-east-1}

echo -e "${GREEN}=== Semantest Infrastructure Deployment ===${NC}"
echo -e "Provider: ${YELLOW}$PROVIDER${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo ""

# Validate inputs
if [[ ! "$PROVIDER" =~ ^(aws|azure)$ ]]; then
    echo -e "${RED}Error: Invalid provider. Use 'aws' or 'azure'${NC}"
    exit 1
fi

if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Error: Invalid environment. Use 'dev', 'staging', or 'prod'${NC}"
    exit 1
fi

# Check prerequisites
if ! command -v pulumi &> /dev/null; then
    echo -e "${RED}Error: Pulumi CLI not found${NC}"
    exit 1
fi

if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Error: Poetry not found${NC}"
    exit 1
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
poetry install --quiet

# Set Pulumi config
echo -e "${YELLOW}Configuring Pulumi...${NC}"
pulumi config set provider "$PROVIDER"
pulumi config set environment "$ENVIRONMENT"
pulumi config set region "$REGION"

# Select or create stack
STACK_NAME="${PROVIDER}-${ENVIRONMENT}"
pulumi stack select "$STACK_NAME" 2>/dev/null || {
    echo -e "${YELLOW}Creating new stack: $STACK_NAME${NC}"
    pulumi stack init "$STACK_NAME"
}

# Preview changes
echo -e "${YELLOW}Previewing changes...${NC}"
poetry run pulumi preview

# Confirm deployment
echo ""
read -p "Deploy these changes? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deploying...${NC}"
    poetry run pulumi up --yes
    echo -e "${GREEN}✓ Deployment complete!${NC}"
    
    # Show outputs
    echo -e "\n${YELLOW}Stack outputs:${NC}"
    pulumi stack output
else
    echo -e "${YELLOW}Deployment cancelled${NC}"
fi