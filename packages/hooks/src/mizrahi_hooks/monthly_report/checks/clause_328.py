"""
Check #5: Clause 328 (סעיף 328)

Verify borrowed quantity consistency according to regulatory requirements.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "clause_328"
CHECK_NAME_HE = "סעיף 328"


async def check_clause_328(data: Dict[str, Any]) -> CheckResult:
    """
    Verify borrowed quantity consistency per Clause 328.

    Args:
        data: Dictionary containing:
            - current_report: Current month's report data

    Returns:
        CheckResult with clause 328 violations as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        current_report = data.get("current_report", [])

        for row in current_report:
            # Check borrowed quantity fields
            borrowed_qty = row.get("borrowed_quantity") or row.get("כמות מושאלת", 0)
            total_qty = row.get("quantity") or row.get("כמות", 0)

            try:
                borrowed_qty = float(borrowed_qty) if borrowed_qty else 0
                total_qty = float(total_qty) if total_qty else 0
            except (ValueError, TypeError):
                continue

            # Clause 328 violation: borrowed quantity exceeds total
            if borrowed_qty > total_qty and total_qty > 0:
                findings.append({
                    "מספר קרן": row.get("fund_id") or row.get("מספר קרן", ""),
                    "שם קרן": row.get("fund_name") or row.get("שם קרן", ""),
                    "מספר נכס": row.get("asset_id") or row.get("מספר נכס", ""),
                    "שם נכס": row.get("asset_name") or row.get("שם נכס", ""),
                    "כמות כוללת": total_qty,
                    "כמות מושאלת": borrowed_qty,
                    "סיבה": "כמות מושאלת עולה על כמות כוללת",
                })

        # Determine status
        if findings:
            status = "fail"
            message = f"נמצאו {len(findings)} חריגות לסעיף 328"
        else:
            status = "pass"
            message = "אין חריגות לסעיף 328"

        logger.info(f"Clause 328 check: {len(findings)} violations found")

        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status=status,
            message=message,
            findings_count=len(findings),
            findings=findings,
            duration_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        logger.exception(f"Clause 328 check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
