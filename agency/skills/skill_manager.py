from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
import json
import yaml
from pathlib import Path
import importlib
from ..core.base_domain import BaseDomain
import asyncio


@dataclass
class SkillDefinition:
    """Definition of a skill with its capabilities, knowledge, and behaviors"""
    name: str
    description: str
    version: str = "1.0.0"
    domain_type: str = ""
    capabilities: List[str] = field(default_factory=list)
    knowledge_base: Dict[str, Any] = field(default_factory=dict)
    behaviors: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, str]] = field(default_factory=list)


class SkillLoader:
    """Loads and parses skill definitions from structured files"""
    
    @staticmethod
    def load_skill_from_file(file_path: str) -> SkillDefinition:
        """Load a skill definition from a file (JSON or YAML)"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Skill file not found: {file_path}")
        
        # Determine file type and load accordingly
        if path.suffix.lower() in ['.yaml', '.yml']:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        elif path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        return SkillDefinition(
            name=data.get('name', ''),
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            domain_type=data.get('domain_type', ''),
            capabilities=data.get('capabilities', []),
            knowledge_base=data.get('knowledge_base', {}),
            behaviors=data.get('behaviors', {}),
            dependencies=data.get('dependencies', []),
            parameters=data.get('parameters', {}),
            examples=data.get('examples', [])
        )


class SkillManager:
    """Manages the loading, registration, and application of skills to domains"""
    
    def __init__(self):
        self.skills: Dict[str, SkillDefinition] = {}
        self.skill_files: Dict[str, str] = {}  # Maps skill name to file path
        self.applied_skills: Dict[str, List[str]] = {}  # Maps domain name to applied skills
    
    async def load_skill(self, skill_name: str, file_path: str) -> bool:
        """Load a skill from a file"""
        try:
            skill_def = SkillLoader.load_skill_from_file(file_path)
            self.skills[skill_name] = skill_def
            self.skill_files[skill_name] = file_path
            return True
        except Exception as e:
            print(f"Error loading skill {skill_name}: {e}")
            return False
    
    async def load_skills_from_directory(self, directory_path: str) -> List[str]:
        """Load all skills from a directory"""
        loaded_skills = []
        path = Path(directory_path)
        
        for file_path in path.glob('*.{json,yaml,yml}'):
            skill_name = file_path.stem
            if await self.load_skill(skill_name, str(file_path)):
                loaded_skills.append(skill_name)
        
        return loaded_skills
    
    def get_skill(self, skill_name: str) -> Optional[SkillDefinition]:
        """Get a skill definition by name"""
        return self.skills.get(skill_name)
    
    def get_skills_for_domain(self, domain_type: str) -> List[SkillDefinition]:
        """Get all skills applicable to a specific domain type"""
        return [
            skill for skill in self.skills.values()
            if skill.domain_type == domain_type or skill.domain_type == ""
        ]
    
    async def apply_skill_to_domain(self, domain: BaseDomain, skill_name: str) -> bool:
        """Apply a skill to a domain instance"""
        skill = self.get_skill(skill_name)
        if not skill:
            return False
        
        try:
            # Apply capabilities
            for capability in skill.capabilities:
                if hasattr(domain, 'capabilities'):
                    if capability not in domain.capabilities:
                        domain.capabilities.append(capability)
                else:
                    domain.capabilities = [capability]
            
            # Apply knowledge base
            if hasattr(domain, 'knowledge_base'):
                domain.knowledge_base.update(skill.knowledge_base)
            else:
                domain.knowledge_base = skill.knowledge_base.copy()
            
            # Apply behaviors
            for behavior_name, behavior_config in skill.behaviors.items():
                # Store behavior configuration in domain
                if not hasattr(domain, 'behaviors'):
                    domain.behaviors = {}
                domain.behaviors[behavior_name] = behavior_config
            
            # Store applied skill
            domain_name = domain.name
            if domain_name not in self.applied_skills:
                self.applied_skills[domain_name] = []
            if skill_name not in self.applied_skills[domain_name]:
                self.applied_skills[domain_name].append(skill_name)
            
            return True
        except Exception as e:
            print(f"Error applying skill {skill_name} to domain {domain.name}: {e}")
            return False
    
    async def apply_skills_to_domain(self, domain: BaseDomain, skill_names: List[str]) -> Dict[str, bool]:
        """Apply multiple skills to a domain instance"""
        results = {}
        for skill_name in skill_names:
            results[skill_name] = await self.apply_skill_to_domain(domain, skill_name)
        return results
    
    def get_applied_skills_for_domain(self, domain_name: str) -> List[str]:
        """Get list of skills applied to a specific domain"""
        return self.applied_skills.get(domain_name, [])


# Global skill manager instance
skill_manager = SkillManager()


def get_skill_manager() -> SkillManager:
    """Get the global skill manager instance"""
    return skill_manager