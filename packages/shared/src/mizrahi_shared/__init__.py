"""
Mizrahi Shared Utilities

Common utilities, models, and services for the Mizrahi Compliance Platform.
"""

from .config import get_config, get_managers, get_hooks_config
from .constants import FUND_MANAGERS, APIFY_ACTORS
from .models import (
    Manager,
    HookConfig,
    CheckConfig,
    CheckResult,
    HookResult,
    JobStatus,
)

__version__ = "1.0.0"

__all__ = [
    # Config
    "get_config",
    "get_managers",
    "get_hooks_config",
    # Constants
    "FUND_MANAGERS",
    "APIFY_ACTORS",
    # Models
    "Manager",
    "HookConfig",
    "CheckConfig",
    "CheckResult",
    "HookResult",
    "JobStatus",
]
