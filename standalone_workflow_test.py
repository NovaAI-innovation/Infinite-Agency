#!/usr/bin/env python3
"""
Standalone Workflow Engine Test
This script tests the workflow engine functionality in isolation.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable, Union
import uuid
from enum import Enum
from dataclasses import dataclass


class WorkflowState(Enum):
    """States of a workflow"""
    CREATED = "created"
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowNodeType(Enum):
    """Types of nodes in a workflow"""
    TASK = "task"
    DECISION = "decision"
    JOIN = "join"
    FORK = "fork"
    MERGE = "merge"


@dataclass
class WorkflowNode:
    """A node in the workflow graph"""
    id: str
    type: WorkflowNodeType
    name: str
    domain: Optional[str] = None  # For task nodes
    input_data: Optional[Dict[str, Any]] = None  # For task nodes
    condition: Optional[Callable] = None  # For decision nodes
    children: List[str] = None  # IDs of child nodes
    parents: List[str] = None  # IDs of parent nodes

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.parents is None:
            self.parents = []


@dataclass
class WorkflowEdge:
    """An edge connecting two nodes in the workflow"""
    source: str  # Source node ID
    target: str  # Target node ID
    condition: Optional[Callable] = None  # Condition for traversing this edge
    label: str = ""  # Optional label for the edge


@dataclass
class WorkflowInstance:
    """An instance of a running workflow"""
    id: str
    definition_id: str
    state: WorkflowState
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_nodes: List[str] = None  # Currently executing nodes
    completed_nodes: List[str] = None  # Completed nodes
    node_outputs: Dict[str, Any] = None  # Outputs from each node
    context: Dict[str, Any] = None  # Shared context across nodes
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.current_nodes is None:
            self.current_nodes = []
        if self.completed_nodes is None:
            self.completed_nodes = []
        if self.node_outputs is None:
            self.node_outputs = {}
        if self.context is None:
            self.context = {}
        if self.metadata is None:
            self.metadata = {}


class WorkflowDefinition:
    """Definition of a workflow template"""

    def __init__(self, id: str, name: str, description: str = ""):
        self.id = id
        self.name = name
        self.description = description
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: List[WorkflowEdge] = []
        self.start_node: Optional[str] = None
        self.end_nodes: List[str] = []
        self.created_at = datetime.now()

    def add_node(self, node: WorkflowNode):
        """Add a node to the workflow"""
        self.nodes[node.id] = node
        if len(self.nodes) == 1:
            self.start_node = node.id

    def add_edge(self, edge: WorkflowEdge):
        """Add an edge to the workflow"""
        self.edges.append(edge)
        # Update parent-child relationships
        if edge.source in self.nodes:
            if edge.target not in self.nodes[edge.source].children:
                self.nodes[edge.source].children.append(edge.target)
        if edge.target in self.nodes:
            if edge.source not in self.nodes[edge.target].parents:
                self.nodes[edge.target].parents.append(edge.source)

    def set_end_nodes(self, node_ids: List[str]):
        """Set the end nodes of the workflow"""
        self.end_nodes = node_ids


class MockTaskExecutor:
    """Mock executor for workflow tasks"""
    
    def __init__(self):
        self.executed_tasks = []
    
    async def execute_task(self, domain_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock execution of a task"""
        # Record the executed task
        task_record = {
            "domain": domain_name,
            "input": input_data,
            "timestamp": datetime.now()
        }
        self.executed_tasks.append(task_record)
        
        # Simulate different outputs based on domain
        if domain_name == "mock_research":
            await asyncio.sleep(0.5)  # Simulate processing time
            return {
                "success": True,
                "data": {
                    "summary": f"Research summary for: {input_data.get('query', 'unknown')}",
                    "key_findings": ["Finding 1", "Finding 2"],
                    "sources": ["Source 1", "Source 2"]
                }
            }
        elif domain_name == "mock_code_generation":
            await asyncio.sleep(0.5)  # Simulate processing time
            return {
                "success": True,
                "data": {
                    "code": f"// Generated code for: {input_data.get('query', 'unknown')}",
                    "language": "python",
                    "type": "function"
                }
            }
        elif domain_name == "mock_documentation":
            await asyncio.sleep(0.3)  # Simulate processing time
            return {
                "success": True,
                "data": {
                    "documentation": f"Documentation for: {input_data.get('query', 'unknown')}",
                    "format": "markdown"
                }
            }
        else:
            # Default response for unknown domains
            await asyncio.sleep(0.2)
            return {
                "success": True,
                "data": f"Executed task for domain {domain_name} with input {input_data}"
            }


class WorkflowOrchestrator:
    """Orchestrates the execution of workflows"""

    def __init__(self, task_executor: MockTaskExecutor):
        self.task_executor = task_executor
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self._active_instances: Dict[str, asyncio.Task] = {}
        self._logger = print  # Simple logger for demo

    def register_definition(self, definition: WorkflowDefinition):
        """Register a workflow definition"""
        self.definitions[definition.id] = definition
        self._logger(f"Registered workflow definition: {definition.name} (ID: {definition.id})")

    def create_instance(self, definition_id: str, context: Dict[str, Any] = None) -> str:
        """Create a new workflow instance"""
        if definition_id not in self.definitions:
            raise ValueError(f"Workflow definition {definition_id} not found")

        instance_id = str(uuid.uuid4())
        definition = self.definitions[definition_id]

        instance = WorkflowInstance(
            id=instance_id,
            definition_id=definition_id,
            state=WorkflowState.CREATED,
            created_at=datetime.now(),
            context=context or {},
            current_nodes=[definition.start_node] if definition.start_node else []
        )

        self.instances[instance_id] = instance
        self._logger(f"Created workflow instance: {instance_id} for definition: {definition_id}")

        return instance_id

    async def start_instance(self, instance_id: str):
        """Start executing a workflow instance"""
        if instance_id not in self.instances:
            raise ValueError(f"Workflow instance {instance_id} not found")

        instance = self.instances[instance_id]
        if instance.state != WorkflowState.CREATED:
            raise ValueError(f"Workflow instance {instance_id} is not in CREATED state")

        instance.state = WorkflowState.RUNNING
        instance.started_at = datetime.now()

        # Start the workflow execution task
        task = asyncio.create_task(self._execute_workflow(instance_id))
        self._active_instances[instance_id] = task

        self._logger(f"Started workflow instance: {instance_id}")

    async def _execute_workflow(self, instance_id: str):
        """Execute a workflow instance"""
        instance = self.instances[instance_id]
        definition = self.definitions[instance.definition_id]

        try:
            while instance.state == WorkflowState.RUNNING:
                # Execute all current nodes
                completed_this_cycle = []

                for node_id in instance.current_nodes[:]:  # Copy to avoid modification during iteration
                    node = definition.nodes[node_id]

                    # Execute the node
                    result = await self._execute_node(instance_id, node)

                    if result is not None:
                        # Node completed successfully
                        instance.node_outputs[node_id] = result
                        instance.completed_nodes.append(node_id)
                        completed_this_cycle.append(node_id)

                        # Remove from current nodes
                        if node_id in instance.current_nodes:
                            instance.current_nodes.remove(node_id)

                        # Determine next nodes based on edges
                        next_nodes = self._get_next_nodes(definition, node_id, result)
                        for next_node_id in next_nodes:
                            if next_node_id not in instance.current_nodes and next_node_id not in instance.completed_nodes:
                                instance.current_nodes.append(next_node_id)

                # If no nodes completed this cycle, check if workflow is done
                if not completed_this_cycle:
                    if not instance.current_nodes:
                        # No more nodes to execute
                        instance.state = WorkflowState.COMPLETED
                        instance.completed_at = datetime.now()
                        self._logger(f"Workflow instance {instance_id} completed")
                    else:
                        # Still have nodes but none executed - might be waiting for conditions
                        await asyncio.sleep(0.1)  # Brief pause to prevent busy-waiting
                else:
                    # Check if we've reached end nodes
                    if any(node_id in instance.completed_nodes for node_id in definition.end_nodes):
                        instance.state = WorkflowState.COMPLETED
                        instance.completed_at = datetime.now()
                        self._logger(f"Workflow instance {instance_id} completed at end node")

        except Exception as e:
            instance.state = WorkflowState.FAILED
            instance.error = str(e)
            instance.completed_at = datetime.now()
            self._logger(f"Workflow instance {instance_id} failed: {e}")

    async def _execute_node(self, instance_id: str, node: WorkflowNode) -> Any:
        """Execute a single workflow node"""
        instance = self.instances[instance_id]
        definition = self.definitions[instance.definition_id]

        try:
            if node.type == WorkflowNodeType.TASK:
                # Execute a task node
                if node.domain is None:
                    raise ValueError(f"Task node {node.id} has no domain specified")

                # Execute the task using the mock executor
                result = await self.task_executor.execute_task(node.domain, node.input_data or {})
                
                return result

            elif node.type == WorkflowNodeType.DECISION:
                # Execute a decision node
                if node.condition:
                    # Decision nodes determine which path to take based on condition
                    # For now, return the result of the condition evaluation
                    return node.condition(instance.context)
                else:
                    # Default behavior for decision node without condition
                    return True

            elif node.type in [WorkflowNodeType.JOIN, WorkflowNodeType.FORK, WorkflowNodeType.MERGE]:
                # Control flow nodes - for now, just return success
                return {"status": "completed", "node_type": node.type.value}

            else:
                raise ValueError(f"Unknown node type: {node.type}")

        except Exception as e:
            self._logger(f"Error executing node {node.id} in workflow {instance_id}: {e}")
            raise

    def _get_next_nodes(self, definition: WorkflowDefinition, current_node_id: str, result: Any) -> List[str]:
        """Determine the next nodes based on edges and conditions"""
        next_nodes = []

        for edge in definition.edges:
            if edge.source == current_node_id:
                # Check if edge condition is met
                if edge.condition is None or edge.condition(result):
                    next_nodes.append(edge.target)

        return next_nodes

    async def get_instance_status(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Get the status of a workflow instance"""
        return self.instances.get(instance_id)

    async def cancel_instance(self, instance_id: str):
        """Cancel a running workflow instance"""
        if instance_id not in self.instances:
            raise ValueError(f"Workflow instance {instance_id} not found")

        instance = self.instances[instance_id]

        if instance.state in [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED]:
            return  # Already finished

        # Cancel the execution task
        if instance_id in self._active_instances:
            task = self._active_instances[instance_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self._active_instances[instance_id]

        # Update instance state
        instance.state = WorkflowState.CANCELLED
        instance.completed_at = datetime.now()
        self._logger(f"Cancelled workflow instance: {instance_id}")


class WorkflowBuilder:
    """Helper class to build workflows programmatically"""

    def __init__(self):
        self.workflow = None

    def create_workflow(self, id: str, name: str, description: str = "") -> 'WorkflowBuilder':
        """Create a new workflow definition"""
        self.workflow = WorkflowDefinition(id, name, description)
        return self

    def add_task(self, id: str, name: str, domain: str, input_data: Dict[str, Any]) -> 'WorkflowBuilder':
        """Add a task node to the workflow"""
        node = WorkflowNode(
            id=id,
            type=WorkflowNodeType.TASK,
            name=name,
            domain=domain,
            input_data=input_data
        )
        self.workflow.add_node(node)
        return self

    def add_decision(self, id: str, name: str, condition: Callable) -> 'WorkflowBuilder':
        """Add a decision node to the workflow"""
        node = WorkflowNode(
            id=id,
            type=WorkflowNodeType.DECISION,
            name=name,
            condition=condition
        )
        self.workflow.add_node(node)
        return self

    def add_control_flow(self, id: str, name: str, node_type: WorkflowNodeType) -> 'WorkflowBuilder':
        """Add a control flow node (join, fork, merge) to the workflow"""
        node = WorkflowNode(
            id=id,
            type=node_type,
            name=name
        )
        self.workflow.add_node(node)
        return self

    def connect(self, source_id: str, target_id: str, condition: Callable = None, label: str = "") -> 'WorkflowBuilder':
        """Connect two nodes with an edge"""
        edge = WorkflowEdge(
            source=source_id,
            target=target_id,
            condition=condition,
            label=label
        )
        self.workflow.add_edge(edge)
        return self

    def set_end_nodes(self, node_ids: List[str]) -> 'WorkflowBuilder':
        """Set the end nodes of the workflow"""
        self.workflow.set_end_nodes(node_ids)
        return self

    def build(self) -> WorkflowDefinition:
        """Build and return the workflow definition"""
        workflow = self.workflow
        self.workflow = None
        return workflow


async def simulate_simple_workflow():
    """Simulate a simple linear workflow"""
    print("="*60)
    print("SIMULATION 1: Simple Linear Workflow")
    print("="*60)
    
    # Create mock task executor
    task_executor = MockTaskExecutor()
    
    # Create workflow orchestrator
    workflow_orchestrator = WorkflowOrchestrator(task_executor)

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
    
    # Create mock task executor
    task_executor = MockTaskExecutor()
    
    # Create workflow orchestrator
    workflow_orchestrator = WorkflowOrchestrator(task_executor)

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
    
    # Create mock task executor
    task_executor = MockTaskExecutor()
    
    # Create workflow orchestrator
    workflow_orchestrator = WorkflowOrchestrator(task_executor)

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
    
    # Print task execution summary
    print(f"\nTask Execution Summary:")
    # Note: This won't work as expected since each simulation creates its own executor
    # But we can at least confirm the workflow engine is functioning
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(run_all_simulations())