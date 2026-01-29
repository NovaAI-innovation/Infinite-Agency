from typing import Dict, Type, List, Optional, Any
import importlib
import pkgutil
import inspect
import functools
from pathlib import Path
from .base_domain import BaseDomain
from ..utils.logger import get_logger


class PluginManager:
    """Manages plugins for the agency system"""
    
    def __init__(self):
        self._domain_plugins: Dict[str, Type[BaseDomain]] = {}
        self._loaded_plugins: Dict[str, Any] = {}
        self._logger = get_logger(__name__)
    
    def register_domain_plugin(self, name: str, domain_class: Type[BaseDomain]):
        """Register a domain plugin"""
        if not issubclass(domain_class, BaseDomain):
            raise TypeError(f"Domain class must inherit from BaseDomain: {domain_class}")
        
        self._domain_plugins[name] = domain_class
        self._logger.info(f"Registered domain plugin: {name} -> {domain_class.__name__}")
    
    def get_domain_plugin(self, name: str) -> Optional[Type[BaseDomain]]:
        """Get a registered domain plugin"""
        return self._domain_plugins.get(name)
    
    def get_all_domain_plugins(self) -> Dict[str, Type[BaseDomain]]:
        """Get all registered domain plugins"""
        return self._domain_plugins.copy()
    
    def load_plugins_from_directory(self, directory: str):
        """Dynamically load plugins from a directory"""
        plugin_dir = Path(directory)
        
        if not plugin_dir.exists():
            self._logger.warning(f"Plugin directory does not exist: {directory}")
            return
        
        # Add the directory to Python path temporarily
        import sys
        sys.path.insert(0, str(plugin_dir.parent))
        
        try:
            # Discover and import modules in the directory
            for _, module_name, _ in pkgutil.iter_modules([str(plugin_dir)]):
                full_module_name = f"{plugin_dir.name}.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)
                    
                    # Find all classes that inherit from BaseDomain
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            obj != BaseDomain and
                            issubclass(obj, BaseDomain) and
                            obj.__module__ == full_module_name
                        ):
                            # Use the class name as the plugin name, or derive from a property
                            plugin_name = getattr(obj, 'PLUGIN_NAME', name.lower())
                            self.register_domain_plugin(plugin_name, obj)
                            
                except ImportError as e:
                    self._logger.error(f"Failed to import plugin module {full_module_name}: {e}")
        finally:
            # Remove the directory from Python path
            if str(plugin_dir.parent) in sys.path:
                sys.path.remove(str(plugin_dir.parent))
    
    def load_plugin_from_module(self, module_name: str, class_name: str):
        """Load a specific plugin from a module"""
        try:
            module = importlib.import_module(module_name)
            domain_class = getattr(module, class_name)
            
            if not issubclass(domain_class, BaseDomain):
                raise TypeError(f"Class {class_name} does not inherit from BaseDomain")
            
            plugin_name = getattr(domain_class, 'PLUGIN_NAME', class_name.lower())
            self.register_domain_plugin(plugin_name, domain_class)
            
            self._logger.info(f"Loaded plugin {plugin_name} from {module_name}.{class_name}")
        except (ImportError, AttributeError) as e:
            self._logger.error(f"Failed to load plugin {class_name} from {module_name}: {e}")
            raise


# Global plugin manager instance
plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager"""
    return plugin_manager


def plugin_entry_point(func):
    """Decorator to mark a function as a plugin entry point"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper