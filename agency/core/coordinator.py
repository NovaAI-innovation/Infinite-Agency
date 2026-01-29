from typing import Dict, List, Any, Optional
from .base_domain import BaseDomain, DomainInput, DomainOutput
from .domain_registry import DomainRegistry
from ..utils.logger import get_logger
import asyncio


class CrossDomainCoordinator:
    """Coordinates execution across multiple domains, enabling them to enhance each other's output"""
    
    def __init__(self, registry: DomainRegistry):
        self.registry = registry
        self.logger = get_logger(__name__)
    
    async def execute_with_enhancement(self, primary_domain: str, input_data: DomainInput) -> DomainOutput:
        """Execute a task with the primary domain and allow other domains to enhance the output"""
        primary_domain_obj = self.registry.get_domain(primary_domain)
        if not primary_domain_obj:
            return DomainOutput(
                success=False,
                error=f"Primary domain '{primary_domain}' not found"
            )
        
        # Execute the primary domain
        primary_result = await primary_domain_obj.execute(input_data)
        
        if not primary_result.success:
            return primary_result
        
        # Allow other domains to enhance the output
        enhancement_results = await self._apply_enhancements(
            primary_domain_obj, 
            input_data, 
            primary_result
        )
        
        # Combine the primary result with enhancements
        final_output = self._combine_results(primary_result, enhancement_results)
        
        return final_output
    
    async def _apply_enhancements(
        self, 
        primary_domain: BaseDomain, 
        input_data: DomainInput, 
        primary_result: DomainOutput
    ) -> List[DomainOutput]:
        """Apply enhancements from other domains to the primary result"""
        enhancement_tasks = []
        
        for domain in self.registry.get_all_domains():
            if domain.name != primary_domain.name and self._can_enhance(domain, primary_result):
                # Create modified input that includes the primary result for context
                enhancement_input = DomainInput(
                    query=input_data.query,
                    context={
                        **input_data.context,
                        "primary_result": primary_result,
                        "enhancement_target": domain.name
                    },
                    parameters=input_data.parameters
                )
                
                enhancement_task = asyncio.create_task(
                    self._execute_enhancement(domain, enhancement_input)
                )
                enhancement_tasks.append(enhancement_task)
        
        enhancement_results = await asyncio.gather(*enhancement_tasks, return_exceptions=True)
        
        # Filter out exceptions and return successful results
        valid_results = []
        for result in enhancement_results:
            if isinstance(result, Exception):
                self.logger.error(f"Enhancement failed: {result}")
            elif isinstance(result, DomainOutput) and result.success:
                valid_results.append(result)
        
        return valid_results
    
    async def _execute_enhancement(self, domain: BaseDomain, input_data: DomainInput) -> DomainOutput:
        """Execute an enhancement with a specific domain"""
        try:
            return await domain.execute(input_data)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Enhancement execution failed: {str(e)}"
            )
    
    def _can_enhance(self, domain: BaseDomain, primary_result: DomainOutput) -> bool:
        """Determine if a domain can enhance the primary result"""
        # Check if the domain can handle enhancement requests
        enhancement_input = DomainInput(
            query="enhance",
            context={"primary_result": primary_result},
            parameters={}
        )
        return domain.can_handle(enhancement_input)
    
    def _combine_results(self, primary_result: DomainOutput, enhancement_results: List[DomainOutput]) -> DomainOutput:
        """Combine the primary result with enhancement results"""
        combined_data = primary_result.data
        
        # Apply enhancements to the primary data
        for enhancement in enhancement_results:
            if enhancement.success and enhancement.data:
                combined_data = self._apply_single_enhancement(combined_data, enhancement)
        
        # Update metadata with information about applied enhancements
        combined_metadata = primary_result.metadata.copy()
        combined_metadata["applied_enhancements"] = [
            {"domain": enh.domain_name if hasattr(enh, 'domain_name') else "unknown", "type": "enhancement"}
            for enh in enhancement_results
        ]
        
        return DomainOutput(
            success=True,
            data=combined_data,
            metadata=combined_metadata
        )
    
    def _apply_single_enhancement(self, primary_data: Any, enhancement: DomainOutput) -> Any:
        """Apply a single enhancement to the primary data"""
        # This is a generic implementation - specific domains may override this behavior
        if isinstance(primary_data, dict) and isinstance(enhancement.data, dict):
            # Merge dictionaries
            import copy
            result = copy.deepcopy(primary_data)
            result.update(enhancement.data)
            return result
        elif isinstance(primary_data, str) and isinstance(enhancement.data, str):
            # Concatenate strings with a separator
            return f"{primary_data}\n\nEnhanced by {enhancement.__class__.__name__}:\n{enhancement.data}"
        else:
            # For other types, just store both in a tuple or list
            return (primary_data, enhancement.data)
    
    async def execute_multi_domain_workflow(self, workflow: List[Dict[str, Any]]) -> DomainOutput:
        """Execute a workflow that involves multiple domains in sequence"""
        current_context = {}
        
        for step in workflow:
            domain_name = step["domain"]
            query = step["query"]
            params = step.get("parameters", {})
            
            domain = self.registry.get_domain(domain_name)
            if not domain:
                return DomainOutput(
                    success=False,
                    error=f"Domain '{domain_name}' not found in workflow"
                )
            
            # Create input with accumulated context
            step_input = DomainInput(
                query=query,
                context=current_context,
                parameters=params
            )
            
            if not domain.can_handle(step_input):
                return DomainOutput(
                    success=False,
                    error=f"Domain '{domain_name}' cannot handle the input: {query}"
                )
            
            result = await domain.execute(step_input)
            
            if not result.success:
                return result
            
            # Update context with the result for the next step
            current_context[f"step_{workflow.index(step)}"] = result.data
            current_context["last_result"] = result.data
        
        return DomainOutput(success=True, data=current_context)