from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import json


class ArchitectureDomain(BaseDomain):
    """Domain responsible for designing system architectures"""

    def __init__(self, name: str = "architecture", description: str = "Designs system architectures including microservices, cloud, and distributed systems", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.architecture_patterns = [
            "monolithic", "microservices", "event_driven", "layered", 
            "service_oriented", "cloud_native", "distributed", "hybrid"
        ]
        self.tech_stacks = [
            "LAMP", "MEAN", "MERN", "Java Spring", "Python Django", 
            "Ruby on Rails", "Go", "Node.js", ".NET", "Flutter", "React Native"
        ]
        self.cloud_platforms = ["aws", "azure", "gcp", "digitalocean", "linode"]
        self.architecture_templates = {
            "microservices": self._generate_microservices_template,
            "monolithic": self._generate_monolithic_template,
            "event_driven": self._generate_event_driven_template,
            "cloud_native": self._generate_cloud_native_template,
            "distributed": self._generate_distributed_template
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Generate architecture based on the input specification"""
        try:
            # Acquire resources before executing
            if not await self.resource_manager.acquire_resources(self.name):
                return DomainOutput(
                    success=False,
                    error=f"Resource limits exceeded for domain {self.name}"
                )

            try:
                query = input_data.query.lower()
                context = input_data.context
                params = input_data.parameters

                # Determine the type of architecture to design
                arch_pattern = self._determine_architecture_pattern(query)
                tech_stack = params.get("tech_stack", context.get("tech_stack", "python_django"))
                cloud_platform = params.get("cloud_platform", context.get("cloud_platform", "aws"))

                if arch_pattern not in self.architecture_patterns:
                    return DomainOutput(
                        success=False,
                        error=f"Architecture pattern '{arch_pattern}' not supported. Available patterns: {', '.join(self.architecture_patterns)}"
                    )

                # Generate the architecture
                generated_arch = self._generate_architecture(arch_pattern, query, tech_stack, cloud_platform, params)

                # Enhance the architecture if other domains are available
                enhanced_arch = await self._enhance_with_other_domains(generated_arch, input_data)

                return DomainOutput(
                    success=True,
                    data={
                        "architecture": enhanced_arch,
                        "pattern": arch_pattern,
                        "tech_stack": tech_stack,
                        "cloud_platform": cloud_platform,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "enhanced": enhanced_arch != generated_arch
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Architecture design failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest architecture design
        arch_keywords = [
            "design architecture", "system architecture", "architectural design", 
            "microservices", "monolith", "distributed system", "cloud architecture", 
            "system design", "architecture pattern", "tech stack", 
            "infrastructure", "deployment architecture", "network architecture", 
            "database architecture", "api architecture", "service design"
        ]

        return any(keyword in query for keyword in arch_keywords)

    def _determine_architecture_pattern(self, query: str) -> str:
        """Determine what type of architecture pattern to use based on the query"""
        if any(word in query for word in ["microservice", "micro services", "micro-services"]):
            return "microservices"
        elif any(word in query for word in ["monolith", "monolithic", "single application"]):
            return "monolithic"
        elif any(word in query for word in ["event driven", "event-driven", "eventdriven", "pubsub", "message queue"]):
            return "event_driven"
        elif any(word in query for word in ["cloud native", "cloud-native", "container", "kubernetes", "docker"]):
            return "cloud_native"
        elif any(word in query for word in ["distributed", "distributed system", "multi node", "cluster"]):
            return "distributed"
        else:
            return "monolithic"  # Default to monolithic

    def _generate_architecture(self, arch_pattern: str, query: str, tech_stack: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate architecture based on pattern, query, tech stack, and cloud platform"""
        if arch_pattern in self.architecture_templates:
            return self.architecture_templates[arch_pattern](query, tech_stack, cloud_platform, params)
        else:
            return self._generate_generic_architecture(query, arch_pattern, tech_stack, cloud_platform, params)

    def _generate_microservices_template(self, query: str, tech_stack: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate a microservices architecture template based on the query"""
        return f"""# Microservices Architecture Design

## Overview
This document outlines the microservices architecture for {query}.

## Services
### User Service
- Purpose: Handle user management
- Tech Stack: {tech_stack}
- Responsibilities: User registration, authentication, profile management

### Order Service
- Purpose: Handle order processing
- Tech Stack: {tech_stack}
- Responsibilities: Order creation, tracking, fulfillment

### Payment Service
- Purpose: Handle payment processing
- Tech Stack: {tech_stack}
- Responsibilities: Payment processing, refunds, billing

### Inventory Service
- Purpose: Manage inventory
- Tech Stack: {tech_stack}
- Responsibilities: Stock management, product catalog

## Communication
- API Gateway: Manages external requests and routes to appropriate services
- Service Discovery: {cloud_platform} service discovery
- Messaging: Event-driven communication using message queues

## Data Management
- Each service has its own database
- Event Sourcing for audit trails
- CQRS (Command Query Responsibility Segregation) pattern

## Infrastructure
- Container Orchestration: Kubernetes on {cloud_platform}
- Load Balancing: {cloud_platform} load balancer
- Monitoring: Distributed tracing and logging

## Security
- OAuth 2.0/JWT for authentication
- Service mesh for inter-service communication security
- Network segmentation
"""
    
    def _generate_monolithic_template(self, query: str, tech_stack: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate a monolithic architecture template based on the query"""
        return f"""# Monolithic Architecture Design

## Overview
This document outlines the monolithic architecture for {query}.

## Application Structure
### Presentation Layer
- Web UI: Built with modern frontend framework
- API Layer: RESTful APIs for external integrations

### Business Logic Layer
- Core business logic and services
- Transaction management
- Validation and processing

### Data Access Layer
- ORM for database interactions
- Data access objects
- Connection pooling

## Technology Stack
- Backend: {tech_stack}
- Frontend: Modern JavaScript framework
- Database: Relational database ({cloud_platform} RDS)
- Caching: Redis for session and data caching

## Infrastructure
- Deployment: Single application server on {cloud_platform}
- Load Balancing: {cloud_platform} load balancer
- Auto-scaling: Vertical scaling based on demand
- Backup: Automated database backups

## Security
- Authentication: Session-based or JWT
- Authorization: Role-based access control
- Input validation: Sanitization and validation
- HTTPS: Encrypted communication

## Deployment
- CI/CD Pipeline: Automated testing and deployment
- Blue-green deployment for zero-downtime updates
- Health checks and monitoring
"""
    
    def _generate_event_driven_template(self, query: str, tech_stack: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate an event-driven architecture template based on the query"""
        return f"""# Event-Driven Architecture Design

## Overview
This document outlines the event-driven architecture for {query}.

## Components
### Event Producers
- User actions (registration, purchases, etc.)
- System events (order completion, payment processing)
- External integrations

### Event Brokers
- Message Queue: Apache Kafka/RabbitMQ on {cloud_platform}
- Topics/Exchanges for different event types
- Partitioning for scalability

### Event Consumers
- Microservices that react to events
- Analytics systems
- Notification services

## Event Types
### User Events
- UserRegistered
- UserProfileUpdated
- UserDeleted

### Order Events
- OrderCreated
- OrderShipped
- OrderDelivered

### Payment Events
- PaymentProcessed
- PaymentFailed
- RefundInitiated

## Data Flow
1. Event producers publish events to message brokers
2. Event consumers subscribe to relevant topics
3. Consumers process events asynchronously
4. State changes trigger new events

## Infrastructure
- Event Streaming Platform: {cloud_platform} managed service
- Serverless Functions: For lightweight event processing
- Monitoring: Event flow tracking and metrics

## Benefits
- Loose coupling between services
- Scalability through parallel processing
- Resilience to component failures
- Audit trail through event logs
"""
    
    def _generate_cloud_native_template(self, query: str, tech_stack: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate a cloud-native architecture template based on the query"""
        return f"""# Cloud-Native Architecture Design

## Overview
This document outlines the cloud-native architecture for {query}.

## Containerization
### Docker Images
- Application containers with {tech_stack}
- Database containers
- Caching containers
- Monitoring containers

### Container Orchestration
- Kubernetes cluster on {cloud_platform}
- Pod management and scaling
- Service discovery and load balancing

## Microservices
### Service Mesh
- Istio/Linkerd for service-to-service communication
- Traffic management and security
- Observability and policy enforcement

### API Gateway
- Kong/Tyk for API management
- Authentication and rate limiting
- Request routing and transformation

## Infrastructure as Code
### Provisioning
- Terraform for infrastructure provisioning
- Helm charts for Kubernetes deployments
- Version-controlled infrastructure

## Storage
- Object Storage: {cloud_platform} S3 equivalent
- Database: Managed database services
- Caching: Managed Redis/Memcached

## Security
- Container scanning for vulnerabilities
- Network policies for pod communication
- Secrets management with {cloud_platform} KMS
- Identity and access management

## Monitoring
- Prometheus for metrics collection
- Grafana for dashboarding
- ELK stack for logging
- Distributed tracing with Jaeger
"""
    
    def _generate_distributed_template(self, query: str, tech_stack: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate a distributed system architecture template based on the query"""
        return f"""# Distributed System Architecture Design

## Overview
This document outlines the distributed system architecture for {query}.

## Nodes
### Application Nodes
- Multiple application servers for load distribution
- {tech_stack} runtime environment
- Load balancing across nodes

### Database Cluster
- Master-slave replication
- Sharding for horizontal scaling
- Consistency models (strong/eventual)

### Cache Cluster
- Distributed caching with {cloud_platform} managed service
- Session replication
- Data partitioning

## Communication Protocols
### RPC Framework
- gRPC for service-to-service communication
- Protocol Buffers for message serialization
- Bidirectional streaming

### Message Queues
- Apache Kafka/RabbitMQ for asynchronous communication
- Dead letter queues for error handling
- Message ordering guarantees

## Consensus Algorithms
- Raft/etcd for leader election
- Distributed locks for coordination
- Quorum-based decision making

## Fault Tolerance
### Replication
- Data replication across multiple nodes
- Automatic failover mechanisms
- Backup and recovery procedures

### Circuit Breakers
- Prevent cascade failures
- Timeout and retry mechanisms
- Bulkhead isolation

## Scaling Strategies
### Horizontal Scaling
- Add/remove nodes based on demand
- Auto-scaling groups
- Load distribution algorithms

### Vertical Scaling
- Increase node capacity
- Resource allocation optimization
- Performance tuning
"""
    
    def _generate_generic_architecture(self, query: str, arch_pattern: str, tech_stack: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate generic architecture when specific pattern isn't determined"""
        return f"""# Architecture Design

## Overview
This document outlines the {arch_pattern} architecture for {query}.

## Components
- Component 1: Description
- Component 2: Description
- Component 3: Description

## Technology Stack
- Backend: {tech_stack}
- Cloud Platform: {cloud_platform}
- Database: Appropriate database technology
- Caching: Caching solution

## Infrastructure
- Deployment strategy
- Scaling considerations
- Security measures
- Monitoring and logging
"""

    async def _enhance_with_other_domains(self, generated_arch: str, input_data: DomainInput) -> str:
        """Allow other domains to enhance the generated architecture"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original architecture
        return generated_arch