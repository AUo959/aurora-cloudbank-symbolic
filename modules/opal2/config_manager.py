#!/usr/bin/env python3
from datetime import datetime
from pathlib import Path
import json
import schedule
"""
Opal2 Modular System - Configuration Manager
Advanced configuration management with validation and hot-reloading
"""

import asyncio
import logging

# Configure logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import toml
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigFormat(Enum):
    """Configuration file format enumeration"""

    YAML = "yaml"
    JSON = "json"
    TOML = "toml"


@dataclass


class ConfigValidationRule:
    """Configuration validation rule"""

    key: str
    required: bool = True
    type_check: Optional[type] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable] = None
    error_message: Optional[str] = None


@dataclass


class ConfigChangeEvent:
    """Configuration change event"""

    timestamp: datetime
    config_path: str
    changed_keys: List[str]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]


class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes"""

    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_modified(self, event):
        if not event.is_directory:
            self.config_manager._handle_file_change(event.src_path)


class ConfigurationManager:
    """
    Advanced configuration management system with validation and hot-reloading
    """

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.configs: Dict[str, Dict[str, Any]] = {}
        self.validation_rules: Dict[str, List[ConfigValidationRule]] = {}
        self.change_callbacks: Dict[str, List[Callable]] = {}
        self.file_observer: Optional[Observer] = None
        self.hot_reload_enabled = False

        # Default configuration schemas
        self._initialize_default_schemas()

        # Load existing configurations
        self._load_all_configurations()

    def _initialize_default_schemas(self):
        """Initialize default configuration schemas"""
        # Opal2 Graphics Configuration Schema
        self.validation_rules["opal2_graphics"] = [
            ConfigValidationRule("renderer", required=True, type_check=dict),
            ConfigValidationRule(
                "renderer.default_engine",
                required=True,
                type_check=str,
                allowed_values=["webgl", "canvas", "svg"],
            ),
            ConfigValidationRule("renderer.quantum_enhancement", required=True, type_check=bool),
            ConfigValidationRule(
                "renderer.performance_mode",
                required=True,
                type_check=str,
                allowed_values=["fast", "balanced", "quality"],
            ),
            ConfigValidationRule(
                "canvas.width",
                required=True,
                type_check=int,
                min_value=100,
                max_value=4096,
            ),
            ConfigValidationRule(
                "canvas.height",
                required=True,
                type_check=int,
                min_value=100,
                max_value=4096,
            ),
            ConfigValidationRule(
                "quantum.coherence_factor",
                required=True,
                type_check=float,
                min_value=0.0,
                max_value=1.0,
            ),
            ConfigValidationRule(
                "quantum.entanglement_strength",
                required=True,
                type_check=float,
                min_value=0.0,
                max_value=1.0,
            ),
            ConfigValidationRule(
                "quantum.superposition_depth",
                required=True,
                type_check=int,
                min_value=1,
                max_value=10,
            ),
        ]

        # Plugin System Configuration Schema
        self.validation_rules["plugin_system"] = [
            ConfigValidationRule("plugins", required=True, type_check=dict),
            ConfigValidationRule("plugins.auto_load", required=True, type_check=bool),
            ConfigValidationRule("plugins.directories", required=True, type_check=list),
            ConfigValidationRule("plugins.blacklist", required=False, type_check=list),
            ConfigValidationRule("plugins.whitelist", required=False, type_check=list),
            ConfigValidationRule("security.allow_dynamic_loading", required=True, type_check=bool),
            ConfigValidationRule("security.require_signatures", required=True, type_check=bool),
        ]

        # API Configuration Schema
        self.validation_rules["api"] = [
            ConfigValidationRule("server", required=True, type_check=dict),
            ConfigValidationRule("server.host", required=True, type_check=str),
            ConfigValidationRule(
                "server.port",
                required=True,
                type_check=int,
                min_value=1,
                max_value=65535,
            ),
            ConfigValidationRule("server.debug", required=True, type_check=bool),
            ConfigValidationRule("cors.enabled", required=True, type_check=bool),
            ConfigValidationRule("cors.origins", required=False, type_check=list),
            ConfigValidationRule("rate_limiting.enabled", required=True, type_check=bool),
            ConfigValidationRule(
                "rate_limiting.requests_per_minute",
                required=False,
                type_check=int,
                min_value=1,
            ),
            ConfigValidationRule("websocket.enabled", required=True, type_check=bool),
            ConfigValidationRule("websocket.max_connections", required=False, type_check=int, min_value=1),
        ]

    def _load_all_configurations(self):
        """Load all configuration files from the config directory"""
        for config_file in self.config_dir.glob("*.yaml"):
            self._load_config_file(config_file)

        for config_file in self.config_dir.glob("*.json"):
            self._load_config_file(config_file)

        for config_file in self.config_dir.glob("*.toml"):
            self._load_config_file(config_file)

    def _load_config_file(self, file_path: Path):
        """Load a single configuration file"""
        try:
            config_name = file_path.stem

            # Determine format
            if file_path.suffix == ".yaml" or file_path.suffix == ".yml":
                format_type = ConfigFormat.YAML
            elif file_path.suffix == ".json":
                format_type = ConfigFormat.JSON
            elif file_path.suffix == ".toml":
                format_type = ConfigFormat.TOML
            else:
                logger.warning(f"Unsupported config file format: {file_path}")
                return

            # Load configuration
            with open(file_path, "r") as f:
                if format_type == ConfigFormat.YAML:
                    config_data = yaml.safe_load(f)
                elif format_type == ConfigFormat.JSON:
                    config_data = json.load(f)
                elif format_type == ConfigFormat.TOML:
                    config_data = toml.load(f)

            # Validate configuration
            if self._validate_config(config_name, config_data):
                self.configs[config_name] = config_data
                logger.info(f"Loaded configuration: {config_name}")
            else:
                logger.error(f"Validation failed for configuration: {config_name}")

        except Exception as e:
            logger.error(f"Failed to load config file {file_path}: {str(e)}")

    def _validate_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Validate configuration data against schema"""
        if config_name not in self.validation_rules:
            logger.warning(f"No validation rules found for config: {config_name}")
            return True

        rules = self.validation_rules[config_name]

        for rule in rules:
            if not self._validate_single_rule(config_data, rule):
                error_msg = rule.error_message or f"Validation failed for key: {rule.key}"
                logger.error(f"Config validation error in {config_name}: {error_msg}")
                return False

        return True

    def _validate_single_rule(self, config_data: Dict[str, Any], rule: ConfigValidationRule) -> bool:
        """Validate a single configuration rule"""
        # Get value using dot notation
        value = self._get_nested_value(config_data, rule.key)

        # Check if required
        if rule.required and value is None:
            return False

        # Skip further validation if value is None and not required
        if value is None:
            return True

        # Type check
        if rule.type_check and not isinstance(value, rule.type_check):
            return False

        # Range checks
        if rule.min_value is not None and value < rule.min_value:
            return False

        if rule.max_value is not None and value > rule.max_value:
            return False

        # Allowed values check
        if rule.allowed_values is not None and value not in rule.allowed_values:
            return False

        # Custom validator
        if rule.custom_validator and not rule.custom_validator(value):
            return False

        return True

    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Any:
        """Get nested value using dot notation"""
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current

    def _set_nested_value(self, data: Dict[str, Any], key: str, value: Any):
        """Set nested value using dot notation"""
        keys = key.split(".")
        current = data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration by name"""
        return self.configs.get(config_name)

    def get_config_value(self, config_name: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration value"""
        config = self.get_config(config_name)
        if config is None:
            return default

        return self._get_nested_value(config, key) or default

    def set_config_value(self, config_name: str, key: str, value: Any) -> bool:
        """Set a configuration value"""
        if config_name not in self.configs:
            self.configs[config_name] = {}

        # Create a temporary config to validate
        temp_config = self.configs[config_name].copy()
        self._set_nested_value(temp_config, key, value)

        # Validate the change
        if self._validate_config(config_name, temp_config):
            old_value = self._get_nested_value(self.configs[config_name], key)
            self._set_nested_value(self.configs[config_name], key, value)

            # Trigger change callbacks
            self._trigger_change_callbacks(config_name, {key: old_value}, {key: value})

            return True

        return False

    def update_config(self, config_name: str, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        if config_name not in self.configs:
            self.configs[config_name] = {}

        # Create a temporary config to validate
        temp_config = self.configs[config_name].copy()

        old_values = {}
        for key, value in updates.items():
            old_values[key] = self._get_nested_value(temp_config, key)
            self._set_nested_value(temp_config, key, value)

        # Validate all changes
        if self._validate_config(config_name, temp_config):
            # Apply changes
            for key, value in updates.items():
                self._set_nested_value(self.configs[config_name], key, value)

            # Trigger change callbacks
            self._trigger_change_callbacks(config_name, old_values, updates)

            return True

        return False

    def save_config(self, config_name: str, format_type: ConfigFormat = ConfigFormat.YAML) -> bool:
        """Save configuration to file"""
        if config_name not in self.configs:
            logger.error(f"Configuration not found: {config_name}")
            return False

        try:
            # Determine file path
            if format_type == ConfigFormat.YAML:
                file_path = self.config_dir / f"{config_name}.yaml"
            elif format_type == ConfigFormat.JSON:
                file_path = self.config_dir / f"{config_name}.json"
            elif format_type == ConfigFormat.TOML:
                file_path = self.config_dir / f"{config_name}.toml"

            # Save configuration
            with open(file_path, "w") as f:
                if format_type == ConfigFormat.YAML:
                    yaml.dump(self.configs[config_name], f, default_flow_style=False, indent=2)
                elif format_type == ConfigFormat.JSON:
                    json.dump(self.configs[config_name], f, indent=2)
                elif format_type == ConfigFormat.TOML:
                    toml.dump(self.configs[config_name], f)

            logger.info(f"Saved configuration: {config_name} to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save config {config_name}: {str(e)}")
            return False

    def register_change_callback(self, config_name: str, callback: Callable):
        """Register a callback for configuration changes"""
        if config_name not in self.change_callbacks:
            self.change_callbacks[config_name] = []

        self.change_callbacks[config_name].append(callback)

    def _trigger_change_callbacks(self, config_name: str, old_values: Dict[str, Any], new_values: Dict[str, Any]):
        """Trigger change callbacks for configuration"""
        if config_name in self.change_callbacks:
            change_event = ConfigChangeEvent(
                timestamp=datetime.now(),
                config_path=config_name,
                changed_keys=list(new_values.keys()),
                old_values=old_values,
                new_values=new_values,
            )

            for callback in self.change_callbacks[config_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(change_event))
                    else:
                        callback(change_event)
                except Exception as e:
                    logger.error(f"Error in change callback: {str(e)}")

    def enable_hot_reload(self):
        """Enable hot-reloading of configuration files"""
        if self.hot_reload_enabled:
            return

        self.file_observer = Observer()
        event_handler = ConfigFileHandler(self)
        self.file_observer.schedule(event_handler, str(self.config_dir), recursive=False)
        self.file_observer.start()

        self.hot_reload_enabled = True
        logger.info("Hot-reload enabled for configuration files")

    def disable_hot_reload(self):
        """Disable hot-reloading of configuration files"""
        if not self.hot_reload_enabled:
            return

        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            self.file_observer = None

        self.hot_reload_enabled = False
        logger.info("Hot-reload disabled for configuration files")

    def _handle_file_change(self, file_path: str):
        """Handle file system change events"""
        path = Path(file_path)

        if path.parent == self.config_dir and path.suffix in [
            ".yaml",
            ".yml",
            ".json",
            ".toml",
        ]:
            logger.info(f"Configuration file changed: {path}")

            # Reload the configuration
            old_config = self.configs.get(path.stem, {}).copy()
            self._load_config_file(path)
            new_config = self.configs.get(path.stem, {})

            # Find changed keys
            changed_keys = self._find_changed_keys(old_config, new_config)

            if changed_keys:
                # Trigger callbacks
                old_values = {key: self._get_nested_value(old_config, key) for key in changed_keys}
                new_values = {key: self._get_nested_value(new_config, key) for key in changed_keys}

                self._trigger_change_callbacks(path.stem, old_values, new_values)

    def _find_changed_keys(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> List[str]:
        """Find keys that have changed between configurations"""
        changed_keys = []

        def compare_dicts(old_dict, new_dict, prefix=""):
            for key in set(old_dict.keys()) | set(new_dict.keys()):
                full_key = f"{prefix}.{key}" if prefix else key

                if key not in old_dict:
                    changed_keys.append(full_key)
                elif key not in new_dict:
                    changed_keys.append(full_key)
                elif isinstance(old_dict[key], dict) and isinstance(new_dict[key], dict):
                    compare_dicts(old_dict[key], new_dict[key], full_key)
                elif old_dict[key] != new_dict[key]:
                    changed_keys.append(full_key)

        compare_dicts(old_config, new_config)
        return changed_keys

    def create_default_config(self, config_name: str) -> bool:
        """Create a default configuration file"""
        default_configs = {
            "opal2_graphics": {
                "renderer": {
                    "default_engine": "webgl",
                    "quantum_enhancement": True,
                    "performance_mode": "balanced",
                },
                "canvas": {"width": 800, "height": 600, "background_color": "#000000"},
                "quantum": {
                    "coherence_factor": 0.8,
                    "entanglement_strength": 0.6,
                    "superposition_depth": 3,
                    "decoherence_rate": 0.1,
                },
                "effects": {
                    "particle_systems": True,
                    "field_visualization": True,
                    "interference_patterns": True,
                },
            },
            "plugin_system": {
                "plugins": {
                    "auto_load": True,
                    "directories": ["plugins", "modules/opal2/plugins"],
                    "blacklist": [],
                    "whitelist": [],
                },
                "security": {
                    "allow_dynamic_loading": True,
                    "require_signatures": False,
                    "sandbox_mode": False,
                },
            },
            "api": {
                "server": {"host": "0.0.0.0", "port": 8000, "debug": False},
                "cors": {"enabled": True, "origins": ["*"]},
                "rate_limiting": {"enabled": True, "requests_per_minute": 60},
                "websocket": {"enabled": True, "max_connections": 100},
            },
        }

        if config_name in default_configs:
            self.configs[config_name] = default_configs[config_name]
            return self.save_config(config_name)

        return False

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded configurations"""
        return self.configs.copy()

    def list_config_names(self) -> List[str]:
        """List all configuration names"""
        return list(self.configs.keys())

    def validate_all_configs(self) -> Dict[str, bool]:
        """Validate all loaded configurations"""
        results = {}

        for config_name, config_data in self.configs.items():
            results[config_name] = self._validate_config(config_name, config_data)

        return results

    def export_config(
        self,
        config_name: str,
        export_path: str,
        format_type: ConfigFormat = ConfigFormat.YAML,
    ) -> bool:
        """Export configuration to a specific path"""
        if config_name not in self.configs:
            return False

        try:
            export_path = Path(export_path)

            with open(export_path, "w") as f:
                if format_type == ConfigFormat.YAML:
                    yaml.dump(self.configs[config_name], f, default_flow_style=False, indent=2)
                elif format_type == ConfigFormat.JSON:
                    json.dump(self.configs[config_name], f, indent=2)
                elif format_type == ConfigFormat.TOML:
                    toml.dump(self.configs[config_name], f)

            return True

        except Exception as e:
            logger.error(f"Failed to export config {config_name}: {str(e)}")
            return False

    def import_config(self, config_name: str, import_path: str) -> bool:
        """Import configuration from a specific path"""
        try:
            import_path = Path(import_path)

            if not import_path.exists():
                return False

            # Temporarily load the config to validate
            temp_config_path = import_path
            self._load_config_file(temp_config_path)

            return config_name in self.configs

        except Exception as e:
            logger.error(f"Failed to import config {config_name}: {str(e)}")
            return False

    def __del__(self):
        """Cleanup when the configuration manager is destroyed"""
        if self.hot_reload_enabled:
            self.disable_hot_reload()
