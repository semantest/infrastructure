# Semantest Infrastructure

Infrastructure as Code for deploying Semantest REST and WebSocket servers to AWS Lambda and Azure Functions using Pulumi.

## Architecture

This project follows the PythonEDA pattern to maintain a clean separation between infrastructure providers while maximizing code reuse.

### Directory Structure

```
.
├── src/                    # Source code
│   └── semantest/
│       ├── domain/        # Domain entities and value objects
│       ├── application/   # Application services
│       └── infrastructure/# Infrastructure implementations
│           ├── aws/       # AWS-specific infrastructure
│           ├── azure/     # Azure-specific infrastructure
│           └── shared/    # Shared infrastructure components
├── tests/                 # Test files
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── __main__.py           # Pulumi entry point
└── Pulumi.yaml           # Pulumi project configuration
```

## Design Principles

1. **Provider Abstraction**: Common infrastructure patterns are abstracted in the shared layer
2. **Domain-Driven Design**: Infrastructure components follow domain boundaries
3. **Event-Driven**: Infrastructure changes trigger events for monitoring and compliance
4. **Testable**: All infrastructure code is unit and integration tested

## Prerequisites

- Python 3.11+
- Pulumi CLI
- AWS CLI (for AWS deployments)
- Azure CLI (for Azure deployments)
- Poetry for dependency management

## Getting Started

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Configure cloud providers:
   ```bash
   # AWS
   aws configure
   
   # Azure
   az login
   ```

3. Initialize Pulumi:
   ```bash
   pulumi login
   pulumi stack init dev
   ```

4. Deploy infrastructure:
   ```bash
   # Deploy to AWS
   pulumi up -s aws-dev
   
   # Deploy to Azure
   pulumi up -s azure-dev
   ```

## Components

### REST API Server
- Deployed as serverless functions
- Auto-scaling enabled
- API Gateway integration

### WebSocket Server
- Persistent connections via managed services
- AWS: API Gateway WebSocket + Lambda
- Azure: Web PubSub + Functions

### Shared Components
- Monitoring and logging
- Security policies
- Network configuration
- Cost optimization rules