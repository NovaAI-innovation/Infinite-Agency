from typing import Dict, Any, List, Optional, Callable
import asyncio
import json
import uuid
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import aiohttp
from ..core.base_domain import DomainInput, DomainOutput
from ..core.task_lifecycle import TaskContext, TaskState
from ..utils.logger import get_logger


class WorkerState(Enum):
    """States of a distributed worker"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class WorkerInfo:
    """Information about a distributed worker"""
    id: str
    host: str
    port: int
    capabilities: List[str]  # Domain capabilities the worker supports
    state: WorkerState
    last_seen: datetime
    load: float  # Current load (0.0 to 1.0)
    total_tasks: int = 0
    successful_tasks: int = 0


@dataclass
class DistributedTask:
    """A task that can be executed in a distributed environment"""
    id: str
    domain: str
    input_data: DomainInput
    priority: int = 0
    created_at: datetime = None
    assigned_worker: Optional[str] = None
    result: Optional[DomainOutput] = None
    state: TaskState = TaskState.CREATED
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class DistributedTaskScheduler:
    """Schedules tasks across distributed workers"""
    
    def __init__(self, heartbeat_interval: float = 30.0):
        self.workers: Dict[str, WorkerInfo] = {}
        self.pending_tasks: List[DistributedTask] = []
        self.running_tasks: Dict[str, DistributedTask] = {}
        self.completed_tasks: Dict[str, DistributedTask] = {}
        self.heartbeat_interval = heartbeat_interval
        self._scheduler_task = None
        self._shutdown = False
        self._logger = get_logger(__name__)
    
    def register_worker(self, worker_info: WorkerInfo):
        """Register a new worker"""
        self.workers[worker_info.id] = worker_info
        self._logger.info(f"Registered worker {worker_info.id} with capabilities: {worker_info.capabilities}")
    
    def unregister_worker(self, worker_id: str):
        """Unregister a worker"""
        if worker_id in self.workers:
            del self.workers[worker_id]
            self._logger.info(f"Unregistered worker {worker_id}")
    
    def submit_task(self, domain: str, input_data: DomainInput, priority: int = 0) -> str:
        """Submit a task for distributed execution"""
        task_id = str(uuid.uuid4())
        task = DistributedTask(
            id=task_id,
            domain=domain,
            input_data=input_data,
            priority=priority
        )
        
        self.pending_tasks.append(task)
        # Sort pending tasks by priority (higher priority first)
        self.pending_tasks.sort(key=lambda t: t.priority, reverse=True)
        
        self._logger.info(f"Submitted task {task_id} for domain {domain}")
        return task_id
    
    def get_task_result(self, task_id: str) -> Optional[DomainOutput]:
        """Get the result of a completed task"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].result
        return None
    
    async def start_scheduler(self):
        """Start the task scheduler"""
        if self._scheduler_task and not self._scheduler_task.done():
            self._logger.warning("Scheduler already running")
            return
        
        self._shutdown = False
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        self._logger.info("Started distributed task scheduler")
    
    async def stop_scheduler(self):
        """Stop the task scheduler"""
        self._shutdown = True
        if self._scheduler_task and not self._scheduler_task.done():
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        self._logger.info("Stopped distributed task scheduler")
    
    async def _scheduler_loop(self):
        """Main scheduling loop"""
        while not self._shutdown:
            try:
                # Assign tasks to available workers
                await self._assign_tasks()
                
                # Update worker status
                await self._update_worker_status()
                
                # Sleep until next cycle
                await asyncio.sleep(1.0)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(1.0)  # Continue despite errors
    
    async def _assign_tasks(self):
        """Assign pending tasks to available workers"""
        # Sort workers by load (lowest load first) and availability
        available_workers = [
            w for w in self.workers.values() 
            if w.state == WorkerState.IDLE and w.id in self.workers
        ]
        
        # Sort by load (ascending)
        available_workers.sort(key=lambda w: w.load)
        
        # Assign tasks to workers
        for task in self.pending_tasks[:]:  # Copy to avoid modification during iteration
            # Find a worker that can handle this domain
            suitable_worker = None
            for worker in available_workers:
                if task.domain in worker.capabilities:
                    suitable_worker = worker
                    break
            
            if suitable_worker:
                # Assign task to worker
                await self._assign_task_to_worker(task, suitable_worker)
                # Remove from pending tasks
                self.pending_tasks.remove(task)
    
    async def _assign_task_to_worker(self, task: DistributedTask, worker: WorkerInfo):
        """Assign a task to a specific worker"""
        try:
            # Update task state
            task.state = TaskState.RUNNING
            task.assigned_worker = worker.id
            task.assigned_at = datetime.now()
            
            # Add to running tasks
            self.running_tasks[task.id] = task
            
            # Update worker state
            worker.state = WorkerState.BUSY
            worker.load = min(1.0, worker.load + 0.1)  # Simplified load calculation
            worker.total_tasks += 1
            
            # Send task to worker (in a real implementation, this would be an HTTP request)
            await self._send_task_to_worker(task, worker)
            
            self._logger.info(f"Assigned task {task.id} to worker {worker.id}")
        except Exception as e:
            self._logger.error(f"Failed to assign task {task.id} to worker {worker.id}: {e}")
            # Mark task as failed
            task.state = TaskState.FAILED
            task.result = DomainOutput(success=False, error=str(e))
            self.completed_tasks[task.id] = self.running_tasks.pop(task.id)
    
    async def _send_task_to_worker(self, task: DistributedTask, worker: WorkerInfo):
        """Send a task to a worker for execution (placeholder implementation)"""
        # In a real implementation, this would make an HTTP request to the worker
        # For now, we'll simulate this with a callback
        self._logger.info(f"Sending task {task.id} to worker {worker.id} at {worker.host}:{worker.port}")
        
        # Simulate task execution completion
        # In a real system, the worker would call back when done
        asyncio.create_task(self._simulate_task_completion(task.id, worker.id))
    
    async def _simulate_task_completion(self, task_id: str, worker_id: str):
        """Simulate task completion (in a real system, this would be a callback from the worker)"""
        await asyncio.sleep(2)  # Simulate processing time
        
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            
            # Simulate a result (in reality, this would come from the worker)
            task.result = DomainOutput(
                success=True,
                data={"result": f"Processed by worker {worker_id}", "task_id": task_id},
                metadata={"processed_by": worker_id, "timestamp": datetime.now().isoformat()}
            )
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.now()
            
            # Move to completed tasks
            self.completed_tasks[task_id] = self.running_tasks.pop(task_id)
            
            # Update worker stats
            if worker_id in self.workers:
                worker = self.workers[worker_id]
                worker.state = WorkerState.IDLE
                worker.load = max(0.0, worker.load - 0.1)  # Reduce load
                worker.successful_tasks += 1
            
            self._logger.info(f"Task {task_id} completed by worker {worker_id}")
    
    async def _update_worker_status(self):
        """Update worker status and detect offline workers"""
        current_time = datetime.now()
        
        for worker_id, worker in list(self.workers.items()):
            # In a real implementation, we would check heartbeats
            # For now, we'll just update the last seen time
            worker.last_seen = current_time
            
            # Check if worker is still responsive
            time_since_seen = (current_time - worker.last_seen).total_seconds()
            if time_since_seen > self.heartbeat_interval * 2:  # Double the heartbeat interval
                worker.state = WorkerState.OFFLINE
                self._logger.warning(f"Worker {worker_id} appears to be offline")
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get statistics about workers and tasks"""
        return {
            "total_workers": len(self.workers),
            "online_workers": len([w for w in self.workers.values() if w.state != WorkerState.OFFLINE]),
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "workers": [
                {
                    "id": w.id,
                    "host": w.host,
                    "port": w.port,
                    "capabilities": w.capabilities,
                    "state": w.state.value,
                    "load": w.load,
                    "total_tasks": w.total_tasks,
                    "success_rate": w.successful_tasks / max(w.total_tasks, 1) if w.total_tasks > 0 else 0
                }
                for w in self.workers.values()
            ]
        }


class DistributedWorker:
    """A worker that can execute tasks in a distributed system"""
    
    def __init__(self, worker_id: str, host: str, port: int, capabilities: List[str]):
        self.id = worker_id
        self.host = host
        self.port = port
        self.capabilities = capabilities
        self.scheduler_host = None
        self.scheduler_port = None
        self._heartbeat_task = None
        self._shutdown = False
        self._logger = get_logger(f"DistributedWorker.{worker_id}")
    
    def connect_to_scheduler(self, scheduler_host: str, scheduler_port: int):
        """Connect to the task scheduler"""
        self.scheduler_host = scheduler_host
        self.scheduler_port = scheduler_port
        self._logger.info(f"Connected to scheduler at {scheduler_host}:{scheduler_port}")
    
    async def start_heartbeat(self, interval: float = 30.0):
        """Start sending heartbeats to the scheduler"""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._logger.warning("Heartbeat already running")
            return
        
        self._shutdown = False
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop(interval))
        self._logger.info(f"Started heartbeat with interval {interval}s")
    
    async def stop_heartbeat(self):
        """Stop sending heartbeats"""
        self._shutdown = True
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        self._logger.info("Stopped heartbeat")
    
    async def _heartbeat_loop(self, interval: float):
        """Main heartbeat loop"""
        while not self._shutdown:
            try:
                await self._send_heartbeat()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(min(interval, 5))  # Retry after shorter interval on error
    
    async def _send_heartbeat(self):
        """Send a heartbeat to the scheduler"""
        if not self.scheduler_host or not self.scheduler_port:
            return
        
        # In a real implementation, this would be an HTTP request
        # For now, we'll just log it
        self._logger.debug(f"Heartbeat sent to scheduler")
    
    async def execute_task(self, task: DistributedTask) -> DomainOutput:
        """Execute a task (placeholder implementation)"""
        self._logger.info(f"Executing task {task.id} for domain {task.domain}")
        
        # In a real implementation, this would delegate to the appropriate domain
        # For now, we'll simulate execution
        await asyncio.sleep(1)  # Simulate processing time
        
        return DomainOutput(
            success=True,
            data={"result": f"Executed task {task.id} for domain {task.domain}"},
            metadata={"executed_by": self.id, "timestamp": datetime.now().isoformat()}
        )


class DistributedTaskManager:
    """Manages distributed task execution across multiple nodes"""
    
    def __init__(self):
        self.scheduler = DistributedTaskScheduler()
        self.local_worker = None
        self._logger = get_logger(__name__)
    
    async def initialize_local_worker(self, worker_id: str, capabilities: List[str]):
        """Initialize a local worker for this node"""
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        self.local_worker = DistributedWorker(
            worker_id=worker_id,
            host=ip_address,
            port=8000,  # Default port
            capabilities=capabilities
        )
        
        # Register with the scheduler (assuming local scheduler for now)
        worker_info = WorkerInfo(
            id=worker_id,
            host=ip_address,
            port=8000,
            capabilities=capabilities,
            state=WorkerState.IDLE,
            last_seen=datetime.now(),
            load=0.0
        )
        
        self.scheduler.register_worker(worker_info)
        await self.scheduler.start_scheduler()
        
        self._logger.info(f"Initialized local worker {worker_id} with capabilities: {capabilities}")
    
    def submit_task(self, domain: str, input_data: DomainInput, priority: int = 0) -> str:
        """Submit a task for distributed execution"""
        return self.scheduler.submit_task(domain, input_data, priority)
    
    def get_task_result(self, task_id: str) -> Optional[DomainOutput]:
        """Get the result of a completed task"""
        return self.scheduler.get_task_result(task_id)
    
    async def get_distributed_stats(self) -> Dict[str, Any]:
        """Get statistics about the distributed system"""
        return self.scheduler.get_worker_stats()
    
    async def shutdown(self):
        """Shutdown the distributed task manager"""
        if self.scheduler:
            await self.scheduler.stop_scheduler()


# Global distributed task manager instance
distributed_task_manager = DistributedTaskManager()


def get_distributed_task_manager() -> DistributedTaskManager:
    """Get the global distributed task manager"""
    return distributed_task_manager