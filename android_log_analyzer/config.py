"""
Configuration management for Android Log Analyzer.

This module handles loading and managing configuration for issue detection patterns,
output formats, and other analyzer settings.
"""
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration for the log analyzer."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config_path = Path(config_path) if config_path else None
        self._config: Dict[str, Any] = {}
        self._load_default_config()
        
        if self.config_path and self.config_path.exists():
            self.load_config(self.config_path)
    
    def _load_default_config(self) -> None:
        """Load default configuration."""
        self._config = {
            "output": {
                "formats": ["console", "json"],
                "json_indent": 2,
                "console_colors": True,
                "max_line_length": 120
            },
            "analysis": {
                "max_file_size_mb": 100,
                "skip_unparseable_lines": True,
                "case_sensitive_tags": True,
                "enable_parallel_processing": False,
                "max_workers": 4
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "platforms": {
                "default": "google",
                "supported": ["google", "mtk", "sprd", "qualcomm"]
            }
        }
    
    def load_config(self, config_path: Union[str, Path]) -> None:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file.
            
        Raises:
            FileNotFoundError: If config file doesn't exist.
            json.JSONDecodeError: If config file is invalid JSON.
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Merge user config with defaults
            self._merge_config(self._config, user_config)
            logger.info(f"Loaded configuration from: {config_path}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config file {config_path}: {e}")
            raise
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """
        Recursively merge configuration dictionaries.
        
        Args:
            base: Base configuration dictionary to update.
            update: Configuration updates to apply.
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "output.json_indent").
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., "output.json_indent").
            value: Value to set.
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the final key
        config[keys[-1]] = value
    
    def save_config(self, output_path: Union[str, Path]) -> None:
        """
        Save current configuration to file.
        
        Args:
            output_path: Path where to save the configuration.
            
        Raises:
            PermissionError: If file can't be written.
        """
        output_path = Path(output_path)
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving config to {output_path}: {e}")
            raise
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get complete configuration dictionary.
        
        Returns:
            Complete configuration dictionary.
        """
        return self._config.copy()


def create_sample_config(output_path: Union[str, Path]) -> None:
    """
    Create a sample configuration file.
    
    Args:
        output_path: Path where to create the sample config.
    """
    config_manager = ConfigManager()
    config_manager.save_config(output_path)
    print(f"Sample configuration created at: {output_path}")


if __name__ == "__main__":
    # Create sample config for testing
    create_sample_config("sample_config.json")
