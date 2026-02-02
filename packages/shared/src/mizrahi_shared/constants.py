"""
Constants for Mizrahi Compliance Platform.

These constants are derived from the YAML configuration files at runtime,
providing a single source of truth while maintaining backwards compatibility.
"""

from typing import Dict
from functools import lru_cache


@lru_cache(maxsize=1)
def _load_fund_managers() -> Dict[str, str]:
    """Load fund managers mapping from config."""
    try:
        from .config import get_managers
        managers = get_managers()
        return {m.name_he: m.id for m in managers.values()}
    except Exception:
        # Fallback to hardcoded values if config loading fails
        return {
            "מגדל": "10040",
            "איילון": "10054",
            "קסם": "10047",
            "סיגמא": "10048",
            "פורסט": "10082",
            "הראל": "10031",
            "אנליסט": "10019",
            "מיטב": "10083",
            "איביאי": "10068",
            "אלטשולר-שחם": "10017",
        }


@lru_cache(maxsize=1)
def _load_apify_actors() -> Dict[str, str]:
    """Load Apify actor IDs from config."""
    try:
        from .config import get_apify_config
        config = get_apify_config()
        return {
            "funds_list": config.get("funds_list_actor", "K9WppTziYC3n2vxTu"),
            "reports": config.get("reports_actor", "5lhI6O39Qbgv9O0gs"),
        }
    except Exception:
        # Fallback to hardcoded values
        return {
            "funds_list": "K9WppTziYC3n2vxTu",
            "reports": "5lhI6O39Qbgv9O0gs",
        }


class _FundManagersProxy:
    """
    Proxy class that lazily loads fund managers from config.
    Behaves like a dictionary for backwards compatibility.
    """

    def __getitem__(self, key: str) -> str:
        return _load_fund_managers()[key]

    def __contains__(self, key: str) -> bool:
        return key in _load_fund_managers()

    def __iter__(self):
        return iter(_load_fund_managers())

    def __len__(self) -> int:
        return len(_load_fund_managers())

    def keys(self):
        return _load_fund_managers().keys()

    def values(self):
        return _load_fund_managers().values()

    def items(self):
        return _load_fund_managers().items()

    def get(self, key: str, default=None):
        return _load_fund_managers().get(key, default)


class _ApifyActorsProxy:
    """Proxy class for Apify actor IDs."""

    def __getitem__(self, key: str) -> str:
        return _load_apify_actors()[key]

    def __contains__(self, key: str) -> bool:
        return key in _load_apify_actors()

    def get(self, key: str, default=None):
        return _load_apify_actors().get(key, default)


# Public constants - these behave like dictionaries but load from config
FUND_MANAGERS = _FundManagersProxy()
APIFY_ACTORS = _ApifyActorsProxy()

# Static constants (these don't change)
DEFAULT_TIMEZONE = "Asia/Jerusalem"
DEFAULT_PRICE_THRESHOLD = 5.0
DEFAULT_SAMPLE_SIZE = 5

# Event IDs for TASE Maya reports
EVENT_IDS = {
    "special_transactions": 5618,
    "monthly_holdings": 5615,  # Verify this
}

# Asset types considered unusual (for monthly report validation)
UNUSUAL_ASSET_TYPES = [
    16, 21, 22, 23, 24, 52, 53, 57, 58, 99, 101, 112, 201, 207, 209
]

# Required asset combinations (Clause 214)
REQUIRED_COMBINATIONS = {
    111: [38, 42, 45, 47, 49, 56],
    212: [326, 327],
    213: [319],
    208: [307],
    210: [310],
}

# Decision method rules for special transactions
DECISION_TYPES_REQUIRING_1 = {12, 22}
DECISION_TYPES_REQUIRING_1_OR_2 = {31, 32, 33, 34, 35, 36}
