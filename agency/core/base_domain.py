from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum


class DomainOutput:
    """Represents the output from a domain operation"""
    def __init__(self, success: bool, data: Any = None, error: str = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}

    def __repr__(self):
        return f"DomainOutput(success={self.success}, data={str(self.data)[:100]}{'...' if len(str(self.data)) > 100 else ''}, error={self.error})"


class DomainInput:
    """Represents the input to a domain operation"""
    def __init__(self, query: str, context: Dict[str, Any] = None, parameters: Dict[str, Any] = None):
        self.query = query
        self.context = context or {}
        self.parameters = parameters or {}


class CommunicationProtocol(Enum):
    """Defines how domains can communicate with each other"""
    REQUEST_RESPONSE = "request_response"
    EVENT_DRIVEN = "event_driven"
    SHARED_MEMORY = "shared_memory"


class BaseDomain(ABC):
    """Abstract base class for all domains in the agency"""

    def __init__(self, name: str, description: str = "", resource_manager=None, cache_enabled: bool = True):
        self.name = name
        self.description = description
        self.dependencies = []
        self.dependents = []
        self.resource_manager = resource_manager
        self.cache_enabled = cache_enabled

        # Import cache here to avoid circular imports
        from .caching import get_domain_cache
        self.cache = get_domain_cache()

    @abstractmethod
    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Execute the domain's primary function"""
        pass

    @abstractmethod
    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the given input"""
        pass

    async def execute_with_cache(self, input_data: DomainInput) -> DomainOutput:
        """Execute with caching support"""
        if self.cache_enabled:
            # Try to get result from cache first
            cached_result = await self.cache.get_cached_result(self.name, "execute", input_data)
            if cached_result is not None:
                return cached_result

        # Execute the actual operation
        result = await self.execute(input_data)

        # Cache the result if successful
        if self.cache_enabled and result.success:
            await self.cache.cache_result(self.name, "execute", input_data, result)

        return result

    def add_dependency(self, domain: 'BaseDomain'):
        """Add a dependency on another domain"""
        if domain not in self.dependencies:
            self.dependencies.append(domain)
            domain.add_dependent(self)

    def add_dependent(self, domain: 'BaseDomain'):
        """Add a dependent domain"""
        if domain not in self.dependents:
            self.dependents.append(domain)

    def get_dependencies(self) -> List['BaseDomain']:
        """Get all domains this domain depends on"""
        return self.dependencies.copy()

    def get_dependents(self) -> List['BaseDomain']:
        """Get all domains that depend on this domain"""
        return self.dependents.copy()

    def get_capability_description(self) -> str:
        """Get a description of what this domain can do"""
        return f"{self.name}: {self.description}"