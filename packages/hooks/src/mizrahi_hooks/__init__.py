"""
Mizrahi Validation Hooks

This package contains validation hooks for the Mizrahi Compliance Platform.
Each hook implements a specific validation workflow.
"""

from .base import BaseHook, HookConfig, CheckResult, HookResult
from .registry import register_hook, get_hook, list_hooks

__version__ = "1.0.0"

__all__ = [
    # Base classes
    "BaseHook",
    "HookConfig",
    "CheckResult",
    "HookResult",
    # Registry
    "register_hook",
    "get_hook",
    "list_hooks",
]

# Import hooks to trigger registration
from . import monthly_report
from . import special_transactions
