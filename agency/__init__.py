from .core.domain_registry import get_registry, DomainRegistry
from .domains.code_generation.domain import CodeGenerationDomain
from .domains.research.domain import ResearchDomain
from .core.coordinator import CrossDomainCoordinator
from .core.scalable_communication import communication_hub
from .core.config import get_config_manager
from .core.plugin_manager import get_plugin_manager
from .core.resource_management import ResourceManager, ResourceQuota
from .core.environment import get_environment_manager
from .core.error_handling import get_error_handling_manager, get_retry_executor
from .core.deployment import get_deployment_manager, get_deployment_orchestrator
from .core.task_lifecycle import get_task_lifecycle_manager
from .core.output_enhancement import get_enhancement_pipeline
from .core.advanced_monitoring import get_monitoring_service, HealthChecker
from .core.workflow_engine import get_workflow_orchestrator
from .core.distributed_task_execution import get_distributed_task_manager
from .core.security import get_security_manager
from .rag import initialize_rag_system
from .mcp import get_mcp_manager, get_mcp_integration
from .decision import get_decision_engine
from .context import get_context_manager


def initialize_agency():
    """Initialize the multi-domain agency with default domains"""
    # Load configuration first
    config_manager = get_config_manager()

    # Initialize all components
    registry = get_registry()
    resource_manager = ResourceManager()
    plugin_manager = get_plugin_manager()
    environment_manager = get_environment_manager()
    error_handling_manager = get_error_handling_manager()
    retry_executor = get_retry_executor()
    deployment_manager = get_deployment_manager()
    deployment_orchestrator = get_deployment_orchestrator()
    task_lifecycle_manager = get_task_lifecycle_manager()
    monitoring_service = get_monitoring_service()

    # Initialize RAG system
    embedding_service, vector_store, knowledge_base, retriever = initialize_rag_system()

    # Initialize MCP manager
    mcp_manager = get_mcp_manager()

    # Initialize decision engine
    decision_engine = get_decision_engine()

    # Initialize context manager
    context_manager = get_context_manager()

    # Initialize MCP integration
    mcp_integration = get_mcp_integration()

    # Register domain types
    registry.register_domain_type("code_generation", CodeGenerationDomain)
    registry.register_domain_type("research", ResearchDomain)

    # Create and register domain instances with resource quotas
    code_gen_domain = registry.create_and_register_domain(
        "code_generation",
        "code_generation",
        description="Generates code in various programming languages",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for code generation domain
    resource_manager.set_quota(
        "code_generation",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    research_domain = registry.create_and_register_domain(
        "research",
        "research",
        description="Conducts research and gathers information from various sources",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for research domain
    resource_manager.set_quota(
        "research",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    # Register domains with task lifecycle management
    task_lifecycle_manager.register_domain_for_tasks(code_gen_domain)
    task_lifecycle_manager.register_domain_for_tasks(research_domain)

    # Set up dependencies if needed
    # For example, research domain might enhance code generation
    # code_gen_domain.add_dependency(research_domain)

    # Register domains with the communication hub
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(communication_hub.register_domain("code_generation"))
    loop.run_until_complete(communication_hub.register_domain("research"))

    # Initialize enhancement pipeline
    enhancement_pipeline = get_enhancement_pipeline(registry)

    # Initialize health checker
    health_checker = HealthChecker(registry, task_lifecycle_manager)

    # Initialize workflow orchestrator
    workflow_orchestrator = get_workflow_orchestrator(task_lifecycle_manager)

    # Initialize distributed task manager
    distributed_task_manager = get_distributed_task_manager()

    # Initialize security manager
    security_manager = get_security_manager()

    # Configure monitoring service
    monitoring_service.set_metrics_collector(None)  # Will be set to actual collector

    # Add some default alert rules
    from .core.advanced_monitoring import AlertRule, AlertType, AlertSeverity
    monitoring_service.create_alert_rule_from_threshold(
        name="high_error_rate",
        metric_name="error_rate",
        condition="gt",
        threshold=0.1,  # More than 10% error rate
        alert_type=AlertType.ERROR_RATE,
        severity=AlertSeverity.HIGH,
        notification_channels=["console"]
    )

    # Start monitoring (deferred to when the event loop is properly running)
    # Monitoring will be started by the application when needed

    # Return coordinator for managing cross-domain tasks
    coordinator = CrossDomainCoordinator(registry)

    return (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    )


# Initialize the agency when this module is imported
(
    registry, coordinator, resource_manager, plugin_manager, config_manager,
    environment_manager, error_handling_manager, retry_executor,
    deployment_manager, deployment_orchestrator, task_lifecycle_manager,
    enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
    distributed_task_manager, security_manager, embedding_service, vector_store,
    knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
) = initialize_agency()


def get_agency_components():
    """Get the initialized agency components"""
    return (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    )