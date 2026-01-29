# Multi-Domain Agency System - QWEN Context

## Project Overview

The Multi-Domain Agency System is a sophisticated Python-based framework that implements a multi-domain architecture with advanced capabilities including RAG (Retrieval-Augmented Generation), MCP (Model Context Protocol) integration, and enhanced agent behaviors. The system is designed to be scalable, resilient, and production-ready with comprehensive monitoring, security, and orchestration features.

### Key Features
- **Multi-Domain Architecture**: Support for multiple specialized domains (code generation, research, etc.)
- **RAG System**: Retrieval-Augmented Generation with vector storage and semantic search
- **MCP Integration**: Model Context Protocol support for external tool connectivity
- **Advanced Decision Engine**: Intelligent decision-making with resource awareness
- **Context Management**: Conversation history and state tracking
- **Scalable Communication**: Inter-domain communication hub
- **Resource Management**: Quota-based resource allocation
- **Monitoring & Health Checks**: Comprehensive system monitoring
- **Workflow Orchestration**: Complex multi-step process management
- **Distributed Task Execution**: Horizontal scaling across multiple nodes
- **Security & Authentication**: JWT tokens, role-based permissions, rate limiting

### Architecture Components
- **Domains**: Specialized agents for specific tasks (code generation, research)
- **Coordinators**: Cross-domain task coordination
- **RAG System**: Knowledge retrieval and storage
- **MCP Integration**: External tool connectivity
- **Decision Engine**: Intelligent task routing and resource management
- **Context Manager**: Conversation state management
- **Workflow Engine**: Multi-step process orchestration
- **Security Manager**: Authentication and authorization
- **Monitoring Service**: System health and metrics

## Building and Running

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
pip install -r requirements.txt
```

### Running the System
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

### Testing
```bash
python -m pytest test_agency.py
```

Or run the example:
```bash
python example_usage.py
```

## Development Conventions

### Code Structure
- `agency/core/` - Core framework components (domains, communication, resource management)
- `agency/domains/` - Specific domain implementations (code generation, research)
- `agency/rags/` - RAG system components
- `agency/mcp/` - Model Context Protocol integration
- `agency/decision/` - Decision engine components
- `agency/context/` - Context management system

### Async/Await Patterns
All domain operations must be asynchronous and follow proper async/await patterns. Use `execute_with_cache()` for operations that benefit from caching.

### Error Handling
The system implements comprehensive error handling with retry mechanisms, circuit breakers, and graceful degradation. All domain operations should return `DomainOutput` objects with appropriate success/error states.

### Resource Management
Domains should respect resource quotas and implement proper resource acquisition/release patterns. The system provides automatic resource management through the `ResourceManager`.

### Testing
All components should have corresponding unit tests. The system includes comprehensive testing infrastructure with async test support.

## Key Dependencies
- `aiohttp` - Async HTTP client/server
- `numpy` - Numerical computing
- `requests` - HTTP requests
- `sentence-transformers` - Text embeddings
- `pytest` - Testing framework
- `pytest-asyncio` - Async testing support
- `bcrypt` - Password hashing
- `PyJWT` - JSON Web Token support

## Advanced Capabilities

### Workflow Orchestration
The system includes a full-featured workflow engine with support for task, decision, join, fork, and merge nodes, allowing for complex multi-step processes with conditional execution paths.

### Distributed Computing
Support for distributed task execution across multiple nodes with worker registration, load balancing, and task scheduling capabilities.

### Security Framework
Comprehensive security with JWT tokens, role-based permissions (READ, WRITE, EXECUTE), rate limiting, and password hashing.

### Monitoring & Alerting
Built-in monitoring with metric collection, threshold-based alerts, and health checking capabilities for operational visibility.

### Plugin Architecture
Extensible plugin system for easy domain addition with dynamic loading and directory-based discovery.