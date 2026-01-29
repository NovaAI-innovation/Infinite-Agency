from .core.domain_registry import get_registry, DomainRegistry
from .domains.code_generation.domain import CodeGenerationDomain
from .domains.research.domain import ResearchDomain
from .domains.documentation.domain import DocumentationDomain
from .domains.architecture.domain import ArchitectureDomain
from .domains.devops.domain import DevOpsDomain
from .domains.frontend.domain import FrontendDomain
from .domains.backend.domain import BackendDomain
from .domains.integrations.domain import IntegrationsDomain
from .domains.data_management.domain import DataManagementDomain
from .domains.communication.domain import CommunicationDomain
from .domains.preferences.domain import PreferencesDomain
from .domains.system_operations.domain import SystemOperationsDomain
from .domains.skill_management.domain import SkillManagementDomain
from .skills.skill_manager import get_skill_manager
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


async def initialize_agency():
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
    registry.register_domain_type("documentation", DocumentationDomain)
    registry.register_domain_type("architecture", ArchitectureDomain)
    registry.register_domain_type("devops", DevOpsDomain)
    registry.register_domain_type("frontend", FrontendDomain)
    registry.register_domain_type("backend", BackendDomain)
    registry.register_domain_type("integrations", IntegrationsDomain)
    registry.register_domain_type("data_management", DataManagementDomain)
    registry.register_domain_type("communication", CommunicationDomain)
    registry.register_domain_type("preferences", PreferencesDomain)
    registry.register_domain_type("system_operations", SystemOperationsDomain)
    registry.register_domain_type("skill_management", SkillManagementDomain)

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

    documentation_domain = registry.create_and_register_domain(
        "documentation",
        "documentation",
        description="Generates project documentation including README, API docs, and technical guides",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for documentation domain
    resource_manager.set_quota(
        "documentation",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    architecture_domain = registry.create_and_register_domain(
        "architecture",
        "architecture",
        description="Designs system architectures including microservices, cloud, and distributed systems",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for architecture domain
    resource_manager.set_quota(
        "architecture",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    devops_domain = registry.create_and_register_domain(
        "devops",
        "devops",
        description="Manages CI/CD pipelines, infrastructure as code, and deployment automation",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for devops domain
    resource_manager.set_quota(
        "devops",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    frontend_domain = registry.create_and_register_domain(
        "frontend",
        "frontend",
        description="Develops frontend applications using modern frameworks and UI/UX best practices",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for frontend domain
    resource_manager.set_quota(
        "frontend",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    backend_domain = registry.create_and_register_domain(
        "backend",
        "backend",
        description="Develops backend services including APIs, databases, and server-side logic",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for backend domain
    resource_manager.set_quota(
        "backend",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    integrations_domain = registry.create_and_register_domain(
        "integrations",
        "integrations",
        description="Manages system integrations including APIs, data flows, and third-party services",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for integrations domain
    resource_manager.set_quota(
        "integrations",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    data_management_domain = registry.create_and_register_domain(
        "data_management",
        "data_management",
        description="Manages comprehensive data including research, databases, documents, indexing, and RAG systems",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for data management domain
    resource_manager.set_quota(
        "data_management",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    communication_domain = registry.create_and_register_domain(
        "communication",
        "communication",
        description="Handles sending notifications to users via agent mail API for task completion, milestones, and other events",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for communication domain
    resource_manager.set_quota(
        "communication",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    preferences_domain = registry.create_and_register_domain(
        "preferences",
        "preferences",
        description="Manages user notification preferences and CRUD operations for notification event preferences",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for preferences domain
    resource_manager.set_quota(
        "preferences",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    system_operations_domain = registry.create_and_register_domain(
        "system_operations",
        "system_operations",
        description="Handles system operations including filesystem operations and file management/directory organization",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for system operations domain
    resource_manager.set_quota(
        "system_operations",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    skill_management_domain = registry.create_and_register_domain(
        "skill_management",
        "skill_management",
        description="Manages skill files across all agents including downloading, installing, copying, and removing skills with marketplace integration",
        resource_manager=resource_manager,
        cache_enabled=environment_manager.get("AGENCY_CACHE_ENABLED", True)
    )

    # Set resource quota for skill management domain
    resource_manager.set_quota(
        "skill_management",
        ResourceQuota(
            cpu_percent=environment_manager.get("AGENCY_RESOURCE_QUOTA_CPU", 50.0),
            memory_mb=environment_manager.get("AGENCY_RESOURCE_QUOTA_MEMORY", 512),
            max_concurrent_tasks=environment_manager.get("AGENCY_MAX_CONCURRENT_TASKS", 10)
        )
    )

    # Register domains with task lifecycle management
    task_lifecycle_manager.register_domain_for_tasks(code_gen_domain)
    task_lifecycle_manager.register_domain_for_tasks(research_domain)
    task_lifecycle_manager.register_domain_for_tasks(documentation_domain)
    task_lifecycle_manager.register_domain_for_tasks(architecture_domain)
    task_lifecycle_manager.register_domain_for_tasks(devops_domain)
    task_lifecycle_manager.register_domain_for_tasks(frontend_domain)
    task_lifecycle_manager.register_domain_for_tasks(backend_domain)
    task_lifecycle_manager.register_domain_for_tasks(integrations_domain)
    task_lifecycle_manager.register_domain_for_tasks(data_management_domain)
    task_lifecycle_manager.register_domain_for_tasks(communication_domain)
    task_lifecycle_manager.register_domain_for_tasks(preferences_domain)
    task_lifecycle_manager.register_domain_for_tasks(system_operations_domain)
    task_lifecycle_manager.register_domain_for_tasks(skill_management_domain)

    # Set up dependencies if needed
    # For example, research domain might enhance code generation
    # code_gen_domain.add_dependency(research_domain)

    # Register domains with the communication hub
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(communication_hub.register_domain("code_generation"))
    loop.run_until_complete(communication_hub.register_domain("research"))
    loop.run_until_complete(communication_hub.register_domain("documentation"))
    loop.run_until_complete(communication_hub.register_domain("architecture"))
    loop.run_until_complete(communication_hub.register_domain("devops"))
    loop.run_until_complete(communication_hub.register_domain("frontend"))
    loop.run_until_complete(communication_hub.register_domain("backend"))
    loop.run_until_complete(communication_hub.register_domain("integrations"))
    loop.run_until_complete(communication_hub.register_domain("data_management"))
    loop.run_until_complete(communication_hub.register_domain("communication"))
    loop.run_until_complete(communication_hub.register_domain("preferences"))
    loop.run_until_complete(communication_hub.register_domain("system_operations"))
    loop.run_until_complete(communication_hub.register_domain("skill_management"))

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

    # Initialize skill manager and load skills
    skill_manager = get_skill_manager()

    # Load skills from the skills directory
    import os
    skills_dir = os.path.join(os.path.dirname(__file__), '..', 'skills')
    if os.path.exists(skills_dir):
        loaded_skills = await skill_manager.load_skills_from_directory(skills_dir)
        print(f"Loaded {len(loaded_skills)} skills: {loaded_skills}")

    # Apply relevant skills to each domain
    await skill_manager.apply_skills_to_domain(code_gen_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["code_generation", "programming", "development", ""]
    ])

    await skill_manager.apply_skills_to_domain(research_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["research", "data_management", "analysis", ""]
    ])

    await skill_manager.apply_skills_to_domain(documentation_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["documentation", "writing", "content", ""]
    ])

    await skill_manager.apply_skills_to_domain(architecture_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["architecture", "design", "planning", ""]
    ])

    await skill_manager.apply_skills_to_domain(devops_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["devops", "infrastructure", "deployment", ""]
    ])

    await skill_manager.apply_skills_to_domain(frontend_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["frontend", "ui", "ux", "web", ""]
    ])

    await skill_manager.apply_skills_to_domain(backend_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["backend", "api", "server", "database", ""]
    ])

    await skill_manager.apply_skills_to_domain(integrations_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["integrations", "api", "connectivity", ""]
    ])

    await skill_manager.apply_skills_to_domain(data_management_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["data_management", "database", "documents", "indexing", "rag", "research", ""]
    ])

    await skill_manager.apply_skills_to_domain(communication_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["communication", "notifications", "messaging", ""]
    ])

    await skill_manager.apply_skills_to_domain(preferences_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["preferences", "settings", "configuration", ""]
    ])

    await skill_manager.apply_skills_to_domain(system_operations_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["system_operations", "filesystem", "admin", ""]
    ])

    await skill_manager.apply_skills_to_domain(skill_management_domain, [
        skill_name for skill_name in skill_manager.skills.keys()
        if skill_manager.get_skill(skill_name).domain_type in ["skill_management", "skills", "marketplace", "plugins", ""]
    ])

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
import asyncio

# Create a function to get the event loop and initialize the agency
def _initialize_agency_sync():
    """Synchronous wrapper for initializing the agency"""
    try:
        loop = asyncio.get_running_loop()
        # If there's already a running loop, we need to use run_coroutine_threadsafe or similar
        import threading
        result = [None]
        exception = [None]

        def run_in_thread():
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result[0] = new_loop.run_until_complete(initialize_agency())
            except Exception as e:
                exception[0] = e
            finally:
                new_loop.close()

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()

        if exception[0]:
            raise exception[0]
        return result[0]
    except RuntimeError:
        # No event loop running, we can use run
        return asyncio.run(initialize_agency())

(
    registry, coordinator, resource_manager, plugin_manager, config_manager,
    environment_manager, error_handling_manager, retry_executor,
    deployment_manager, deployment_orchestrator, task_lifecycle_manager,
    enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
    distributed_task_manager, security_manager, embedding_service, vector_store,
    knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
) = _initialize_agency_sync()


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