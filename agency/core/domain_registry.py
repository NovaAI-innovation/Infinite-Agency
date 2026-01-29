from typing import Dict, List, Optional, Type
from .base_domain import BaseDomain
import asyncio


class DomainRegistry:
    """Manages registration and retrieval of domains in the agency"""
    
    def __init__(self):
        self._domains: Dict[str, BaseDomain] = {}
        self._domain_types: Dict[str, Type[BaseDomain]] = {}
    
    def register_domain_type(self, name: str, domain_class: Type[BaseDomain]):
        """Register a domain type that can be instantiated later"""
        self._domain_types[name] = domain_class
    
    def create_and_register_domain(self, name: str, domain_type: str, **kwargs) -> BaseDomain:
        """Create an instance of a registered domain type and register it"""
        if domain_type not in self._domain_types:
            raise ValueError(f"Domain type '{domain_type}' not registered")
        
        domain_instance = self._domain_types[domain_type](name, **kwargs)
        self.register_domain(domain_instance)
        return domain_instance
    
    def register_domain(self, domain: BaseDomain):
        """Register a domain instance"""
        self._domains[domain.name] = domain
    
    def get_domain(self, name: str) -> Optional[BaseDomain]:
        """Retrieve a domain by name"""
        return self._domains.get(name)
    
    def get_all_domains(self) -> List[BaseDomain]:
        """Get all registered domains"""
        return list(self._domains.values())
    
    def get_domains_by_capability(self, capability_query: str) -> List[BaseDomain]:
        """Find domains that can handle a specific capability"""
        matching_domains = []
        for domain in self._domains.values():
            # Simple keyword matching for now - could be enhanced with more sophisticated matching
            if capability_query.lower() in domain.get_capability_description().lower():
                matching_domains.append(domain)
        return matching_domains
    
    def remove_domain(self, name: str):
        """Remove a domain from the registry"""
        if name in self._domains:
            del self._domains[name]
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get a representation of domain dependencies"""
        graph = {}
        for domain_name, domain in self._domains.items():
            graph[domain_name] = [dep.name for dep in domain.get_dependencies()]
        return graph


# Global registry instance
registry = DomainRegistry()


def get_registry() -> DomainRegistry:
    """Get the global domain registry"""
    return registry