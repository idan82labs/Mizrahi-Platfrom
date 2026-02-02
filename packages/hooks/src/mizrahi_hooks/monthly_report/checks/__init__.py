"""
Monthly Report validation checks.

Each check is implemented as an async function that takes the data dictionary
and returns a CheckResult.
"""

from .completeness import check_completeness
from .unusual_assets import check_unusual_assets
from .new_assets import check_new_assets
from .quantity_changes import check_quantity_changes
from .clause_328 import check_clause_328
from .required_combinations import check_required_combinations
from .price_reasonableness import check_price_reasonableness

__all__ = [
    "check_completeness",
    "check_unusual_assets",
    "check_new_assets",
    "check_quantity_changes",
    "check_clause_328",
    "check_required_combinations",
    "check_price_reasonableness",
]
