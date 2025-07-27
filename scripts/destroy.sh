#!/bin/bash
set -euo pipefail

# Destroy script for Semantest infrastructure

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
PROVIDER=${1:-aws}
ENVIRONMENT=${2:-dev}

echo -e "${RED}=== Semantest Infrastructure Destruction ===${NC}"
echo -e "Provider: ${YELLOW}$PROVIDER${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
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

# Extra confirmation for production
if [[ "$ENVIRONMENT" == "prod" ]]; then
    echo -e "${RED}WARNING: You are about to destroy PRODUCTION infrastructure!${NC}"
    echo -e "${RED}This action cannot be undone.${NC}"
    echo ""
    read -p "Type 'destroy-production' to confirm: " confirmation
    if [[ "$confirmation" != "destroy-production" ]]; then
        echo -e "${YELLOW}Destruction cancelled${NC}"
        exit 0
    fi
fi

# Check if Pulumi is installed
if ! command -v pulumi &> /dev/null; then
    echo -e "${RED}Error: Pulumi CLI not found${NC}"
    exit 1
fi

# Select stack
STACK_NAME="${PROVIDER}-${ENVIRONMENT}"
echo -e "${YELLOW}Selecting stack: $STACK_NAME${NC}"
if ! pulumi stack select "$STACK_NAME" 2>/dev/null; then
    echo -e "${RED}Error: Stack $STACK_NAME not found${NC}"
    exit 1
fi

# Preview destruction
echo -e "${YELLOW}Previewing destruction...${NC}"
poetry run pulumi preview --diff

# Confirm destruction
echo ""
echo -e "${RED}This will destroy all resources in the stack!${NC}"
read -p "Are you sure? (y/N) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Destroying infrastructure...${NC}"
    poetry run pulumi destroy --yes
    
    echo -e "${GREEN}✓ Infrastructure destroyed${NC}"
    
    # Ask if stack should be removed
    echo ""
    read -p "Remove the stack completely? (y/N) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pulumi stack rm --yes
        echo -e "${GREEN}✓ Stack removed${NC}"
    fi
else
    echo -e "${YELLOW}Destruction cancelled${NC}"
fi