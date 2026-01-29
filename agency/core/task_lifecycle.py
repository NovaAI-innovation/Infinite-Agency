from typing import Dict, Any, Optional, List, Callable, Awaitable
import asyncio
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from ..core.base_domain import BaseDomain, DomainInput, DomainOutput
from ..core.monitoring import get_monitor
from ..utils.logger import get_logger


class TaskState(Enum):
    """Possible states of a task"""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskContext:
    """Context information for a task"""
    task_id: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    state: TaskState = TaskState.CREATED
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None
    result: Optional[DomainOutput] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


class SingleAgent:
    """A single agent that manages task lifecycle and execution"""
    
    def __init__(self, name: str, domain: BaseDomain, max_concurrent_tasks: int = 5):
        self.name = name
        self.domain = domain
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue = asyncio.PriorityQueue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_contexts: Dict[str, TaskContext] = {}
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._shutdown = False
        self._logger = get_logger(f"SingleAgent.{name}")
        self.monitor = get_monitor()
    
    async def submit_task(self, input_data: DomainInput, priority: TaskPriority = TaskPriority.NORMAL, 
                         dependencies: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Submit a task for execution"""
        task_id = str(uuid.uuid4())
        
        context = TaskContext(
            task_id=task_id,
            created_at=datetime.now(),
            priority=priority,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        self.task_contexts[task_id] = context
        
        # Add task to queue with priority (lower number = higher priority)
        await self.task_queue.put((-priority.value, task_id, input_data))
        
        self._logger.info(f"Task {task_id} submitted with priority {priority.name}")
        
        # Start processing if not already running
        if not hasattr(self, '_processing_task') or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_tasks())
        
        return task_id
    
    async def _process_tasks(self):
        """Process tasks from the queue"""
        while not self._shutdown and not self.task_queue.empty():
            try:
                priority, task_id, input_data = await self.task_queue.get()
                
                # Check if all dependencies are completed
                if not await self._check_dependencies(task_id):
                    # Put the task back in the queue to try again later
                    await self.task_queue.put((priority, task_id, input_data))
                    await asyncio.sleep(0.1)  # Brief pause to avoid busy-waiting
                    continue
                
                # Start the task execution
                task_coro = self._execute_task(task_id, input_data)
                task = asyncio.create_task(task_coro)
                self.active_tasks[task_id] = task
                
                # Wait for the task to complete or be cancelled
                try:
                    await task
                except asyncio.CancelledError:
                    self._logger.info(f"Task {task_id} was cancelled")
                    self.task_contexts[task_id].state = TaskState.CANCELLED
                
                # Clean up
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]
                
            except asyncio.CancelledError:
                self._logger.info("Task processor was cancelled")
                break
            except Exception as e:
                self._logger.error(f"Error in task processor: {e}")
    
    async def _check_dependencies(self, task_id: str) -> bool:
        """Check if all dependencies for a task are completed"""
        context = self.task_contexts[task_id]
        for dep_id in context.dependencies:
            if dep_id not in self.task_contexts:
                return False  # Dependency doesn't exist
            dep_context = self.task_contexts[dep_id]
            if dep_context.state != TaskState.COMPLETED:
                return False  # Dependency not completed
        return True
    
    async def _execute_task(self, task_id: str, input_data: DomainInput):
        """Execute a single task"""
        context = self.task_contexts[task_id]
        context.state = TaskState.RUNNING
        context.started_at = datetime.now()
        
        self.monitor.start_operation(task_id, self.domain.name, "task_execution")
        
        try:
            # Acquire semaphore to limit concurrent execution
            async with self.semaphore:
                result = await self.domain.execute(input_data)
                context.result = result
                context.state = TaskState.COMPLETED if result.success else TaskState.FAILED
                context.completed_at = datetime.now()
                
                if not result.success:
                    context.error = result.error
                    self._logger.error(f"Task {task_id} failed: {result.error}")
                else:
                    self._logger.info(f"Task {task_id} completed successfully")
        
        except Exception as e:
            context.error = str(e)
            context.state = TaskState.FAILED
            context.completed_at = datetime.now()
            self._logger.error(f"Task {task_id} failed with exception: {e}")
        
        finally:
            self.monitor.end_operation(task_id, self.domain.name, context.state == TaskState.COMPLETED, context.error)
    
    async def get_task_result(self, task_id: str) -> Optional[DomainOutput]:
        """Get the result of a completed task"""
        if task_id not in self.task_contexts:
            return None
        
        context = self.task_contexts[task_id]
        if context.state == TaskState.COMPLETED:
            return context.result
        elif context.state == TaskState.FAILED:
            self._logger.error(f"Task {task_id} failed: {context.error}")
            return DomainOutput(success=False, error=context.error)
        else:
            # Task is still running or queued
            return None
    
    async def get_task_context(self, task_id: str) -> Optional[TaskContext]:
        """Get the context of a task"""
        return self.task_contexts.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or queued task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            return True
        elif task_id in self.task_contexts:
            context = self.task_contexts[task_id]
            if context.state in [TaskState.CREATED, TaskState.QUEUED]:
                context.state = TaskState.CANCELLED
                return True
        return False
    
    async def wait_for_task(self, task_id: str, timeout: float = None) -> Optional[DomainOutput]:
        """Wait for a task to complete and return its result"""
        if task_id not in self.task_contexts:
            return None
        
        context = self.task_contexts[task_id]
        
        # If already completed, return immediately
        if context.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
            return await self.get_task_result(task_id)
        
        # Wait for the task to complete
        start_time = asyncio.get_event_loop().time()
        while context.state not in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    break
            await asyncio.sleep(0.1)
        
        return await self.get_task_result(task_id)
    
    async def shutdown(self):
        """Shutdown the agent and cancel all running tasks"""
        self._shutdown = True
        
        # Cancel all active tasks
        for task in self.active_tasks.values():
            task.cancel()
        
        # Wait for all tasks to finish cancelling
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)
        
        self._logger.info(f"Agent {self.name} shutdown complete")


class AgentPool:
    """Manages a pool of single agents for load distribution"""
    
    def __init__(self, domain: BaseDomain, num_agents: int = 3):
        self.domain = domain
        self.agents: List[SingleAgent] = []
        self.current_agent_index = 0
        
        for i in range(num_agents):
            agent = SingleAgent(f"{domain.name}_agent_{i}", domain)
            self.agents.append(agent)
    
    async def submit_task(self, input_data: DomainInput, priority: TaskPriority = TaskPriority.NORMAL, 
                         dependencies: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """Submit a task to the next available agent"""
        # Round-robin assignment to distribute load
        agent = self.agents[self.current_agent_index]
        self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
        
        return await agent.submit_task(input_data, priority, dependencies, metadata)
    
    async def get_task_result(self, task_id: str) -> Optional[DomainOutput]:
        """Get task result from any agent in the pool"""
        for agent in self.agents:
            result = await agent.get_task_result(task_id)
            if result is not None:
                return result
        return None
    
    async def wait_for_task(self, task_id: str, timeout: float = None) -> Optional[DomainOutput]:
        """Wait for a task to complete across the pool"""
        for agent in self.agents:
            # Try to find the task in this agent
            context = await agent.get_task_context(task_id)
            if context is not None:
                return await agent.wait_for_task(task_id, timeout)
        
        # If task not found in any agent
        return None
    
    async def shutdown_all(self):
        """Shutdown all agents in the pool"""
        await asyncio.gather(*[agent.shutdown() for agent in self.agents])


class TaskLifecycleManager:
    """Manages the lifecycle of tasks across multiple domains and agents"""
    
    def __init__(self):
        self.agent_pools: Dict[str, AgentPool] = {}
        self._logger = get_logger(__name__)
    
    def register_domain_for_tasks(self, domain: BaseDomain, num_agents: int = 3):
        """Register a domain with the task lifecycle manager"""
        pool = AgentPool(domain, num_agents)
        self.agent_pools[domain.name] = pool
        self._logger.info(f"Registered domain {domain.name} with task lifecycle manager")
    
    async def execute_task(self, domain_name: str, input_data: DomainInput, 
                          priority: TaskPriority = TaskPriority.NORMAL) -> Optional[DomainOutput]:
        """Execute a task on the specified domain"""
        if domain_name not in self.agent_pools:
            self._logger.error(f"Domain {domain_name} not registered with task lifecycle manager")
            return None
        
        pool = self.agent_pools[domain_name]
        task_id = await pool.submit_task(input_data, priority)
        return await pool.wait_for_task(task_id)
    
    async def execute_workflow(self, workflow: List[Dict[str, Any]]) -> List[DomainOutput]:
        """Execute a multi-step workflow across domains"""
        results = []
        task_dependencies = {}
        
        for step_idx, step in enumerate(workflow):
            domain_name = step["domain"]
            input_data = step["input"]
            priority = TaskPriority(step.get("priority", TaskPriority.NORMAL.value))
            
            if domain_name not in self.agent_pools:
                self._logger.error(f"Domain {domain_name} not registered")
                results.append(DomainOutput(success=False, error=f"Domain {domain_name} not registered"))
                continue
            
            # Determine dependencies for this step
            dependencies = []
            for dep_idx in step.get("depends_on", []):
                if dep_idx in task_dependencies:
                    dependencies.append(task_dependencies[dep_idx])
            
            pool = self.agent_pools[domain_name]
            task_id = await pool.submit_task(input_data, priority, dependencies)
            task_dependencies[step_idx] = task_id
            
            result = await pool.wait_for_task(task_id)
            results.append(result)
        
        return results
    
    async def shutdown(self):
        """Shutdown all agent pools"""
        await asyncio.gather(*[pool.shutdown_all() for pool in self.agent_pools.values()])


# Global task lifecycle manager instance
task_lifecycle_manager = TaskLifecycleManager()


def get_task_lifecycle_manager() -> TaskLifecycleManager:
    """Get the global task lifecycle manager"""
    return task_lifecycle_manager