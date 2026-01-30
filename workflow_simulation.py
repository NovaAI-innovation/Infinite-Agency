#!/usr/bin/env python3
"""
Workflow Simulation for Validation
This script simulates various workflow scenarios to validate the workflow engine functionality.
"""

import asyncio
import time
from datetime import datetime
from agency import get_agency_components
from agency.core.base_domain import DomainInput
from agency.core.workflow_engine import WorkflowBuilder, WorkflowNodeType
from agency.core.task_lifecycle import TaskPriority


async def simulate_simple_workflow():
    """Simulate a simple linear workflow"""
    print("="*60)
    print("SIMULATION 1: Simple Linear Workflow")
    print("="*60)
    
    # Get agency components
    (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    ) = get_agency_components()

    # Create a simple workflow: research -> code generation
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("simple_validation_workflow", "Simple Validation Workflow")
        .add_task("research_step", "Research Step", "research", {
            "query": "research the concept of fibonacci sequence",
            "parameters": {"method": "literature_review"}
        })
        .add_task("code_step", "Code Generation Step", "code_generation", {
            "query": "generate a python function to calculate fibonacci numbers",
            "parameters": {"language": "python"}
        })
        .connect("research_step", "code_step")  # Connect research to code generation
        .set_end_nodes(["code_step"])  # Set code generation as the end node
        .build()
    )

    # Register the workflow definition
    workflow_orchestrator.register_definition(workflow_def)

    # Create and start a workflow instance
    start_time = time.time()
    instance_id = workflow_orchestrator.create_instance("simple_validation_workflow")
    print(f"Created workflow instance: {instance_id}")
    
    await workflow_orchestrator.start_instance(instance_id)
    print(f"Started workflow instance: {instance_id}")

    # Wait for the workflow to complete
    max_wait_time = 30  # seconds
    elapsed = 0
    while elapsed < max_wait_time:
        status = await workflow_orchestrator.get_instance_status(instance_id)
        if status.state in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    print(f"Final workflow status: {final_status.state.value}")
    print(f"Completed nodes: {final_status.completed_nodes}")
    print(f"Execution time: {total_time:.2f} seconds")
    
    if final_status.error:
        print(f"Error: {final_status.error}")
        
    return final_status.state.value == "completed"


async def simulate_parallel_workflow():
    """Simulate a workflow with parallel execution paths"""
    print("\n" + "="*60)
    print("SIMULATION 2: Parallel Workflow")
    print("="*60)
    
    # Get agency components
    (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    ) = get_agency_components()

    # Create a workflow with parallel execution: research -> (code_gen + documentation) -> review
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("parallel_validation_workflow", "Parallel Validation Workflow")
        .add_task("research_step", "Research Step", "research", {
            "query": "research best practices for API design",
            "parameters": {"method": "literature_review"}
        })
        .add_task("code_gen_step", "Code Generation Step", "code_generation", {
            "query": "generate a python API endpoint based on best practices for API design",
            "parameters": {"language": "python"}
        })
        .add_task("doc_gen_step", "Documentation Generation Step", "documentation", {
            "query": "generate documentation for the API endpoint",
            "parameters": {"format": "markdown"}
        })
        .add_task("review_step", "Review Step", "research", {
            "query": "review the generated code and documentation for consistency",
            "parameters": {"aspect": "consistency_check"}
        })
        .connect("research_step", "code_gen_step")  # Research feeds into code generation
        .connect("research_step", "doc_gen_step")   # Research also feeds into documentation
        .connect("code_gen_step", "review_step")    # Code gen connects to review
        .connect("doc_gen_step", "review_step")     # Doc gen also connects to review
        .set_end_nodes(["review_step"])             # Review is the end node
        .build()
    )

    # Register the workflow definition
    workflow_orchestrator.register_definition(workflow_def)

    # Create and start a workflow instance
    start_time = time.time()
    instance_id = workflow_orchestrator.create_instance("parallel_validation_workflow")
    print(f"Created workflow instance: {instance_id}")
    
    await workflow_orchestrator.start_instance(instance_id)
    print(f"Started workflow instance: {instance_id}")

    # Wait for the workflow to complete
    max_wait_time = 60  # seconds
    elapsed = 0
    while elapsed < max_wait_time:
        status = await workflow_orchestrator.get_instance_status(instance_id)
        if status.state in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    print(f"Final workflow status: {final_status.state.value}")
    print(f"Completed nodes: {final_status.completed_nodes}")
    print(f"Execution time: {total_time:.2f} seconds")
    
    if final_status.error:
        print(f"Error: {final_status.error}")
        
    return final_status.state.value == "completed"


async def simulate_decision_workflow():
    """Simulate a workflow with decision points"""
    print("\n" + "="*60)
    print("SIMULATION 3: Decision-Based Workflow")
    print("="*60)
    
    # Get agency components
    (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    ) = get_agency_components()

    # Define a condition function for decision nodes
    def check_complexity_condition(result):
        """Condition to check if the task result indicates complexity"""
        if isinstance(result, dict) and 'data' in result:
            # Simplified condition - in reality, this would check specific criteria
            return len(str(result.get('data', ''))) > 100
        return True

    # Create a workflow with decision points
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("decision_validation_workflow", "Decision Validation Workflow")
        .add_task("initial_task", "Initial Analysis", "research", {
            "query": "analyze the complexity of implementing a REST API with authentication",
            "parameters": {"method": "analysis"}
        })
        .add_decision("complexity_check", "Complexity Check", check_complexity_condition)
        .add_task("simple_impl", "Simple Implementation", "code_generation", {
            "query": "generate a basic REST API without authentication",
            "parameters": {"language": "python", "framework": "flask"}
        })
        .add_task("complex_impl", "Complex Implementation", "code_generation", {
            "query": "generate a complete REST API with authentication and authorization",
            "parameters": {"language": "python", "framework": "flask"}
        })
        .add_task("documentation", "Documentation", "documentation", {
            "query": "document the implemented API",
            "parameters": {"format": "markdown"}
        })
        .connect("initial_task", "complexity_check")  # Initial task -> decision
        .connect("complexity_check", "simple_impl", lambda r: not check_complexity_condition(r))  # If not complex
        .connect("complexity_check", "complex_impl", check_complexity_condition)  # If complex
        .connect("simple_impl", "documentation")  # Simple impl -> documentation
        .connect("complex_impl", "documentation")  # Complex impl -> documentation
        .set_end_nodes(["documentation"])  # Documentation is the end node
        .build()
    )

    # Register the workflow definition
    workflow_orchestrator.register_definition(workflow_def)

    # Create and start a workflow instance
    start_time = time.time()
    instance_id = workflow_orchestrator.create_instance("decision_validation_workflow")
    print(f"Created workflow instance: {instance_id}")
    
    await workflow_orchestrator.start_instance(instance_id)
    print(f"Started workflow instance: {instance_id}")

    # Wait for the workflow to complete
    max_wait_time = 60  # seconds
    elapsed = 0
    while elapsed < max_wait_time:
        status = await workflow_orchestrator.get_instance_status(instance_id)
        if status.state in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    print(f"Final workflow status: {final_status.state.value}")
    print(f"Completed nodes: {final_status.completed_nodes}")
    print(f"Execution time: {total_time:.2f} seconds")
    
    if final_status.error:
        print(f"Error: {final_status.error}")
        
    return final_status.state.value == "completed"


async def simulate_error_handling_workflow():
    """Simulate a workflow with error handling"""
    print("\n" + "="*60)
    print("SIMULATION 4: Error Handling Workflow")
    print("="*60)
    
    # Get agency components
    (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    ) = get_agency_components()

    # Create a workflow that might fail and has recovery steps
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("error_handling_workflow", "Error Handling Validation Workflow")
        .add_task("primary_task", "Primary Task", "research", {
            "query": "research current trends in machine learning",
            "parameters": {"method": "literature_review"}
        })
        .add_task("secondary_task", "Secondary Task", "code_generation", {
            "query": "generate a simple python function based on ml research",
            "parameters": {"language": "python"}
        })
        .add_task("fallback_task", "Fallback Task", "documentation", {
            "query": "create a summary document of ml research findings",
            "parameters": {"format": "markdown"}
        })
        .connect("primary_task", "secondary_task")  # Primary -> secondary
        .connect("secondary_task", "fallback_task", lambda r: not (isinstance(r, dict) and r.get('success', False)))  # If secondary fails, go to fallback
        .set_end_nodes(["secondary_task", "fallback_task"])  # Either secondary or fallback ends the workflow
        .build()
    )

    # Register the workflow definition
    workflow_orchestrator.register_definition(workflow_def)

    # Create and start a workflow instance
    start_time = time.time()
    instance_id = workflow_orchestrator.create_instance("error_handling_workflow")
    print(f"Created workflow instance: {instance_id}")
    
    await workflow_orchestrator.start_instance(instance_id)
    print(f"Started workflow instance: {instance_id}")

    # Wait for the workflow to complete
    max_wait_time = 60  # seconds
    elapsed = 0
    while elapsed < max_wait_time:
        status = await workflow_orchestrator.get_instance_status(instance_id)
        if status.state in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    print(f"Final workflow status: {final_status.state.value}")
    print(f"Completed nodes: {final_status.completed_nodes}")
    print(f"Execution time: {total_time:.2f} seconds")
    
    if final_status.error:
        print(f"Error: {final_status.error}")
        
    return final_status.state.value == "completed"


async def simulate_resource_constrained_workflow():
    """Simulate a workflow with resource constraints"""
    print("\n" + "="*60)
    print("SIMULATION 5: Resource-Constrained Workflow")
    print("="*60)
    
    # Get agency components
    (
        registry, coordinator, resource_manager, plugin_manager, config_manager,
        environment_manager, error_handling_manager, retry_executor,
        deployment_manager, deployment_orchestrator, task_lifecycle_manager,
        enhancement_pipeline, monitoring_service, health_checker, workflow_orchestrator,
        distributed_task_manager, security_manager, embedding_service, vector_store,
        knowledge_base, retriever, mcp_manager, decision_engine, context_manager, mcp_integration
    ) = get_agency_components()

    # Temporarily adjust resource quotas for testing
    original_quota = resource_manager.get_quota("code_generation")
    resource_manager.set_quota("code_generation", type(original_quota)(
        cpu_percent=original_quota.cpu_percent,
        memory_mb=min(original_quota.memory_mb, 256),  # Lower memory limit for testing
        max_concurrent_tasks=max(original_quota.max_concurrent_tasks, 2)
    ))

    # Create a workflow that tests resource management
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("resource_constrained_workflow", "Resource-Constrained Validation Workflow")
        .add_task("task1", "First Task", "code_generation", {
            "query": "generate a simple python function",
            "parameters": {"language": "python"}
        })
        .add_task("task2", "Second Task", "code_generation", {
            "query": "generate another python function",
            "parameters": {"language": "python"}
        })
        .add_task("task3", "Third Task", "code_generation", {
            "query": "generate a third python function",
            "parameters": {"language": "python"}
        })
        .connect("task1", "task2")  # Sequential execution to test resource management
        .connect("task2", "task3")
        .set_end_nodes(["task3"])
        .build()
    )

    # Register the workflow definition
    workflow_orchestrator.register_definition(workflow_def)

    # Create and start a workflow instance
    start_time = time.time()
    instance_id = workflow_orchestrator.create_instance("resource_constrained_workflow")
    print(f"Created workflow instance: {instance_id}")
    
    await workflow_orchestrator.start_instance(instance_id)
    print(f"Started workflow instance: {instance_id}")

    # Wait for the workflow to complete
    max_wait_time = 60  # seconds
    elapsed = 0
    while elapsed < max_wait_time:
        status = await workflow_orchestrator.get_instance_status(instance_id)
        if status.state in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Restore original quota
    resource_manager.set_quota("code_generation", original_quota)
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    print(f"Final workflow status: {final_status.state.value}")
    print(f"Completed nodes: {final_status.completed_nodes}")
    print(f"Execution time: {total_time:.2f} seconds")
    
    if final_status.error:
        print(f"Error: {final_status.error}")
        
    return final_status.state.value == "completed"


async def run_all_simulations():
    """Run all workflow simulations and report results"""
    print("Starting Workflow Simulations for Validation\n")
    
    results = []
    
    # Run each simulation
    results.append(("Simple Workflow", await simulate_simple_workflow()))
    results.append(("Parallel Workflow", await simulate_parallel_workflow()))
    results.append(("Decision Workflow", await simulate_decision_workflow()))
    results.append(("Error Handling Workflow", await simulate_error_handling_workflow()))
    results.append(("Resource-Constrained Workflow", await simulate_resource_constrained_workflow()))
    
    # Report results
    print("\n" + "="*60)
    print("WORKFLOW SIMULATION RESULTS")
    print("="*60)
    
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Result: {'ALL SIMULATIONS PASSED' if all_passed else 'SOME SIMULATIONS FAILED'}")
    return all_passed


if __name__ == "__main__":
    asyncio.run(run_all_simulations())