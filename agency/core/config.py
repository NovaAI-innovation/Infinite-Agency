from typing import Dict, Any, Optional
import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from ..utils.logger import get_logger


@dataclass
class AgencyConfig:
    """Configuration for the multi-domain agency"""
    # Communication settings
    max_message_queue_size: int = 1000
    communication_timeout: float = 30.0
    broadcast_exclude_sender: bool = True
    
    # Resource management settings
    default_cpu_quota: float = 50.0
    default_memory_quota: int = 512
    default_max_concurrent_tasks: int = 10
    
    # Error handling settings
    max_retry_attempts: int = 3
    retry_delay_base: float = 1.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Domain settings
    domain_scan_path: str = "./domains"
    auto_register_domains: bool = True


class ConfigManager:
    """Manages configuration for the agency system"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = AgencyConfig()
        self._logger = get_logger(__name__)
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        else:
            self._logger.info("Using default configuration")
    
    def load_config(self, config_file: str):
        """Load configuration from a file"""
        try:
            with open(config_file, 'r') as f:
                config_dict = json.load(f)
            
            # Update config with loaded values
            for key, value in config_dict.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            self._logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            self._logger.error(f"Failed to load config from {config_file}: {e}")
            # Keep using defaults
    
    def save_config(self, config_file: str):
        """Save current configuration to a file"""
        try:
            config_dict = asdict(self.config)
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self._logger.info(f"Saved configuration to {config_file}")
        except Exception as e:
            self._logger.error(f"Failed to save config to {config_file}: {e}")
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return getattr(self.config, key, default)
    
    def set_config_value(self, key: str, value: Any):
        """Set a configuration value"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self._logger.debug(f"Set config {key} = {value}")
        else:
            raise AttributeError(f"Configuration has no attribute '{key}'")


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        # Look for config file in standard locations
        config_locations = [
            "./agency_config.json",
            "./config/agency_config.json",
            os.path.expanduser("~/.agency/agency_config.json"),
            "/etc/agency/agency_config.json"
        ]
        
        config_file = None
        for location in config_locations:
            if os.path.exists(location):
                config_file = location
                break
        
        _config_manager = ConfigManager(config_file)
    
    return _config_manager


def get_config() -> AgencyConfig:
    """Get the current agency configuration"""
    return get_config_manager().config