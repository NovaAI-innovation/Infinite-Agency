#!/usr/bin/env python3
"""
Example usage of the multi-domain agency system.
This demonstrates how code generation and research domains can work together.
"""

import asyncio
from agency import get_agency_components
from agency.core.base_domain import DomainInput
from agency.core.task_lifecycle import TaskPriority


async def main():
    print("Initializing multi-domain agency...")
    (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    ) = get_agency_components()

    print("\nAvailable domains:")
    for domain in registry.get_all_domains():
        print(f"- {domain.name}: {domain.description}")

    print("\nResource quotas:")
    for domain_name in ["code_generation", "research"]:
        quota = resource_manager.get_quota(domain_name)
        if quota:
            print(f"- {domain_name}: CPU={quota.cpu_percent}%, Memory={quota.memory_mb}MB, Max tasks={quota.max_concurrent_tasks}")

    print("\nEnvironment variables:")
    env_vars = environment_manager.get_all_defined()
    for name, value in list(env_vars.items())[:5]:  # Show first 5 variables
        print(f"- {name}: {value}")

    print("\n" + "="*60)
    print("EXAMPLE 1: Code Generation")
    print("="*60)

    # Example 1: Code generation
    code_input = DomainInput(
        query="generate a python function that calculates fibonacci numbers",
        parameters={"language": "python"}
    )

    code_domain = registry.get_domain("code_generation")
    if code_domain and code_domain.can_handle(code_input):
        print(f"Executing code generation for: {code_input.query}")
        result = await code_domain.execute(code_input)

        if result.success:
            print("Generated code:")
            print(result.data["code"])
        else:
            print(f"Code generation failed: {result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 2: Research")
    print("="*60)

    # Example 2: Research
    research_input = DomainInput(
        query="research the benefits of using microservices architecture",
        parameters={"method": "literature_review"}
    )

    research_domain = registry.get_domain("research")
    if research_domain and research_domain.can_handle(research_input):
        print(f"Conducting research for: {research_input.query}")
        result = await research_domain.execute(research_input)

        if result.success:
            print("Research summary:", result.data["summary"])
            print("Key findings:", result.data["key_findings"])
        else:
            print(f"Research failed: {result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 3: Cross-Domain Coordination")
    print("="*60)

    # Example 3: Cross-domain coordination
    print("Executing cross-domain workflow...")

    workflow = [
        {
            "domain": "research",
            "query": "research best practices for API design",
            "parameters": {"method": "literature_review"}
        },
        {
            "domain": "code_generation",
            "query": "generate a python API endpoint based on best practices for API design",
            "parameters": {"language": "python"}
        }
    ]

    workflow_result = await coordinator.execute_multi_domain_workflow(workflow)

    if workflow_result.success:
        print("Cross-domain workflow completed successfully!")
        print("Final result keys:", list(workflow_result.data.keys()))
    else:
        print(f"Cross-domain workflow failed: {workflow_result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 4: Enhancement Request")
    print("="*60)

    # Example 4: Enhancement using coordinator
    print("Testing enhancement capability...")

    # First, generate some code
    code_input = DomainInput(
        query="generate a basic python calculator class",
        parameters={"language": "python", "type": "class"}
    )

    primary_result = await code_domain.execute(code_input)

    if primary_result.success:
        print("Original code generated, now applying enhancements...")

        # Create input for enhancement
        enhancement_input = DomainInput(
            query="enhance the calculator class with error handling and logging",
            context={"primary_result": primary_result},
            parameters={"language": "python"}
        )

        # Execute with enhancement
        enhanced_result = await coordinator.execute_with_enhancement("code_generation", enhancement_input)

        if enhanced_result.success:
            print("Enhanced code generated successfully!")
            print("Enhanced code preview:")
            preview = str(enhanced_result.data["code"])[:500] + "..." if len(str(enhanced_result.data["code"])) > 500 else str(enhanced_result.data["code"])
            print(preview)
        else:
            print(f"Enhancement failed: {enhanced_result.error}")
    else:
        print(f"Initial code generation failed: {primary_result.error}")

    print("\n" + "="*60)
    print("EXAMPLE 5: Task Lifecycle Management")
    print("="*60)

    # Example 5: Using task lifecycle management
    print("Submitting tasks with lifecycle management...")

    # Submit a task to the code generation domain
    result = await task_lifecycle_manager.execute_task(
        "code_generation",
        DomainInput(
            query="generate a simple python function to reverse a string",
            parameters={"language": "python"}
        ),
        priority=TaskPriority.NORMAL
    )

    if result and result.success:
        print("Task lifecycle management result:")
        print(result.data["code"][:200] + "..." if len(result.data["code"]) > 200 else result.data["code"])
    else:
        print("Task lifecycle management failed")

    print("\n" + "="*60)
    print("EXAMPLE 6: Health Check")
    print("="*60)

    # Example 6: Health checking
    print("Performing system health check...")
    health_report = await health_checker.check_system_health()
    print(f"Overall system status: {health_report['overall_status']}")
    print(f"Health check timestamp: {health_report['timestamp']}")
    print(f"Issues found: {len(health_report['issues'])}")
    if health_report['issues']:
        for issue in health_report['issues']:
            print(f"  - {issue}")

    print("\n" + "="*60)
    print("EXAMPLE 7: Workflow Orchestration")
    print("="*60)

    # Example 7: Workflow orchestration
    print("Creating and executing a simple workflow...")

    from agency.core.workflow_engine import WorkflowBuilder

    # Create a simple workflow: research -> code generation
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("simple_workflow", "Simple Research-to-Code Workflow")
        .add_task("research_step", "Research Step", "research", {
            "query": "research best practices for secure coding",
            "parameters": {"method": "literature_review"}
        })
        .add_task("code_step", "Code Generation Step", "code_generation", {
            "query": "generate a python function implementing secure coding best practices",
            "parameters": {"language": "python"}
        })
        .connect("research_step", "code_step")  # Connect research to code generation
        .set_end_nodes(["code_step"])  # Set code generation as the end node
        .build()
    )

    # Register the workflow definition
    workflow_orchestrator.register_definition(workflow_def)

    # Create and start a workflow instance
    instance_id = workflow_orchestrator.create_instance("simple_workflow")
    await workflow_orchestrator.start_instance(instance_id)

    # Wait a bit for the workflow to complete
    await asyncio.sleep(2)

    # Check the status
    status = await workflow_orchestrator.get_instance_status(instance_id)
    print(f"Workflow instance {instance_id} status: {status.state.value}")
    print(f"Completed nodes: {status.completed_nodes}")
    print(f"Total execution time: {status.completed_at - status.started_at if status.completed_at and status.started_at else 'N/A'}")

    print("\n" + "="*60)
    print("EXAMPLE 8: Distributed Task Execution")
    print("="*60)

    # Example 8: Distributed task execution
    print("Initializing distributed task execution...")

    # Initialize the local worker
    await distributed_task_manager.initialize_local_worker(
        worker_id="local_worker_1",
        capabilities=["code_generation", "research"]
    )

    # Submit a task for distributed execution
    task_id = distributed_task_manager.submit_task(
        domain="code_generation",
        input_data=DomainInput(
            query="generate a simple python function to calculate factorial",
            parameters={"language": "python"}
        ),
        priority=1
    )

    print(f"Submitted distributed task with ID: {task_id}")

    # Wait for the task to complete
    await asyncio.sleep(3)

    # Get the result
    result = distributed_task_manager.get_task_result(task_id)
    if result:
        print(f"Distributed task result: {result.success}")
        if result.success:
            print("Result data:", result.data)
    else:
        print("Task not completed yet or failed")

    # Get distributed system stats
    stats = await distributed_task_manager.get_distributed_stats()
    print(f"Distributed system stats: {stats['total_workers']} workers, {stats['pending_tasks']} pending tasks")

    print("\n" + "="*60)
    print("EXAMPLE 9: Security and Authentication")
    print("="*60)

    # Example 9: Security and authentication
    print("Setting up security and authentication...")

    from agency.core.security import Permission

    # Create a user with specific permissions
    user = security_manager.create_user(
        username="alice",
        email="alice@example.com",
        password="securepassword123",
        permissions=[Permission.READ, Permission.WRITE, Permission.EXECUTE]
    )

    print(f"Created user: {user.username} with ID: {user.id}")

    # Authenticate the user
    authenticated_user = security_manager.authenticate_basic("alice", "securepassword123")
    print(f"User {authenticated_user.username} authenticated successfully")

    # Create a JWT token for the user
    jwt_token = security_manager.create_jwt_token(authenticated_user.id)
    print(f"JWT token created for user: {authenticated_user.username}")

    # Verify the token
    verified_user = security_manager.verify_jwt_token(jwt_token)
    print(f"Token verified for user: {verified_user.username}")

    # Check permissions
    has_execute = security_manager.check_permission(verified_user, Permission.EXECUTE)
    print(f"User has EXECUTE permission: {has_execute}")

    # Test rate limiting
    is_allowed = security_manager.rate_limit("alice_ip", max_requests=5, window=60)
    print(f"Rate limit check for alice_ip: {is_allowed}")

    print("\n" + "="*60)
    print("EXAMPLE 10: RAG System Integration")
    print("="*60)

    # Example 10: RAG system integration
    print("Testing RAG (Retrieval-Augmented Generation) system...")

    # Add some sample documents to the knowledge base
    sample_docs = [
        {
            "content": "Microservices architecture is a software development technique that structures an application as a collection of loosely coupled services.",
            "metadata": {"source": "architecture_guide", "category": "microservices"}
        },
        {
            "content": "API best practices include using consistent naming conventions, implementing proper error handling, and documenting endpoints thoroughly.",
            "metadata": {"source": "api_design", "category": "best_practices"}
        },
        {
            "content": "Secure coding practices involve input validation, proper authentication, and protection against common vulnerabilities like SQL injection.",
            "metadata": {"source": "security_guide", "category": "security"}
        }
    ]

    # Add documents to knowledge base
    add_results = await knowledge_base.add_documents(sample_docs)
    print(f"Added {sum(add_results)} documents to knowledge base")

    # Search for relevant information
    search_results = await retriever.retrieve("best practices for API design", top_k=2)
    print(f"Found {len(search_results)} relevant documents for 'best practices for API design'")
    for i, result in enumerate(search_results):
        print(f"  Result {i+1} (score: {result.score:.2f}): {result.content[:100]}...")

    print("\n" + "="*60)
    print("EXAMPLE 11: Decision Engine")
    print("="*60)

    # Example 11: Decision engine
    print("Testing decision engine with improved decision-making...")

    from agency.decision import DecisionContext, DecisionOutcome

    # Create a decision context
    context = DecisionContext(
        query="generate a complex algorithm for data processing",
        domain="code_generation",
        available_resources={
            "cpu_percent": 60.0,
            "memory_mb": 400.0
        },
        historical_performance={
            "code_generation": {
                "success_rate": 0.85,
                "avg_response_time": 5.2
            }
        },
        current_state={"active_tasks": 3, "queue_length": 2},
        external_factors={"priority": "high", "deadline": "urgent"}
    )

    # Make a decision using the decision engine
    decision_result = decision_engine.make_decision(context)
    print(f"Decision outcome: {decision_result.outcome.value}")
    print(f"Confidence: {decision_result.confidence:.2f}")
    print(f"Reasoning: {decision_result.reasoning}")
    print(f"Recommended action: {decision_result.recommended_action}")

    print("\n" + "="*60)
    print("EXAMPLE 12: MCP Integration")
    print("="*60)

    # Example 12: MCP integration
    print("Testing MCP (Model Context Protocol) integration...")

    # Note: This is a demonstration - in a real implementation, you would connect to actual MCP servers
    print("MCP manager initialized with support for external tool integration")
    print("Available tools across registered servers:", len(mcp_manager.get_all_tools()))

    print("\n" + "="*60)
    print("EXAMPLE 13: Context Management")
    print("="*60)

    # Example 13: Context management
    print("Testing context management for agent conversations...")

    # Create a new conversation
    conversation_id = "test_conv_001"
    participants = ["user_alice", "assistant_bob"]
    await context_manager.create_conversation(conversation_id, participants, tags=["testing", "demo"])

    # Add some turns to the conversation
    await context_manager.add_turn(conversation_id, "user", "Hello, can you help me with Python code generation?")
    await context_manager.add_turn(conversation_id, "assistant", "Of course! I can help you generate Python code. What specifically do you need?")
    await context_manager.add_turn(conversation_id, "user", "I need a function to calculate factorials")

    # Retrieve the conversation
    conversation = await context_manager.get_conversation(conversation_id)
    print(f"Conversation {conversation_id} has {len(conversation.turns)} turns")

    # Get recent turns
    recent_turns = await context_manager.get_recent_turns(conversation_id, count=2)
    print(f"Recent turns in conversation:")
    for turn in recent_turns:
        print(f"  {turn.role}: {turn.content[:50]}...")

    # Search conversations
    search_results = await context_manager.search_conversations("Python", tags=["testing"])
    print(f"Found {len(search_results)} conversations matching 'Python' with 'testing' tag")

    # Update conversation metadata
    await context_manager.update_metadata(conversation_id, {"topic": "code_generation", "status": "active"})
    print("Updated conversation metadata")

    print("\n" + "="*60)
    print("EXAMPLE 14: MCP Integration Points")
    print("="*60)

    # Example 14: MCP integration points
    print("Testing MCP integration with external tools...")

    # Note: This is a demonstration - in a real implementation, you would connect to actual MCP servers
    print("MCP integration initialized with support for external tool integration")
    print("Available tools across registered servers:", len(mcp_manager.get_all_tools()))

    # Demonstrate registering a mock external tool server
    # In a real scenario, this would connect to an actual external service
    print("Demonstrating MCP integration capabilities:")
    print("- Register external tools via MCP protocol")
    print("- Execute external tools through standardized interface")
    print("- Retrieve tool results and integrate with agency workflows")

    # Show available external tools (would be populated when actual servers are registered)
    all_tools = mcp_integration.get_available_external_tools("example_server") if "example_server" in mcp_manager.clients else []
    print(f"Available external tools from example server: {len(all_tools)}")

    print("\nMCP integration demonstrated successfully!")


if __name__ == "__main__":
    asyncio.run(main())