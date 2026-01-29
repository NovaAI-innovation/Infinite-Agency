from typing import Dict, Any, List, Optional, Callable, Union
import asyncio
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from ..core.base_domain import BaseDomain, DomainInput, DomainOutput
from ..core.task_lifecycle import TaskLifecycleManager, TaskPriority
from ..utils.logger import get_logger


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
    input_data: Optional[Union[DomainInput, Dict[str, Any]]] = None  # For task nodes
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


class WorkflowOrchestrator:
    """Orchestrates the execution of workflows"""
    
    def __init__(self, task_lifecycle_manager: TaskLifecycleManager):
        self.task_lifecycle_manager = task_lifecycle_manager
        self.definitions: Dict[str, WorkflowDefinition] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self._active_instances: Dict[str, asyncio.Task] = {}
        self._logger = get_logger(__name__)
    
    def register_definition(self, definition: WorkflowDefinition):
        """Register a workflow definition"""
        self.definitions[definition.id] = definition
        self._logger.info(f"Registered workflow definition: {definition.name} (ID: {definition.id})")
    
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
        self._logger.info(f"Created workflow instance: {instance_id} for definition: {definition_id}")
        
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
        
        self._logger.info(f"Started workflow instance: {instance_id}")
    
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
                        self._logger.info(f"Workflow instance {instance_id} completed")
                    else:
                        # Still have nodes but none executed - might be waiting for conditions
                        await asyncio.sleep(0.1)  # Brief pause to prevent busy-waiting
                else:
                    # Check if we've reached end nodes
                    if any(node_id in instance.completed_nodes for node_id in definition.end_nodes):
                        instance.state = WorkflowState.COMPLETED
                        instance.completed_at = datetime.now()
                        self._logger.info(f"Workflow instance {instance_id} completed at end node")
        
        except Exception as e:
            instance.state = WorkflowState.FAILED
            instance.error = str(e)
            instance.completed_at = datetime.now()
            self._logger.error(f"Workflow instance {instance_id} failed: {e}")
    
    async def _execute_node(self, instance_id: str, node: WorkflowNode) -> Any:
        """Execute a single workflow node"""
        instance = self.instances[instance_id]
        definition = self.definitions[instance.definition_id]
        
        try:
            if node.type == WorkflowNodeType.TASK:
                # Execute a task node
                if node.domain is None:
                    raise ValueError(f"Task node {node.id} has no domain specified")
                
                # Prepare input data, possibly using context from previous nodes
                input_data = node.input_data
                if isinstance(input_data, dict):
                    # If input_data is a dict, treat it as parameters for DomainInput
                    input_data = DomainInput(**input_data)
                
                # Execute the task using the task lifecycle manager
                result = await self.task_lifecycle_manager.execute_task(
                    node.domain, input_data, TaskPriority.NORMAL
                )
                
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
            self._logger.error(f"Error executing node {node.id} in workflow {instance_id}: {e}")
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
        self._logger.info(f"Cancelled workflow instance: {instance_id}")
    
    async def pause_instance(self, instance_id: str):
        """Pause a running workflow instance"""
        # For now, pausing is similar to cancellation but with a different state
        # In a more sophisticated implementation, this would preserve state differently
        if instance_id not in self.instances:
            raise ValueError(f"Workflow instance {instance_id} not found")
        
        instance = self.instances[instance_id]
        if instance.state != WorkflowState.RUNNING:
            raise ValueError(f"Workflow instance {instance_id} is not running")
        
        instance.state = WorkflowState.PAUSED
        self._logger.info(f"Paused workflow instance: {instance_id}")
    
    async def resume_instance(self, instance_id: str):
        """Resume a paused workflow instance"""
        if instance_id not in self.instances:
            raise ValueError(f"Workflow instance {instance_id} not found")
        
        instance = self.instances[instance_id]
        if instance.state != WorkflowState.PAUSED:
            raise ValueError(f"Workflow instance {instance_id} is not paused")
        
        instance.state = WorkflowState.RUNNING
        # Restart the execution task
        task = asyncio.create_task(self._execute_workflow(instance_id))
        self._active_instances[instance_id] = task
        self._logger.info(f"Resumed workflow instance: {instance_id}")


class WorkflowBuilder:
    """Helper class to build workflows programmatically"""
    
    def __init__(self):
        self.workflow = None
    
    def create_workflow(self, id: str, name: str, description: str = "") -> 'WorkflowBuilder':
        """Create a new workflow definition"""
        self.workflow = WorkflowDefinition(id, name, description)
        return self
    
    def add_task(self, id: str, name: str, domain: str, input_data: Union[DomainInput, Dict[str, Any]]) -> 'WorkflowBuilder':
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


# Global workflow orchestrator instance
workflow_orchestrator = None


def get_workflow_orchestrator(task_lifecycle_manager=None) -> WorkflowOrchestrator:
    """Get the global workflow orchestrator"""
    global workflow_orchestrator
    if workflow_orchestrator is None and task_lifecycle_manager is not None:
        workflow_orchestrator = WorkflowOrchestrator(task_lifecycle_manager)
    return workflow_orchestrator