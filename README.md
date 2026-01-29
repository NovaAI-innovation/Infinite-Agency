# Multi-Domain Agency System

A sophisticated multi-domain agency system with advanced capabilities including RAG (Retrieval-Augmented Generation), MCP (Model Context Protocol) integration, and enhanced agent behaviors.

## Features

- **Multi-Domain Architecture**: Support for multiple specialized domains (code generation, research, etc.)
- **RAG System**: Retrieval-Augmented Generation with vector storage and semantic search
- **MCP Integration**: Model Context Protocol support for external tool connectivity
- **Advanced Decision Engine**: Intelligent decision-making with resource awareness
- **Context Management**: Conversation history and state tracking
- **Scalable Communication**: Inter-domain communication hub
- **Resource Management**: Quota-based resource allocation
- **Monitoring & Health Checks**: Comprehensive system monitoring

## Architecture

The system consists of several key components:

- **Domains**: Specialized agents for specific tasks (code generation, research)
- **Coordinators**: Cross-domain task coordination
- **RAG System**: Knowledge retrieval and storage
- **MCP Integration**: External tool connectivity
- **Decision Engine**: Intelligent task routing and resource management
- **Context Manager**: Conversation state management

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from agency import get_agency_components
from agency.core.base_domain import DomainInput

# Get all agency components
(
    registry, coordinator, resource_manager, plugin_manager, config_manager,
    environment_manager, error_handling_manager, retry_executor,
    deployment_manager, deployment_orchestrator, task_lifecycle_manager,
    enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
    distributed_task_manager, security_manager, embedding_service, vector_store,
    knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
) = get_agency_components()

# Example: Generate code
code_input = DomainInput(
    query="generate a python function that calculates fibonacci numbers",
    parameters={"language": "python"}
)

code_domain = registry.get_domain("code_generation")
result = await code_domain.execute(code_input)
```

## Components

### RAG System
- Vector Store: Semantic search with async locking
- Embedding Service: Text embedding with fallback mechanisms
- Knowledge Base: Document storage and retrieval
- Retriever: Query-based document retrieval

### MCP Integration
- HTTP-based MCP client
- Server management
- Tool execution interface
- External service connectivity

### Decision Engine
- Resource-aware policies
- Historical performance evaluation
- Multi-criteria decision making

### Context Management
- Conversation tracking
- Metadata management
- State persistence
- Search capabilities

## Examples

See `example_usage.py` for comprehensive examples demonstrating all features.

## Testing

```bash
python -m pytest test_agency.py
```

## License

MIT