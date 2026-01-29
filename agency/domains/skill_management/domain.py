from typing import Dict, Any, List, Optional
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import asyncio
import os
import json
import yaml
from pathlib import Path
import requests
from datetime import datetime
import shutil


class SkillManagementDomain(BaseDomain):
    """Domain responsible for managing skill files across all agents including downloading, installing, copying, and removing skills"""

    def __init__(self, name: str = "skill_management", description: str = "Manages skill files across all agents including downloading, installing, copying, and removing skills with marketplace integration", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.operation_types = [
            "download", "install", "copy", "remove", "list", 
            "search_marketplace", "install_from_marketplace", 
            "export", "import", "update"
        ]
        self.marketplace_url = "https://api.agency-marketplace.com"  # Placeholder URL
        self.local_skills_dir = Path("./skills")
        self.agent_skills_dir = Path("./agent_skills")
        
        # Ensure directories exist
        self.local_skills_dir.mkdir(exist_ok=True)
        self.agent_skills_dir.mkdir(exist_ok=True)

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Execute skill management operations based on the input specification"""
        try:
            # Acquire resources before executing
            if not await self.resource_manager.acquire_resources(self.name):
                return DomainOutput(
                    success=False,
                    error=f"Resource limits exceeded for domain {self.name}"
                )

            try:
                query = input_data.query.lower()
                context = input_data.context
                params = input_data.parameters

                # Determine the type of skill management operation to perform
                operation_type = self._determine_operation_type(query)
                source_agent = params.get("source_agent", context.get("source_agent", ""))
                target_agent = params.get("target_agent", context.get("target_agent", ""))
                skill_name = params.get("skill_name", context.get("skill_name", ""))
                skill_url = params.get("skill_url", context.get("skill_url", ""))

                if operation_type not in self.operation_types:
                    return DomainOutput(
                        success=False,
                        error=f"Operation type '{operation_type}' not supported. Available types: {', '.join(self.operation_types)}"
                    )

                # Execute the skill management operation
                result_data = await self._execute_skill_operation(operation_type, query, source_agent, target_agent, skill_name, skill_url, params)

                # Enhance the result if other domains are available
                enhanced_result = await self._enhance_with_other_domains(result_data, input_data)

                return DomainOutput(
                    success=enhanced_result.get("success", False),
                    data={
                        "result": enhanced_result,
                        "operation_type": operation_type,
                        "source_agent": source_agent,
                        "target_agent": target_agent,
                        "skill_name": skill_name,
                        "skill_url": skill_url,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "operation_performed": operation_type
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"Skill management operation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest skill management
        skill_management_keywords = [
            "skill", "skills", "capability", "capabilities", 
            "download skill", "install skill", "remove skill", "delete skill",
            "copy skill", "transfer skill", "move skill",
            "marketplace", "plugin", "plugins", "extension", "extensions",
            "get skill", "add skill", "update skill", "upgrade skill",
            "export skill", "import skill", "share skill", "sync skill",
            "skill management", "skill store", "skill library",
            "install from marketplace", "download from marketplace",
            "skill repository", "skill registry", "skill catalog"
        ]

        return any(keyword in query for keyword in skill_management_keywords)

    def _determine_operation_type(self, query: str) -> str:
        """Determine what type of skill management operation to perform based on the query"""
        if any(word in query for word in ["download", "get from marketplace", "fetch from marketplace"]):
            return "download"
        elif any(word in query for word in ["install", "add", "apply"]):
            return "install"
        elif any(word in query for word in ["copy", "transfer", "move", "duplicate"]):
            return "copy"
        elif any(word in query for word in ["remove", "delete", "uninstall", "erase"]):
            return "remove"
        elif any(word in query for word in ["list", "show", "view", "display"]):
            return "list"
        elif any(word in query for word in ["search marketplace", "find skill", "browse marketplace"]):
            return "search_marketplace"
        elif any(word in query for word in ["install from marketplace", "download from marketplace"]):
            return "install_from_marketplace"
        elif any(word in query for word in ["export", "backup"]):
            return "export"
        elif any(word in query for word in ["import", "restore"]):
            return "import"
        elif any(word in query for word in ["update", "upgrade", "refresh"]):
            return "update"
        else:
            return "list"  # Default to list

    async def _execute_skill_operation(self, operation_type: str, query: str, source_agent: str, target_agent: str, skill_name: str, skill_url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate skill management operation based on type"""
        if operation_type == "download":
            return await self._download_skill(skill_name, skill_url, params)
        elif operation_type == "install":
            return await self._install_skill(skill_name, target_agent, params)
        elif operation_type == "copy":
            return await self._copy_skill(skill_name, source_agent, target_agent, params)
        elif operation_type == "remove":
            return await self._remove_skill(skill_name, target_agent, params)
        elif operation_type == "list":
            return await self._list_skills(target_agent, params)
        elif operation_type == "search_marketplace":
            return await self._search_marketplace(query, params)
        elif operation_type == "install_from_marketplace":
            return await self._install_from_marketplace(skill_name, target_agent, params)
        elif operation_type == "export":
            return await self._export_skill(skill_name, params)
        elif operation_type == "import":
            return await self._import_skill(skill_name, params)
        elif operation_type == "update":
            return await self._update_skill(skill_name, params)
        else:
            return await self._execute_generic_skill_operation(query, operation_type, source_agent, target_agent, skill_name, skill_url, params)

    async def _download_skill(self, skill_name: str, skill_url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Download a skill from a URL or marketplace"""
        try:
            if skill_url:
                # Download from URL
                response = requests.get(skill_url)
                if response.status_code == 200:
                    file_extension = Path(skill_url).suffix
                    skill_file_path = self.local_skills_dir / f"{skill_name}{file_extension}"
                    
                    with open(skill_file_path, 'wb') as f:
                        f.write(response.content)
                    
                    return {
                        "success": True,
                        "operation": "download",
                        "skill_name": skill_name,
                        "file_path": str(skill_file_path),
                        "message": f"Skill '{skill_name}' downloaded successfully"
                    }
                else:
                    return {
                        "success": False,
                        "operation": "download",
                        "skill_name": skill_name,
                        "error": f"Failed to download skill. Status code: {response.status_code}"
                    }
            else:
                # If no URL provided, try to download from marketplace
                return await self._search_and_download_from_marketplace(skill_name, params)
                
        except Exception as e:
            return {
                "success": False,
                "operation": "download",
                "skill_name": skill_name,
                "error": str(e)
            }

    async def _install_skill(self, skill_name: str, target_agent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Install a skill to a specific agent"""
        try:
            # Find the skill file locally
            skill_file = None
            for ext in ['.yaml', '.yml', '.json']:
                potential_file = self.local_skills_dir / f"{skill_name}{ext}"
                if potential_file.exists():
                    skill_file = potential_file
                    break
            
            if not skill_file:
                return {
                    "success": False,
                    "operation": "install",
                    "skill_name": skill_name,
                    "target_agent": target_agent,
                    "error": f"Skill file for '{skill_name}' not found locally"
                }
            
            # Copy skill to agent's skill directory
            agent_skill_dir = self.agent_skills_dir / target_agent
            agent_skill_dir.mkdir(exist_ok=True)
            
            target_file = agent_skill_dir / skill_file.name
            shutil.copy2(skill_file, target_file)
            
            # Apply the skill to the agent if it's loaded
            from ..skills.skill_manager import get_skill_manager
            skill_manager = get_skill_manager()
            
            # Try to get the agent domain from the registry
            from ..core.domain_registry import get_registry
            registry = get_registry()
            agent_domain = registry.get_domain(target_agent)
            
            if agent_domain:
                success = await skill_manager.apply_skill_to_domain(agent_domain, skill_name)
                if success:
                    return {
                        "success": True,
                        "operation": "install",
                        "skill_name": skill_name,
                        "target_agent": target_agent,
                        "file_path": str(target_file),
                        "applied_to_agent": True,
                        "message": f"Skill '{skill_name}' installed and applied to agent '{target_agent}'"
                    }
                else:
                    return {
                        "success": True,
                        "operation": "install",
                        "skill_name": skill_name,
                        "target_agent": target_agent,
                        "file_path": str(target_file),
                        "applied_to_agent": False,
                        "message": f"Skill '{skill_name}' installed to agent '{target_agent}' but could not be applied"
                    }
            else:
                return {
                    "success": True,
                    "operation": "install",
                    "skill_name": skill_name,
                    "target_agent": target_agent,
                    "file_path": str(target_file),
                    "applied_to_agent": False,
                    "message": f"Skill '{skill_name}' installed to agent '{target_agent}' but agent not found in registry"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "install",
                "skill_name": skill_name,
                "target_agent": target_agent,
                "error": str(e)
            }

    async def _copy_skill(self, skill_name: str, source_agent: str, target_agent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Copy a skill from one agent to another"""
        try:
            # Find the skill in the source agent's directory
            source_skill_dir = self.agent_skills_dir / source_agent
            skill_file = None
            
            for ext in ['.yaml', '.yml', '.json']:
                potential_file = source_skill_dir / f"{skill_name}{ext}"
                if potential_file.exists():
                    skill_file = potential_file
                    break
            
            if not skill_file:
                return {
                    "success": False,
                    "operation": "copy",
                    "skill_name": skill_name,
                    "source_agent": source_agent,
                    "target_agent": target_agent,
                    "error": f"Skill file for '{skill_name}' not found in source agent '{source_agent}'"
                }
            
            # Copy to target agent's directory
            target_skill_dir = self.agent_skills_dir / target_agent
            target_skill_dir.mkdir(exist_ok=True)
            
            target_file = target_skill_dir / skill_file.name
            shutil.copy2(skill_file, target_file)
            
            # Apply the skill to the target agent if it's loaded
            from ..skills.skill_manager import get_skill_manager
            skill_manager = get_skill_manager()
            
            # Try to get the target agent domain from the registry
            from ..core.domain_registry import get_registry
            registry = get_registry()
            target_agent_domain = registry.get_domain(target_agent)
            
            if target_agent_domain:
                success = await skill_manager.apply_skill_to_domain(target_agent_domain, skill_name)
                if success:
                    return {
                        "success": True,
                        "operation": "copy",
                        "skill_name": skill_name,
                        "source_agent": source_agent,
                        "target_agent": target_agent,
                        "source_file": str(skill_file),
                        "target_file": str(target_file),
                        "applied_to_target": True,
                        "message": f"Skill '{skill_name}' copied from '{source_agent}' to '{target_agent}' and applied"
                    }
                else:
                    return {
                        "success": True,
                        "operation": "copy",
                        "skill_name": skill_name,
                        "source_agent": source_agent,
                        "target_agent": target_agent,
                        "source_file": str(skill_file),
                        "target_file": str(target_file),
                        "applied_to_target": False,
                        "message": f"Skill '{skill_name}' copied from '{source_agent}' to '{target_agent}' but could not be applied"
                    }
            else:
                return {
                    "success": True,
                    "operation": "copy",
                    "skill_name": skill_name,
                    "source_agent": source_agent,
                    "target_agent": target_agent,
                    "source_file": str(skill_file),
                    "target_file": str(target_file),
                    "applied_to_target": False,
                    "message": f"Skill '{skill_name}' copied from '{source_agent}' to '{target_agent}' but target agent not found in registry"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "copy",
                "skill_name": skill_name,
                "source_agent": source_agent,
                "target_agent": target_agent,
                "error": str(e)
            }

    async def _remove_skill(self, skill_name: str, target_agent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a skill from a specific agent"""
        try:
            # Find the skill in the target agent's directory
            agent_skill_dir = self.agent_skills_dir / target_agent
            skill_file = None
            
            for ext in ['.yaml', '.yml', '.json']:
                potential_file = agent_skill_dir / f"{skill_name}{ext}"
                if potential_file.exists():
                    skill_file = potential_file
                    break
            
            if not skill_file:
                return {
                    "success": False,
                    "operation": "remove",
                    "skill_name": skill_name,
                    "target_agent": target_agent,
                    "error": f"Skill file for '{skill_name}' not found in agent '{target_agent}'"
                }
            
            # Remove the file
            skill_file.unlink()
            
            # Try to remove the skill from the agent's active skills if possible
            from ..skills.skill_manager import get_skill_manager
            skill_manager = get_skill_manager()
            
            # Try to get the agent domain from the registry
            from ..core.domain_registry import get_registry
            registry = get_registry()
            agent_domain = registry.get_domain(target_agent)
            
            if agent_domain and hasattr(agent_domain, 'capabilities'):
                # Remove skill from agent's capabilities if it was added
                if skill_name in agent_domain.capabilities:
                    agent_domain.capabilities.remove(skill_name)
            
            return {
                "success": True,
                "operation": "remove",
                "skill_name": skill_name,
                "target_agent": target_agent,
                "file_removed": str(skill_file),
                "message": f"Skill '{skill_name}' removed from agent '{target_agent}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "remove",
                "skill_name": skill_name,
                "target_agent": target_agent,
                "error": str(e)
            }

    async def _list_skills(self, target_agent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """List skills for a specific agent or all agents"""
        try:
            if target_agent:
                # List skills for a specific agent
                agent_skill_dir = self.agent_skills_dir / target_agent
                if not agent_skill_dir.exists():
                    return {
                        "success": True,
                        "operation": "list",
                        "target_agent": target_agent,
                        "skills": [],
                        "count": 0,
                        "message": f"No skills directory found for agent '{target_agent}'"
                    }
                
                skills = []
                for file_path in agent_skill_dir.glob('*.{yaml,yml,json}'):
                    skills.append({
                        "name": file_path.stem,
                        "path": str(file_path),
                        "extension": file_path.suffix,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                
                return {
                    "success": True,
                    "operation": "list",
                    "target_agent": target_agent,
                    "skills": skills,
                    "count": len(skills),
                    "message": f"Found {len(skills)} skills for agent '{target_agent}'"
                }
            else:
                # List skills for all agents
                all_agent_skills = {}
                for agent_dir in self.agent_skills_dir.iterdir():
                    if agent_dir.is_dir():
                        agent_skills = []
                        for file_path in agent_dir.glob('*.{yaml,yml,json}'):
                            agent_skills.append({
                                "name": file_path.stem,
                                "path": str(file_path),
                                "extension": file_path.suffix,
                                "size": file_path.stat().st_size,
                                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                            })
                        all_agent_skills[agent_dir.name] = {
                            "skills": agent_skills,
                            "count": len(agent_skills)
                        }
                
                return {
                    "success": True,
                    "operation": "list",
                    "all_agents": all_agent_skills,
                    "total_agents": len(all_agent_skills),
                    "message": f"Skills listed for {len(all_agent_skills)} agents"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "list",
                "target_agent": target_agent,
                "error": str(e)
            }

    async def _search_marketplace(self, query: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search the skill marketplace"""
        try:
            # This is a simulated marketplace search
            # In a real implementation, this would call the marketplace API
            search_term = params.get("search_term", query)
            
            # Simulated marketplace data
            marketplace_skills = [
                {
                    "name": "python_development",
                    "title": "Python Development Skills",
                    "description": "Skills for Python development including best practices and common patterns",
                    "author": "Community",
                    "version": "1.0.0",
                    "downloads": 1250,
                    "rating": 4.7,
                    "tags": ["python", "development", "best_practices"],
                    "url": f"{self.marketplace_url}/skills/python_development"
                },
                {
                    "name": "web_development",
                    "title": "Web Development Skills",
                    "description": "Skills for web development including HTML, CSS, and JavaScript",
                    "author": "Community",
                    "version": "1.2.0",
                    "downloads": 980,
                    "rating": 4.5,
                    "tags": ["web", "html", "css", "javascript"],
                    "url": f"{self.marketplace_url}/skills/web_development"
                },
                {
                    "name": "data_analysis",
                    "title": "Data Analysis Skills",
                    "description": "Skills for data analysis using Python and common libraries",
                    "author": "Analytics Team",
                    "version": "1.1.0",
                    "downloads": 750,
                    "rating": 4.8,
                    "tags": ["data", "analysis", "pandas", "numpy"],
                    "url": f"{self.marketplace_url}/skills/data_analysis"
                }
            ]
            
            # Filter results based on search term
            filtered_skills = [
                skill for skill in marketplace_skills
                if search_term.lower() in skill['name'].lower() or 
                   search_term.lower() in skill['title'].lower() or
                   search_term.lower() in skill['description'].lower() or
                   any(search_term.lower() in tag.lower() for tag in skill['tags'])
            ]
            
            return {
                "success": True,
                "operation": "search_marketplace",
                "query": search_term,
                "results": filtered_skills,
                "count": len(filtered_skills),
                "message": f"Found {len(filtered_skills)} skills matching '{search_term}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "search_marketplace",
                "query": query,
                "error": str(e)
            }

    async def _install_from_marketplace(self, skill_name: str, target_agent: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Install a skill directly from the marketplace"""
        try:
            # First, download the skill from marketplace
            download_result = await self._search_and_download_from_marketplace(skill_name, params)
            
            if not download_result.get("success"):
                return download_result
            
            # Then install it to the target agent
            install_result = await self._install_skill(skill_name, target_agent, params)
            
            return {
                "success": install_result.get("success", False),
                "operation": "install_from_marketplace",
                "skill_name": skill_name,
                "target_agent": target_agent,
                "download_result": download_result,
                "install_result": install_result,
                "message": f"Skill '{skill_name}' downloaded from marketplace and installed to agent '{target_agent}'"
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "install_from_marketplace",
                "skill_name": skill_name,
                "target_agent": target_agent,
                "error": str(e)
            }

    async def _export_skill(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export a skill to a file for sharing"""
        try:
            # Find the skill file in local skills directory
            skill_file = None
            for ext in ['.yaml', '.yml', '.json']:
                potential_file = self.local_skills_dir / f"{skill_name}{ext}"
                if potential_file.exists():
                    skill_file = potential_file
                    break
            
            if not skill_file:
                return {
                    "success": False,
                    "operation": "export",
                    "skill_name": skill_name,
                    "error": f"Skill file for '{skill_name}' not found locally"
                }
            
            # Create export directory if it doesn't exist
            export_dir = Path(params.get("export_dir", "./exports"))
            export_dir.mkdir(exist_ok=True)
            
            # Copy the skill file to the export directory
            export_file = export_dir / f"{skill_name}_export{skill_file.suffix}"
            shutil.copy2(skill_file, export_file)
            
            return {
                "success": True,
                "operation": "export",
                "skill_name": skill_name,
                "source_file": str(skill_file),
                "export_file": str(export_file),
                "message": f"Skill '{skill_name}' exported to {export_file}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "export",
                "skill_name": skill_name,
                "error": str(e)
            }

    async def _import_skill(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import a skill from a file"""
        try:
            import_file_path = params.get("file_path")
            if not import_file_path:
                return {
                    "success": False,
                    "operation": "import",
                    "skill_name": skill_name,
                    "error": "No file path provided for import"
                }
            
            import_file = Path(import_file_path)
            if not import_file.exists():
                return {
                    "success": False,
                    "operation": "import",
                    "skill_name": skill_name,
                    "error": f"Import file does not exist: {import_file_path}"
                }
            
            # Copy the imported file to the local skills directory
            target_file = self.local_skills_dir / f"{skill_name}{import_file.suffix}"
            shutil.copy2(import_file, target_file)
            
            return {
                "success": True,
                "operation": "import",
                "skill_name": skill_name,
                "source_file": str(import_file),
                "target_file": str(target_file),
                "message": f"Skill '{skill_name}' imported from {import_file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "import",
                "skill_name": skill_name,
                "error": str(e)
            }

    async def _update_skill(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a skill to the latest version"""
        try:
            # First, check if the skill exists locally
            local_skill_file = None
            for ext in ['.yaml', '.yml', '.json']:
                potential_file = self.local_skills_dir / f"{skill_name}{ext}"
                if potential_file.exists():
                    local_skill_file = potential_file
                    break
            
            if not local_skill_file:
                return {
                    "success": False,
                    "operation": "update",
                    "skill_name": skill_name,
                    "error": f"Skill '{skill_name}' not found locally"
                }
            
            # Check for updates in the marketplace
            search_result = await self._search_marketplace(skill_name, params)
            
            if not search_result.get("success") or search_result.get("count", 0) == 0:
                return {
                    "success": False,
                    "operation": "update",
                    "skill_name": skill_name,
                    "error": f"No updates found for skill '{skill_name}' in marketplace"
                }
            
            marketplace_skill = None
            for skill in search_result["results"]:
                if skill["name"] == skill_name:
                    marketplace_skill = skill
                    break
            
            if not marketplace_skill:
                return {
                    "success": False,
                    "operation": "update",
                    "skill_name": skill_name,
                    "error": f"Skill '{skill_name}' not found in marketplace"
                }
            
            # Compare versions
            local_version = self._get_local_skill_version(local_skill_file)
            marketplace_version = marketplace_skill["version"]
            
            if self._compare_versions(local_version, marketplace_version) >= 0:
                return {
                    "success": True,
                    "operation": "update",
                    "skill_name": skill_name,
                    "message": f"Skill '{skill_name}' is already up to date (version {local_version})"
                }
            
            # Download the updated version
            download_result = await self._download_skill(skill_name, marketplace_skill["url"], params)
            
            if not download_result.get("success"):
                return download_result
            
            return {
                "success": True,
                "operation": "update",
                "skill_name": skill_name,
                "old_version": local_version,
                "new_version": marketplace_version,
                "download_result": download_result,
                "message": f"Skill '{skill_name}' updated from version {local_version} to {marketplace_version}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "operation": "update",
                "skill_name": skill_name,
                "error": str(e)
            }

    async def _search_and_download_from_marketplace(self, skill_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search and download a skill from the marketplace"""
        try:
            # Search for the skill in marketplace
            search_result = await self._search_marketplace(skill_name, params)
            
            if not search_result.get("success") or search_result.get("count", 0) == 0:
                return {
                    "success": False,
                    "operation": "download",
                    "skill_name": skill_name,
                    "error": f"Skill '{skill_name}' not found in marketplace"
                }
            
            # Find the exact skill match
            target_skill = None
            for skill in search_result["results"]:
                if skill["name"] == skill_name:
                    target_skill = skill
                    break
            
            if not target_skill:
                return {
                    "success": False,
                    "operation": "download",
                    "skill_name": skill_name,
                    "error": f"Exact match for skill '{skill_name}' not found in search results"
                }
            
            # Download the skill file
            skill_url = target_skill["url"]
            response = requests.get(skill_url)
            
            if response.status_code == 200:
                # Determine file extension from content type or URL
                file_extension = Path(skill_url).suffix
                if not file_extension:
                    # Default to YAML if not specified
                    file_extension = ".yaml"
                
                skill_file_path = self.local_skills_dir / f"{skill_name}{file_extension}"
                
                with open(skill_file_path, 'wb') as f:
                    f.write(response.content)
                
                return {
                    "success": True,
                    "operation": "download",
                    "skill_name": skill_name,
                    "file_path": str(skill_file_path),
                    "source_url": skill_url,
                    "message": f"Skill '{skill_name}' downloaded from marketplace"
                }
            else:
                return {
                    "success": False,
                    "operation": "download",
                    "skill_name": skill_name,
                    "error": f"Failed to download skill from marketplace. Status code: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "download",
                "skill_name": skill_name,
                "error": str(e)
            }

    def _get_local_skill_version(self, skill_file: Path) -> str:
        """Get the version of a local skill file"""
        try:
            if skill_file.suffix.lower() in ['.yaml', '.yml']:
                with open(skill_file, 'r') as f:
                    data = yaml.safe_load(f)
            elif skill_file.suffix.lower() == '.json':
                with open(skill_file, 'r') as f:
                    data = json.load(f)
            else:
                return "unknown"
            
            return data.get('version', '1.0.0')
        except:
            return "unknown"

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings (returns -1 if v1<v2, 0 if equal, 1 if v1>v2)"""
        try:
            v1_parts = [int(part) for part in version1.split('.')]
            v2_parts = [int(part) for part in version2.split('.')]
            
            # Pad shorter version with zeros
            while len(v1_parts) < len(v2_parts):
                v1_parts.append(0)
            while len(v2_parts) < len(v1_parts):
                v2_parts.append(0)
            
            for i in range(min(len(v1_parts), len(v2_parts))):
                if v1_parts[i] < v2_parts[i]:
                    return -1
                elif v1_parts[i] > v2_parts[i]:
                    return 1
            
            return 0
        except:
            # If parsing fails, just compare as strings
            if version1 < version2:
                return -1
            elif version1 > version2:
                return 1
            else:
                return 0

    async def _execute_generic_skill_operation(self, query: str, operation_type: str, source_agent: str, target_agent: str, skill_name: str, skill_url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic skill operation when specific type isn't determined"""
        return {
            "operation_type": operation_type,
            "source_agent": source_agent,
            "target_agent": target_agent,
            "skill_name": skill_name,
            "skill_url": skill_url,
            "query": query,
            "result": f"Performed {operation_type} operation for {query}",
            "timestamp": datetime.now().isoformat(),
            "success": True
        }

    async def _enhance_with_other_domains(self, result_data: Dict[str, Any], input_data: DomainInput) -> Dict[str, Any]:
        """Allow other domains to enhance the skill management result"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original result
        return result_data