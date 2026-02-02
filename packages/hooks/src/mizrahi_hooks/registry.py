"""
Hook registry for discovering and instantiating hooks.

This module provides:
- @register_hook decorator for registering hook classes
- get_hook() for retrieving hook instances
- list_hooks() for listing available hooks
"""

from typing import Dict, Type, Optional, List
import logging

from .base import BaseHook
from mizrahi_shared.models import HookConfig
from mizrahi_shared.config import get_hook_config

logger = logging.getLogger(__name__)

# Registry of all available hooks
_HOOK_REGISTRY: Dict[str, Type[BaseHook]] = {}


def register_hook(hook_id: str):
    """
    Decorator to register a hook class.

    Usage:
        @register_hook("monthly_report")
        class MonthlyReportHook(BaseHook):
            ...

    Args:
        hook_id: Unique identifier for the hook (must match hooks.yaml)

    Returns:
        Decorator function
    """
    def decorator(cls: Type[BaseHook]) -> Type[BaseHook]:
        if hook_id in _HOOK_REGISTRY:
            logger.warning(f"Hook '{hook_id}' already registered, overwriting")

        _HOOK_REGISTRY[hook_id] = cls
        logger.debug(f"Registered hook: {hook_id} -> {cls.__name__}")
        return cls

    return decorator


def get_hook(hook_id: str, config: Optional[HookConfig] = None) -> Optional[BaseHook]:
    """
    Get an instance of a hook by ID.

    Args:
        hook_id: The hook identifier
        config: Optional configuration. If not provided, loads from hooks.yaml

    Returns:
        Hook instance or None if not found
    """
    hook_class = _HOOK_REGISTRY.get(hook_id)

    if hook_class is None:
        logger.error(f"Hook not found: {hook_id}")
        return None

    # Load config if not provided
    if config is None:
        config = get_hook_config(hook_id)
        if config is None:
            logger.error(f"Configuration not found for hook: {hook_id}")
            return None

    return hook_class(config)


def list_hooks() -> List[str]:
    """
    List all registered hook IDs.

    Returns:
        List of hook IDs
    """
    return list(_HOOK_REGISTRY.keys())


def get_hook_class(hook_id: str) -> Optional[Type[BaseHook]]:
    """
    Get a hook class without instantiating.

    Args:
        hook_id: The hook identifier

    Returns:
        Hook class or None if not found
    """
    return _HOOK_REGISTRY.get(hook_id)


def get_all_hooks() -> Dict[str, Type[BaseHook]]:
    """
    Get all registered hooks.

    Returns:
        Dictionary mapping hook IDs to hook classes
    """
    return _HOOK_REGISTRY.copy()
