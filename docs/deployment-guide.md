# Deployment Guide

This guide explains how to deploy Semantest infrastructure to AWS Lambda and Azure Functions.

## Prerequisites

1. Install required tools:
   ```bash
   # Install Python 3.11+
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install Pulumi
   curl -fsSL https://get.pulumi.com | sh
   ```

2. Configure cloud providers:
   ```bash
   # For AWS
   aws configure
   
   # For Azure
   az login
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

## Deployment

### Quick Deploy

Use the deploy script:
```bash
# Deploy to AWS (default)
./scripts/deploy.sh

# Deploy to AWS with specific environment and region
./scripts/deploy.sh aws staging eu-west-1

# Deploy to Azure
./scripts/deploy.sh azure dev eastus
```

### Manual Deploy

1. Set configuration:
   ```bash
   pulumi config set provider aws
   pulumi config set environment dev
   pulumi config set region us-east-1
   ```

2. Initialize stack:
   ```bash
   pulumi stack init aws-dev
   ```

3. Deploy:
   ```bash
   pulumi up
   ```

## Stack Management

### List stacks
```bash
pulumi stack ls
```

### Switch stacks
```bash
pulumi stack select aws-dev
```

### View outputs
```bash
pulumi stack output
```

### Destroy resources
```bash
pulumi destroy
```

## Multi-Region Deployment

Deploy to multiple regions:
```bash
# AWS US East
./scripts/deploy.sh aws prod us-east-1

# AWS EU West
./scripts/deploy.sh aws prod eu-west-1

# Azure East US
./scripts/deploy.sh azure prod eastus

# Azure West Europe
./scripts/deploy.sh azure prod westeurope
```

## Cost Optimization

The infrastructure uses serverless components to minimize costs:
- AWS Lambda: Pay only for execution time
- Azure Functions: Consumption plan with automatic scaling
- No idle infrastructure costs

## Monitoring

After deployment, monitor your functions:
- AWS: CloudWatch Logs and Metrics
- Azure: Application Insights

## Troubleshooting

### Pulumi state issues
```bash
pulumi refresh
pulumi stack export > backup.json
```

### Provider authentication
```bash
# AWS
aws sts get-caller-identity

# Azure
az account show
```