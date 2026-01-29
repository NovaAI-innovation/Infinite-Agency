from typing import Any, Dict, Optional, Union, List
import os
import json
from pathlib import Path
import yaml
from dataclasses import dataclass, fields
from enum import Enum
from ..utils.logger import get_logger


class EnvVarType(Enum):
    """Types of environment variables"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    PATH = "path"


@dataclass
class EnvVarDefinition:
    """Definition of an environment variable"""
    name: str
    var_type: EnvVarType
    default: Any = None
    description: str = ""
    required: bool = False
    validator: callable = None  # A function to validate the value


class EnvironmentManager:
    """Manages environment variables with validation and type conversion"""
    
    def __init__(self):
        self.definitions: Dict[str, EnvVarDefinition] = {}
        self._logger = get_logger(__name__)
    
    def define_var(self, name: str, var_type: EnvVarType, default: Any = None, 
                   description: str = "", required: bool = False, validator: callable = None):
        """Define an environment variable"""
        self.definitions[name] = EnvVarDefinition(
            name=name,
            var_type=var_type,
            default=default,
            description=description,
            required=required,
            validator=validator
        )
    
    def get(self, name: str, default: Any = None) -> Any:
        """Get an environment variable with type conversion"""
        if name not in self.definitions:
            # If not defined, fall back to standard os.getenv with provided default
            value = os.getenv(name, default)
            return value
        
        definition = self.definitions[name]
        env_value = os.getenv(name)
        
        # Use the definition's default if no environment value is set
        if env_value is None:
            if definition.required:
                raise ValueError(f"Required environment variable '{name}' is not set")
            return definition.default
        
        # Convert the value based on the defined type
        converted_value = self._convert_value(env_value, definition.var_type)
        
        # Validate the value if a validator is provided
        if definition.validator and not definition.validator(converted_value):
            raise ValueError(f"Validation failed for environment variable '{name}': {converted_value}")
        
        return converted_value
    
    def get_all_defined(self) -> Dict[str, Any]:
        """Get all defined environment variables"""
        result = {}
        for name in self.definitions:
            try:
                result[name] = self.get(name)
            except Exception as e:
                self._logger.warning(f"Could not get environment variable '{name}': {e}")
                result[name] = None
        return result
    
    def _convert_value(self, value: str, var_type: EnvVarType) -> Any:
        """Convert a string value to the specified type"""
        if var_type == EnvVarType.STRING:
            return value
        elif var_type == EnvVarType.INTEGER:
            return int(value)
        elif var_type == EnvVarType.FLOAT:
            return float(value)
        elif var_type == EnvVarType.BOOLEAN:
            # Common boolean representations
            lower_val = value.lower()
            if lower_val in ('true', '1', 'yes', 'on', 'enabled'):
                return True
            elif lower_val in ('false', '0', 'no', 'off', 'disabled'):
                return False
            else:
                raise ValueError(f"Cannot convert '{value}' to boolean")
        elif var_type == EnvVarType.LIST:
            # Assume comma-separated values
            return [item.strip() for item in value.split(',')]
        elif var_type == EnvVarType.DICT:
            # Assume JSON-formatted string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError(f"Cannot parse '{value}' as JSON dictionary")
        elif var_type == EnvVarType.PATH:
            return Path(value)
        else:
            return value
    
    def load_from_file(self, file_path: Union[str, Path], file_format: str = 'auto'):
        """Load environment variables from a file"""
        file_path = Path(file_path)
        
        if file_format == 'auto':
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                file_format = 'yaml'
            elif file_path.suffix.lower() == '.json':
                file_format = 'json'
            else:
                file_format = 'env'  # Default to .env format
        
        if file_format == 'env':
            self._load_env_file(file_path)
        elif file_format == 'json':
            self._load_json_file(file_path)
        elif file_format == 'yaml':
            self._load_yaml_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    
    def _load_env_file(self, file_path: Path):
        """Load environment variables from a .env file"""
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    os.environ[key] = value
    
    def _load_json_file(self, file_path: Path):
        """Load environment variables from a JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for key, value in data.items():
            os.environ[key] = str(value)
    
    def _load_yaml_file(self, file_path: Path):
        """Load environment variables from a YAML file"""
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        for key, value in data.items():
            os.environ[key] = str(value)
    
    def validate_all(self) -> List[str]:
        """Validate all defined environment variables and return a list of errors"""
        errors = []
        
        for name, definition in self.definitions.items():
            try:
                self.get(name)
            except Exception as e:
                errors.append(f"{name}: {str(e)}")
        
        return errors


class ConfigurableComponent:
    """Base class for components that can be configured via environment variables"""
    
    def __init__(self):
        self.env_manager = get_environment_manager()
    
    def get_env(self, name: str, default: Any = None) -> Any:
        """Get an environment variable value"""
        return self.env_manager.get(name, default)


# Global environment manager instance
environment_manager = EnvironmentManager()


def get_environment_manager() -> EnvironmentManager:
    """Get the global environment manager"""
    return environment_manager


# Define common environment variables for the agency system
def setup_common_env_vars():
    """Setup common environment variables for the agency system"""
    env_mgr = get_environment_manager()
    
    # Core system variables
    env_mgr.define_var(
        "AGENCY_DEBUG",
        EnvVarType.BOOLEAN,
        default=False,
        description="Enable debug logging"
    )
    
    env_mgr.define_var(
        "AGENCY_LOG_LEVEL",
        EnvVarType.STRING,
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    env_mgr.define_var(
        "AGENCY_MAX_CONCURRENT_TASKS",
        EnvVarType.INTEGER,
        default=10,
        description="Maximum number of concurrent tasks per domain"
    )
    
    env_mgr.define_var(
        "AGENCY_COMMUNICATION_TIMEOUT",
        EnvVarType.FLOAT,
        default=30.0,
        description="Timeout for inter-domain communication in seconds"
    )
    
    env_mgr.define_var(
        "AGENCY_CACHE_ENABLED",
        EnvVarType.BOOLEAN,
        default=True,
        description="Enable/disable caching for domains"
    )
    
    env_mgr.define_var(
        "AGENCY_RESOURCE_QUOTA_CPU",
        EnvVarType.FLOAT,
        default=50.0,
        description="CPU quota percentage for domains"
    )
    
    env_mgr.define_var(
        "AGENCY_RESOURCE_QUOTA_MEMORY",
        EnvVarType.INTEGER,
        default=512,
        description="Memory quota in MB for domains"
    )
    
    # Validation function for port numbers
    def validate_port(port):
        return 0 <= port <= 65535
    
    env_mgr.define_var(
        "AGENCY_SERVER_PORT",
        EnvVarType.INTEGER,
        default=8000,
        description="Port for the agency server",
        validator=validate_port
    )


# Setup common environment variables on import
setup_common_env_vars()