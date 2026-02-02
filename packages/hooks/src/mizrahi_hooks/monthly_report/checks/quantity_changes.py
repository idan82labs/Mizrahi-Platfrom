"""
Check #4: Quantity Changes (שינויים בכמות)

Identify unusual quantity changes between months.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "quantity_changes"
CHECK_NAME_HE = "שינויים בכמות"


async def check_quantity_changes(data: Dict[str, Any]) -> CheckResult:
    """
    Detect unusual quantity changes month-over-month.

    Args:
        data: Dictionary containing:
            - current_report: Current month's report data
            - previous_report: Previous month's report data

    Returns:
        CheckResult with quantity changes as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        current_report = data.get("current_report", [])
        previous_report = data.get("previous_report", [])

        # Build map of previous month quantities
        previous_quantities: Dict[tuple, float] = {}
        for row in previous_report:
            fund_id = str(row.get("fund_id") or row.get("מספר קרן", ""))
            asset_id = str(row.get("asset_id") or row.get("מספר נכס", ""))
            quantity = row.get("quantity") or row.get("כמות", 0)

            if fund_id and asset_id:
                try:
                    previous_quantities[(fund_id, asset_id)] = float(quantity)
                except (ValueError, TypeError):
                    pass

        # Compare with current month
        for row in current_report:
            fund_id = str(row.get("fund_id") or row.get("מספר קרן", ""))
            asset_id = str(row.get("asset_id") or row.get("מספר נכס", ""))
            current_quantity = row.get("quantity") or row.get("כמות", 0)

            if not fund_id or not asset_id:
                continue

            try:
                current_quantity = float(current_quantity)
            except (ValueError, TypeError):
                continue

            key = (fund_id, asset_id)
            if key in previous_quantities:
                previous_quantity = previous_quantities[key]

                # Calculate change
                if previous_quantity != 0:
                    change_pct = ((current_quantity - previous_quantity) / abs(previous_quantity)) * 100
                else:
                    change_pct = 100 if current_quantity != 0 else 0

                # Flag significant changes (> 50% change)
                if abs(change_pct) > 50:
                    findings.append({
                        "מספר קרן": fund_id,
                        "שם קרן": row.get("fund_name") or row.get("שם קרן", ""),
                        "מספר נכס": asset_id,
                        "שם נכס": row.get("asset_name") or row.get("שם נכס", ""),
                        "כמות קודמת": previous_quantity,
                        "כמות נוכחית": current_quantity,
                        "שינוי %": round(change_pct, 2),
                    })

        # Determine status
        if findings:
            status = "warning"
            message = f"נמצאו {len(findings)} שינויים משמעותיים בכמות"
        else:
            status = "pass"
            message = "לא נמצאו שינויים חריגים בכמות"

        logger.info(f"Quantity changes check: {len(findings)} significant changes found")

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
        logger.exception(f"Quantity changes check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
