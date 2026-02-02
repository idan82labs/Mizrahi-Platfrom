"""
Monthly Report Validation Hook

Hook #1: בקרה אוטומטית על דוח חודשי

Validates monthly fund holdings reports by:
- Cross-referencing funds between Magna list and Manager reports
- Identifying unusual asset types
- Detecting new assets and quantity changes
- Checking regulatory compliance (Clauses 214, 328)
- Validating price reasonableness
"""

from .hook import MonthlyReportHook

__all__ = ["MonthlyReportHook"]
