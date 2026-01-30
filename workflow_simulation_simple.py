#!/usr/bin/env python3
"""
Workflow Simulation for Validation (Simplified)
This script simulates various workflow scenarios to validate the workflow engine functionality.
This version uses a simplified agency setup to avoid import issues with problematic domains.
"""

import asyncio
import time
from datetime import datetime
from agency.core.workflow_engine import WorkflowBuilder, WorkflowNodeType, get_workflow_orchestrator
from agency.core.task_lifecycle import TaskLifecycleManager, get_task_lifecycle_manager
from agency.core.base_domain import BaseDomain, DomainInput, DomainOutput


# Create simple mock domains for testing
class MockCodeGenerationDomain(BaseDomain):
    def __init__(self):
        super().__init__("mock_code_generation", "Mock code generation domain")
    
    async def execute(self, input_data: DomainInput) -> DomainOutput:
        # Simulate some processing time
        await asyncio.sleep(0.5)
        return DomainOutput(
            success=True,
            data={
                "code": f"// Generated code for: {input_data.query}",
                "language": "python",
                "type": "function"
            }
        )
    
    def can_handle(self, input_data: DomainInput) -> bool:
        return "code" in input_data.query.lower() or "generate" in input_data.query.lower()


class MockResearchDomain(BaseDomain):
    def __init__(self):
        super().__init__("mock_research", "Mock research domain")
    
    async def execute(self, input_data: DomainInput) -> DomainOutput:
        # Simulate some processing time
        await asyncio.sleep(0.5)
        return DomainOutput(
            success=True,
            data={
                "summary": f"Research summary for: {input_data.query}",
                "key_findings": ["Finding 1", "Finding 2"],
                "sources": ["Source 1", "Source 2"]
            }
        )
    
    def can_handle(self, input_data: DomainInput) -> bool:
        return "research" in input_data.query.lower() or "find" in input_data.query.lower()


class MockDocumentationDomain(BaseDomain):
    def __init__(self):
        super().__init__("mock_documentation", "Mock documentation domain")
    
    async def execute(self, input_data: DomainInput) -> DomainOutput:
        # Simulate some processing time
        await asyncio.sleep(0.3)
        return DomainOutput(
            success=True,
            data={
                "documentation": f"Documentation for: {input_data.query}",
                "format": "markdown"
            }
        )
    
    def can_handle(self, input_data: DomainInput) -> bool:
        return "document" in input_data.query.lower() or "doc" in input_data.query.lower()


async def setup_mock_agency():
    """Setup a mock agency with simplified components for workflow testing"""
    # Create task lifecycle manager
    task_lifecycle_manager = get_task_lifecycle_manager()
    
    # Create mock domains
    code_domain = MockCodeGenerationDomain()
    research_domain = MockResearchDomain()
    doc_domain = MockDocumentationDomain()
    
    # Register domains with task lifecycle manager
    task_lifecycle_manager.register_domain_for_tasks(code_domain, num_agents=1)
    task_lifecycle_manager.register_domain_for_tasks(research_domain, num_agents=1)
    task_lifecycle_manager.register_domain_for_tasks(doc_domain, num_agents=1)
    
    # Create workflow orchestrator
    workflow_orchestrator = get_workflow_orchestrator(task_lifecycle_manager)
    
    return workflow_orchestrator, task_lifecycle_manager


async def simulate_simple_workflow():
    """Simulate a simple linear workflow"""
    print("="*60)
    print("SIMULATION 1: Simple Linear Workflow")
    print("="*60)
    
    # Setup mock agency
    workflow_orchestrator, task_lifecycle_manager = await setup_mock_agency()

    # Create a simple workflow: research -> code generation
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("simple_validation_workflow", "Simple Validation Workflow")
        .add_task("research_step", "Research Step", "mock_research", {
            "query": "research the concept of fibonacci sequence"
        })
        .add_task("code_step", "Code Generation Step", "mock_code_generation", {
            "query": "generate a python function to calculate fibonacci numbers"
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
        if status and status.state.value in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    if final_status:
        print(f"Final workflow status: {final_status.state.value}")
        print(f"Completed nodes: {final_status.completed_nodes}")
        print(f"Execution time: {total_time:.2f} seconds")
        
        if final_status.error:
            print(f"Error: {final_status.error}")
            
        return final_status.state.value == "completed"
    else:
        print("Could not retrieve final status")
        return False


async def simulate_parallel_workflow():
    """Simulate a workflow with parallel execution paths"""
    print("\n" + "="*60)
    print("SIMULATION 2: Parallel Workflow")
    print("="*60)
    
    # Setup mock agency
    workflow_orchestrator, task_lifecycle_manager = await setup_mock_agency()

    # Create a workflow with parallel execution: research -> (code_gen + documentation) -> review
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("parallel_validation_workflow", "Parallel Validation Workflow")
        .add_task("research_step", "Research Step", "mock_research", {
            "query": "research best practices for API design"
        })
        .add_task("code_gen_step", "Code Generation Step", "mock_code_generation", {
            "query": "generate a python API endpoint based on best practices for API design"
        })
        .add_task("doc_gen_step", "Documentation Generation Step", "mock_documentation", {
            "query": "generate documentation for the API endpoint"
        })
        .connect("research_step", "code_gen_step")  # Research feeds into code generation
        .connect("research_step", "doc_gen_step")   # Research also feeds into documentation
        .set_end_nodes(["code_gen_step", "doc_gen_step"])  # Both code gen and doc gen are end nodes
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
        if status and status.state.value in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    if final_status:
        print(f"Final workflow status: {final_status.state.value}")
        print(f"Completed nodes: {final_status.completed_nodes}")
        print(f"Execution time: {total_time:.2f} seconds")
        
        if final_status.error:
            print(f"Error: {final_status.error}")
            
        return final_status.state.value == "completed"
    else:
        print("Could not retrieve final status")
        return False


async def simulate_decision_workflow():
    """Simulate a workflow with decision points"""
    print("\n" + "="*60)
    print("SIMULATION 3: Decision-Based Workflow")
    print("="*60)
    
    # Setup mock agency
    workflow_orchestrator, task_lifecycle_manager = await setup_mock_agency()

    # Define a condition function for decision nodes
    def check_complexity_condition(result):
        """Condition to check if the task result indicates complexity"""
        # Simplified condition - in reality, this would check specific criteria
        return True  # Always return true for this simulation

    # Create a workflow with decision points
    builder = WorkflowBuilder()
    workflow_def = (builder
        .create_workflow("decision_validation_workflow", "Decision Validation Workflow")
        .add_task("initial_task", "Initial Analysis", "mock_research", {
            "query": "analyze the complexity of implementing a REST API with authentication"
        })
        .add_decision("complexity_check", "Complexity Check", check_complexity_condition)
        .add_task("simple_impl", "Simple Implementation", "mock_code_generation", {
            "query": "generate a basic REST API without authentication"
        })
        .add_task("complex_impl", "Complex Implementation", "mock_code_generation", {
            "query": "generate a complete REST API with authentication and authorization"
        })
        .add_task("documentation", "Documentation", "mock_documentation", {
            "query": "document the implemented API"
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
        if status and status.state.value in ["completed", "failed", "cancelled"]:
            break
        await asyncio.sleep(1)
        elapsed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Check the final status
    final_status = await workflow_orchestrator.get_instance_status(instance_id)
    if final_status:
        print(f"Final workflow status: {final_status.state.value}")
        print(f"Completed nodes: {final_status.completed_nodes}")
        print(f"Execution time: {total_time:.2f} seconds")
        
        if final_status.error:
            print(f"Error: {final_status.error}")
            
        return final_status.state.value == "completed"
    else:
        print("Could not retrieve final status")
        return False


async def run_all_simulations():
    """Run all workflow simulations and report results"""
    print("Starting Workflow Simulations for Validation\n")
    
    results = []
    
    # Run each simulation
    results.append(("Simple Workflow", await simulate_simple_workflow()))
    results.append(("Parallel Workflow", await simulate_parallel_workflow()))
    results.append(("Decision Workflow", await simulate_decision_workflow()))
    
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