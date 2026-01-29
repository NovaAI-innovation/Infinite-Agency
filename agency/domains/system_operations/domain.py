from typing import Dict, Any, List, Optional
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import asyncio
import os
import shutil
import json
from pathlib import Path
import tempfile
from datetime import datetime


class SystemOperationsDomain(BaseDomain):
    """Domain responsible for system operations including filesystem operations and file management"""

    def __init__(self, name: str = "system_operations", description: str = "Handles system operations including filesystem operations and file management/directory organization", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.operation_types = [
            "file_operations", "directory_operations", "file_management", 
            "directory_organization", "backup_restore", "file_search", "permissions"
        ]
        self.file_operations = [
            "create", "read", "write", "delete", "copy", "move", 
            "rename", "compress", "decompress", "encrypt", "decrypt"
        ]
        self.directory_operations = [
            "create", "delete", "list", "navigate", "organize", 
            "backup", "restore", "search", "cleanup"
        ]
        self.system_templates = {
            "file_operations": self._handle_file_operations,
            "directory_operations": self._handle_directory_operations,
            "file_management": self._handle_file_management,
            "directory_organization": self._handle_directory_organization,
            "backup_restore": self._handle_backup_restore,
            "file_search": self._handle_file_search,
            "permissions": self._handle_permissions
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Execute system operations based on the input specification"""
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

                # Determine the type of system operation to perform
                operation_type = self._determine_operation_type(query)
                operation_subtype = params.get("subtype", context.get("subtype", ""))
                path = params.get("path", context.get("path", "./"))
                destination = params.get("destination", context.get("destination", ""))

                if operation_type not in self.operation_types:
                    return DomainOutput(
                        success=False,
                        error=f"Operation type '{operation_type}' not supported. Available types: {', '.join(self.operation_types)}"
                    )

                # Execute the system operation
                result_data = await self._execute_system_operation(operation_type, query, operation_subtype, path, destination, params)

                # Enhance the result if other domains are available
                enhanced_result = await self._enhance_with_other_domains(result_data, input_data)

                return DomainOutput(
                    success=enhanced_result.get("success", False),
                    data={
                        "result": enhanced_result,
                        "operation_type": operation_type,
                        "operation_subtype": operation_subtype,
                        "path": path,
                        "destination": destination,
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
                error=f"System operation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest system operations
        system_keywords = [
            "file", "directory", "folder", "filesystem", "fs", 
            "create file", "delete file", "move file", "copy file",
            "create directory", "delete directory", "move directory", "copy directory",
            "read file", "write file", "edit file", "update file",
            "list files", "list directories", "browse", "navigate",
            "organize", "arrange", "structure", "manage files",
            "backup", "restore", "archive", "compress", "zip", "tar",
            "search file", "find file", "locate file", "grep",
            "permissions", "chmod", "ownership", "access",
            "disk space", "storage", "cleanup", "clean", "remove",
            "symlink", "hardlink", "link", "mount", "unmount",
            "system", "operation", "admin", "administration"
        ]

        return any(keyword in query for keyword in system_keywords)

    def _determine_operation_type(self, query: str) -> str:
        """Determine what type of system operation to perform based on the query"""
        if any(word in query for word in ["file", "read", "write", "create", "delete", "copy", "move", "rename"]):
            return "file_operations"
        elif any(word in query for word in ["directory", "folder", "create dir", "delete dir", "make dir", "mkdir"]):
            return "directory_operations"
        elif any(word in query for word in ["manage", "organize", "arrange", "structure", "file management"]):
            return "file_management"
        elif any(word in query for word in ["organize", "structure", "directory organization", "folder structure"]):
            return "directory_organization"
        elif any(word in query for word in ["backup", "restore", "archive", "snapshot"]):
            return "backup_restore"
        elif any(word in query for word in ["search", "find", "locate", "grep", "lookup"]):
            return "file_search"
        elif any(word in query for word in ["permission", "chmod", "access", "ownership", "security"]):
            return "permissions"
        else:
            return "file_operations"  # Default to file operations

    async def _execute_system_operation(self, operation_type: str, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate system operation based on type"""
        if operation_type in self.system_templates:
            return await self.system_templates[operation_type](query, operation_subtype, path, destination, params)
        else:
            return await self._execute_generic_system_operation(query, operation_type, operation_subtype, path, destination, params)

    async def _handle_file_operations(self, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations like create, read, write, delete, copy, move, etc."""
        operation = operation_subtype or self._determine_file_operation(query)
        
        try:
            file_path = Path(path)
            
            if operation == "create":
                content = params.get("content", "")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                return {
                    "success": True,
                    "operation": "create_file",
                    "path": str(file_path),
                    "message": f"File created at {file_path}"
                }
            
            elif operation == "read":
                if not file_path.exists():
                    return {
                        "success": False,
                        "operation": "read_file",
                        "path": str(file_path),
                        "error": f"File does not exist: {file_path}"
                    }
                
                content = file_path.read_text()
                return {
                    "success": True,
                    "operation": "read_file",
                    "path": str(file_path),
                    "content": content,
                    "size": len(content),
                    "message": f"File read successfully from {file_path}"
                }
            
            elif operation == "write":
                content = params.get("content", "")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                return {
                    "success": True,
                    "operation": "write_file",
                    "path": str(file_path),
                    "size": len(content),
                    "message": f"Content written to {file_path}"
                }
            
            elif operation == "delete":
                if not file_path.exists():
                    return {
                        "success": False,
                        "operation": "delete_file",
                        "path": str(file_path),
                        "error": f"File does not exist: {file_path}"
                    }
                
                file_path.unlink()
                return {
                    "success": True,
                    "operation": "delete_file",
                    "path": str(file_path),
                    "message": f"File deleted: {file_path}"
                }
            
            elif operation == "copy":
                dest_path = Path(destination)
                if not file_path.exists():
                    return {
                        "success": False,
                        "operation": "copy_file",
                        "source": str(file_path),
                        "destination": str(dest_path),
                        "error": f"Source file does not exist: {file_path}"
                    }
                
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(file_path), str(dest_path))
                return {
                    "success": True,
                    "operation": "copy_file",
                    "source": str(file_path),
                    "destination": str(dest_path),
                    "message": f"File copied from {file_path} to {dest_path}"
                }
            
            elif operation == "move":
                dest_path = Path(destination)
                if not file_path.exists():
                    return {
                        "success": False,
                        "operation": "move_file",
                        "source": str(file_path),
                        "destination": str(dest_path),
                        "error": f"Source file does not exist: {file_path}"
                    }
                
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
                return {
                    "success": True,
                    "operation": "move_file",
                    "source": str(file_path),
                    "destination": str(dest_path),
                    "message": f"File moved from {file_path} to {dest_path}"
                }
            
            elif operation == "rename":
                new_name = params.get("new_name")
                if not new_name:
                    return {
                        "success": False,
                        "operation": "rename_file",
                        "path": str(file_path),
                        "error": "New name not provided"
                    }
                
                new_path = file_path.parent / new_name
                if not file_path.exists():
                    return {
                        "success": False,
                        "operation": "rename_file",
                        "path": str(file_path),
                        "new_path": str(new_path),
                        "error": f"File does not exist: {file_path}"
                    }
                
                file_path.rename(new_path)
                return {
                    "success": True,
                    "operation": "rename_file",
                    "old_path": str(file_path),
                    "new_path": str(new_path),
                    "message": f"File renamed from {file_path} to {new_path}"
                }
            
            else:
                return {
                    "success": False,
                    "operation": operation,
                    "path": str(file_path),
                    "error": f"Unsupported file operation: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": operation,
                "path": str(file_path),
                "error": str(e)
            }

    async def _handle_directory_operations(self, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle directory operations like create, delete, list, navigate, etc."""
        operation = operation_subtype or self._determine_directory_operation(query)
        
        try:
            dir_path = Path(path)
            
            if operation == "create":
                dir_path.mkdir(parents=True, exist_ok=True)
                return {
                    "success": True,
                    "operation": "create_directory",
                    "path": str(dir_path),
                    "message": f"Directory created at {dir_path}"
                }
            
            elif operation == "delete":
                if not dir_path.exists() or not dir_path.is_dir():
                    return {
                        "success": False,
                        "operation": "delete_directory",
                        "path": str(dir_path),
                        "error": f"Directory does not exist or is not a directory: {dir_path}"
                    }
                
                # Check if directory is empty or force delete is requested
                force = params.get("force", False)
                if not force and any(dir_path.iterdir()):
                    return {
                        "success": False,
                        "operation": "delete_directory",
                        "path": str(dir_path),
                        "error": f"Directory is not empty. Use force=True to delete non-empty directory."
                    }
                
                shutil.rmtree(str(dir_path))
                return {
                    "success": True,
                    "operation": "delete_directory",
                    "path": str(dir_path),
                    "message": f"Directory deleted: {dir_path}"
                }
            
            elif operation == "list":
                if not dir_path.exists() or not dir_path.is_dir():
                    return {
                        "success": False,
                        "operation": "list_directory",
                        "path": str(dir_path),
                        "error": f"Directory does not exist or is not a directory: {dir_path}"
                    }
                
                items = []
                recursive = params.get("recursive", False)
                
                if recursive:
                    for item in dir_path.rglob("*"):
                        items.append({
                            "name": item.name,
                            "path": str(item),
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else 0,
                            "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                else:
                    for item in dir_path.iterdir():
                        items.append({
                            "name": item.name,
                            "path": str(item),
                            "type": "directory" if item.is_dir() else "file",
                            "size": item.stat().st_size if item.is_file() else 0,
                            "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                
                return {
                    "success": True,
                    "operation": "list_directory",
                    "path": str(dir_path),
                    "items": items,
                    "count": len(items),
                    "message": f"Listed {len(items)} items in {dir_path}"
                }
            
            elif operation == "navigate":
                if not dir_path.exists() or not dir_path.is_dir():
                    return {
                        "success": False,
                        "operation": "navigate_directory",
                        "path": str(dir_path),
                        "error": f"Directory does not exist or is not a directory: {dir_path}"
                    }
                
                # Return directory structure
                structure = self._get_directory_structure(dir_path)
                return {
                    "success": True,
                    "operation": "navigate_directory",
                    "path": str(dir_path),
                    "structure": structure,
                    "message": f"Navigated to {dir_path}"
                }
            
            else:
                return {
                    "success": False,
                    "operation": operation,
                    "path": str(dir_path),
                    "error": f"Unsupported directory operation: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": operation,
                "path": str(dir_path),
                "error": str(e)
            }

    async def _handle_file_management(self, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file management operations like organizing, categorizing, etc."""
        try:
            base_path = Path(path)
            
            if not base_path.exists():
                return {
                    "success": False,
                    "operation": "file_management",
                    "path": str(base_path),
                    "error": f"Path does not exist: {base_path}"
                }
            
            # Organize files by extension
            if "organize" in query or "by extension" in query or operation_subtype == "organize_by_extension":
                return await self._organize_files_by_extension(base_path)
            
            # Organize files by date
            elif "by date" in query or "by month" in query or operation_subtype == "organize_by_date":
                return await self._organize_files_by_date(base_path)
            
            # Organize files by type
            elif "by type" in query or operation_subtype == "organize_by_type":
                return await self._organize_files_by_type(base_path)
            
            # Clean up temporary files
            elif "cleanup" in query or "clean" in query or operation_subtype == "cleanup":
                return await self._cleanup_temporary_files(base_path)
            
            else:
                return {
                    "success": False,
                    "operation": "file_management",
                    "path": str(base_path),
                    "error": f"Unsupported file management operation for query: {query}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "file_management",
                "path": str(Path(path)),
                "error": str(e)
            }

    async def _handle_directory_organization(self, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle directory organization operations like structuring, templating, etc."""
        try:
            base_path = Path(path)
            
            if not base_path.exists():
                return {
                    "success": False,
                    "operation": "directory_organization",
                    "path": str(base_path),
                    "error": f"Path does not exist: {base_path}"
                }
            
            # Create project structure
            if "project" in query or "structure" in query or operation_subtype == "create_project_structure":
                return await self._create_project_structure(base_path, params)
            
            # Standardize directory naming
            elif "standardize" in query or "normalize" in query or operation_subtype == "standardize_naming":
                return await self._standardize_directory_naming(base_path)
            
            # Create organizational hierarchy
            elif "hierarchy" in query or "organize hierarchy" in query or operation_subtype == "create_hierarchy":
                return await self._create_directory_hierarchy(base_path, params)
            
            else:
                return {
                    "success": False,
                    "operation": "directory_organization",
                    "path": str(base_path),
                    "error": f"Unsupported directory organization operation for query: {query}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "directory_organization",
                "path": str(Path(path)),
                "error": str(e)
            }

    async def _handle_backup_restore(self, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle backup and restore operations"""
        try:
            source_path = Path(path)
            backup_path = Path(destination) if destination else Path(params.get("backup_location", "./backups"))
            
            if "backup" in query or operation_subtype == "create_backup":
                return await self._create_backup(source_path, backup_path, params)
            
            elif "restore" in query or operation_subtype == "restore_backup":
                return await self._restore_backup(backup_path, source_path, params)
            
            else:
                return {
                    "success": False,
                    "operation": "backup_restore",
                    "source": str(source_path),
                    "destination": str(backup_path),
                    "error": f"Unsupported backup/restore operation for query: {query}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "backup_restore",
                "source": str(Path(path)),
                "destination": str(Path(destination)),
                "error": str(e)
            }

    async def _handle_file_search(self, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file search operations"""
        try:
            search_path = Path(path)
            search_term = params.get("search_term", query.split()[-1] if query.split() else "")
            
            if not search_path.exists():
                return {
                    "success": False,
                    "operation": "file_search",
                    "path": str(search_path),
                    "error": f"Search path does not exist: {search_path}"
                }
            
            # Search for files by name
            if "filename" in query or "name" in query or operation_subtype == "search_by_name":
                return await self._search_files_by_name(search_path, search_term, params)
            
            # Search for files by content
            elif "content" in query or "text" in query or operation_subtype == "search_by_content":
                return await self._search_files_by_content(search_path, search_term, params)
            
            # Search for files by extension
            elif "extension" in query or "ext" in query or operation_subtype == "search_by_extension":
                extension = params.get("extension", search_term)
                return await self._search_files_by_extension(search_path, extension, params)
            
            else:
                # Default to name search
                return await self._search_files_by_name(search_path, search_term, params)
                
        except Exception as e:
            return {
                "success": False,
                "operation": "file_search",
                "path": str(Path(path)),
                "error": str(e)
            }

    async def _handle_permissions(self, query: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file and directory permissions operations"""
        try:
            target_path = Path(path)
            
            if not target_path.exists():
                return {
                    "success": False,
                    "operation": "permissions",
                    "path": str(target_path),
                    "error": f"Path does not exist: {target_path}"
                }
            
            # Change permissions
            if "chmod" in query or "permission" in query or operation_subtype == "change_permissions":
                permissions = params.get("permissions", "644")
                return await self._change_permissions(target_path, permissions)
            
            # Get permissions
            elif "get" in query or "view" in query or operation_subtype == "get_permissions":
                return await self._get_permissions(target_path)
            
            # Change ownership
            elif "owner" in query or "ownership" in query or operation_subtype == "change_ownership":
                owner = params.get("owner")
                group = params.get("group")
                return await self._change_ownership(target_path, owner, group)
            
            else:
                return {
                    "success": False,
                    "operation": "permissions",
                    "path": str(target_path),
                    "error": f"Unsupported permissions operation for query: {query}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "operation": "permissions",
                "path": str(Path(path)),
                "error": str(e)
            }

    async def _execute_generic_system_operation(self, query: str, operation_type: str, operation_subtype: str, path: str, destination: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute generic system operation when specific type isn't determined"""
        return {
            "operation_type": operation_type,
            "operation_subtype": operation_subtype,
            "path": path,
            "destination": destination,
            "query": query,
            "result": f"Performed {operation_type} operation for {query}",
            "timestamp": datetime.now().isoformat(),
            "success": True
        }

    def _determine_file_operation(self, query: str) -> str:
        """Determine specific file operation from query"""
        if "create" in query or "new" in query:
            return "create"
        elif "read" in query or "view" in query or "show" in query:
            return "read"
        elif "write" in query or "update" in query or "edit" in query:
            return "write"
        elif "delete" in query or "remove" in query or "erase" in query:
            return "delete"
        elif "copy" in query or "duplicate" in query:
            return "copy"
        elif "move" in query or "transfer" in query:
            return "move"
        elif "rename" in query or "change name" in query:
            return "rename"
        else:
            return "read"  # Default to read

    def _determine_directory_operation(self, query: str) -> str:
        """Determine specific directory operation from query"""
        if "create" in query or "new" in query or "mkdir" in query:
            return "create"
        elif "delete" in query or "remove" in query or "rmdir" in query:
            return "delete"
        elif "list" in query or "ls" in query or "browse" in query:
            return "list"
        elif "navigate" in query or "cd" in query or "enter" in query:
            return "navigate"
        else:
            return "list"  # Default to list

    def _get_directory_structure(self, path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Get directory structure recursively"""
        if current_depth >= max_depth:
            return {"name": path.name, "path": str(path), "type": "directory", "truncated": True}
        
        structure = {
            "name": path.name,
            "path": str(path),
            "type": "directory",
            "children": []
        }
        
        try:
            for item in path.iterdir():
                if item.is_dir():
                    child_structure = self._get_directory_structure(item, max_depth, current_depth + 1)
                    structure["children"].append(child_structure)
                else:
                    structure["children"].append({
                        "name": item.name,
                        "path": str(item),
                        "type": "file",
                        "size": item.stat().st_size
                    })
        except PermissionError:
            structure["error"] = "Permission denied"
        
        return structure

    async def _organize_files_by_extension(self, base_path: Path) -> Dict[str, Any]:
        """Organize files by their extensions"""
        operations = []
        
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()[1:]  # Remove the dot
                
                if ext:  # Only organize files with extensions
                    ext_dir = base_path / ext
                    ext_dir.mkdir(exist_ok=True)
                    
                    new_path = ext_dir / file_path.name
                    if new_path != file_path:  # Don't move to same location
                        shutil.move(str(file_path), str(new_path))
                        operations.append({
                            "action": "moved",
                            "from": str(file_path),
                            "to": str(new_path)
                        })
        
        return {
            "success": True,
            "operation": "organize_by_extension",
            "path": str(base_path),
            "operations_performed": len(operations),
            "operations": operations,
            "message": f"Organized files by extension in {base_path}"
        }

    async def _organize_files_by_date(self, base_path: Path) -> Dict[str, Any]:
        """Organize files by their modification dates"""
        operations = []
        
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                mod_date = datetime.fromtimestamp(stat.st_mtime)
                
                year_dir = base_path / str(mod_date.year)
                month_dir = year_dir / f"{mod_date.month:02d}"
                
                year_dir.mkdir(exist_ok=True)
                month_dir.mkdir(exist_ok=True)
                
                new_path = month_dir / file_path.name
                if new_path != file_path:  # Don't move to same location
                    shutil.move(str(file_path), str(new_path))
                    operations.append({
                        "action": "moved",
                        "from": str(file_path),
                        "to": str(new_path),
                        "date": mod_date.isoformat()
                    })
        
        return {
            "success": True,
            "operation": "organize_by_date",
            "path": str(base_path),
            "operations_performed": len(operations),
            "operations": operations,
            "message": f"Organized files by date in {base_path}"
        }

    async def _organize_files_by_type(self, base_path: Path) -> Dict[str, Any]:
        """Organize files by their types (documents, images, videos, etc.)"""
        # Define file type categories
        type_map = {
            "documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
            "videos": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"],
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
            "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".html", ".css", ".json", ".xml"]
        }
        
        operations = []
        
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                
                # Find the category for this extension
                category = "others"  # Default category
                for cat, exts in type_map.items():
                    if ext in exts:
                        category = cat
                        break
                
                cat_dir = base_path / category
                cat_dir.mkdir(exist_ok=True)
                
                new_path = cat_dir / file_path.name
                if new_path != file_path:  # Don't move to same location
                    shutil.move(str(file_path), str(new_path))
                    operations.append({
                        "action": "moved",
                        "from": str(file_path),
                        "to": str(new_path),
                        "category": category
                    })
        
        return {
            "success": True,
            "operation": "organize_by_type",
            "path": str(base_path),
            "operations_performed": len(operations),
            "operations": operations,
            "message": f"Organized files by type in {base_path}"
        }

    async def _cleanup_temporary_files(self, base_path: Path) -> Dict[str, Any]:
        """Clean up temporary files"""
        temp_extensions = [".tmp", ".temp", ".cache", ".log", "~", ".bak", ".old"]
        operations = []
        
        for file_path in base_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                name = file_path.name.lower()
                
                # Check if it's a temporary file
                is_temp = any(ext == temp_ext for temp_ext in temp_extensions) or \
                         any(temp_pattern in name for temp_pattern in ["temp", "cache", "~"])
                
                if is_temp:
                    try:
                        file_path.unlink()
                        operations.append({
                            "action": "deleted",
                            "file": str(file_path)
                        })
                    except Exception as e:
                        operations.append({
                            "action": "failed_to_delete",
                            "file": str(file_path),
                            "error": str(e)
                        })
        
        return {
            "success": True,
            "operation": "cleanup",
            "path": str(base_path),
            "files_cleaned": len(operations),
            "operations": operations,
            "message": f"Cleaned up temporary files in {base_path}"
        }

    async def _create_project_structure(self, base_path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standard project directory structure"""
        # Define a standard project structure
        structure = params.get("structure", {
            "src": {},
            "tests": {},
            "docs": {},
            "config": {},
            "assets": {
                "images": {},
                "styles": {},
                "scripts": {}
            },
            "lib": {},
            "bin": {}
        })
        
        def create_structure(current_path: Path, structure_dict: Dict[str, Any]):
            for name, contents in structure_dict.items():
                item_path = current_path / name
                item_path.mkdir(exist_ok=True)
                
                if isinstance(contents, dict):
                    create_structure(item_path, contents)
        
        create_structure(base_path, structure)
        
        return {
            "success": True,
            "operation": "create_project_structure",
            "path": str(base_path),
            "structure": structure,
            "message": f"Created project structure in {base_path}"
        }

    async def _standardize_directory_naming(self, base_path: Path) -> Dict[str, Any]:
        """Standardize directory naming (convert to lowercase with underscores)"""
        operations = []
        
        # Process directories first (bottom-up to avoid path issues)
        for dir_path in sorted(base_path.rglob("*"), key=lambda x: str(x), reverse=True):
            if dir_path.is_dir():
                # Convert name to standardized format
                original_name = dir_path.name
                standardized_name = self._standardize_name(original_name)
                
                if standardized_name != original_name:
                    new_path = dir_path.parent / standardized_name
                    try:
                        dir_path.rename(new_path)
                        operations.append({
                            "action": "renamed_directory",
                            "from": str(dir_path),
                            "to": str(new_path)
                        })
                    except Exception as e:
                        operations.append({
                            "action": "failed_to_rename_directory",
                            "path": str(dir_path),
                            "error": str(e)
                        })
        
        return {
            "success": True,
            "operation": "standardize_naming",
            "path": str(base_path),
            "operations_performed": len(operations),
            "operations": operations,
            "message": f"Standardized directory naming in {base_path}"
        }

    def _standardize_name(self, name: str) -> str:
        """Convert a name to standardized format (lowercase with underscores)"""
        import re
        # Replace spaces and special characters with underscores
        standardized = re.sub(r'[^\w]', '_', name.lower())
        # Remove multiple consecutive underscores
        standardized = re.sub(r'_+', '_', standardized)
        # Remove leading/trailing underscores
        standardized = standardized.strip('_')
        return standardized or name  # Return original if result is empty

    async def _create_directory_hierarchy(self, base_path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a directory hierarchy based on parameters"""
        hierarchy = params.get("hierarchy", {})
        
        def create_hierarchy_recursive(current_path: Path, hierarchy_dict: Dict[str, Any]):
            for name, contents in hierarchy_dict.items():
                item_path = current_path / name
                item_path.mkdir(exist_ok=True)
                
                if isinstance(contents, dict):
                    create_hierarchy_recursive(item_path, contents)
        
        create_hierarchy_recursive(base_path, hierarchy)
        
        return {
            "success": True,
            "operation": "create_hierarchy",
            "path": str(base_path),
            "hierarchy": hierarchy,
            "message": f"Created directory hierarchy in {base_path}"
        }

    async def _create_backup(self, source_path: Path, backup_path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup of the source directory"""
        import zipfile
        from datetime import datetime
        
        # Create backup directory if it doesn't exist
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Create a timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{source_path.name}_{timestamp}.zip"
        backup_file = backup_path / backup_name
        
        try:
            # Create a zip archive of the source
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if source_path.is_file():
                    # Backup a single file
                    zipf.write(source_path, source_path.name)
                else:
                    # Backup a directory
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_path.parent)
                            zipf.write(file_path, arcname)
            
            return {
                "success": True,
                "operation": "create_backup",
                "source": str(source_path),
                "backup_file": str(backup_file),
                "size": backup_file.stat().st_size,
                "message": f"Backup created at {backup_file}"
            }
        except Exception as e:
            return {
                "success": False,
                "operation": "create_backup",
                "source": str(source_path),
                "backup_path": str(backup_path),
                "error": str(e)
            }

    async def _restore_backup(self, backup_path: Path, restore_path: Path, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restore from a backup file"""
        import zipfile
        
        if not backup_path.exists():
            return {
                "success": False,
                "operation": "restore_backup",
                "backup_file": str(backup_path),
                "error": f"Backup file does not exist: {backup_path}"
            }
        
        try:
            # Create restore directory if it doesn't exist
            restore_path.mkdir(parents=True, exist_ok=True)
            
            # Extract the backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_path)
            
            return {
                "success": True,
                "operation": "restore_backup",
                "backup_file": str(backup_path),
                "restore_path": str(restore_path),
                "message": f"Backup restored to {restore_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "operation": "restore_backup",
                "backup_file": str(backup_path),
                "restore_path": str(restore_path),
                "error": str(e)
            }

    async def _search_files_by_name(self, search_path: Path, search_term: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files by name"""
        case_sensitive = params.get("case_sensitive", False)
        recursive = params.get("recursive", True)
        
        matches = []
        
        if recursive:
            iterator = search_path.rglob("*")
        else:
            iterator = search_path.iterdir()
        
        for item in iterator:
            name = item.name
            if not case_sensitive:
                name = name.lower()
                search_term_lower = search_term.lower()
            else:
                search_term_lower = search_term
            
            if search_term_lower in name:
                matches.append({
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
        
        return {
            "success": True,
            "operation": "search_by_name",
            "search_path": str(search_path),
            "search_term": search_term,
            "matches": matches,
            "count": len(matches),
            "message": f"Found {len(matches)} matches for '{search_term}' in {search_path}"
        }

    async def _search_files_by_content(self, search_path: Path, search_term: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files by content"""
        case_sensitive = params.get("case_sensitive", False)
        recursive = params.get("recursive", True)
        
        matches = []
        
        if recursive:
            files = [f for f in search_path.rglob("*") if f.is_file()]
        else:
            files = [f for f in search_path.iterdir() if f.is_file()]
        
        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                search_content = content
                search_term_for_match = search_term
                
                if not case_sensitive:
                    search_content = search_content.lower()
                    search_term_for_match = search_term_for_match.lower()
                
                if search_term_for_match in search_content:
                    # Get the context around the match
                    lines = content.split('\n')
                    matching_lines = []
                    for i, line in enumerate(lines):
                        line_content = line
                        if not case_sensitive:
                            line_content = line_content.lower()
                        
                        if search_term_for_match in line_content:
                            matching_lines.append({
                                "line_number": i + 1,
                                "content": line.strip()
                            })
                    
                    matches.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "type": "file",
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "matching_lines": matching_lines
                    })
            except Exception:
                # Skip files that can't be read
                continue
        
        return {
            "success": True,
            "operation": "search_by_content",
            "search_path": str(search_path),
            "search_term": search_term,
            "matches": matches,
            "count": len(matches),
            "message": f"Found {len(matches)} files containing '{search_term}' in {search_path}"
        }

    async def _search_files_by_extension(self, search_path: Path, extension: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files by extension"""
        if not extension.startswith('.'):
            extension = '.' + extension
        
        recursive = params.get("recursive", True)
        
        matches = []
        
        if recursive:
            files = [f for f in search_path.rglob("*") if f.is_file() and f.suffix.lower() == extension.lower()]
        else:
            files = [f for f in search_path.iterdir() if f.is_file() and f.suffix.lower() == extension.lower()]
        
        for file_path in files:
            matches.append({
                "name": file_path.name,
                "path": str(file_path),
                "type": "file",
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        
        return {
            "success": True,
            "operation": "search_by_extension",
            "search_path": str(search_path),
            "extension": extension,
            "matches": matches,
            "count": len(matches),
            "message": f"Found {len(matches)} files with extension '{extension}' in {search_path}"
        }

    async def _change_permissions(self, target_path: Path, permissions: str) -> Dict[str, Any]:
        """Change file/directory permissions"""
        try:
            # Convert string permissions to integer (e.g., "755" to 0o755)
            perm_int = int(permissions, 8)  # Octal representation
            target_path.chmod(perm_int)
            
            return {
                "success": True,
                "operation": "change_permissions",
                "path": str(target_path),
                "permissions": permissions,
                "message": f"Changed permissions of {target_path} to {permissions}"
            }
        except Exception as e:
            return {
                "success": False,
                "operation": "change_permissions",
                "path": str(target_path),
                "permissions": permissions,
                "error": str(e)
            }

    async def _get_permissions(self, target_path: Path) -> Dict[str, Any]:
        """Get file/directory permissions"""
        try:
            import stat
            file_stat = target_path.stat()
            permissions = stat.filemode(file_stat.st_mode)
            
            return {
                "success": True,
                "operation": "get_permissions",
                "path": str(target_path),
                "permissions": permissions,
                "numeric_permissions": oct(file_stat.st_mode)[-3:],
                "message": f"Permissions for {target_path}: {permissions}"
            }
        except Exception as e:
            return {
                "success": False,
                "operation": "get_permissions",
                "path": str(target_path),
                "error": str(e)
            }

    async def _change_ownership(self, target_path: Path, owner: str = None, group: str = None) -> Dict[str, Any]:
        """Change file/directory ownership (requires appropriate privileges)"""
        try:
            # Note: This requires appropriate system privileges
            # On Unix systems, this typically requires root access
            import pwd
            import grp
            
            uid = -1
            gid = -1
            
            if owner:
                uid = pwd.getpwnam(owner).pw_uid
            if group:
                gid = grp.getgrnam(group).gr_gid
            
            # Only change what was specified
            if uid != -1 or gid != -1:
                os.chown(str(target_path), uid if uid != -1 else -1, gid if gid != -1 else -1)
            
            return {
                "success": True,
                "operation": "change_ownership",
                "path": str(target_path),
                "owner": owner,
                "group": group,
                "message": f"Changed ownership of {target_path} to {owner}:{group}" if owner and group else f"Changed ownership of {target_path}"
            }
        except Exception as e:
            return {
                "success": False,
                "operation": "change_ownership",
                "path": str(target_path),
                "owner": owner,
                "group": group,
                "error": str(e)
            }

    async def _enhance_with_other_domains(self, result_data: Dict[str, Any], input_data: DomainInput) -> Dict[str, Any]:
        """Allow other domains to enhance the system operations result"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original result
        return result_data