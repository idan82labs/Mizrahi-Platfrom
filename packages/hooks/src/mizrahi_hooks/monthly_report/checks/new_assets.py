"""
Check #3: New Assets (נכסים חדשים)

Detect new assets added since previous month.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "new_assets"
CHECK_NAME_HE = "נכסים חדשים"


async def check_new_assets(data: Dict[str, Any]) -> CheckResult:
    """
    Identify assets that appear in current month but not in previous month.

    Args:
        data: Dictionary containing:
            - current_report: Current month's report data
            - previous_report: Previous month's report data

    Returns:
        CheckResult with new assets as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        current_report = data.get("current_report", [])
        previous_report = data.get("previous_report", [])

        # Build set of previous month asset identifiers
        previous_assets = set()
        for row in previous_report:
            fund_id = row.get("fund_id") or row.get("מספר קרן", "")
            asset_id = row.get("asset_id") or row.get("מספר נכס", "")
            if fund_id and asset_id:
                previous_assets.add((str(fund_id), str(asset_id)))

        # Find new assets in current month
        for row in current_report:
            fund_id = row.get("fund_id") or row.get("מספר קרן", "")
            asset_id = row.get("asset_id") or row.get("מספר נכס", "")

            if fund_id and asset_id:
                key = (str(fund_id), str(asset_id))
                if key not in previous_assets:
                    findings.append({
                        "מספר קרן": fund_id,
                        "שם קרן": row.get("fund_name") or row.get("שם קרן", ""),
                        "מספר נכס": asset_id,
                        "שם נכס": row.get("asset_name") or row.get("שם נכס", ""),
                        "סוג נכס": row.get("asset_type") or row.get("סוג נכס", ""),
                        "שווי": row.get("value") or row.get("שווי", 0),
                    })

        # Determine status
        if findings:
            status = "warning"
            message = f"נמצאו {len(findings)} נכסים חדשים"
        else:
            status = "pass"
            message = "לא נמצאו נכסים חדשים"

        logger.info(f"New assets check: {len(findings)} new assets found")

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
        logger.exception(f"New assets check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
