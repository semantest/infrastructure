# Architecture Overview

## PythonEDA-Style Infrastructure as Code

This infrastructure project follows the PythonEDA (Python Event-Driven Architecture) pattern to create a clean, maintainable, and extensible infrastructure codebase.

### Key Design Decisions

1. **Domain-Driven Design**: Infrastructure components are modeled as domain entities
2. **Provider Abstraction**: Cloud-specific details are isolated in provider modules
3. **Shared Components**: Common patterns are abstracted for reuse across providers
4. **Type Safety**: Pydantic models ensure configuration validity
5. **Event-Driven**: Infrastructure changes can trigger events for monitoring

### Architecture Layers

```
┌─────────────────────────────────────────┐
│           Pulumi Program                │
│         (__main__.py)                   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│          Domain Layer                   │
│   (Entities & Value Objects)           │
│                                        │
│  • FunctionApp                         │
│  • ApiEndpoint                         │
│  • WebSocketEndpoint                   │
│  • CloudProvider, Region, etc.         │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Infrastructure Layer              │
│                                        │
│  ┌─────────────┐ ┌─────────────┐      │
│  │  AWS Stack  │ │ Azure Stack │      │
│  │             │ │             │      │
│  │ • Lambda    │ │ • Functions │      │
│  │ • API GW    │ │ • API Mgmt  │      │
│  │ • WebSocket │ │ • Web PubSub│      │
│  └──────┬──────┘ └──────┬──────┘      │
│         │               │              │
│         └───────┬───────┘              │
│                 │                      │
│         ┌───────▼────────┐             │
│         │ Shared Base    │             │
│         │ Components     │             │
│         └────────────────┘             │
└─────────────────────────────────────────┘
```

### Provider Abstraction

The same domain model deploys to different clouds:

```python
# Domain model
app = FunctionApp(
    name="semantest-api",
    runtime=FunctionRuntime.NODEJS20,
    handler="index.handler"
)

# AWS deployment
lambda_function = aws.lambda_.Function(
    name=app.name,
    runtime=app.get_provider_specific_config(CloudProvider.AWS)["runtime"],
    ...
)

# Azure deployment  
function_app = azure.web.WebApp(
    name=app.name,
    site_config=azure.web.SiteConfigArgs(
        linux_fx_version=app.get_provider_specific_config(CloudProvider.AZURE)["runtime"],
        ...
    )
)
```

### Benefits

1. **Portability**: Easy to add new cloud providers
2. **Testability**: Domain logic can be unit tested without cloud dependencies
3. **Maintainability**: Clear separation of concerns
4. **Type Safety**: Catch configuration errors at development time
5. **Reusability**: Share common patterns across providers

### Next Steps

As requested by Aria, the architecture is designed to:
- Minimize provider-specific code
- Maximize code reuse between AWS and Azure
- Enable easy addition of new providers
- Support both REST and WebSocket workloads