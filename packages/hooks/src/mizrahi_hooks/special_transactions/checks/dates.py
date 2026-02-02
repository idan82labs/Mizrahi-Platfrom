"""
Check #3: Date Validation (חריגות תאריך)

Ensure transaction dates fall within the report month.
"""

import time
import logging
from datetime import datetime
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "chk3_dates"
CHECK_NAME_HE = "חריגות תאריך"


async def check_dates(data: Dict[str, Any]) -> CheckResult:
    """
    Validate that transaction dates fall within the report month.

    Args:
        data: Dictionary containing:
            - transactions: List of transaction records
            - report_month: Report month (YYYY-MM format or similar)

    Returns:
        CheckResult with date exceptions as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        transactions = data.get("transactions", [])
        report_month = data.get("report_month")

        # Parse report month to get expected date range
        if report_month:
            try:
                # Try different date formats
                if isinstance(report_month, str):
                    if "-" in report_month:
                        year, month = report_month.split("-")[:2]
                    else:
                        # Assume current month if not specified
                        now = datetime.now()
                        year, month = now.year, now.month
                else:
                    now = datetime.now()
                    year, month = now.year, now.month

                year, month = int(year), int(month)
            except (ValueError, AttributeError):
                now = datetime.now()
                year, month = now.year, now.month
        else:
            now = datetime.now()
            year, month = now.year, now.month

        # Calculate first and last day of month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1)
        else:
            last_day = datetime(year, month + 1, 1)

        for txn in transactions:
            txn_date_str = txn.get("transaction_date") or txn.get("תאריך", "")

            if not txn_date_str:
                continue

            try:
                # Parse transaction date (try multiple formats)
                txn_date = None
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y%m%d"]:
                    try:
                        txn_date = datetime.strptime(str(txn_date_str), fmt)
                        break
                    except ValueError:
                        continue

                if txn_date is None:
                    continue

                # Check if outside report month
                if txn_date < first_day or txn_date >= last_day:
                    findings.append({
                        "מספר ני\"ע": txn.get("security_no") or txn.get("מספר ני\"ע", ""),
                        "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                        "תאריך עסקה": str(txn_date_str),
                        "חודש דוח": f"{year}-{month:02d}",
                        "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                        "שם קרן": txn.get("fund_name") or txn.get("שם קרן", ""),
                        "סיבה": "תאריך מחוץ לחודש הדוח",
                    })

            except Exception as e:
                logger.debug(f"Could not parse date '{txn_date_str}': {e}")

        # Determine status
        if findings:
            status = "fail"
            message = f"נמצאו {len(findings)} עסקאות עם תאריך מחוץ לחודש הדוח"
        else:
            status = "pass"
            message = "כל התאריכים בטווח חודש הדוח"

        logger.info(f"Dates check: {len(findings)} date exceptions found")

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
        logger.exception(f"Dates check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
