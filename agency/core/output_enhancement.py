from typing import Dict, Any, List, Optional, Callable
import asyncio
import re
from dataclasses import dataclass
from ..core.base_domain import BaseDomain, DomainInput, DomainOutput
from ..utils.logger import get_logger


@dataclass
class EnhancementRule:
    """Defines a rule for enhancing domain output"""
    name: str
    condition: Callable[[DomainOutput], bool]  # Condition to check if enhancement applies
    transformer: Callable[[DomainOutput], DomainOutput]  # Function to transform the output
    priority: int = 0  # Higher priority enhancements are applied first
    description: str = ""


class OutputEnhancer:
    """Manages enhancement of domain outputs"""
    
    def __init__(self):
        self.enhancement_rules: List[EnhancementRule] = []
        self._logger = get_logger(__name__)
    
    def register_enhancement_rule(self, rule: EnhancementRule):
        """Register an enhancement rule"""
        self.enhancement_rules.append(rule)
        self.enhancement_rules.sort(key=lambda r: r.priority, reverse=True)  # Sort by priority (highest first)
        self._logger.info(f"Registered enhancement rule: {rule.name}")
    
    def create_enhancement_rule(
        self, 
        name: str, 
        condition: Callable[[DomainOutput], bool], 
        transformer: Callable[[DomainOutput], DomainOutput],
        priority: int = 0,
        description: str = ""
    ):
        """Create and register an enhancement rule"""
        rule = EnhancementRule(name, condition, transformer, priority, description)
        self.register_enhancement_rule(rule)
        return rule
    
    def enhance_output(self, output: DomainOutput) -> DomainOutput:
        """Apply all applicable enhancements to an output"""
        enhanced_output = output
        
        for rule in self.enhancement_rules:
            try:
                if rule.condition(enhanced_output):
                    enhanced_output = rule.transformer(enhanced_output)
                    self._logger.debug(f"Applied enhancement rule '{rule.name}' to output")
            except Exception as e:
                self._logger.error(f"Error applying enhancement rule '{rule.name}': {e}")
        
        return enhanced_output
    
    async def enhance_output_async(self, output: DomainOutput) -> DomainOutput:
        """Asynchronously apply all applicable enhancements to an output"""
        enhanced_output = output
        
        for rule in self.enhancement_rules:
            try:
                if rule.condition(enhanced_output):
                    # If the transformer is a coroutine, await it
                    if asyncio.iscoroutinefunction(rule.transformer):
                        enhanced_output = await rule.transformer(enhanced_output)
                    else:
                        enhanced_output = rule.transformer(enhanced_output)
                    self._logger.debug(f"Applied enhancement rule '{rule.name}' to output")
            except Exception as e:
                self._logger.error(f"Error applying enhancement rule '{rule.name}': {e}")
        
        return enhanced_output


class CrossDomainEnhancer:
    """Enhances outputs by leveraging other domains"""
    
    def __init__(self, registry):
        self.registry = registry
        self.output_enhancer = OutputEnhancer()
        self._logger = get_logger(__name__)
    
    async def enhance_with_other_domains(
        self, 
        primary_output: DomainOutput, 
        primary_domain: BaseDomain, 
        input_context: DomainInput
    ) -> DomainOutput:
        """Enhance an output by leveraging other domains in the system"""
        if not primary_output.success:
            return primary_output
        
        enhanced_output = primary_output
        
        # Get all domains except the primary one
        other_domains = [d for d in self.registry.get_all_domains() if d.name != primary_domain.name]
        
        for domain in other_domains:
            try:
                # Check if this domain can enhance the output
                enhancement_input = DomainInput(
                    query="enhance",
                    context={
                        "primary_output": enhanced_output,
                        "primary_domain": primary_domain.name,
                        "original_input": input_context
                    },
                    parameters={"target_domain": domain.name}
                )
                
                if domain.can_handle(enhancement_input):
                    # Ask the domain to enhance the output
                    enhancement_result = await domain.execute(enhancement_input)
                    
                    if enhancement_result.success and enhancement_result.data:
                        # Apply the enhancement to the primary output
                        enhanced_output = self._apply_domain_enhancement(
                            enhanced_output, 
                            enhancement_result, 
                            domain.name
                        )
                        
                        self._logger.info(f"Output enhanced by domain {domain.name}")
            except Exception as e:
                self._logger.error(f"Error getting enhancement from domain {domain.name}: {e}")
        
        return enhanced_output
    
    def _apply_domain_enhancement(
        self, 
        primary_output: DomainOutput, 
        enhancement_output: DomainOutput, 
        enhancer_domain: str
    ) -> DomainOutput:
        """Apply an enhancement from another domain to the primary output"""
        # Create a new output with merged data
        new_data = self._merge_output_data(primary_output.data, enhancement_output.data)
        
        # Update metadata to include enhancement information
        new_metadata = primary_output.metadata.copy()
        if "enhancements_applied" not in new_metadata:
            new_metadata["enhancements_applied"] = []
        new_metadata["enhancements_applied"].append({
            "domain": enhancer_domain,
            "timestamp": asyncio.get_event_loop().time(),
            "enhancement_data": enhancement_output.data
        })
        
        return DomainOutput(
            success=primary_output.success,
            data=new_data,
            error=primary_output.error,
            metadata=new_metadata
        )
    
    def _merge_output_data(self, primary_data: Any, enhancement_data: Any) -> Any:
        """Merge enhancement data with primary output data"""
        if isinstance(primary_data, dict) and isinstance(enhancement_data, dict):
            # Deep merge dictionaries
            import copy
            result = copy.deepcopy(primary_data)
            
            for key, value in enhancement_data.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    # Recursively merge nested dictionaries
                    result[key] = self._merge_output_data(result[key], value)
                else:
                    result[key] = value
            
            return result
        elif isinstance(primary_data, str) and isinstance(enhancement_data, str):
            # Concatenate strings
            return f"{primary_data}\n\nEnhanced by other domains:\n{enhancement_data}"
        elif isinstance(primary_data, list) and isinstance(enhancement_data, list):
            # Extend lists
            return primary_data + enhancement_data
        else:
            # For other types, create a tuple or return the enhancement
            return enhancement_data if enhancement_data is not None else primary_data


class QualityEnhancer:
    """Enhances output quality through various techniques"""
    
    def __init__(self):
        self._logger = get_logger(__name__)
    
    def enhance_code_quality(self, output: DomainOutput) -> DomainOutput:
        """Enhance code quality in outputs"""
        if not output.success or not isinstance(output.data, dict):
            return output
        
        if "code" in output.data:
            enhanced_code = self._improve_code_quality(output.data["code"])
            output.data["code"] = enhanced_code
            output.data["quality_enhanced"] = True
        
        return output
    
    def _improve_code_quality(self, code: str) -> str:
        """Apply code quality improvements"""
        # Add basic formatting and documentation
        lines = code.split('\n')
        enhanced_lines = []
        
        for line in lines:
            enhanced_lines.append(line)
            
            # Add documentation for functions/classes if missing
            if line.strip().startswith(('def ', 'class ')) and not any('"""' in l or "'''" in l for l in enhanced_lines[-3:]):
                # Add basic docstring
                if line.strip().startswith('def '):
                    enhanced_lines.append('    """TODO: Add function description."""')
                elif line.strip().startswith('class '):
                    enhanced_lines.append('    """TODO: Add class description."""')
        
        return '\n'.join(enhanced_lines)
    
    def enhance_research_quality(self, output: DomainOutput) -> DomainOutput:
        """Enhance research output quality"""
        if not output.success or not isinstance(output.data, dict):
            return output
        
        # Add credibility scoring if not present
        if "results" in output.data and isinstance(output.data["results"], dict):
            results = output.data["results"]
            if "credibility_score" not in results:
                results["credibility_score"] = self._calculate_credibility_score(results)
        
        return output
    
    def _calculate_credibility_score(self, results: Dict[str, Any]) -> float:
        """Calculate a basic credibility score for research results"""
        score = 0.5  # Base score
        
        # Increase score if reliable sources are cited
        if "sources_consulted" in results and len(results["sources_consulted"]) > 0:
            score += 0.2
        
        # Increase score if multiple findings are provided
        if "key_findings" in results and len(results["key_findings"]) >= 3:
            score += 0.2
        
        # Cap the score between 0 and 1
        return min(1.0, max(0.0, score))


class EnhancementPipeline:
    """Pipeline for applying multiple enhancement strategies"""
    
    def __init__(self, registry):
        self.cross_domain_enhancer = CrossDomainEnhancer(registry)
        self.quality_enhancer = QualityEnhancer()
        self.output_enhancer = OutputEnhancer()
        self._logger = get_logger(__name__)
    
    async def enhance_output(
        self, 
        output: DomainOutput, 
        primary_domain: BaseDomain, 
        input_context: DomainInput
    ) -> DomainOutput:
        """Enhance an output through the full pipeline"""
        if not output.success:
            return output
        
        # Apply cross-domain enhancements
        enhanced_output = await self.cross_domain_enhancer.enhance_with_other_domains(
            output, primary_domain, input_context
        )
        
        # Apply quality enhancements
        if primary_domain.name == "code_generation":
            enhanced_output = self.quality_enhancer.enhance_code_quality(enhanced_output)
        elif primary_domain.name == "research":
            enhanced_output = self.quality_enhancer.enhance_research_quality(enhanced_output)
        
        # Apply registered enhancement rules
        enhanced_output = await self.output_enhancer.enhance_output_async(enhanced_output)
        
        # Update metadata to indicate enhancement was performed
        if "enhancement_pipeline_applied" not in enhanced_output.metadata:
            enhanced_output.metadata["enhancement_pipeline_applied"] = True
        
        self._logger.info(f"Output enhancement pipeline completed for domain {primary_domain.name}")
        
        return enhanced_output


# Global enhancement pipeline instance
enhancement_pipeline = None


def get_enhancement_pipeline(registry=None):
    """Get the global enhancement pipeline"""
    global enhancement_pipeline
    if enhancement_pipeline is None and registry is not None:
        enhancement_pipeline = EnhancementPipeline(registry)
    return enhancement_pipeline