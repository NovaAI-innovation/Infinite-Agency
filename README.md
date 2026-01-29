# Multi-Domain Agency System

A sophisticated multi-domain agency system with advanced capabilities including RAG (Retrieval-Augmented Generation), MCP (Model Context Protocol) integration, and enhanced agent behaviors.

## Features

- **Multi-Domain Architecture**: Support for multiple specialized domains (code generation, research, documentation, architecture, devops, frontend, backend, integrations, data management, communication, preferences, system operations, skill management)
- **RAG System**: Retrieval-Augmented Generation with vector storage and semantic search
- **MCP Integration**: Model Context Protocol support for external tool connectivity
- **Advanced Decision Engine**: Intelligent decision-making with resource awareness
- **Context Management**: Conversation history and state tracking
- **Scalable Communication**: Inter-domain communication hub
- **Resource Management**: Quota-based resource allocation
- **Monitoring & Health Checks**: Comprehensive system monitoring
- **Skill Management**: Centralized skill management with marketplace integration
- **System Operations**: Filesystem operations and directory organization

## Architecture

The system consists of several key components:

- **Domains**: Specialized agents for specific tasks (code generation, research, documentation, architecture, devops, frontend, backend, integrations, data management, communication, preferences, system operations, skill management)
- **Coordinators**: Cross-domain task coordination
- **RAG System**: Knowledge retrieval and storage
- **MCP Integration**: External tool connectivity
- **Decision Engine**: Intelligent task routing and resource management
- **Context Manager**: Conversation state management
- **Skill Manager**: Centralized skill management with marketplace integration
- **Resource Manager**: Quota-based resource allocation

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Setup
```bash
pip install -r requirements.txt
```

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd agency

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
python -m pytest test_agency.py
```

## Usage

### Basic Usage
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

### Working with Different Domains

#### Code Generation Domain
```python
from agency.core.base_domain import DomainInput

# Generate code in different languages
code_input = DomainInput(
    query="create a React component for a button",
    parameters={"language": "javascript", "framework": "react"}
)

code_domain = registry.get_domain("frontend")
result = await code_domain.execute(code_input)
```

#### Documentation Domain
```python
# Generate documentation
doc_input = DomainInput(
    query="create a README for a Python project",
    parameters={"format": "markdown"}
)

doc_domain = registry.get_domain("documentation")
result = await doc_domain.execute(doc_input)
```

#### Architecture Domain
```python
# Design system architecture
arch_input = DomainInput(
    query="design a microservices architecture for an e-commerce platform",
    parameters={"pattern": "microservices", "cloud_platform": "aws"}
)

arch_domain = registry.get_domain("architecture")
result = await arch_domain.execute(arch_input)
```

#### Skill Management
```python
# Manage skills across agents
skill_input = DomainInput(
    query="install python development skills to the code generation agent",
    parameters={
        "skill_name": "python_development",
        "target_agent": "code_generation"
    }
)

skill_mgmt_domain = registry.get_domain("skill_management")
result = await skill_mgmt_domain.execute(skill_input)
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

### Skill Management
- Marketplace integration for skill discovery
- Skill installation, removal, and copying between agents
- Skill export/import functionality
- Version management and updates

### System Operations
- Filesystem operations (create, read, write, delete, copy, move)
- Directory operations (create, delete, list, navigate)
- File management (organize by extension, date, type)
- Directory organization (project structures, standardization)
- Backup and restore operations
- File search capabilities
- Permissions management

## Domains Overview

### Core Domains
- **Code Generation**: Generates code in various programming languages
- **Research**: Conducts research and gathers information from various sources
- **Documentation**: Generates project documentation including README, API docs, and technical guides
- **Architecture**: Designs system architectures including microservices, cloud, and distributed systems
- **DevOps**: Manages CI/CD pipelines, infrastructure as code, and deployment automation

### Specialized Domains
- **Frontend**: Develops frontend applications using modern frameworks and UI/UX best practices
- **Backend**: Develops backend services including APIs, databases, and server-side logic
- **Integrations**: Manages system integrations including APIs, data flows, and third-party services
- **Data Management**: Manages comprehensive data including research, databases, documents, indexing, and RAG systems

### Utility Domains
- **Communication**: Handles sending notifications to users via agent mail API for task completion, milestones, and other events
- **Preferences**: Manages user notification preferences and CRUD operations for notification event preferences
- **System Operations**: Handles system operations including filesystem operations and file management/directory organization
- **Skill Management**: Manages skill files across all agents including downloading, installing, copying, and removing skills with marketplace integration

## Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker build -t agency-system .
docker run -p 8000:8000 agency-system

# Or use docker-compose for full setup
docker-compose up -d
```

### Production Deployment
```bash
# Using Gunicorn for production
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

### Kubernetes Deployment
See `k8s/` directory for Kubernetes manifests.

## Configuration

The system can be configured using environment variables:

```bash
# Resource quotas
AGENCY_RESOURCE_QUOTA_CPU=80.0
AGENCY_RESOURCE_QUOTA_MEMORY=1024
AGENCY_MAX_CONCURRENT_TASKS=20

# Caching
AGENCY_CACHE_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest test_agency.py

# Run with coverage
python -m pytest --cov=agency test_agency.py

# Run specific test
python -m pytest test_agency.py::TestMultiDomainAgency::test_code_generation_domain
```

### Test Coverage
The system includes comprehensive tests covering:
- All domain functionality
- Cross-domain workflows
- Resource management
- RAG system components
- Context management
- Skill management operations

## Development

### Adding New Domains
To add a new domain:

1. Create a new domain class extending `BaseDomain`
2. Implement the required methods (`execute`, `can_handle`)
3. Register the domain in the main `__init__.py` file
4. Add tests for the new domain

### Adding Skills
Skills can be added as YAML or JSON files in the `skills/` directory:

```yaml
name: "python_development"
description: "Skills for Python development including best practices"
version: "1.0.0"
domain_type: "code_generation"
capabilities:
  - "python_code_generation"
  - "python_best_practices"
knowledge_base:
  common_patterns:
    - "Use list comprehensions for simple iterations"
behaviors:
  code_style: "pep8_compliant"
```

### Best Practices
- Follow async/await patterns consistently
- Implement proper error handling and resource management
- Use type hints for all functions and methods
- Write comprehensive tests for new functionality
- Document new components and features

## Examples

See `example_usage.py` for comprehensive examples demonstrating all features.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT