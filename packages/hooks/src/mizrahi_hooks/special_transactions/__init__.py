"""
Special Transactions Validation Hook

Hook #2: בקרה אוטומטית על דוח עסקאות מתואמות ועסקאות מחוץ לבורסה

Validates coordinated/off-exchange trades including:
- Inter-fund transactions (duplicates)
- Date validation
- Decision method compliance
- Price verification with TASE
- Problematic securities flagging
"""

from .hook import SpecialTransactionsHook

__all__ = ["SpecialTransactionsHook"]
