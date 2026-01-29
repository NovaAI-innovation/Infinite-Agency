from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
from ..utils.logger import get_logger


class ResourceType(Enum):
    """Types of resources that can be managed"""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    DISK = "disk"
    CONCURRENT_TASKS = "concurrent_tasks"


@dataclass
class ResourceQuota:
    """Defines resource limits for a domain"""
    cpu_percent: float = 50.0  # Percentage of CPU
    memory_mb: int = 512       # Memory in MB
    network_mb: int = 100      # Network bandwidth in MB
    disk_mb: int = 100         # Disk space in MB
    max_concurrent_tasks: int = 10  # Max concurrent tasks


@dataclass
class ResourceUsage:
    """Tracks current resource usage"""
    cpu_percent: float = 0.0
    memory_mb: int = 0
    network_mb: int = 0
    disk_mb: int = 0
    active_tasks: int = 0


class ResourceManager:
    """Manages resource allocation and quotas for domains"""
    
    def __init__(self):
        self._quotas: Dict[str, ResourceQuota] = {}
        self._usage: Dict[str, ResourceUsage] = {}
        self._active_tasks: Dict[str, asyncio.Semaphore] = {}
        self._logger = get_logger(__name__)
    
    def set_quota(self, domain_name: str, quota: ResourceQuota):
        """Set resource quota for a domain"""
        self._quotas[domain_name] = quota
        self._usage[domain_name] = ResourceUsage()
        self._active_tasks[domain_name] = asyncio.Semaphore(quota.max_concurrent_tasks)
        self._logger.info(f"Set resource quota for domain {domain_name}: {quota}")
    
    def get_quota(self, domain_name: str) -> Optional[ResourceQuota]:
        """Get resource quota for a domain"""
        return self._quotas.get(domain_name)
    
    def get_usage(self, domain_name: str) -> Optional[ResourceUsage]:
        """Get current resource usage for a domain"""
        return self._usage.get(domain_name)
    
    async def acquire_resources(self, domain_name: str) -> bool:
        """Attempt to acquire resources for a domain task"""
        if domain_name not in self._quotas:
            # Domain doesn't have a quota, use default
            self.set_quota(domain_name, ResourceQuota())

        quota = self._quotas[domain_name]
        usage = self._usage[domain_name]

        # Check if we've reached the max concurrent tasks limit
        # The semaphore size equals the max concurrent tasks, so if the semaphore
        # is at max capacity (value is 0), we can't acquire more
        if self._active_tasks[domain_name]._value <= 0:
            self._logger.warning(f"Max concurrent tasks exceeded for domain {domain_name}")
            return False

        # Acquire the semaphore (this will always succeed since we checked above)
        await self._active_tasks[domain_name].acquire()

        # Update usage (in a real system, this would check actual resource usage)
        usage.active_tasks += 1

        return True
    
    def release_resources(self, domain_name: str):
        """Release resources after a domain task completes"""
        if domain_name in self._usage:
            self._usage[domain_name].active_tasks -= 1
        
        if domain_name in self._active_tasks:
            self._active_tasks[domain_name].release()
    
    def is_within_limits(self, domain_name: str) -> bool:
        """Check if a domain is within its resource limits"""
        if domain_name not in self._quotas:
            return True  # No quota defined, assume unlimited
        
        quota = self._quotas[domain_name]
        usage = self._usage[domain_name]
        
        return (
            usage.active_tasks <= quota.max_concurrent_tasks
        )


class ResourceLimitedDomainMixin:
    """Mixin to add resource management to domains"""

    def __init__(self, resource_manager: ResourceManager = None, **kwargs):
        # Extract the parameters that BaseDomain expects
        name = kwargs.pop('name', 'unnamed_domain')
        description = kwargs.pop('description', 'A domain with resource management')

        # Call parent init with the expected parameters
        super().__init__(name=name, description=description)

        # Initialize resource management
        self.resource_manager = resource_manager or ResourceManager()
        self.default_quota = ResourceQuota()
    
    async def execute_with_resource_limit(self, *args, **kwargs):
        """Execute domain operation with resource limits"""
        if not await self.resource_manager.acquire_resources(self.name):
            raise RuntimeError(f"Resource limits exceeded for domain {self.name}")
        
        try:
            result = await self.execute(*args, **kwargs)
            return result
        finally:
            self.resource_manager.release_resources(self.name)