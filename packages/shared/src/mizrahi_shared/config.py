"""
Configuration loader for YAML configuration files.

This module provides functions to load and access configuration from YAML files
in the config/ directory.
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, Optional

import yaml

from .models import Manager, HookConfig, CheckConfig


def _find_config_dir() -> Path:
    """Find the config directory relative to the project root."""
    # Try common locations
    candidates = [
        Path(__file__).parent.parent.parent.parent.parent.parent / "config",  # From package
        Path.cwd() / "config",  # From current directory
        Path(os.environ.get("CONFIG_DIR", "")) if os.environ.get("CONFIG_DIR") else None,
    ]

    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Config directory not found. Set CONFIG_DIR environment variable or run from project root."
    )


def _load_yaml(filename: str) -> Dict[str, Any]:
    """Load a YAML file from the config directory."""
    config_dir = _find_config_dir()
    filepath = config_dir / filename

    if not filepath.exists():
        raise FileNotFoundError(f"Config file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _substitute_env_vars(value: Any) -> Any:
    """Recursively substitute environment variables in config values."""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        return os.environ.get(env_var, value)
    elif isinstance(value, dict):
        return {k: _substitute_env_vars(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_substitute_env_vars(item) for item in value]
    return value


@lru_cache(maxsize=1)
def get_managers() -> Dict[str, Manager]:
    """
    Load fund managers configuration.

    Returns:
        Dictionary mapping manager key to Manager object.
    """
    data = _load_yaml("managers.yaml")
    managers = {}

    for key, config in data.get("managers", {}).items():
        managers[key] = Manager(
            key=key,
            id=config["id"],
            name_he=config["name_he"],
            name_en=config["name_en"],
            enabled=config.get("enabled", True),
        )

    return managers


def get_manager_by_id(manager_id: str) -> Optional[Manager]:
    """Get a manager by their ID."""
    managers = get_managers()
    for manager in managers.values():
        if manager.id == manager_id:
            return manager
    return None


def get_manager_by_name_he(name_he: str) -> Optional[Manager]:
    """Get a manager by their Hebrew name."""
    managers = get_managers()
    for manager in managers.values():
        if manager.name_he == name_he:
            return manager
    return None


@lru_cache(maxsize=1)
def get_hooks_config() -> Dict[str, HookConfig]:
    """
    Load hooks configuration.

    Returns:
        Dictionary mapping hook ID to HookConfig object.
    """
    data = _load_yaml("hooks.yaml")
    hooks = {}
    defaults = data.get("defaults", {})

    for hook_id, config in data.get("hooks", {}).items():
        schedule = config.get("schedule", {})
        email = config.get("email", {})

        checks = [
            CheckConfig(
                id=c["id"],
                name_he=c.get("name_he", c["id"]),
                description=c.get("description", ""),
                enabled=c.get("enabled", True),
            )
            for c in config.get("checks", [])
        ]

        hooks[hook_id] = HookConfig(
            id=hook_id,
            name=config.get("name", hook_id),
            name_he=config.get("name_he", config.get("name", hook_id)),
            description=config.get("description", ""),
            status=config.get("status", "specification"),
            schedule_enabled=schedule.get("enabled", False),
            schedule_cron=schedule.get("cron"),
            schedule_timezone=schedule.get("timezone", defaults.get("timezone", "UTC")),
            parameters=config.get("parameters", {}),
            checks=checks,
            email_enabled=email.get("enabled", False),
            email_template=email.get("template", hook_id),
            email_cc=email.get("cc", []),
        )

    return hooks


def get_hook_config(hook_id: str) -> Optional[HookConfig]:
    """Get configuration for a specific hook."""
    hooks = get_hooks_config()
    return hooks.get(hook_id)


@lru_cache(maxsize=1)
def get_apify_config() -> Dict[str, Any]:
    """Get Apify configuration."""
    data = _load_yaml("managers.yaml")
    return data.get("apify", {})


def get_config(environment: Optional[str] = None) -> Dict[str, Any]:
    """
    Load environment-specific configuration.

    Args:
        environment: Environment name (development, staging, production).
                    If not provided, uses ENVIRONMENT env var or defaults to development.

    Returns:
        Dictionary with environment configuration.
    """
    if environment is None:
        environment = os.environ.get("ENVIRONMENT", "development")

    try:
        config = _load_yaml(f"environments/{environment}.yaml")
        return _substitute_env_vars(config)
    except FileNotFoundError:
        # Return minimal default config
        return {
            "environment": environment,
            "server": {"host": "127.0.0.1", "port": 8000},
            "database": {"url": "sqlite:///./dev.db"},
        }


def clear_config_cache():
    """Clear cached configuration (useful for testing)."""
    get_managers.cache_clear()
    get_hooks_config.cache_clear()
    get_apify_config.cache_clear()
